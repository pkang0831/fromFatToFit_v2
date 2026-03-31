"""
Deterministic CUT geometry-warp preview (V2).

Contour-aware dual-component warp that directly deforms the image.
No alpha blending — the displacement field IS the edit, and it is zero
in protected regions so the warp itself preserves those areas.

Components:
  A. Lateral flank contraction — boundary-inward pull calibrated to
     achieve a target waist-width reduction percentage.
  B. Lower-abdomen flattening — mild upward + inward compression
     centered below the navel.

Calibration targets (waist-width reduction at narrowest torso region):
  mild:   ~3%
  medium: ~6%
  strong: ~9%
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
from PIL import Image, ImageOps

from .edit_prep import prepare_cut_edit

logger = logging.getLogger(__name__)

# ── Presets: target waist-width reduction % + abdomen max px ──────────────────

PRESETS = {
    "mild":   {"target_reduction_pct": 0.04, "abdomen_px": 7},
    "medium": {"target_reduction_pct": 0.08, "abdomen_px": 14},
    "strong": {"target_reduction_pct": 0.11, "abdomen_px": 18},
}

WAISTBAND_PRESERVE_PX = 30
SMOOTH_SIGMA = 6.0


@dataclass
class CutWarpResult:
    width: int
    height: int
    warped_image_b64: str
    displacement_viz_b64: str
    debug_info: dict = field(default_factory=dict)


# ── Encoding helpers ─────────────────────────────────────────────────────────

def _img_to_jpeg_b64(img: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


def _img_to_png_b64(img: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _decode_mask(b64: str, w: int, h: int) -> np.ndarray:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("L").resize((w, h), Image.BILINEAR)
    return np.array(img).astype(np.float32) / 255.0


def _decode_bool_mask(b64: str, w: int, h: int) -> np.ndarray:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("L").resize((w, h), Image.NEAREST)
    return np.array(img) > 128


# ═══════════════════════════════════════════════════════════════════════════════
# § 1  Torso contour analysis
# ═══════════════════════════════════════════════════════════════════════════════

def _torso_contour(edit_mask: np.ndarray):
    """Extract per-row torso boundary geometry.

    Returns:
        x_left:  (H,) left boundary x per row (NaN if no pixels)
        x_right: (H,) right boundary x per row
        cx:      (H,) centerline
        width:   (H,) torso width per row
        top_y, bot_y: vertical extent of edit region
    """
    h, w = edit_mask.shape
    x_left = np.full(h, np.nan, dtype=np.float32)
    x_right = np.full(h, np.nan, dtype=np.float32)

    for y in range(h):
        xs = np.where(edit_mask[y])[0]
        if len(xs) >= 2:
            x_left[y] = float(xs.min())
            x_right[y] = float(xs.max())

    # Smooth boundaries to remove pixel noise
    valid = ~np.isnan(x_left)
    if valid.sum() < 3:
        cx = np.full(h, w / 2.0, dtype=np.float32)
        return x_left, x_right, cx, np.zeros(h, dtype=np.float32), 0, h

    ks = max(3, h // 30) | 1
    for arr in (x_left, x_right):
        v = arr.copy()
        # Interpolate NaN gaps
        nans = np.isnan(v)
        if nans.any() and (~nans).any():
            v[nans] = np.interp(np.where(nans)[0], np.where(~nans)[0], v[~nans])
        arr[:] = cv2.GaussianBlur(v.reshape(-1, 1), (1, ks), 0).ravel()

    cx = (x_left + x_right) / 2.0
    width = np.maximum(x_right - x_left, 0.0)

    ys = np.where(valid)[0]
    return x_left, x_right, cx, width, int(ys.min()), int(ys.max())


def _y_shrink_profile(top_y: int, bot_y: int, h: int) -> np.ndarray:
    """Per-row shrink multiplier [0, 1].

    Near-zero at top (chest), rises through waist, strongest at
    lower abdomen, fades to zero at waistband.
    """
    profile = np.zeros(h, dtype=np.float32)
    span = max(1, bot_y - top_y)

    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / span  # 0 at top, 1 at bottom

        if t < 0.15:
            # Upper chest: near zero
            profile[y] = t / 0.15 * 0.15
        elif t < 0.45:
            # Mid torso: ramp up
            profile[y] = 0.15 + (t - 0.15) / 0.30 * 0.55
        elif t < 0.85:
            # Lower abdomen + flanks: peak zone
            profile[y] = 0.70 + (t - 0.45) / 0.40 * 0.30
        else:
            # Waistband fade-out
            profile[y] = 1.0 * max(0.0, (1.0 - t) / 0.15)

    return profile


# ═══════════════════════════════════════════════════════════════════════════════
# § 2  Component A: Lateral flank contraction (contour-aware)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_lateral_field(
    edit_mask: np.ndarray,
    x_left: np.ndarray,
    x_right: np.ndarray,
    cx: np.ndarray,
    width: np.ndarray,
    shrink_profile: np.ndarray,
    target_reduction: float,
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Contour-aware lateral displacement.

    For each row y inside the torso:
      - target_shrink_px = width[y] * target_reduction * shrink_profile[y]
      - left boundary moves right by target_shrink_px/2
      - right boundary moves left by target_shrink_px/2
      - interior pixels are displaced proportionally using a smooth
        falloff from boundary toward centerline

    The result is a physically plausible waist narrowing.
    """
    dx = np.zeros((img_h, img_w), dtype=np.float32)

    for y in range(img_h):
        if np.isnan(x_left[y]) or width[y] < 10:
            continue

        shrink = shrink_profile[y]
        if shrink < 0.01:
            continue

        target_shrink_px = width[y] * target_reduction * shrink
        half_shrink = target_shrink_px / 2.0
        half_w = width[y] / 2.0
        c = cx[y]

        xs = np.where(edit_mask[y])[0]
        if len(xs) == 0:
            continue

        xl = float(x_left[y])
        xr = float(x_right[y])

        for x in xs:
            dist_from_center = x - c
            norm_dist = abs(dist_from_center) / max(1.0, half_w)

            # Smooth boundary-to-center falloff: cubic ease
            # 1.0 at boundary → 0.0 at centerline
            edge_factor = norm_dist ** 0.7

            displacement = half_shrink * edge_factor

            if dist_from_center > 0:
                dx[y, x] = -displacement  # pull left (toward center)
            elif dist_from_center < 0:
                dx[y, x] = displacement   # pull right (toward center)

    return dx


# ═══════════════════════════════════════════════════════════════════════════════
# § 3  Component B: Lower-abdomen flattening
# ═══════════════════════════════════════════════════════════════════════════════

def _build_abdomen_field(
    edit_mask: np.ndarray,
    cx: np.ndarray,
    width: np.ndarray,
    top_y: int,
    bot_y: int,
    max_px: float,
    img_w: int,
    img_h: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Lower-abdomen upward + inward compression.

    Effect starts at 45% of the edit span and peaks at 75-85%.
    """
    dx = np.zeros((img_h, img_w), dtype=np.float32)
    dy = np.zeros((img_h, img_w), dtype=np.float32)

    span = max(1, bot_y - top_y)
    abdomen_start_y = top_y + int(span * 0.45)
    abdomen_peak_y = top_y + int(span * 0.80)

    for y in range(abdomen_start_y, bot_y + 1):
        xs = np.where(edit_mask[y])[0]
        if len(xs) == 0 or width[y] < 10:
            continue

        # Vertical ramp: 0 at abdomen_start → 1 at peak → fade to 0 at bottom
        t = (y - abdomen_start_y) / max(1, bot_y - abdomen_start_y)
        if t < 0.7:
            v_strength = (t / 0.7) ** 1.2
        else:
            # Waistband fade
            v_strength = max(0.0, 1.0 - (t - 0.7) / 0.3)

        half_w = width[y] / 2.0
        c = cx[y]

        for x in xs:
            dist_from_center = abs(x - c)
            norm_dist = dist_from_center / max(1.0, half_w)

            # Upward compression: strongest at center, fades at edges
            center_weight = max(0.0, 1.0 - norm_dist ** 1.5)
            dy[y, x] = -v_strength * max_px * center_weight

            # Mild inward push at flanks
            if norm_dist > 0.3:
                flank_push = (norm_dist - 0.3) / 0.7 * 0.4
                sign = -1.0 if (x - c) > 0 else 1.0
                dx[y, x] = sign * v_strength * max_px * flank_push

    return dx, dy


# ═══════════════════════════════════════════════════════════════════════════════
# § 4  Safety: waistband preserve + protect freeze + smoothing
# ═══════════════════════════════════════════════════════════════════════════════

def _apply_safety(
    dx: np.ndarray,
    dy: np.ndarray,
    protect_mask: np.ndarray,
    edit_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Smooth, freeze protected, and apply waistband preserve."""
    # Smooth first
    ksize = int(SMOOTH_SIGMA * 4) | 1
    dx = cv2.GaussianBlur(dx, (ksize, ksize), SMOOTH_SIGMA)
    dy = cv2.GaussianBlur(dy, (ksize, ksize), SMOOTH_SIGMA)

    # Hard freeze protected areas after smoothing
    dx[protect_mask] = 0.0
    dy[protect_mask] = 0.0

    # Waistband preserve band
    ys = np.where(edit_mask.any(axis=1))[0]
    if len(ys) > 0:
        bot_y = int(ys.max())
        fade_start = max(0, bot_y - WAISTBAND_PRESERVE_PX)
        for y in range(fade_start, min(bot_y + 1, dx.shape[0])):
            fade = max(0.0, (bot_y - y) / max(1, WAISTBAND_PRESERVE_PX))
            dx[y] *= fade
            dy[y] *= fade

    # Feather displacement at edit boundary: distance-based fade over 15px
    # so the warp blends smoothly into unedited regions
    dist_from_edit = cv2.distanceTransform(
        (~edit_mask).astype(np.uint8), cv2.DIST_L2, 5,
    )
    # Pixels OUTSIDE edit_mask: fade displacement to 0 over 15px
    outside = ~edit_mask
    fade_zone = outside & (dist_from_edit < 15)
    fade_factor = np.ones_like(dx)
    fade_factor[fade_zone] = dist_from_edit[fade_zone] / 15.0
    fade_factor[outside & (dist_from_edit >= 15)] = 0.0
    # Actually we want outside to be 0, with a thin fade:
    fade_factor[outside & ~fade_zone] = 0.0
    # Invert: inside=1, boundary fade, outside=0
    inside_dist = cv2.distanceTransform(
        edit_mask.astype(np.uint8), cv2.DIST_L2, 5,
    )
    boundary_fade = np.clip(inside_dist / 12.0, 0.0, 1.0)
    dx *= boundary_fade
    dy *= boundary_fade

    # Final protect freeze
    dx[protect_mask] = 0.0
    dy[protect_mask] = 0.0

    return dx, dy


# ═══════════════════════════════════════════════════════════════════════════════
# § 5  Apply warp (direct, no alpha blending)
# ═══════════════════════════════════════════════════════════════════════════════

def _apply_warp(image: np.ndarray, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    grid_x, grid_y = np.meshgrid(
        np.arange(w, dtype=np.float32),
        np.arange(h, dtype=np.float32),
    )
    map_x = grid_x - dx
    map_y = grid_y - dy
    return cv2.remap(
        image, map_x, map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# § 6  Metrics + visualization
# ═══════════════════════════════════════════════════════════════════════════════

def _waist_metrics(
    dx: np.ndarray,
    edit_mask: np.ndarray,
    width: np.ndarray,
    top_y: int,
    bot_y: int,
) -> dict:
    """Measure effective waist contraction from the displacement field.

    For each scanline, computes the total inward pull: the sum of
    leftward dx on the right flank + rightward dx on the left flank.
    This gives the effective width reduction that the warp achieves.
    """
    span = max(1, bot_y - top_y)
    scan_fracs = [0.30, 0.50, 0.65, 0.80]
    measurements = []

    for frac in scan_fracs:
        y = top_y + int(span * frac)
        if y >= edit_mask.shape[0] or width[y] < 10:
            continue
        xs = np.where(edit_mask[y])[0]
        if len(xs) < 10:
            continue

        w_before = float(width[y])

        # Sum inward pull from both flanks.
        # On the right side (x > center), dx is negative (pulling left) = contraction.
        # On the left side (x < center), dx is positive (pulling right) = contraction.
        row_dx = dx[y, xs]
        cx = (xs.min() + xs.max()) / 2.0
        left_mask = xs < cx
        right_mask = xs > cx

        left_pull = float(row_dx[left_mask].max()) if left_mask.any() else 0.0
        right_pull = float(-row_dx[right_mask].min()) if right_mask.any() else 0.0
        total_contraction = left_pull + right_pull

        w_after = max(10.0, w_before - total_contraction)
        reduction = (w_before - w_after) / w_before

        measurements.append({
            "y": y,
            "frac": frac,
            "width_before": round(w_before, 1),
            "width_after": round(w_after, 1),
            "contraction_px": round(total_contraction, 1),
            "reduction_pct": round(reduction * 100, 2),
        })

    return {"scanlines": measurements}


def _displacement_stats(dx: np.ndarray, dy: np.ndarray, edit_mask: np.ndarray) -> dict:
    mag = np.sqrt(dx ** 2 + dy ** 2)
    edit_mag = mag[edit_mask]
    if len(edit_mag) == 0:
        return {"p50": 0, "p90": 0, "p95": 0, "max": 0}
    return {
        "p50": round(float(np.percentile(edit_mag, 50)), 2),
        "p90": round(float(np.percentile(edit_mag, 90)), 2),
        "p95": round(float(np.percentile(edit_mag, 95)), 2),
        "max": round(float(edit_mag.max()), 2),
    }


def _visualize_displacement(dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    mag_x = np.abs(dx)
    mag_y = np.abs(dy)
    mag = np.sqrt(dx ** 2 + dy ** 2)
    max_mag = max(1.0, float(mag.max()))

    r = np.clip(mag_x / max_mag * 255, 0, 255).astype(np.uint8)
    g = np.clip(mag_y / max_mag * 255, 0, 255).astype(np.uint8)
    b = np.clip(mag / max_mag * 255, 0, 255).astype(np.uint8)
    return np.stack([r, g, b], axis=-1)


# ═══════════════════════════════════════════════════════════════════════════════
# § 7  Main entry point
# ═══════════════════════════════════════════════════════════════════════════════

async def cut_warp_preview(
    image_base64: str,
    preset: str = "medium",
    intensity: float = 0.5,
) -> CutWarpResult:
    t0 = time.monotonic()

    params = PRESETS.get(preset, PRESETS["medium"])
    target_reduction = params["target_reduction_pct"]
    abdomen_px = params["abdomen_px"]

    logger.info(
        f"CUT warp v2: preset={preset}, "
        f"target_reduction={target_reduction*100:.0f}%, abdomen={abdomen_px}px"
    )

    # Step 1: Edit-prep masks
    prep = await prepare_cut_edit(image_base64, intensity=intensity)
    img_w, img_h = prep.width, prep.height

    # Decode image
    raw = base64.b64decode(image_base64)
    pil_img = Image.open(io.BytesIO(raw))
    pil_img = ImageOps.exif_transpose(pil_img) or pil_img
    pil_img = pil_img.convert("RGB")
    original = np.array(pil_img)

    # Decode masks
    edit_mask = _decode_bool_mask(prep.edit_mask_b64, img_w, img_h)
    protect_mask = _decode_bool_mask(prep.protect_mask_b64, img_w, img_h)

    # Step 2: Torso contour analysis
    x_left, x_right, cx, width, top_y, bot_y = _torso_contour(edit_mask)
    shrink_profile = _y_shrink_profile(top_y, bot_y, img_h)

    # Step 3: Build displacement fields
    dx_lateral = _build_lateral_field(
        edit_mask, x_left, x_right, cx, width,
        shrink_profile, target_reduction, img_w, img_h,
    )

    dx_abdomen, dy_abdomen = _build_abdomen_field(
        edit_mask, cx, width, top_y, bot_y, abdomen_px, img_w, img_h,
    )

    dx = dx_lateral + dx_abdomen
    dy = dy_abdomen.copy()

    # Step 4: Safety
    dx, dy = _apply_safety(dx, dy, protect_mask, edit_mask)

    # Step 5: Warp directly (no alpha blending)
    result = _apply_warp(original, dx, dy)

    # Step 6: Metrics
    waist = _waist_metrics(dx, edit_mask, width, top_y, bot_y)
    disp_stats = _displacement_stats(dx, dy, edit_mask)
    disp_viz = _visualize_displacement(dx, dy)

    elapsed = round((time.monotonic() - t0) * 1000, 1)

    logger.info(
        f"CUT warp done in {elapsed}ms: "
        f"disp p50={disp_stats['p50']}, p90={disp_stats['p90']}, "
        f"p95={disp_stats['p95']}, max={disp_stats['max']}"
    )

    return CutWarpResult(
        width=img_w,
        height=img_h,
        warped_image_b64=_img_to_jpeg_b64(result),
        displacement_viz_b64=_img_to_png_b64(disp_viz),
        debug_info={
            "elapsed_ms": elapsed,
            "preset": preset,
            "target_reduction_pct": target_reduction * 100,
            "abdomen_max_px": abdomen_px,
            "intensity": intensity,
            "displacement_stats": disp_stats,
            "waist_metrics": waist,
        },
    )
