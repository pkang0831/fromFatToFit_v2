"""
Deterministic CUT edit-preparation pipeline (V1).

Consumes the raw fashn 18-class parsing map + MediaPipe Pose landmarks
and produces four pixel-aligned masks/maps for downstream warp + diffusion:

  protect_mask   – binary: regions that must NEVER be modified
  edit_mask      – binary: regions where edits are allowed
  weight_map     – continuous 0-1: per-pixel edit intensity
  feather_mask   – continuous 0-1: soft boundary falloff

All outputs are at the original image resolution.

V1 scope: CUT only (body-fat reduction), upper-body, torso-first.

V2 extension points (not implemented):
  - user_protect_mask: OR-merged into protect_mask (phone, tattoos, etc.)
  - arm editing: add fashn 12 to edit_mask with low base weight
  - bulk/recomp: different weight_map profiles
  - lower body: include fashn 14 (legs) with appropriate weights
"""

from __future__ import annotations

import base64
import io
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

from .fashn_human_parser import (
    load_and_normalize_image,
    run_fashn_parsing,
    detect_pose,
    lm_px,
    lm_visible,
    _remap_to_seg_classes,
    LM_LEFT_SHOULDER,
    LM_RIGHT_SHOULDER,
    LM_LEFT_HIP,
    LM_RIGHT_HIP,
)

# 8-class label IDs (from segmenter_interface.SEG_CLASSES)
SEG_CHEST = 2
SEG_TORSO = 3
SEG_LEFT_SHOULDER = 4
SEG_RIGHT_SHOULDER = 5

logger = logging.getLogger(__name__)

# ── Fashn label IDs ───────────────────────────────────────────────────────────

FASHN_BACKGROUND = 0
FASHN_FACE = 1
FASHN_HAIR = 2
FASHN_TOP = 3
FASHN_DRESS = 4
FASHN_SKIRT = 5
FASHN_PANTS = 6
FASHN_BELT = 7
FASHN_BAG = 8
FASHN_HAT = 9
FASHN_SCARF = 10
FASHN_GLASSES = 11
FASHN_ARMS = 12
FASHN_HANDS = 13
FASHN_LEGS = 14
FASHN_FEET = 15
FASHN_TORSO = 16
FASHN_JEWELRY = 17

# All labels that must be protected from editing
PROTECT_LABELS = frozenset({
    FASHN_BACKGROUND, FASHN_FACE, FASHN_HAIR, FASHN_HANDS,
    FASHN_PANTS, FASHN_BELT, FASHN_SKIRT, FASHN_LEGS, FASHN_FEET,
    FASHN_BAG, FASHN_HAT, FASHN_SCARF, FASHN_GLASSES, FASHN_JEWELRY,
})

# Labels that form the editable torso region
EDIT_LABELS = frozenset({FASHN_TORSO, FASHN_TOP, FASHN_DRESS})

# Feather radius in pixels — controls the soft falloff at edit boundaries
FEATHER_RADIUS_PX = 25

# Gaussian blur sigma for weight map smoothing
WEIGHT_BLUR_SIGMA = 15


# ── Output contract ──────────────────────────────────────────────────────────

@dataclass
class CutEditPrepResult:
    """All masks/maps needed for the downstream warp + diffusion stages."""
    width: int
    height: int
    protect_mask_b64: str       # binary PNG (white = protected)
    edit_mask_b64: str          # binary PNG (white = editable)
    weight_map_b64: str         # grayscale PNG (0 = no edit, 255 = max edit)
    feather_mask_b64: str       # grayscale PNG (soft boundary falloff)
    combined_map_b64: str       # weight_map * feather_mask, ready-to-use
    debug_info: dict = field(default_factory=dict)


# ── Encoding helpers ─────────────────────────────────────────────────────────

def _bool_to_png_b64(mask: np.ndarray) -> str:
    img = Image.fromarray((mask.astype(np.uint8) * 255), mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _float_to_png_b64(arr: np.ndarray) -> str:
    """float32 [0,1] → 8-bit grayscale PNG."""
    clipped = np.clip(arr * 255, 0, 255).astype(np.uint8)
    img = Image.fromarray(clipped, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ── Stage 1: Protect mask ────────────────────────────────────────────────────

def _build_protect_mask(
    fashn_map: np.ndarray,
    user_protect: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Binary mask: True = pixel must never be edited.

    Covers: background, face, hair, hands, pants, belt, skirt, legs,
    feet, bags, hats, scarves, glasses, jewelry.

    A future user_protect_mask (e.g. phone region drawn by user) is
    OR-merged when provided.
    """
    protect = np.zeros(fashn_map.shape, dtype=bool)
    for label_id in PROTECT_LABELS:
        protect |= (fashn_map == label_id)

    # Arms are excluded from editing in V1 — protect them too
    protect |= (fashn_map == FASHN_ARMS)

    if user_protect is not None:
        protect |= (user_protect > 0)

    return protect


# ── Stage 2: Edit mask ───────────────────────────────────────────────────────

def _build_edit_mask(
    fashn_map: np.ndarray,
    protect_mask: np.ndarray,
) -> np.ndarray:
    """Binary mask: True = pixel is eligible for CUT editing.

    Includes torso, top, and dress regions, minus anything in protect_mask.
    """
    edit = np.zeros(fashn_map.shape, dtype=bool)
    for label_id in EDIT_LABELS:
        edit |= (fashn_map == label_id)

    # Hard subtract protection — never edit a protected pixel
    edit &= ~protect_mask

    return edit


# ── Stage 3: Weight map ─────────────────────────────────────────────────────

def _build_weight_map(
    edit_mask: np.ndarray,
    fashn_map: np.ndarray,
    landmarks,
    img_w: int,
    img_h: int,
    intensity: float = 0.5,
) -> np.ndarray:
    """Continuous weight map [0.0, 1.0] at original resolution.

    With pose landmarks:
      4 horizontal bands within the torso, smoothly interpolated.
      Flank boost for left/right edges of the torso.

    Without pose:
      Linear vertical gradient (top = mild, bottom = strong).

    The intensity parameter (0-1) scales the entire map.
    """
    wmap = np.zeros((img_h, img_w), dtype=np.float32)

    if not np.any(edit_mask):
        return wmap

    # Torso-only mask for geometry analysis
    torso_skin = np.zeros_like(edit_mask)
    for lid in EDIT_LABELS:
        torso_skin |= (fashn_map == lid)
    torso_skin &= edit_mask

    if landmarks is not None and _has_torso_landmarks(landmarks):
        wmap = _weight_map_with_pose(
            torso_skin, landmarks, img_w, img_h,
        )
    else:
        wmap = _weight_map_fallback(torso_skin, img_w, img_h)

    # Apply global intensity scaling
    wmap *= np.clip(intensity * 2.0, 0.0, 1.0)

    # Zero outside edit mask
    wmap[~edit_mask] = 0.0

    # Smooth the whole map to avoid hard band transitions
    ksize = int(WEIGHT_BLUR_SIGMA * 4) | 1
    wmap = cv2.GaussianBlur(wmap, (ksize, ksize), WEIGHT_BLUR_SIGMA)

    # Re-zero outside edit mask after blur
    wmap[~edit_mask] = 0.0

    return np.clip(wmap, 0.0, 1.0)


def _has_torso_landmarks(landmarks) -> bool:
    return (
        lm_visible(landmarks, LM_LEFT_SHOULDER)
        and lm_visible(landmarks, LM_RIGHT_SHOULDER)
        and lm_visible(landmarks, LM_LEFT_HIP)
        and lm_visible(landmarks, LM_RIGHT_HIP)
    )


def _weight_map_with_pose(
    torso_mask: np.ndarray,
    landmarks,
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Pose-guided weight map with 4 horizontal bands + flank boost."""
    ls = lm_px(landmarks[LM_LEFT_SHOULDER], img_w, img_h)
    rs = lm_px(landmarks[LM_RIGHT_SHOULDER], img_w, img_h)
    lh = lm_px(landmarks[LM_LEFT_HIP], img_w, img_h)
    rh = lm_px(landmarks[LM_RIGHT_HIP], img_w, img_h)

    shoulder_y = (ls[1] + rs[1]) / 2
    hip_y = (lh[1] + rh[1]) / 2
    torso_span = max(1.0, hip_y - shoulder_y)

    # Band boundaries as fractions of torso span from shoulder_y
    # band 0: shoulder → 0.25  (lower chest)         weight 0.15
    # band 1: 0.25 → 0.55     (mid abdomen)          weight 0.50
    # band 2: 0.55 → 0.80     (lower abdomen)        weight 0.85
    # band 3: 0.80 → 1.0+     (love handles / waist) weight 1.00
    band_weights = [0.15, 0.50, 0.85, 1.00]
    band_boundaries = [0.0, 0.25, 0.55, 0.80, 1.20]

    ys = np.arange(img_h, dtype=np.float32)
    t = (ys - shoulder_y) / torso_span  # normalized position in torso

    # Linearly interpolate weight across bands
    base_weight = np.zeros(img_h, dtype=np.float32)
    for i in range(len(band_weights)):
        lo = band_boundaries[i]
        hi = band_boundaries[i + 1]
        w = band_weights[i]
        in_band = (t >= lo) & (t < hi)
        base_weight[in_band] = w

    # Smooth transitions between bands via interpolation
    for i in range(len(band_weights) - 1):
        boundary = band_boundaries[i + 1]
        blend_zone = 0.08
        lo = boundary - blend_zone
        hi = boundary + blend_zone
        in_zone = (t >= lo) & (t < hi)
        if np.any(in_zone):
            alpha = (t[in_zone] - lo) / (hi - lo)
            base_weight[in_zone] = (
                band_weights[i] * (1 - alpha) + band_weights[i + 1] * alpha
            )

    # Broadcast to 2D
    wmap = np.broadcast_to(base_weight[:, None], (img_h, img_w)).copy()

    # Flank boost: pixels near the left/right boundary of the torso
    # get extra weight (+0.15 at the very edge, fading inward)
    _apply_flank_boost(wmap, torso_mask, img_w, img_h, boost=0.15)

    return wmap


def _apply_flank_boost(
    wmap: np.ndarray,
    torso_mask: np.ndarray,
    img_w: int,
    img_h: int,
    boost: float = 0.15,
) -> None:
    """Add extra weight to pixels near the left/right edges of the torso.

    Uses the distance from each torso pixel to the nearest non-torso pixel
    on the same row.  Pixels closer to the edge get more boost.
    """
    for y in range(img_h):
        row = torso_mask[y]
        xs = np.where(row)[0]
        if len(xs) < 4:
            continue
        left_edge = xs.min()
        right_edge = xs.max()
        span = right_edge - left_edge
        if span < 10:
            continue
        # Boost zone: outer 25% on each side
        zone_width = max(5, int(span * 0.25))
        for x in xs:
            dist_left = x - left_edge
            dist_right = right_edge - x
            min_dist = min(dist_left, dist_right)
            if min_dist < zone_width:
                factor = 1.0 - (min_dist / zone_width)
                wmap[y, x] = min(1.0, wmap[y, x] + boost * factor)


def _weight_map_fallback(
    torso_mask: np.ndarray,
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Simple vertical gradient when pose is unavailable."""
    ys, xs = np.where(torso_mask)
    if len(ys) == 0:
        return np.zeros((img_h, img_w), dtype=np.float32)

    top_y = ys.min()
    bot_y = ys.max()
    span = max(1, bot_y - top_y)

    wmap = np.zeros((img_h, img_w), dtype=np.float32)
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / span
        # top=0.15 → bottom=0.90
        weight = 0.15 + 0.75 * t
        row_mask = torso_mask[y]
        wmap[y, row_mask] = weight

    return wmap


# ── Stage 4-5: Safety buffer + region dampening ─────────────────────────────

_PROTECT_BUFFER_KERNEL_PX = 31
_PROTECT_FALLOFF_NEAR = 8.0
_PROTECT_FALLOFF_FAR = 36.0


def _apply_protect_buffer(
    edit_mask: np.ndarray,
    weight_map: np.ndarray,
    protect_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Erode edit zone near protect boundaries and attenuate weights.

    1. Dilate protect_mask to create a no-edit buffer around jaw, neck,
       phone edges, hand-phone contact.
    2. Subtract the dilated zone from edit_mask.
    3. Apply a smooth distance-based falloff to weight_map so that even
       pixels just inside the safe zone have reduced intensity.
    """
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (_PROTECT_BUFFER_KERNEL_PX, _PROTECT_BUFFER_KERNEL_PX),
    )
    protect_dilated = cv2.dilate(
        protect_mask.astype(np.uint8), kernel, iterations=1,
    ) > 0

    safe_edit = edit_mask & ~protect_dilated

    dist = cv2.distanceTransform(
        (~protect_dilated).astype(np.uint8), cv2.DIST_L2, 5,
    )
    falloff = np.clip(
        (dist - _PROTECT_FALLOFF_NEAR) / _PROTECT_FALLOFF_FAR, 0.0, 1.0,
    ).astype(np.float32)

    safe_weight = weight_map * falloff
    safe_weight[~safe_edit] = 0.0

    return safe_edit, safe_weight


def _apply_region_dampening(
    weight_map: np.ndarray,
    label_map: np.ndarray,
) -> np.ndarray:
    """Scale weight per body-part region.

    Shoulders are nearly zeroed out — V1 gains nothing from editing them
    and risks visible artifacts.  Chest is reduced to mild.  Torso keeps
    full weight (the primary CUT target).
    """
    out = weight_map.copy()
    out[label_map == SEG_LEFT_SHOULDER] *= 0.05
    out[label_map == SEG_RIGHT_SHOULDER] *= 0.05
    out[label_map == SEG_CHEST] *= 0.35
    return out


# ── Stage 6: Feather mask ───────────────────────────────────────────────────

def _build_feather_mask(
    edit_mask: np.ndarray,
    radius: int = FEATHER_RADIUS_PX,
) -> np.ndarray:
    """Soft falloff [0, 1] around edit_mask boundaries.

    Uses distance transform from the edit_mask boundary.
    Pixels inside the edit region ramp from 0 at the boundary to 1
    at `radius` pixels inward.
    """
    if not np.any(edit_mask):
        return np.zeros(edit_mask.shape, dtype=np.float32)

    # Distance from each edit pixel to the nearest non-edit pixel
    dist_inside = distance_transform_edt(edit_mask.astype(np.float64))

    # Normalize: 0 at boundary → 1 at `radius` pixels inward
    feather = np.clip(dist_inside / max(1, radius), 0.0, 1.0).astype(np.float32)

    return feather


# ── Main entry point ─────────────────────────────────────────────────────────

async def prepare_cut_edit(
    image_base64: str,
    intensity: float = 0.5,
    user_protect_mask_b64: Optional[str] = None,
) -> CutEditPrepResult:
    """Run the full CUT edit-preparation pipeline.

    Args:
        image_base64: raw base64 JPEG/PNG (no data: prefix).
        intensity: global edit strength multiplier [0.0, 1.0].
        user_protect_mask_b64: optional user-drawn protection mask (base64 PNG).

    Returns:
        CutEditPrepResult with all masks at original resolution.
    """
    t0 = time.monotonic()

    pil_img = load_and_normalize_image(image_base64)
    img_w, img_h = pil_img.size

    logger.info(f"CUT edit prep start: {img_w}×{img_h}, intensity={intensity}")

    # Parse user protect mask if provided
    user_protect: Optional[np.ndarray] = None
    if user_protect_mask_b64:
        raw = base64.b64decode(user_protect_mask_b64)
        pm = Image.open(io.BytesIO(raw)).convert("L").resize((img_w, img_h), Image.NEAREST)
        user_protect = np.array(pm) > 128

    # Run fashn parsing (reuses cached model)
    fashn_map = run_fashn_parsing(pil_img)

    # Run pose detection
    img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    landmarks = detect_pose(img_bgr)
    use_pose = landmarks is not None

    # Stage 1: Protect mask
    protect_mask = _build_protect_mask(fashn_map, user_protect)

    # Stage 2: Edit mask (initial)
    edit_mask = _build_edit_mask(fashn_map, protect_mask)

    # Stage 3: Weight map (initial)
    weight_map = _build_weight_map(
        edit_mask, fashn_map, landmarks, img_w, img_h, intensity,
    )

    # Stage 4: Safety buffer — erode edit zone near protect boundaries
    # Prevents warp/diffusion from disturbing jawline, neck, phone edges,
    # hand-phone contact points.
    edit_mask, weight_map = _apply_protect_buffer(
        edit_mask, weight_map, protect_mask,
    )

    # Stage 5: Region-specific weight dampening
    # Shoulders nearly zero, chest mild, torso full.
    label_map = _remap_to_seg_classes(fashn_map, landmarks, img_w, img_h)
    weight_map = _apply_region_dampening(weight_map, label_map)

    # Stage 6: Feather mask
    feather_mask = _build_feather_mask(edit_mask)

    # Combined map: weight * feather (ready for warp/diffusion consumption)
    combined = weight_map * feather_mask

    elapsed = round((time.monotonic() - t0) * 1000, 1)

    protect_px = int(protect_mask.sum())
    edit_px = int(edit_mask.sum())
    weight_mean = float(weight_map[edit_mask].mean()) if edit_px > 0 else 0.0
    weight_max = float(weight_map.max())

    logger.info(
        f"CUT edit prep done in {elapsed}ms: "
        f"protect={protect_px}px, edit={edit_px}px, "
        f"weight_mean={weight_mean:.3f}, weight_max={weight_max:.3f}, "
        f"pose={use_pose}"
    )

    return CutEditPrepResult(
        width=img_w,
        height=img_h,
        protect_mask_b64=_bool_to_png_b64(protect_mask),
        edit_mask_b64=_bool_to_png_b64(edit_mask),
        weight_map_b64=_float_to_png_b64(weight_map),
        feather_mask_b64=_float_to_png_b64(feather_mask),
        combined_map_b64=_float_to_png_b64(combined),
        debug_info={
            "elapsed_ms": elapsed,
            "intensity": intensity,
            "pose_detected": use_pose,
            "protect_pixels": protect_px,
            "edit_pixels": edit_px,
            "weight_mean": round(weight_mean, 4),
            "weight_max": round(weight_max, 4),
            "feather_radius_px": FEATHER_RADIUS_PX,
            "fashn_labels_found": sorted(set(int(v) for v in np.unique(fashn_map))),
            "user_protect_provided": user_protect is not None,
        },
    )
