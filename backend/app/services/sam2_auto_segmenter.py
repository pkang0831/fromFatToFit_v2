"""
SAM2 auto-segmenter: proposal → filter → pose-guided semantic labeling.

Pipeline
--------
1. **Pose detection** — MediaPipe PoseLandmarker finds the person's skeleton.
   This gives us a bounding box and per-body-part reference regions.
2. **SAM2 mask proposals** — Replicate's SAM2 auto-segments the full image
   into class-agnostic masks (object proposals).
3. **Proposal filtering** — each SAM2 mask is scored for "person-ness"
   using overlap with the person bbox.  Masks below threshold are rejected
   early and tagged with a rejection reason.
4. **Semantic labeling** — accepted masks are assigned a body-part class
   via a multi-signal scorer (pose-region overlap, centroid distance to
   landmark, class-specific gating rules).  Best-class wins.
5. **Label-map assembly** — accepted masks are composited into a final
   label map.  Smaller masks paint last (higher priority) so that
   specific regions (e.g. shoulder) override broader ones (e.g. chest).
6. **Foreground & editable-region masks** — the union of accepted masks
   gives the foreground; a morphological dilation gives the safe edit zone.
7. **Candidate-segment export** — every proposal (accepted or rejected) is
   serialized with its metadata so the frontend can offer click-to-reassign.

Anatomical convention
---------------------
left/right = person's anatomical left/right.
Mirror-selfie detection is NOT implemented.  The user corrects laterality
in the editor if needed.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
import os
import urllib.request
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image, ImageOps

from .replicate_utils import (
    curl_json,
    get_replicate_api_key,
    image_to_data_uri,
    poll_prediction,
    curl_download,
)
from .segmenter_interface import (
    SegmenterAdapter,
    SegmentationResult,
    CandidateSegment,
    SEG_CLASSES,
)

logger = logging.getLogger(__name__)

# ── Replicate SAM2 config ────────────────────────────────────────────────────

SAM2_PREDICTIONS_URL = "https://api.replicate.com/v1/predictions"
SAM2_VERSION = "fe97b453a6455861e3bac769b441ca1f1086110da7466dbb65cf1eecfd60dc83"

# ── MediaPipe PoseLandmarker config ──────────────────────────────────────────

_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
_MODEL_PATH = "/tmp/pose_landmarker_heavy.task"
_landmarker: Optional[vision.PoseLandmarker] = None

# Landmark indices we use
LM_NOSE = 0
LM_LEFT_EAR = 7
LM_RIGHT_EAR = 8
LM_LEFT_SHOULDER = 11
LM_RIGHT_SHOULDER = 12
LM_LEFT_ELBOW = 13
LM_RIGHT_ELBOW = 14
LM_LEFT_WRIST = 15
LM_RIGHT_WRIST = 16
LM_LEFT_HIP = 23
LM_RIGHT_HIP = 24

# Minimum overlap with the person bbox to consider a mask "near the person"
_PERSON_OVERLAP_THRESHOLD = 0.35
# Minimum area fraction of person bbox for a mask to be useful
_MIN_PERSON_AREA_FRAC = 0.003
# Maximum area fraction of person bbox — reject whole-body / background blobs
_MAX_PERSON_AREA_FRAC = 0.70
# Minimum semantic assignment score to accept a mask
_MIN_ASSIGNMENT_SCORE = 0.08
# Dilation kernel size for editable region (pixels)
_EDITABLE_REGION_DILATE_PX = 40


# ═══════════════════════════════════════════════════════════════════════════════
# § 1  MediaPipe Pose
# ═══════════════════════════════════════════════════════════════════════════════

def _get_landmarker() -> vision.PoseLandmarker:
    global _landmarker
    if _landmarker is None:
        if not os.path.exists(_MODEL_PATH):
            logger.info("Downloading pose_landmarker_heavy model…")
            urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            num_poses=1,
        )
        _landmarker = vision.PoseLandmarker.create_from_options(options)
    return _landmarker


def _detect_pose(image_bgr: np.ndarray):
    """Return the first detected pose's landmark list, or None."""
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = _get_landmarker().detect(mp_image)
    if not result.pose_landmarks or len(result.pose_landmarks) == 0:
        return None
    return result.pose_landmarks[0]


def _lm_px(lm, w: int, h: int) -> tuple[int, int]:
    """Normalized landmark → clamped pixel coords."""
    return (
        max(0, min(w - 1, int(lm.x * w))),
        max(0, min(h - 1, int(lm.y * h))),
    )


def _vis(landmarks, idx: int, threshold: float = 0.3) -> bool:
    return landmarks[idx].visibility > threshold


def _person_bbox(landmarks, w: int, h: int, margin: float = 0.10):
    """Bounding box of visible landmarks, expanded by *margin* fraction."""
    xs, ys = [], []
    for lm in landmarks:
        if lm.visibility < 0.3:
            continue
        xs.append(lm.x * w)
        ys.append(lm.y * h)
    if not xs:
        return 0, 0, w, h
    mx, my = margin * w, margin * h
    return (
        max(0, int(min(xs) - mx)),
        max(0, int(min(ys) - my)),
        min(w, int(max(xs) + mx)),
        min(h, int(max(ys) + my)),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# § 2  Pose-derived body-part reference regions
# ═══════════════════════════════════════════════════════════════════════════════

def _build_body_part_regions(landmarks, w: int, h: int) -> dict[int, np.ndarray]:
    """Approximate body-part masks derived from pose landmarks.

    Each region is a bool (H, W) array.  These are NOT the final masks —
    they are "expected zones" used to score SAM2 proposals.
    """
    regions: dict[int, np.ndarray] = {}
    px = lambda idx: _lm_px(landmarks[idx], w, h)
    vis = lambda idx: _vis(landmarks, idx)

    # --- Head: circle around nose, extended upward ---
    if vis(LM_NOSE) and vis(LM_LEFT_SHOULDER) and vis(LM_RIGHT_SHOULDER):
        nose = px(LM_NOSE)
        ls, rs = px(LM_LEFT_SHOULDER), px(LM_RIGHT_SHOULDER)
        shoulder_w = abs(ls[0] - rs[0])
        head_r = max(int(shoulder_w * 0.55), 30)
        m = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(m, nose, head_r, 255, -1)
        top_y = max(0, nose[1] - int(head_r * 1.5))
        cv2.rectangle(m, (nose[0] - head_r, top_y), (nose[0] + head_r, nose[1]), 255, -1)
        regions[1] = m > 0

    # --- Chest: shoulders → mid-torso ---
    if vis(LM_LEFT_SHOULDER) and vis(LM_RIGHT_SHOULDER) and vis(LM_LEFT_HIP) and vis(LM_RIGHT_HIP):
        ls, rs = px(LM_LEFT_SHOULDER), px(LM_RIGHT_SHOULDER)
        lh, rh = px(LM_LEFT_HIP), px(LM_RIGHT_HIP)
        mid_y = (ls[1] + rs[1] + lh[1] + rh[1]) // 4
        pts = np.array([ls, rs, (rs[0], mid_y), (ls[0], mid_y)], dtype=np.int32)
        m = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(m, pts, 255)
        regions[2] = m > 0

    # --- Torso: mid-torso → hips ---
    if vis(LM_LEFT_SHOULDER) and vis(LM_RIGHT_SHOULDER) and vis(LM_LEFT_HIP) and vis(LM_RIGHT_HIP):
        ls, rs = px(LM_LEFT_SHOULDER), px(LM_RIGHT_SHOULDER)
        lh, rh = px(LM_LEFT_HIP), px(LM_RIGHT_HIP)
        mid_y = (ls[1] + rs[1] + lh[1] + rh[1]) // 4
        pts = np.array([(ls[0], mid_y), (rs[0], mid_y), rh, lh], dtype=np.int32)
        m = np.zeros((h, w), dtype=np.uint8)
        cv2.fillConvexPoly(m, pts, 255)
        regions[3] = m > 0

    # --- Shoulders (circles around shoulder landmarks) ---
    for cls_id, s_idx, e_idx in [(4, LM_LEFT_SHOULDER, LM_LEFT_ELBOW),
                                  (5, LM_RIGHT_SHOULDER, LM_RIGHT_ELBOW)]:
        if vis(s_idx) and vis(e_idx):
            sp, ep = px(s_idx), px(e_idx)
            r = max(int(abs(sp[0] - ep[0]) * 0.5), 20)
            m = np.zeros((h, w), dtype=np.uint8)
            cv2.circle(m, sp, r, 255, -1)
            regions[cls_id] = m > 0

    # --- Arms (corridor from shoulder → elbow → wrist) ---
    def _arm_corridor(s_idx, e_idx, w_idx, cls_id):
        if not (vis(s_idx) and vis(e_idx)):
            return
        sp, ep = px(s_idx), px(e_idx)
        wp = px(w_idx) if vis(w_idx) else ep
        other_s = LM_RIGHT_SHOULDER if s_idx == LM_LEFT_SHOULDER else LM_LEFT_SHOULDER
        arm_w = max(20, int(abs(sp[0] - px(other_s)[0]) * 0.25)) if vis(other_s) else 25
        m = np.zeros((h, w), dtype=np.uint8)
        for p1, p2 in [(sp, ep), (ep, wp)]:
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            length = max(1, int((dx**2 + dy**2) ** 0.5))
            nx, ny = -dy / length, dx / length
            pts = np.array([
                [p1[0] + nx * arm_w, p1[1] + ny * arm_w],
                [p1[0] - nx * arm_w, p1[1] - ny * arm_w],
                [p2[0] - nx * arm_w, p2[1] - ny * arm_w],
                [p2[0] + nx * arm_w, p2[1] + ny * arm_w],
            ], dtype=np.int32)
            cv2.fillConvexPoly(m, pts, 255)
        regions[cls_id] = m > 0

    _arm_corridor(LM_LEFT_SHOULDER, LM_LEFT_ELBOW, LM_LEFT_WRIST, 6)
    _arm_corridor(LM_RIGHT_SHOULDER, LM_RIGHT_ELBOW, LM_RIGHT_WRIST, 7)

    return regions


def _landmark_pixel_map(landmarks, w: int, h: int) -> dict[int, tuple[int, int]]:
    """Map class_id → representative landmark in pixel coords.

    Used for centroid-distance scoring.
    """
    px = lambda idx: _lm_px(landmarks[idx], w, h)
    vis = lambda idx: _vis(landmarks, idx)
    m: dict[int, tuple[int, int]] = {}
    if vis(LM_NOSE):
        m[1] = px(LM_NOSE)
    if vis(LM_LEFT_SHOULDER) and vis(LM_RIGHT_SHOULDER):
        ls, rs = px(LM_LEFT_SHOULDER), px(LM_RIGHT_SHOULDER)
        m[2] = ((ls[0] + rs[0]) // 2, (ls[1] + rs[1]) // 2)
    if vis(LM_LEFT_HIP) and vis(LM_RIGHT_HIP):
        lh, rh = px(LM_LEFT_HIP), px(LM_RIGHT_HIP)
        mid_chest = m.get(2, (w // 2, h // 3))
        m[3] = ((lh[0] + rh[0] + mid_chest[0]) // 3,
                (lh[1] + rh[1] + mid_chest[1]) // 3)
    if vis(LM_LEFT_SHOULDER):
        m[4] = px(LM_LEFT_SHOULDER)
    if vis(LM_RIGHT_SHOULDER):
        m[5] = px(LM_RIGHT_SHOULDER)
    if vis(LM_LEFT_ELBOW):
        m[6] = px(LM_LEFT_ELBOW)
    if vis(LM_RIGHT_ELBOW):
        m[7] = px(LM_RIGHT_ELBOW)
    return m


# ═══════════════════════════════════════════════════════════════════════════════
# § 3  Mask utilities
# ═══════════════════════════════════════════════════════════════════════════════

def _download_mask_np(url: str, target_size: tuple[int, int]) -> np.ndarray:
    """Download a mask PNG → (H, W) bool array at *target_size*."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        curl_download(url, tmp_path)
        img = Image.open(tmp_path).convert("L").resize(target_size, Image.NEAREST)
        return np.array(img) > 128
    finally:
        os.unlink(tmp_path)


def _mask_stats(mask: np.ndarray, w: int, h: int) -> dict:
    """Compute centroid (normalized), bbox, and area for a bool mask."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return {"cx": 0.5, "cy": 0.5, "area": 0,
                "bbox": (0, 0, 0, 0)}
    return {
        "cx": float(xs.mean()) / w,
        "cy": float(ys.mean()) / h,
        "area": int(len(ys)),
        "bbox": (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),
    }


def _mask_overlap_fraction(mask: np.ndarray, region: np.ndarray) -> float:
    """Fraction of *mask* pixels that fall inside *region*."""
    n = mask.sum()
    if n == 0:
        return 0.0
    return float((mask & region).sum()) / float(n)


def _mask_to_rle(mask: np.ndarray) -> str:
    """Encode a bool (H, W) mask as a compact COCO-style RLE string.

    Format: comma-separated run lengths starting from 0-pixels.
    """
    flat = mask.ravel().astype(np.uint8)
    if len(flat) == 0:
        return ""
    diffs = np.diff(flat)
    change_idx = np.where(diffs != 0)[0] + 1
    runs_starts = np.concatenate([[0], change_idx])
    runs_ends = np.concatenate([change_idx, [len(flat)]])
    run_lengths = runs_ends - runs_starts
    # RLE convention: first run is for value=0.
    # If mask starts with 1, prepend a 0-length run for value=0.
    if flat[0] == 1:
        run_lengths = np.concatenate([[0], run_lengths])
    return ",".join(str(int(r)) for r in run_lengths)


def _mask_to_png_b64(mask: np.ndarray) -> str:
    """Bool (H, W) mask → base64 grayscale PNG."""
    img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _label_map_to_png_b64(label_map: np.ndarray) -> str:
    """uint8 (H, W) label map → base64 grayscale PNG."""
    img = Image.fromarray(label_map, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# § 4  Proposal filtering
# ═══════════════════════════════════════════════════════════════════════════════

def _person_region_mask(bbox: tuple[int, int, int, int], h: int, w: int) -> np.ndarray:
    """Create a bool mask for the person bounding box."""
    m = np.zeros((h, w), dtype=bool)
    x0, y0, x1, y1 = bbox
    m[y0:y1, x0:x1] = True
    return m


def _filter_proposals(
    masks: list[np.ndarray],
    person_bbox: tuple[int, int, int, int],
    img_w: int,
    img_h: int,
) -> list[tuple[np.ndarray, dict, Optional[str]]]:
    """Score each SAM2 mask for person-ness and return (mask, stats, rejection_reason).

    Rejection reasons:
      - "empty": zero pixels
      - "too_small": < _MIN_PERSON_AREA_FRAC of person bbox
      - "too_large": > _MAX_PERSON_AREA_FRAC of person bbox
      - "low_person_overlap": < _PERSON_OVERLAP_THRESHOLD overlap with person bbox
    """
    person_mask = _person_region_mask(person_bbox, img_h, img_w)
    bbox_area = max(1, (person_bbox[2] - person_bbox[0]) * (person_bbox[3] - person_bbox[1]))

    results: list[tuple[np.ndarray, dict, Optional[str]]] = []

    for mask in masks:
        stats = _mask_stats(mask, img_w, img_h)

        if stats["area"] == 0:
            results.append((mask, stats, "empty"))
            continue

        bbox_frac = stats["area"] / bbox_area
        if bbox_frac < _MIN_PERSON_AREA_FRAC:
            results.append((mask, stats, "too_small"))
            continue
        if bbox_frac > _MAX_PERSON_AREA_FRAC:
            results.append((mask, stats, "too_large"))
            continue

        overlap = _mask_overlap_fraction(mask, person_mask)
        if overlap < _PERSON_OVERLAP_THRESHOLD:
            results.append((mask, stats, "low_person_overlap"))
            continue

        results.append((mask, stats, None))

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# § 5  Multi-signal semantic labeling
# ═══════════════════════════════════════════════════════════════════════════════

def _class_specific_gate(cls_id: int, cx: float, cy: float, area_frac: float) -> bool:
    """Return False if the mask's position/size is physically implausible for *cls_id*.

    These gates prevent obviously wrong assignments even when overlap is high
    (e.g. a huge mask getting labeled "head").
    """
    if cls_id == 1:  # head must be in upper portion, not too large
        return cy < 0.40 and area_frac < 0.15
    if cls_id == 2:  # chest must be in upper-center
        return 0.10 < cy < 0.55 and area_frac < 0.30
    if cls_id == 3:  # torso is mid-body
        return 0.20 < cy < 0.75
    if cls_id in (4, 5):  # shoulders: upper body
        return 0.08 < cy < 0.50 and area_frac < 0.15
    if cls_id in (6, 7):  # arms: not too large, not dead center
        return area_frac < 0.20
    return True


def _score_mask_for_class(
    mask: np.ndarray,
    stats: dict,
    cls_id: int,
    region: np.ndarray,
    landmark_px: Optional[tuple[int, int]],
    person_bbox: tuple[int, int, int, int],
    img_w: int,
    img_h: int,
) -> float:
    """Multi-signal score ∈ [0, 1] for assigning *mask* to *cls_id*.

    Signals combined:
      - region_overlap (weight 0.50): fraction of mask inside the pose-derived region
      - centroid_proximity (weight 0.30): closeness of mask centroid to the class landmark
      - class_gate (weight 0.20): binary gate based on position plausibility
    """
    bbox_area = max(1, (person_bbox[2] - person_bbox[0]) * (person_bbox[3] - person_bbox[1]))
    area_frac = stats["area"] / bbox_area

    # Gate check — hard reject if physically implausible
    if not _class_specific_gate(cls_id, stats["cx"], stats["cy"], area_frac):
        return 0.0

    # Signal 1: region overlap
    overlap = _mask_overlap_fraction(mask, region)

    # Signal 2: centroid proximity to reference landmark
    centroid_score = 0.0
    if landmark_px is not None:
        lx_n = landmark_px[0] / max(1, img_w)
        ly_n = landmark_px[1] / max(1, img_h)
        dist = ((stats["cx"] - lx_n) ** 2 + (stats["cy"] - ly_n) ** 2) ** 0.5
        # Map distance to score: 0 distance → 1.0, >0.4 distance → 0.0
        centroid_score = max(0.0, 1.0 - dist / 0.4)

    # Signal 3: gate passes → bonus
    gate_score = 1.0  # already passed the hard gate above

    return 0.50 * overlap + 0.30 * centroid_score + 0.20 * gate_score


def _assign_classes_pose(
    proposals: list[tuple[np.ndarray, dict, Optional[str]]],
    regions: dict[int, np.ndarray],
    landmark_map: dict[int, tuple[int, int]],
    person_bbox: tuple[int, int, int, int],
    img_w: int,
    img_h: int,
) -> list[CandidateSegment]:
    """Assign body-part classes to accepted proposals using multi-signal scoring."""
    candidates: list[CandidateSegment] = []

    for seg_id, (mask, stats, rejection) in enumerate(proposals):
        if rejection is not None:
            candidates.append(CandidateSegment(
                segment_id=seg_id,
                assigned_class=0,
                score=0.0,
                bbox=stats["bbox"],
                area=stats["area"],
                centroid=(stats["cx"], stats["cy"]),
                mask_rle=_mask_to_rle(mask),
                rejection_reason=rejection,
            ))
            continue

        best_class = 0
        best_score = _MIN_ASSIGNMENT_SCORE

        for cls_id, region in regions.items():
            score = _score_mask_for_class(
                mask, stats, cls_id, region,
                landmark_map.get(cls_id),
                person_bbox, img_w, img_h,
            )
            if score > best_score:
                best_score = score
                best_class = cls_id

        if best_class == 0:
            rejection = "no_class_above_threshold"

        candidates.append(CandidateSegment(
            segment_id=seg_id,
            assigned_class=best_class,
            score=best_score,
            bbox=stats["bbox"],
            area=stats["area"],
            centroid=(stats["cx"], stats["cy"]),
            mask_rle=_mask_to_rle(mask),
            rejection_reason=rejection,
        ))

    return candidates


def _assign_classes_fallback(
    proposals: list[tuple[np.ndarray, dict, Optional[str]]],
    img_w: int,
    img_h: int,
) -> list[CandidateSegment]:
    """Fallback assignment when pose is unavailable: centroid-only heuristic.

    Only assigns head (1), chest (2), and torso (3).
    """
    candidates: list[CandidateSegment] = []

    for seg_id, (mask, stats, rejection) in enumerate(proposals):
        if rejection is not None:
            candidates.append(CandidateSegment(
                segment_id=seg_id, assigned_class=0, score=0.0,
                bbox=stats["bbox"], area=stats["area"],
                centroid=(stats["cx"], stats["cy"]),
                mask_rle=_mask_to_rle(mask),
                rejection_reason=rejection,
            ))
            continue

        cx, cy = stats["cx"], stats["cy"]
        area_frac = stats["area"] / (img_w * img_h)
        cls_id, score = 0, 0.0

        if cy < 0.22 and area_frac < 0.10:
            cls_id, score = 1, 0.5
        elif 0.20 < cy < 0.45 and 0.30 < cx < 0.70 and area_frac < 0.15:
            cls_id, score = 2, 0.4
        elif 0.35 < cy < 0.65 and 0.30 < cx < 0.70:
            cls_id, score = 3, 0.35

        reason = None if cls_id > 0 else "no_class_above_threshold"
        candidates.append(CandidateSegment(
            segment_id=seg_id, assigned_class=cls_id, score=score,
            bbox=stats["bbox"], area=stats["area"],
            centroid=(stats["cx"], stats["cy"]),
            mask_rle=_mask_to_rle(mask),
            rejection_reason=reason,
        ))

    return candidates


# ═══════════════════════════════════════════════════════════════════════════════
# § 6  Label-map + foreground + editable region assembly
# ═══════════════════════════════════════════════════════════════════════════════

def _assemble_label_map(
    candidates: list[CandidateSegment],
    masks: list[np.ndarray],
    img_w: int,
    img_h: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Build (label_map, foreground_mask, editable_region) from scored candidates.

    Returns:
        label_map: uint8 (H, W) with class IDs
        foreground: bool (H, W) union of all accepted masks
        editable:   bool (H, W) dilated foreground
    """
    label_map = np.zeros((img_h, img_w), dtype=np.uint8)
    foreground = np.zeros((img_h, img_w), dtype=bool)

    # Collect accepted masks sorted by area desc (largest painted first,
    # smallest painted last = highest priority).
    accepted = [
        (c, masks[c.segment_id])
        for c in candidates
        if c.assigned_class > 0 and c.rejection_reason is None
    ]
    accepted.sort(key=lambda t: -t[0].area)

    for cand, mask in accepted:
        label_map[mask] = cand.assigned_class
        foreground |= mask

    # Editable region = dilated foreground
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (_EDITABLE_REGION_DILATE_PX, _EDITABLE_REGION_DILATE_PX),
    )
    editable = cv2.dilate(foreground.astype(np.uint8), kernel, iterations=1) > 0

    return label_map, foreground, editable


# ═══════════════════════════════════════════════════════════════════════════════
# § 7  SAM2 adapter
# ═══════════════════════════════════════════════════════════════════════════════

class SAM2AutoSegmenter(SegmenterAdapter):
    """Proposal → filter → pose-guided semantic labeling pipeline."""

    async def segment(self, image_base64: str) -> SegmentationResult:
        api_key = get_replicate_api_key()

        raw = base64.b64decode(image_base64)
        pil_img = Image.open(io.BytesIO(raw))

        # Apply EXIF orientation so phone photos are upright before any
        # processing.  Without this, portrait photos may be rotated 90°
        # and pose detection / region assignment will fail.
        pil_img = ImageOps.exif_transpose(pil_img) or pil_img
        pil_img = pil_img.convert("RGB")

        img_w, img_h = pil_img.size
        logger.info(f"SAM2 pipeline start: {img_w}×{img_h} (after EXIF transpose)")

        # Re-encode the orientation-corrected image so SAM2 also receives
        # the upright version (the original base64 may have EXIF rotation
        # that SAM2's server might or might not respect).
        corrected_buf = io.BytesIO()
        pil_img.save(corrected_buf, format="JPEG", quality=92)
        corrected_b64 = base64.b64encode(corrected_buf.getvalue()).decode()

        # ── Step 1: Pose detection ────────────────────────────────────────
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        landmarks = _detect_pose(img_bgr)
        use_pose = landmarks is not None

        person_bbox = (0, 0, img_w, img_h)
        regions: dict[int, np.ndarray] = {}
        landmark_map: dict[int, tuple[int, int]] = {}

        if use_pose:
            person_bbox = _person_bbox(landmarks, img_w, img_h)
            regions = _build_body_part_regions(landmarks, img_w, img_h)
            landmark_map = _landmark_pixel_map(landmarks, img_w, img_h)
            logger.info(f"Pose OK: bbox={person_bbox}, regions={sorted(regions.keys())}")
        else:
            logger.warning("No pose detected — using centroid fallback")

        # ── Step 2: SAM2 mask proposals ───────────────────────────────────
        data_uri = image_to_data_uri(corrected_b64, "jpeg")
        payload = {
            "version": SAM2_VERSION,
            "input": {
                "image": data_uri,
                "points_per_side": 32,
                "pred_iou_thresh": 0.86,
                "stability_score_thresh": 0.92,
                "use_m2m": True,
            },
        }

        loop = asyncio.get_event_loop()
        pred = await loop.run_in_executor(
            None, curl_json, "POST", SAM2_PREDICTIONS_URL, api_key, payload,
        )

        pred_id = pred.get("id")
        if not pred_id:
            raise RuntimeError(f"SAM2 prediction failed: {pred.get('detail', str(pred)[:300])}")

        if pred.get("status") != "succeeded":
            poll_url = pred.get("urls", {}).get(
                "get", f"https://api.replicate.com/v1/predictions/{pred_id}",
            )
            pred = await poll_prediction(poll_url, api_key, max_polls=90, interval=2.0)

        output = pred.get("output", {})
        mask_urls = output.get("individual_masks", [])
        if not mask_urls:
            combined = output.get("combined_mask")
            if combined:
                mask_urls = [combined]
            else:
                raise RuntimeError("SAM2 returned no masks")

        logger.info(f"SAM2 returned {len(mask_urls)} masks, downloading…")

        np_masks: list[np.ndarray] = []
        for url in mask_urls:
            try:
                m = await loop.run_in_executor(
                    None, _download_mask_np, url, (img_w, img_h),
                )
                np_masks.append(m)
            except Exception as e:
                logger.warning(f"Mask download failed: {e}")

        # ── Step 3: Filter proposals ──────────────────────────────────────
        proposals = _filter_proposals(np_masks, person_bbox, img_w, img_h)

        accepted_count = sum(1 for _, _, r in proposals if r is None)
        rejected_count = len(proposals) - accepted_count
        logger.info(f"Proposals: {accepted_count} accepted, {rejected_count} rejected")

        # ── Step 4: Semantic labeling ─────────────────────────────────────
        if use_pose and regions:
            candidates = _assign_classes_pose(
                proposals, regions, landmark_map, person_bbox, img_w, img_h,
            )
        else:
            candidates = _assign_classes_fallback(proposals, img_w, img_h)

        # ── Step 5: Assemble outputs ──────────────────────────────────────
        label_map, foreground, editable = _assemble_label_map(
            candidates, np_masks, img_w, img_h,
        )

        unique_classes = set(int(v) for v in np.unique(label_map) if v > 0)
        labeled_pixels = int(np.count_nonzero(label_map))
        fg_pixels = int(foreground.sum())

        logger.info(
            f"Pipeline done: {len(unique_classes)} classes, "
            f"{labeled_pixels} labeled px, {fg_pixels} foreground px, "
            f"pose_guided={use_pose}"
        )

        # ── Build debug info ──────────────────────────────────────────────
        rejection_reasons: dict[str, int] = {}
        for c in candidates:
            if c.rejection_reason:
                rejection_reasons[c.rejection_reason] = (
                    rejection_reasons.get(c.rejection_reason, 0) + 1
                )

        debug_info = {
            "total_sam_masks": len(mask_urls),
            "downloaded": len(np_masks),
            "accepted": accepted_count,
            "rejected": rejected_count,
            "rejection_breakdown": rejection_reasons,
            "assigned_classes": sorted(unique_classes),
            "labeled_pixels": labeled_pixels,
            "foreground_pixels": fg_pixels,
            "pose_detected": use_pose,
            "person_bbox": list(person_bbox),
        }

        return SegmentationResult(
            width=img_w,
            height=img_h,
            label_map_b64=_label_map_to_png_b64(label_map),
            foreground_mask_b64=_mask_to_png_b64(foreground),
            editable_region_b64=_mask_to_png_b64(editable),
            classes=SEG_CLASSES,
            candidate_segments=[c.to_dict() for c in candidates],
            debug_info=debug_info,
        )
