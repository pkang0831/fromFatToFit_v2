"""
Two-pass CUT refinement pipeline (CPU-only).

Bridges the geometry warp stage → local diffusion inpainting.

PASS 1 — Seam repair
  Thin contour mask around warp-displacement edges.
  Low strength, few steps.  Fixes artifacts without changing geometry.

PASS 2 — Upper-ab / oblique texture refinement
  Targeted mask covering upper-ab center, linea alba, and side obliques.
  Explicitly excludes lower-belly center to prevent belly re-inflation.
  Very low strength — texture only, geometry is owned by warp.

Both passes operate on a small ROI crop (~512px) for CPU feasibility,
then composite back into the full-resolution image.
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

from .diffusion import get_backend
from .diffusion.base import RefineRequest
from .diffusion.roi import compute_roi, crop_to_roi, crop_mask_to_roi, composite_roi
from .diffusion import prompts as P

logger = logging.getLogger(__name__)

# ── Preset parameters ────────────────────────────────────────────────────────

REFINE_PRESETS = {
    "mild": {
        "seam_strength": 0.30,
        "seam_guidance": 5.0,
        "seam_steps": 12,
        "torso_strength": 0.22,
        "torso_guidance": 5.5,
        "torso_steps": 12,
    },
    "medium": {
        "seam_strength": 0.40,
        "seam_guidance": 6.0,
        "seam_steps": 15,
        "torso_strength": 0.30,
        "torso_guidance": 6.5,
        "torso_steps": 15,
    },
    "strong": {
        "seam_strength": 0.45,
        "seam_guidance": 6.5,
        "seam_steps": 15,
        "torso_strength": 0.35,
        "torso_guidance": 7.0,
        "torso_steps": 16,
    },
}

# Seam contour mask: distance from displacement edges considered "seam"
_SEAM_WIDTH_PX = 18

# Pass-2 torso mask parameters
_PROTECT_BUFFER_PX = 20
_SHOULDER_SUPPRESS_FRAC = 0.25
_WAISTBAND_SUPPRESS_FRAC = 0.08
_NAVEL_EXCLUDE_RADIUS_FRAC = 0.06
_LOWER_BELLY_CENTER_SUPPRESS_FRAC = 0.55
_LOWER_BELLY_CENTER_WIDTH_FRAC = 0.45
_OBLIQUE_INNER_FRAC = 0.30
_MIN_TORSO_CORE_PX = 1500
_PASS2_MIN_TARGET_W = 256
_PASS2_MIN_TARGET_H = 192

# Auto-reject: if pass2 makes the lower-belly center MAE exceed this
# threshold vs pass1 output, fall back to pass1 result.
PASS2_LOWER_BELLY_REJECT_MAE = 8.0
PASS2_AUTO_REJECT_ENABLED = True


# ── Output contract ──────────────────────────────────────────────────────────

@dataclass
class CutRefineResult:
    width: int
    height: int
    refined_image_b64: str
    seed_used: int = -1
    backend_used: str = ""
    debug_info: dict = field(default_factory=dict)


# ── Mask builders ────────────────────────────────────────────────────────────

def _build_seam_mask(
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
) -> np.ndarray:
    """Narrow contour mask along the edit_mask boundary.

    White = pixels within _SEAM_WIDTH_PX of the edit boundary,
    excluding protect regions.
    """
    edit_u8 = edit_mask.astype(np.uint8) * 255

    dist_inside = cv2.distanceTransform(edit_u8, cv2.DIST_L2, 5)
    dist_outside = cv2.distanceTransform(255 - edit_u8, cv2.DIST_L2, 5)

    seam = ((dist_inside > 0) & (dist_inside <= _SEAM_WIDTH_PX)) | \
           ((dist_outside > 0) & (dist_outside <= _SEAM_WIDTH_PX // 2))
    seam = seam & ~protect_mask

    return seam.astype(np.uint8) * 255


def _build_torso_interior_mask(
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    weight_map: np.ndarray,
    seam_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Upper-ab + oblique texture refinement mask for pass 2.

    Produces a spatially shaped mask that targets ONLY:
      - upper-ab center strip (above navel)
      - linea alba region
      - left/right oblique side bands
      - lower-chest to upper-ab transition

    Explicitly EXCLUDES:
      - shoulders / collarbone zone
      - lower-belly center (below navel)
      - waistband / shorts transition
      - arms, protect regions, seam band
      - navel circular buffer

    Returns
    -------
    spatial_mask : uint8 (0 or 255)
    strength_map : float32 [0, 1]
    """
    h, w = edit_mask.shape
    empty_u8 = np.zeros((h, w), dtype=np.uint8)
    empty_f32 = np.zeros((h, w), dtype=np.float32)

    # 1. Start from edit_mask
    candidate = edit_mask.copy()

    # 2. Exclude dilated protect region
    buf_k = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (_PROTECT_BUFFER_PX, _PROTECT_BUFFER_PX),
    )
    protect_buf = cv2.dilate(
        protect_mask.astype(np.uint8), buf_k, iterations=1,
    ) > 0
    candidate &= ~protect_buf

    # 3. Exclude seam band (don't overlap pass 1)
    if seam_mask is not None:
        seam_dilated = cv2.dilate(
            (seam_mask > 0).astype(np.uint8) * 255,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
            iterations=1,
        ) > 0
        candidate &= ~seam_dilated
    else:
        erode_k = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (_SEAM_WIDTH_PX, _SEAM_WIDTH_PX),
        )
        candidate &= cv2.erode(
            edit_mask.astype(np.uint8) * 255, erode_k, iterations=1,
        ) > 0

    # 4. Find active rows of the candidate
    rows_active = np.where(candidate.any(axis=1))[0]
    if len(rows_active) < 10:
        return empty_u8, empty_f32
    top_y = int(rows_active.min())
    bot_y = int(rows_active.max())
    span = bot_y - top_y
    if span < 20:
        return empty_u8, empty_f32

    # 5. Spatial shaping — define vertical zones
    shoulder_cutoff = top_y + int(span * _SHOULDER_SUPPRESS_FRAC)
    waistband_cutoff = bot_y - int(span * _WAISTBAND_SUPPRESS_FRAC)
    navel_y = top_y + int(span * 0.52)
    navel_radius = int(span * _NAVEL_EXCLUDE_RADIUS_FRAC)
    lower_belly_start = top_y + int(span * _LOWER_BELLY_CENTER_SUPPRESS_FRAC)

    # 5a. Suppress shoulders/collarbone
    candidate[:shoulder_cutoff, :] = False

    # 5b. Suppress waistband
    candidate[waistband_cutoff:, :] = False

    # 5c. Suppress lower-belly CENTER (below navel),
    #     but keep side obliques even in the lower zone.
    for y in range(lower_belly_start, waistband_cutoff):
        row_cols = np.where(candidate[y])[0]
        if len(row_cols) < 4:
            continue
        row_left = int(row_cols.min())
        row_right = int(row_cols.max())
        row_width = row_right - row_left
        if row_width < 4:
            continue
        center_margin = int(row_width * _LOWER_BELLY_CENTER_WIDTH_FRAC * 0.5)
        center_x = (row_left + row_right) // 2
        suppress_left = center_x - center_margin
        suppress_right = center_x + center_margin
        candidate[y, suppress_left:suppress_right + 1] = False

    # 5d. Navel exclusion buffer (circular)
    yy, xx = np.ogrid[:h, :w]
    navel_dist = np.sqrt((yy - navel_y) ** 2 + (xx - w // 2) ** 2)
    navel_exclude = navel_dist <= navel_radius
    candidate &= ~navel_exclude

    # 6. Distance-from-boundary → prefer interior pixels
    cand_u8 = candidate.astype(np.uint8) * 255
    dist = cv2.distanceTransform(cand_u8, cv2.DIST_L2, 5)
    pos_dists = dist[dist > 0]
    if len(pos_dists) < 50:
        return empty_u8, empty_f32

    # 7. Threshold: keep pixels that are reasonably inside
    core_thresh = max(2.0, float(np.percentile(pos_dists, 20)))
    core = dist >= core_thresh

    if not np.any(core):
        core = candidate.copy()

    # 8. Largest connected component
    n_labels, labels = cv2.connectedComponents(core.astype(np.uint8))
    if n_labels <= 1:
        return empty_u8, empty_f32

    component_sizes = [(lb, int((labels == lb).sum())) for lb in range(1, n_labels)]
    component_sizes.sort(key=lambda x: x[1], reverse=True)

    # Keep top components (main body + possibly separate oblique bands)
    core = np.zeros((h, w), dtype=bool)
    kept = 0
    for lb, sz in component_sizes:
        if sz < 500 and kept > 0:
            break
        core |= (labels == lb)
        kept += 1
        if kept >= 3:
            break

    # 9. Morphological closing to fill small gaps
    close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    core_u8 = cv2.morphologyEx(
        core.astype(np.uint8) * 255, cv2.MORPH_CLOSE, close_k,
    )
    dil_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    core_u8 = cv2.dilate(core_u8, dil_k, iterations=1)

    # Clip back to candidate
    core_final = (core_u8 > 0) & candidate

    if int(core_final.sum()) < _MIN_TORSO_CORE_PX:
        core_final = candidate

    spatial = core_final.astype(np.uint8) * 255

    # 10. Per-zone strength modulation
    #     upper_ab (top 45%):        strong (0.85 - 1.0)
    #     oblique side bands:         moderate (0.60 - 0.80)
    #     lower_chest transition:     mild (0.35 - 0.50)
    #     lower remaining fringe:     minimal (0.15 - 0.25)
    strength = empty_f32.copy()
    if np.any(core_final):
        active_rows = np.where(core_final.any(axis=1))[0]
        if len(active_rows) > 0:
            mask_top = int(active_rows.min())
            mask_bot = int(active_rows.max())
            mask_span = max(1, mask_bot - mask_top)

            for y in range(mask_top, mask_bot + 1):
                if not core_final[y].any():
                    continue
                frac = (y - mask_top) / mask_span
                row_cols = np.where(core_final[y])[0]
                if len(row_cols) == 0:
                    continue
                row_left = int(row_cols.min())
                row_right = int(row_cols.max())
                row_cx = (row_left + row_right) / 2.0
                row_hw = max(1.0, (row_right - row_left) / 2.0)

                for x in row_cols:
                    lat = abs(x - row_cx) / row_hw

                    if frac < 0.12:
                        # Lower-chest transition
                        s = 0.35 + 0.15 * (frac / 0.12)
                    elif frac < 0.50:
                        # Upper-ab zone — strongest
                        s = 0.85 + 0.15 * (1.0 - abs(frac - 0.30) / 0.20)
                        s = min(1.0, s)
                    else:
                        # Below mid-torso: fade quickly for center, keep for sides
                        vert_fade = max(0.15, 1.0 - (frac - 0.50) / 0.50)
                        s = vert_fade * 0.50

                    # Oblique boost: side pixels get a bump
                    if lat > 0.45:
                        oblique_boost = min(0.25, (lat - 0.45) / 0.55 * 0.25)
                        s = min(1.0, s + oblique_boost)

                    strength[y, x] = s

    return spatial, strength


def _build_lower_belly_center_mask(
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    seam_mask: np.ndarray | None = None,
) -> np.ndarray:
    """Build the lower-belly center analysis region for regression checks.

    This is the region most vulnerable to pass2 re-inflating the belly.
    """
    h, w = edit_mask.shape
    candidate = edit_mask.copy()

    buf_k = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (_PROTECT_BUFFER_PX, _PROTECT_BUFFER_PX),
    )
    protect_buf = cv2.dilate(
        protect_mask.astype(np.uint8), buf_k, iterations=1,
    ) > 0
    candidate &= ~protect_buf

    if seam_mask is not None:
        seam_dilated = cv2.dilate(
            (seam_mask > 0).astype(np.uint8) * 255,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
            iterations=1,
        ) > 0
        candidate &= ~seam_dilated

    rows_active = np.where(candidate.any(axis=1))[0]
    if len(rows_active) < 10:
        return np.zeros((h, w), dtype=bool)

    top_y = int(rows_active.min())
    bot_y = int(rows_active.max())
    span = bot_y - top_y
    if span < 20:
        return np.zeros((h, w), dtype=bool)

    lower_start = top_y + int(span * 0.55)
    lower_end = bot_y - int(span * 0.08)

    lb_mask = np.zeros((h, w), dtype=bool)
    for y in range(lower_start, min(lower_end, h)):
        row_cols = np.where(candidate[y])[0]
        if len(row_cols) < 4:
            continue
        row_left = int(row_cols.min())
        row_right = int(row_cols.max())
        row_width = row_right - row_left
        if row_width < 4:
            continue
        center_margin = int(row_width * 0.30)
        center_x = (row_left + row_right) // 2
        lb_mask[y, center_x - center_margin:center_x + center_margin + 1] = True

    lb_mask &= candidate
    return lb_mask


# ── Helpers ──────────────────────────────────────────────────────────────────

def _decode_b64_image(b64: str) -> Image.Image:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img) or img
    return img.convert("RGB")


def _decode_b64_mask(b64: str, w: int, h: int) -> np.ndarray:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("L").resize((w, h), Image.NEAREST)
    return np.array(img) > 128


def _decode_b64_float(b64: str, w: int, h: int) -> np.ndarray:
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("L").resize((w, h), Image.BILINEAR)
    return np.array(img).astype(np.float32) / 255.0


def _encode_jpeg_b64(img: np.ndarray) -> str:
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


# ── Main entry point ─────────────────────────────────────────────────────────

async def cut_refine(
    warped_image_b64: str,
    edit_mask_b64: str,
    protect_mask_b64: str,
    weight_map_b64: str,
    feather_mask_b64: str,
    *,
    preset: str = "medium",
    seed: int = -1,
) -> CutRefineResult:
    """Run two-pass CPU diffusion refinement on a warped body image.

    Both passes process only a small ROI crop for CPU feasibility.
    """
    t0 = time.monotonic()

    params = REFINE_PRESETS.get(preset, REFINE_PRESETS["medium"])

    # Decode everything
    warped_pil = _decode_b64_image(warped_image_b64)
    img_w, img_h = warped_pil.size
    warped_np = np.array(warped_pil)

    edit_mask = _decode_b64_mask(edit_mask_b64, img_w, img_h)
    protect_mask = _decode_b64_mask(protect_mask_b64, img_w, img_h)
    weight_map = _decode_b64_float(weight_map_b64, img_w, img_h)

    # Get backend
    backend = get_backend()
    if not backend.is_ready():
        logger.info("Loading diffusion backend...")
        backend.load()

    from ...config import settings
    roi_max = settings.diffusion_roi_max_px

    result_np = warped_np.copy()
    pass_debug = {}

    # ── PASS 1: Seam repair ──────────────────────────────────────────────
    seam_mask = _build_seam_mask(edit_mask, protect_mask)
    if np.any(seam_mask > 0):
        roi_seam = compute_roi(seam_mask, max_side=roi_max)
        roi_img = crop_to_roi(result_np, roi_seam)
        roi_mask = crop_mask_to_roi(seam_mask, roi_seam)

        req_seam = RefineRequest(
            init_image=roi_img,
            mask_image=roi_mask,
            prompt=P.SEAM_PROMPT,
            negative_prompt=P.SEAM_NEGATIVE,
            strength=params["seam_strength"],
            guidance_scale=params["seam_guidance"],
            num_steps=params["seam_steps"],
            seed=seed,
            width=roi_seam.target_w,
            height=roi_seam.target_h,
        )
        seam_result = backend.refine_seam(req_seam)
        result_np = composite_roi(
            result_np, seam_result.image, seam_mask > 0, roi_seam,
            feather_px=8,
        )
        seed = seam_result.seed_used
        pass_debug["pass1_seam"] = {
            "elapsed_ms": seam_result.elapsed_ms,
            "roi": f"{roi_seam.target_w}x{roi_seam.target_h}",
            "seed": seed,
        }
        logger.info(f"Pass 1 seam: {seam_result.elapsed_ms}ms")
    else:
        pass_debug["pass1_seam"] = {"skipped": True}

    after_seam_np = result_np.copy()

    # ── PASS 2: Upper-ab / oblique texture refinement ────────────────────
    torso_mask, torso_strength = _build_torso_interior_mask(
        edit_mask, protect_mask, weight_map, seam_mask=seam_mask,
    )
    torso_mask_px = int((torso_mask > 0).sum())
    pass2_rejected = False

    if torso_mask_px > 0:
        roi_torso = compute_roi(
            torso_mask, max_side=roi_max,
            min_target_w=_PASS2_MIN_TARGET_W,
            min_target_h=_PASS2_MIN_TARGET_H,
        )
        roi_img = crop_to_roi(result_np, roi_torso)
        roi_mask = crop_mask_to_roi(torso_mask, roi_torso)

        req_torso = RefineRequest(
            init_image=roi_img,
            mask_image=roi_mask,
            prompt=P.get_torso_prompt(5.0, preset),
            negative_prompt=P.get_torso_negative(5.0, preset),
            strength=params["torso_strength"],
            guidance_scale=params["torso_guidance"],
            num_steps=params["torso_steps"],
            seed=seed,
            width=roi_torso.target_w,
            height=roi_torso.target_h,
        )
        torso_result = backend.refine_torso(req_torso)
        pass2_candidate = composite_roi(
            result_np.copy(), torso_result.image, torso_mask > 0, roi_torso,
            feather_px=14,
            strength_map=torso_strength,
        )

        # ── Auto-reject: check lower-belly regression ────────────────
        if PASS2_AUTO_REJECT_ENABLED:
            lb_mask = _build_lower_belly_center_mask(
                edit_mask, protect_mask, seam_mask,
            )
            lb_px = int(lb_mask.sum())
            if lb_px > 100:
                diff_lb = np.abs(
                    pass2_candidate.astype(np.float32)
                    - after_seam_np.astype(np.float32),
                ).mean(axis=2)
                lb_mae = float(diff_lb[lb_mask].mean())
                if lb_mae > PASS2_LOWER_BELLY_REJECT_MAE:
                    logger.warning(
                        f"Pass 2 auto-rejected: lower-belly MAE={lb_mae:.1f} "
                        f"> threshold={PASS2_LOWER_BELLY_REJECT_MAE}"
                    )
                    pass2_rejected = True

        if not pass2_rejected:
            result_np = pass2_candidate

        pass_debug["pass2_torso"] = {
            "elapsed_ms": torso_result.elapsed_ms,
            "roi": f"{roi_torso.target_w}x{roi_torso.target_h}",
            "mask_px": torso_mask_px,
            "seed": torso_result.seed_used,
            "auto_rejected": pass2_rejected,
        }
        logger.info(
            f"Pass 2 torso: {torso_result.elapsed_ms}ms, "
            f"mask={torso_mask_px}px, roi={roi_torso.target_w}x{roi_torso.target_h}"
            f"{' [REJECTED]' if pass2_rejected else ''}"
        )
    else:
        pass_debug["pass2_torso"] = {"skipped": True, "mask_px": 0}

    elapsed = round((time.monotonic() - t0) * 1000, 1)
    backend_info = backend.get_debug_info()

    logger.info(
        f"CUT refine done in {elapsed}ms: backend={backend_info.get('backend')}"
    )

    return CutRefineResult(
        width=img_w,
        height=img_h,
        refined_image_b64=_encode_jpeg_b64(result_np),
        seed_used=seed,
        backend_used=backend_info.get("backend", ""),
        debug_info={
            "elapsed_ms": elapsed,
            "preset": preset,
            "roi_max_px": roi_max,
            "passes": pass_debug,
            "backend": backend_info,
        },
    )
