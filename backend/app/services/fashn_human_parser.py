"""
Body-part segmenter using fashn-ai/fashn-human-parser (SegFormer-B4).

Replaces SAM2 + heuristic pipeline.  Runs locally on CPU — no API calls,
no cost, 1-3 seconds per image.  The model directly outputs semantic
class labels for human body parts, so no post-hoc heuristic is needed.

fashn-human-parser label IDs:
  0  background    1  face      2  hair       3  top
  4  dress         5  skirt     6  pants      7  belt
  8  bag           9  hat      10  scarf     11  glasses
 12  arms         13  hands    14  legs      15  feet
 16  torso        17  jewelry

We map these to our 8-class SEG_CLASSES scheme:
  0  background   (fashn 0 + clothing + accessories)
  1  head         (fashn 1 face + 2 hair)
  2  chest        (upper half of fashn 16 torso / 3 top)
  3  torso        (lower half of fashn 16 torso / 3 top)
  4  left_shoulder   (from pose landmarks + arms mask)
  5  right_shoulder  (from pose landmarks + arms mask)
  6  left_arm     (left portion of fashn 12 arms)
  7  right_arm    (right portion of fashn 12 arms)

For chest/torso split and left/right arm separation we use MediaPipe Pose
landmarks.  If pose detection fails we fall back to a vertical midpoint
split for chest/torso and skip shoulders + arm laterality.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import urllib.request
from typing import Optional

import cv2
import mediapipe as mp_lib
import numpy as np
import torch
from mediapipe.tasks.python import BaseOptions, vision
from PIL import Image, ImageOps
from transformers import SegformerImageProcessor, SegformerForSemanticSegmentation

from ..config import settings
from .body_image_utils import load_and_normalize_image, lm_visible
from .segmenter_interface import (
    CandidateSegment,
    SegmentationResult,
    SegmenterAdapter,
    SEG_CLASSES,
)

logger = logging.getLogger(__name__)

# ── Model singletons ─────────────────────────────────────────────────────────

_processor: Optional[SegformerImageProcessor] = None
_model: Optional[SegformerForSemanticSegmentation] = None

_POSE_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
_POSE_MODEL_PATH = "/tmp/pose_landmarker_heavy.task"
_landmarker: Optional[vision.PoseLandmarker] = None

# MediaPipe landmark indices
LM_NOSE = 0
LM_LEFT_SHOULDER = 11
LM_RIGHT_SHOULDER = 12
LM_LEFT_ELBOW = 13
LM_RIGHT_ELBOW = 14
LM_LEFT_HIP = 23
LM_RIGHT_HIP = 24
LM_LEFT_EYE = 2
LM_RIGHT_EYE = 5

# Dilation kernel size for editable region
_EDITABLE_REGION_DILATE_PX = 40


def _fashn_pretrained_kwargs() -> dict:
    """HF Hub cache dir + optional token for private mirrors."""
    kw: dict = {}
    if settings.hf_cache_dir:
        kw["cache_dir"] = settings.hf_cache_dir
    if settings.hf_token:
        kw["token"] = settings.hf_token
    return kw


_hf_http_configured = False


def _configure_hf_hub_http():
    """Corporate proxies / custom CAs often break SSL to huggingface.co; optional dev bypass."""
    global _hf_http_configured
    if _hf_http_configured:
        return
    _hf_http_configured = True
    if not settings.hf_hub_disable_ssl_verification:
        return
    import httpx
    from huggingface_hub.utils import set_client_factory
    from huggingface_hub.utils._http import hf_request_event_hook

    def factory() -> httpx.Client:
        return httpx.Client(
            verify=False,
            event_hooks={"request": [hf_request_event_hook]},
            follow_redirects=True,
            timeout=None,
        )

    set_client_factory(factory)
    logger.warning(
        "HF Hub SSL verification is DISABLED (hf_hub_disable_ssl_verification). "
        "Use only on trusted dev networks."
    )


def _is_huggingface_repo_id(model_id: str) -> bool:
    """True for Hub ids like 'org/model'. False for filesystem paths (contain leading / or ./)."""
    s = model_id.strip()
    if not s:
        return False
    if s.startswith(("/", "~")):
        return False
    if len(s) >= 2 and s[1] == ":" and s[0].isalpha():  # Windows path
        return False
    if s.startswith("./") or s.startswith("../"):
        return False
    parts = [p for p in s.split("/") if p]
    # HF models are namespace/name (single slash). Avoid treating /tmp/foo as hub.
    return len(parts) == 2 and ".." not in s and not s.startswith("/")


def _exception_chain_has_403(exc: BaseException) -> bool:
    """Hub wraps HTTP errors (e.g. 403) inside LocalEntryNotFoundError — walk __cause__/__context__."""
    seen: set[int] = set()
    stack: list[BaseException | None] = [exc]
    while stack:
        e = stack.pop()
        if e is None or id(e) in seen:
            continue
        seen.add(id(e))
        msg = str(e).lower()
        if "403" in msg or "forbidden" in msg:
            return True
        resp = getattr(e, "response", None)
        if resp is not None and getattr(resp, "status_code", None) == 403:
            return True
        stack.append(getattr(e, "__cause__", None))
        ctx = getattr(e, "__context__", None)
        if ctx is not None and ctx is not getattr(e, "__cause__", None):
            stack.append(ctx)
    return False


def _hf_snapshot_download(repo_id: str, cache_dir: str | None) -> str:
    """Download model snapshot; retry without token if HF returns 403 (invalid token breaks public repos)."""
    from huggingface_hub import snapshot_download

    token = (settings.hf_token or os.environ.get("HF_TOKEN") or "").strip() or None

    def _snap(tok: str | None) -> str:
        return snapshot_download(repo_id=repo_id, cache_dir=cache_dir, token=tok)

    try:
        return _snap(token)
    except Exception as e:
        if token and _exception_chain_has_403(e):
            logger.warning(
                "HF Hub returned 403 with HF_TOKEN (token may be invalid/expired). "
                "Retrying without token — fashn-human-parser is public."
            )
            return _snap(None)
        raise


def _get_parser():
    """Lazy-load the SegFormer model + processor (CPU)."""
    global _processor, _model
    if _model is None:
        # Must run before any Hub HTTP — sets httpx verify=False when HF_HUB_DISABLE_SSL_VERIFICATION=true
        _configure_hf_hub_http()
        model_id = (settings.fashn_human_parser_model or "fashn-ai/fashn-human-parser").strip()
        if model_id.startswith("/") or model_id.startswith("."):
            prep = os.path.join(model_id, "preprocessor_config.json")
            if not os.path.isfile(prep):
                logger.warning(
                    "fashn_human_parser_model path %s is missing preprocessor_config.json — "
                    "falling back to Hugging Face Hub fashn-ai/fashn-human-parser",
                    model_id,
                )
                model_id = "fashn-ai/fashn-human-parser"
        hf_kw = _fashn_pretrained_kwargs()
        load_id = model_id
        load_kw = dict(hf_kw)
        # Hub repo id (e.g. fashn-ai/fashn-human-parser) — NOT os.path.sep check: '/' is in the repo id!
        if _is_huggingface_repo_id(model_id):
            try:
                logger.warning(
                    "Downloading fashn-human-parser snapshot from Hugging Face (first run ~244MB)…"
                )
                load_id = _hf_snapshot_download(
                    model_id,
                    hf_kw.get("cache_dir") or None,
                )
                logger.warning("Snapshot ready at %s", load_id)
            except Exception as e:
                logger.error("snapshot_download failed: %s", e, exc_info=True)
                raise RuntimeError(
                    f"Could not download {model_id} from Hugging Face. "
                    "Check SSL (HF_HUB_DISABLE_SSL_VERIFICATION), network, or remove/rotate HF_TOKEN if 403."
                ) from e
            # Load from on-disk snapshot only (avoid transformers re-fetching Hub URLs)
            load_kw = {"local_files_only": True}

        logger.warning("Loading fashn-human-parser weights from %s…", load_id)
        try:
            _processor = SegformerImageProcessor.from_pretrained(load_id, **load_kw)
            _model = SegformerForSemanticSegmentation.from_pretrained(load_id, **load_kw)
        except OSError as e:
            err_s = str(e).lower()
            ssl_hint = ""
            if "certificate" in err_s or "ssl" in err_s:
                ssl_hint = (
                    " Likely HTTPS/SSL to Hugging Face failed (proxy, corporate CA). "
                    "Set HF_HUB_DISABLE_SSL_VERIFICATION=true in backend .env for local dev."
                )
            logger.error("Fashn model load failed:%s", ssl_hint, exc_info=True)
            raise RuntimeError(
                f"Could not load fashn-human-parser from {load_id}. "
                "Ensure the machine can reach https://huggingface.co (check SSL/proxy) "
                "or download the repo to a local folder and set FASHN_HUMAN_PARSER_MODEL."
            ) from e
        _model.eval()
        logger.warning("fashn-human-parser loaded (CPU)")
    return _processor, _model


def _get_landmarker() -> vision.PoseLandmarker:
    global _landmarker
    if _landmarker is None:
        if not os.path.exists(_POSE_MODEL_PATH):
            logger.info("Downloading pose_landmarker_heavy…")
            urllib.request.urlretrieve(_POSE_MODEL_URL, _POSE_MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_POSE_MODEL_PATH),
            num_poses=1,
        )
        _landmarker = vision.PoseLandmarker.create_from_options(options)
    return _landmarker


# ── Public helpers (used by edit_prep.py and other downstream stages) ─────────
# load_and_normalize_image, lm_visible → body_image_utils (torch-free)


def detect_pose(image_bgr: np.ndarray):
    """Detect pose landmarks. Returns landmark list or None."""
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp_lib.Image(image_format=mp_lib.ImageFormat.SRGB, data=rgb)
    result = _get_landmarker().detect(mp_image)
    if not result.pose_landmarks or len(result.pose_landmarks) == 0:
        return None
    return result.pose_landmarks[0]


def lm_px(lm, w: int, h: int) -> tuple[int, int]:
    """Convert a normalized landmark to clamped pixel coords."""
    return (max(0, min(w - 1, int(lm.x * w))),
            max(0, min(h - 1, int(lm.y * h))))


def run_fashn_parsing(pil_img: Image.Image) -> np.ndarray:
    """Run fashn-human-parser → (H, W) uint8 array of fashn label IDs.

    Upsamples logits to original resolution via bilinear interpolation
    BEFORE argmax so class boundaries are smooth, not pixelated.
    """
    processor, model = _get_parser()
    inputs = processor(images=pil_img, return_tensors="pt")
    target_h, target_w = pil_img.size[1], pil_img.size[0]

    with torch.no_grad():
        outputs = model(pixel_values=inputs["pixel_values"])

    logits = torch.nn.functional.interpolate(
        outputs.logits,
        size=(target_h, target_w),
        mode="bilinear",
        align_corners=False,
    )
    seg = logits.argmax(dim=1)[0].cpu().numpy().astype(np.uint8)
    return seg


# ── Label remapping ───────────────────────────────────────────────────────────

def _remap_to_seg_classes(
    fashn_map: np.ndarray,
    landmarks,
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Convert fashn 18-class map → our 8-class SEG_CLASSES label map.

    Uses pose landmarks to:
      - Split torso/top into chest (upper) vs torso (lower)
      - Split arms into left vs right
      - Create shoulder regions near shoulder landmarks
    """
    out = np.zeros((img_h, img_w), dtype=np.uint8)

    # --- Head: face (1) + hair (2) ---
    out[(fashn_map == 1) | (fashn_map == 2)] = 1

    # --- Torso area: fashn torso (16) + top (3) + dress (4) ---
    torso_area = (fashn_map == 16) | (fashn_map == 3) | (fashn_map == 4)

    # --- Arms: fashn arms (12) + hands (13) ---
    arms_area = (fashn_map == 12)
    hands_area = (fashn_map == 13)

    if landmarks is not None and lm_visible(landmarks, LM_LEFT_SHOULDER) and lm_visible(landmarks, LM_RIGHT_SHOULDER):
        ls = lm_px(landmarks[LM_LEFT_SHOULDER], img_w, img_h)
        rs = lm_px(landmarks[LM_RIGHT_SHOULDER], img_w, img_h)

        # chest/torso split line: midpoint between shoulders and hips
        if lm_visible(landmarks, LM_LEFT_HIP) and lm_visible(landmarks, LM_RIGHT_HIP):
            lh = lm_px(landmarks[LM_LEFT_HIP], img_w, img_h)
            rh = lm_px(landmarks[LM_RIGHT_HIP], img_w, img_h)
            split_y = (ls[1] + rs[1] + lh[1] + rh[1]) // 4
        else:
            split_y = (ls[1] + rs[1]) // 2 + int(img_h * 0.10)

        # Chest = torso area above split_y
        chest_mask = torso_area & (np.arange(img_h)[:, None] < split_y)
        out[chest_mask] = 2

        # Torso = torso area at or below split_y
        torso_mask = torso_area & (np.arange(img_h)[:, None] >= split_y)
        out[torso_mask] = 3

        # Shoulder regions: ellipse around shoulder landmark, clipped to
        # body pixels (torso + arms).  The ellipse is wider than tall to
        # match actual shoulder anatomy.
        shoulder_w = abs(ls[0] - rs[0])
        s_rx = max(int(shoulder_w * 0.28), 25)  # horizontal radius
        s_ry = max(int(shoulder_w * 0.20), 18)  # vertical radius (shorter)

        body_mask = torso_area | arms_area
        for cls_id, sp in [(4, ls), (5, rs)]:
            s_mask = np.zeros((img_h, img_w), dtype=np.uint8)
            cv2.ellipse(s_mask, sp, (s_rx, s_ry), 0, 0, 360, 255, -1)
            shoulder_region = (s_mask > 0) & body_mask
            out[shoulder_region] = cls_id

        # Left/right arm split: use the midpoint between shoulders as divider
        mid_x = (ls[0] + rs[0]) // 2

        # Determine which screen-side is anatomical left vs right.
        # Anatomical left shoulder is the landmark LM_LEFT_SHOULDER.
        # If ls.x > rs.x, anatomical left is on the right side of screen (standard photo).
        # If ls.x < rs.x, anatomical left is on the left side of screen (mirror selfie).
        if ls[0] > mid_x:
            # Standard front-facing: person's left is viewer's right (higher x)
            left_side = np.arange(img_w)[None, :] > mid_x
            right_side = ~left_side
        else:
            # Mirror selfie: person's left is viewer's left (lower x)
            left_side = np.arange(img_w)[None, :] < mid_x
            right_side = ~left_side

        out[arms_area & left_side] = 6   # person's left arm
        out[arms_area & right_side] = 7  # person's right arm
        # Hands (13) — same laterality as arms (were missing → counted as background)
        out[hands_area & left_side] = 6
        out[hands_area & right_side] = 7
    else:
        # No pose: torso area → split by vertical midpoint
        mid_y = img_h // 2
        out[torso_area & (np.arange(img_h)[:, None] < mid_y)] = 2
        out[torso_area & (np.arange(img_h)[:, None] >= mid_y)] = 3

        # Arms without laterality info → all as left arm (user corrects)
        out[arms_area] = 6
        out[hands_area] = 6

    # Skirt, pants, belt, legs, feet — not in torso_area (16,3,4); were left as 0 and
    # made full-body photos fail body-area ratio despite a visible person.
    lower_body = (
        (fashn_map == 5)  # skirt
        | (fashn_map == 6)  # pants
        | (fashn_map == 7)  # belt
        | (fashn_map == 14)  # legs
        | (fashn_map == 15)  # feet
    )
    out[lower_body] = 3

    return out


# ── Mask encoding ─────────────────────────────────────────────────────────────

def _mask_to_rle(mask: np.ndarray) -> str:
    flat = mask.ravel().astype(np.uint8)
    if len(flat) == 0:
        return ""
    diffs = np.diff(flat)
    change_idx = np.where(diffs != 0)[0] + 1
    runs_starts = np.concatenate([[0], change_idx])
    runs_ends = np.concatenate([change_idx, [len(flat)]])
    run_lengths = runs_ends - runs_starts
    if flat[0] == 1:
        run_lengths = np.concatenate([[0], run_lengths])
    return ",".join(str(int(r)) for r in run_lengths)


def _mask_to_png_b64(mask: np.ndarray) -> str:
    img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _label_map_to_png_b64(label_map: np.ndarray) -> str:
    img = Image.fromarray(label_map, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _mask_stats(mask: np.ndarray, w: int, h: int) -> dict:
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return {"cx": 0.5, "cy": 0.5, "area": 0, "bbox": (0, 0, 0, 0)}
    return {
        "cx": float(xs.mean()) / w,
        "cy": float(ys.mean()) / h,
        "area": int(len(ys)),
        "bbox": (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())),
    }


# ── Build candidate segments from label map ───────────────────────────────────

def _label_map_to_candidates(
    label_map: np.ndarray,
    img_w: int,
    img_h: int,
) -> list[CandidateSegment]:
    """Extract one CandidateSegment per connected component per class."""
    candidates: list[CandidateSegment] = []
    seg_id = 0

    for cls_id in range(1, 8):
        class_mask = (label_map == cls_id).astype(np.uint8)
        if class_mask.sum() == 0:
            continue

        num_labels, components = cv2.connectedComponents(class_mask)
        for comp_id in range(1, num_labels):
            comp_mask = components == comp_id
            stats = _mask_stats(comp_mask, img_w, img_h)
            if stats["area"] < 50:
                continue
            candidates.append(CandidateSegment(
                segment_id=seg_id,
                assigned_class=cls_id,
                score=1.0,
                bbox=stats["bbox"],
                area=stats["area"],
                centroid=(stats["cx"], stats["cy"]),
                mask_rle=_mask_to_rle(comp_mask),
                rejection_reason=None,
            ))
            seg_id += 1

    return candidates


# ── Shirtless detection ───────────────────────────────────────────────────────

def _compute_shirtless_ratio(
    fashn_map: np.ndarray,
    landmarks,
    img_w: int,
    img_h: int,
) -> dict:
    """Compute skin vs clothing ratio in the upper-body region.

    Uses pose landmarks (shoulders → hips) to define the ROI.
    fashn label 16 = torso (bare skin), label 3 = top (clothing).

    Returns dict with shirtless_ratio (0–1, higher = more skin), pixel counts,
    and the ROI bounds used.
    """
    fallback = {
        "shirtless_ratio": -1.0,
        "upper_body_skin_pixels": 0,
        "upper_body_clothing_pixels": 0,
        "shirtless_roi": None,
    }

    if landmarks is None:
        return fallback

    if not (
        lm_visible(landmarks, LM_LEFT_SHOULDER)
        and lm_visible(landmarks, LM_RIGHT_SHOULDER)
    ):
        return fallback

    ls = lm_px(landmarks[LM_LEFT_SHOULDER], img_w, img_h)
    rs = lm_px(landmarks[LM_RIGHT_SHOULDER], img_w, img_h)

    top_y = min(ls[1], rs[1])

    if (
        lm_visible(landmarks, LM_LEFT_HIP)
        and lm_visible(landmarks, LM_RIGHT_HIP)
    ):
        lh = lm_px(landmarks[LM_LEFT_HIP], img_w, img_h)
        rh = lm_px(landmarks[LM_RIGHT_HIP], img_w, img_h)
        bottom_y = max(lh[1], rh[1])
    else:
        bottom_y = top_y + int(img_h * 0.35)

    top_y = max(0, top_y)
    bottom_y = min(img_h, bottom_y)
    if bottom_y <= top_y:
        return fallback

    left_x = max(0, min(ls[0], rs[0]) - int(img_w * 0.05))
    right_x = min(img_w, max(ls[0], rs[0]) + int(img_w * 0.05))

    roi = fashn_map[top_y:bottom_y, left_x:right_x]
    skin_px = int(np.count_nonzero(roi == 16))
    clothing_px = int(np.count_nonzero(roi == 3))
    clothing_px += int(np.count_nonzero(roi == 4))  # dress
    total = skin_px + clothing_px

    # -1.0 = inconclusive (neither skin nor clothing detected in ROI)
    ratio = skin_px / total if total > 0 else -1.0

    return {
        "shirtless_ratio": round(ratio, 4),
        "upper_body_skin_pixels": skin_px,
        "upper_body_clothing_pixels": clothing_px,
        "shirtless_roi": [top_y, bottom_y, left_x, right_x],
    }


# ── Adapter ───────────────────────────────────────────────────────────────────

class FashnHumanParserSegmenter(SegmenterAdapter):
    """SegFormer-based human parsing segmenter.  Runs locally, no API calls."""

    async def segment(self, image_base64: str) -> SegmentationResult:
        import time
        t0 = time.monotonic()

        raw = base64.b64decode(image_base64)
        pil_img = Image.open(io.BytesIO(raw))
        pil_img = ImageOps.exif_transpose(pil_img) or pil_img
        pil_img = pil_img.convert("RGB")
        img_w, img_h = pil_img.size

        logger.info(f"FashnParser start: {img_w}×{img_h}")

        # Step 1: Pose detection
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        landmarks = detect_pose(img_bgr)
        use_pose = landmarks is not None

        if use_pose:
            logger.info("Pose detected — will split chest/torso and L/R arms")
        else:
            logger.warning("No pose — falling back to midpoint splits")

        # Step 2: fashn parsing (the heavy lift — but only 1-3s on CPU)
        fashn_map = run_fashn_parsing(pil_img)

        # Step 3: Remap fashn labels → our 8-class scheme
        label_map = _remap_to_seg_classes(fashn_map, landmarks, img_w, img_h)

        # Step 4: Foreground + editable region
        foreground = label_map > 0
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (_EDITABLE_REGION_DILATE_PX, _EDITABLE_REGION_DILATE_PX),
        )
        editable = cv2.dilate(foreground.astype(np.uint8), kernel, iterations=1) > 0

        # Step 5: Candidate segments
        candidates = _label_map_to_candidates(label_map, img_w, img_h)

        # Step 6: Shirtless detection (skin vs clothing in upper-body ROI)
        shirtless_info = _compute_shirtless_ratio(fashn_map, landmarks, img_w, img_h)

        unique_classes = set(int(v) for v in np.unique(label_map) if v > 0)
        labeled_px = int(np.count_nonzero(label_map))
        elapsed = round((time.monotonic() - t0) * 1000, 1)

        logger.info(
            f"FashnParser done in {elapsed}ms: "
            f"{len(unique_classes)} classes, {labeled_px} labeled px, "
            f"{len(candidates)} segments, pose={use_pose}"
        )

        def _lm_pack(lm) -> tuple:
            return (
                lm.x,
                lm.y,
                lm.visibility,
                float(getattr(lm, "z", 0.0)),
            )

        pose_summary = None
        if landmarks is not None:
            pose_summary = {
                "nose": _lm_pack(landmarks[LM_NOSE]),
                "left_eye": _lm_pack(landmarks[LM_LEFT_EYE]),
                "right_eye": _lm_pack(landmarks[LM_RIGHT_EYE]),
                "left_shoulder": _lm_pack(landmarks[LM_LEFT_SHOULDER]),
                "right_shoulder": _lm_pack(landmarks[LM_RIGHT_SHOULDER]),
                "left_hip": _lm_pack(landmarks[LM_LEFT_HIP]),
                "right_hip": _lm_pack(landmarks[LM_RIGHT_HIP]),
            }

        return SegmentationResult(
            width=img_w,
            height=img_h,
            label_map_b64=_label_map_to_png_b64(label_map),
            foreground_mask_b64=_mask_to_png_b64(foreground),
            editable_region_b64=_mask_to_png_b64(editable),
            classes=SEG_CLASSES,
            candidate_segments=[c.to_dict() for c in candidates],
            debug_info={
                "segmenter": "fashn-human-parser",
                "elapsed_ms": elapsed,
                "fashn_unique_labels": sorted(set(int(v) for v in np.unique(fashn_map))),
                "assigned_classes": sorted(unique_classes),
                "labeled_pixels": labeled_px,
                "foreground_pixels": int(foreground.sum()),
                "total_segments": len(candidates),
                "pose_detected": use_pose,
                "pose_summary": pose_summary,
                "shirtless_ratio": shirtless_info["shirtless_ratio"],
                "upper_body_skin_pixels": shirtless_info["upper_body_skin_pixels"],
                "upper_body_clothing_pixels": shirtless_info["upper_body_clothing_pixels"],
                "shirtless_roi": shirtless_info["shirtless_roi"],
            },
        )
