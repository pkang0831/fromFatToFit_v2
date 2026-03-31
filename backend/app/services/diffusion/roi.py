"""
ROI (Region of Interest) crop / composite utilities.

Running SD inpainting on a full-res photo is impractical on CPU.
Instead we:
  1. Extract the bounding box of the edit_mask with a safe margin.
  2. Resize the crop to the model's native resolution (~512px).
  3. Run diffusion only on the small ROI.
  4. Up-scale the result back to original crop size.
  5. Feathered-composite back into the full image.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# Minimum margin around the edit_mask bbox (pixels in original resolution).
_MIN_MARGIN_PX = 32
# Fraction of bbox size to use as margin (whichever is larger wins).
_MARGIN_FRAC = 0.15


@dataclass
class ROICrop:
    """Describes the crop rectangle inside the full image."""
    x0: int
    y0: int
    x1: int
    y1: int
    # The target size after resizing for diffusion
    target_w: int
    target_h: int
    # Original full-image dimensions
    full_w: int
    full_h: int


def compute_roi(
    edit_mask: np.ndarray,
    max_side: int = 512,
    min_target_w: int = 0,
    min_target_h: int = 0,
) -> ROICrop:
    """Compute a square-ish ROI bounding box around the edit region.

    The crop is padded with a safe margin so the diffusion model sees
    enough context, then quantized to multiples of 8.

    ``min_target_w`` / ``min_target_h`` prevent extremely thin strip
    ROIs by expanding the crop around the mask centre when needed.
    """
    h, w = edit_mask.shape[:2]
    ys, xs = np.where(edit_mask > 0)
    if len(ys) == 0:
        cx, cy = w // 2, h // 2
        half = min(w, h, max_side) // 2
        return ROICrop(
            x0=max(0, cx - half), y0=max(0, cy - half),
            x1=min(w, cx + half), y1=min(h, cy + half),
            target_w=max_side, target_h=max_side,
            full_w=w, full_h=h,
        )

    bbox_x0, bbox_y0 = int(xs.min()), int(ys.min())
    bbox_x1, bbox_y1 = int(xs.max()), int(ys.max())
    bbox_w = bbox_x1 - bbox_x0
    bbox_h = bbox_y1 - bbox_y0

    margin_x = max(_MIN_MARGIN_PX, int(bbox_w * _MARGIN_FRAC))
    margin_y = max(_MIN_MARGIN_PX, int(bbox_h * _MARGIN_FRAC))

    x0 = max(0, bbox_x0 - margin_x)
    y0 = max(0, bbox_y0 - margin_y)
    x1 = min(w, bbox_x1 + margin_x)
    y1 = min(h, bbox_y1 + margin_y)

    crop_w = x1 - x0
    crop_h = y1 - y0

    # ── Enforce minimum target dimensions ─────────────────────────────
    # Estimate the downscale factor from the current crop, then compute
    # the crop size needed to meet the minimum target after scaling.
    if min_target_w > 0 or min_target_h > 0:
        scale_est = min(max_side / max(crop_w, 1),
                        max_side / max(crop_h, 1), 1.0)

        if min_target_h > 0:
            needed_h = int(np.ceil(min_target_h / max(scale_est, 0.05)))
            if crop_h < needed_h:
                cy = (y0 + y1) // 2
                y0 = max(0, cy - needed_h // 2)
                y1 = min(h, y0 + needed_h)
                y0 = max(0, y1 - needed_h)
                crop_h = y1 - y0

        if min_target_w > 0:
            # Recompute scale after potential height expansion
            scale_est = min(max_side / max(crop_w, 1),
                            max_side / max(crop_h, 1), 1.0)
            needed_w = int(np.ceil(min_target_w / max(scale_est, 0.05)))
            if crop_w < needed_w:
                cx = (x0 + x1) // 2
                x0 = max(0, cx - needed_w // 2)
                x1 = min(w, x0 + needed_w)
                x0 = max(0, x1 - needed_w)
                crop_w = x1 - x0

    # Compute target size: fit the longer side to max_side, keep aspect,
    # then round to multiples of 8.
    scale = min(max_side / max(crop_w, 1), max_side / max(crop_h, 1), 1.0)
    target_w = max(64, (int(crop_w * scale) // 8) * 8)
    target_h = max(64, (int(crop_h * scale) // 8) * 8)

    # Final safety: clamp target to requested minimums (may slightly
    # exceed max_side if the image is tiny).
    if min_target_w > 0:
        target_w = max(target_w, (min(min_target_w, max_side) // 8) * 8)
    if min_target_h > 0:
        target_h = max(target_h, (min(min_target_h, max_side) // 8) * 8)

    logger.info(
        f"ROI: crop={crop_w}x{crop_h} → target={target_w}x{target_h}"
    )

    return ROICrop(
        x0=x0, y0=y0, x1=x1, y1=y1,
        target_w=target_w, target_h=target_h,
        full_w=w, full_h=h,
    )


def crop_to_roi(
    image: np.ndarray,
    roi: ROICrop,
) -> Image.Image:
    """Crop + resize an image (HxWx3 or HxW) to the ROI target size."""
    crop = image[roi.y0:roi.y1, roi.x0:roi.x1]
    pil = Image.fromarray(crop)
    return pil.resize((roi.target_w, roi.target_h), Image.LANCZOS)


def crop_mask_to_roi(
    mask: np.ndarray,
    roi: ROICrop,
) -> Image.Image:
    """Crop + resize a boolean or uint8 mask to the ROI target size."""
    if mask.dtype == bool:
        mask = (mask.astype(np.uint8) * 255)
    crop = mask[roi.y0:roi.y1, roi.x0:roi.x1]
    pil = Image.fromarray(crop, mode="L")
    return pil.resize((roi.target_w, roi.target_h), Image.LANCZOS)


def composite_roi(
    full_image: np.ndarray,
    roi_result: Image.Image,
    mask: np.ndarray,
    roi: ROICrop,
    feather_px: int = 12,
    strength_map: np.ndarray | None = None,
) -> np.ndarray:
    """Paste the diffusion ROI result back into the full image.

    Uses the edit mask + feathering to blend seamlessly.
    If ``strength_map`` (float32, full-image resolution) is provided it
    modulates the blend alpha so weight_map controls refinement
    intensity without collapsing the spatial mask.
    """
    out = full_image.copy()

    # Up-scale diffusion result back to original crop size
    crop_w = roi.x1 - roi.x0
    crop_h = roi.y1 - roi.y0
    upscaled = roi_result.resize((crop_w, crop_h), Image.LANCZOS)
    upscaled_np = np.array(upscaled)

    # Build a smooth blend mask from the edit mask within the crop
    crop_mask = mask[roi.y0:roi.y1, roi.x0:roi.x1]
    if crop_mask.dtype == bool:
        crop_mask = crop_mask.astype(np.uint8) * 255

    # Feather the mask edges for seamless compositing
    if feather_px > 0:
        dist = cv2.distanceTransform(crop_mask, cv2.DIST_L2, 5)
        blend = np.clip(dist / max(1, feather_px), 0.0, 1.0).astype(np.float32)
    else:
        blend = (crop_mask / 255.0).astype(np.float32)

    # Modulate blend by per-pixel strength (weight_map driven)
    if strength_map is not None:
        crop_strength = strength_map[roi.y0:roi.y1, roi.x0:roi.x1]
        blend = blend * crop_strength

    if len(upscaled_np.shape) == 3:
        blend_3ch = blend[:, :, None]
    else:
        blend_3ch = blend

    original_crop = out[roi.y0:roi.y1, roi.x0:roi.x1].astype(np.float32)
    refined_crop = upscaled_np.astype(np.float32)
    blended = original_crop * (1.0 - blend_3ch) + refined_crop * blend_3ch

    out[roi.y0:roi.y1, roi.x0:roi.x1] = np.clip(blended, 0, 255).astype(np.uint8)
    return out
