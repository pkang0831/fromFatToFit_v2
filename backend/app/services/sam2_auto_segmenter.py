"""
SAM2-based auto-segmenter with body-part heuristic labeling.

Flow:
  1. SAM2 auto-segments the image via Replicate into individual masks.
  2. For each mask we compute centroid (cx_norm, cy_norm) and area fraction.
  3. A heuristic assigns each mask to a body-part class based on position/size.
  4. Overlapping masks are resolved by priority (smaller / more specific wins).
  5. The result is a label map PNG at the original image resolution.

Anatomical convention:
  left/right = person's anatomical left/right.
  In a standard (non-mirror) front-facing photo, the person's LEFT side
  appears on the viewer's RIGHT.  For mirror selfies the opposite applies.
  We assume front-facing by default; the user corrects any errors.
"""

from __future__ import annotations

import asyncio
import base64
import io
import logging
from typing import Optional

import numpy as np
from PIL import Image

from .replicate_utils import (
    curl_json,
    get_replicate_api_key,
    image_to_data_uri,
    poll_prediction,
    curl_download,
)
from .segmenter_interface import SegmenterAdapter, SegmentationResult, SEG_CLASSES

logger = logging.getLogger(__name__)

SAM2_PREDICTIONS_URL = "https://api.replicate.com/v1/predictions"
SAM2_VERSION = "fe97b453a6455861e3bac769b441ca1f1086110da7466dbb65cf1eecfd60dc83"


def _download_mask_np(url: str, target_size: tuple[int, int]) -> np.ndarray:
    """Download a mask PNG and return as a (H,W) bool array at target_size."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        curl_download(url, tmp_path)
        img = Image.open(tmp_path).convert("L").resize(target_size, Image.NEAREST)
        return np.array(img) > 128
    finally:
        os.unlink(tmp_path)


def _mask_stats(mask: np.ndarray, img_w: int, img_h: int) -> dict:
    """Compute centroid and area fraction for a boolean mask."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return {"cx": 0.5, "cy": 0.5, "area_frac": 0.0, "count": 0}
    return {
        "cx": float(xs.mean()) / img_w,
        "cy": float(ys.mean()) / img_h,
        "area_frac": float(len(ys)) / (img_w * img_h),
        "count": int(len(ys)),
    }


def _assign_body_part(cx: float, cy: float, area_frac: float) -> int:
    """Heuristic: map centroid position + area to a class ID.

    Returns 0 (background) if no good match.
    Assumes a standard front-facing body photo with head at the top.

    left/right = person's anatomical left/right.
    In a front-facing photo the person's left is viewer's RIGHT (cx > 0.5).
    """
    # Skip tiny masks (noise) or huge masks (full image background)
    if area_frac < 0.005 or area_frac > 0.6:
        return 0

    # Head: top of image, any X
    if cy < 0.20 and area_frac < 0.15:
        return 1  # head

    # Shoulders: upper body, lateral
    if 0.12 < cy < 0.38:
        if cx > 0.62:
            return 4  # person's left shoulder (viewer's right)
        if cx < 0.38:
            return 5  # person's right shoulder (viewer's left)

    # Arms: mid-to-lower body, far lateral
    if 0.20 < cy < 0.70:
        if cx > 0.72 and area_frac < 0.10:
            return 6  # person's left arm
        if cx < 0.28 and area_frac < 0.10:
            return 7  # person's right arm

    # Chest: upper-center
    if 0.18 < cy < 0.42 and 0.30 < cx < 0.70:
        if area_frac < 0.15:
            return 2  # chest

    # Torso: mid-center, typically the largest central mask
    if 0.30 < cy < 0.70 and 0.25 < cx < 0.75:
        return 3  # torso

    return 0


def _build_label_map(
    masks: list[np.ndarray],
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Build a (H, W) uint8 label map from SAM2 masks + heuristic.

    When masks overlap, smaller (more specific) masks take priority.
    """
    label_map = np.zeros((img_h, img_w), dtype=np.uint8)

    scored: list[tuple[int, int, np.ndarray]] = []
    for mask in masks:
        stats = _mask_stats(mask, img_w, img_h)
        class_id = _assign_body_part(stats["cx"], stats["cy"], stats["area_frac"])
        if class_id > 0:
            scored.append((stats["count"], class_id, mask))

    # Paint largest masks first so smaller/more-specific masks overwrite
    scored.sort(key=lambda x: -x[0])
    for _, class_id, mask in scored:
        label_map[mask] = class_id

    return label_map


def _label_map_to_png_b64(label_map: np.ndarray) -> str:
    """Encode a uint8 label map as a grayscale PNG, return base64."""
    img = Image.fromarray(label_map, mode="L")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


class SAM2AutoSegmenter(SegmenterAdapter):
    """SAM2-based segmenter with position/size heuristic for body-part labels."""

    async def segment(self, image_base64: str) -> SegmentationResult:
        api_key = get_replicate_api_key()

        raw = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(raw))
        img_w, img_h = img.size

        logger.info(f"SAM2 auto-segment: {img_w}x{img_h}")

        data_uri = image_to_data_uri(image_base64, "jpeg")

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
            detail = pred.get("detail", str(pred)[:300])
            raise RuntimeError(f"SAM2 prediction failed: {detail}")

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

        logger.info(f"SAM2 returned {len(mask_urls)} masks, downloading & labeling...")

        np_masks: list[np.ndarray] = []
        for url in mask_urls:
            try:
                m = await loop.run_in_executor(
                    None, _download_mask_np, url, (img_w, img_h),
                )
                np_masks.append(m)
            except Exception as e:
                logger.warning(f"Failed to download mask: {e}")

        label_map = _build_label_map(np_masks, img_w, img_h)
        label_map_b64 = _label_map_to_png_b64(label_map)

        unique_classes = set(int(v) for v in np.unique(label_map) if v > 0)
        logger.info(
            f"SAM2 auto-segment done: {len(np_masks)} masks -> "
            f"{len(unique_classes)} body-part classes assigned"
        )

        return SegmentationResult(
            width=img_w,
            height=img_h,
            label_map_b64=label_map_b64,
            classes=SEG_CLASSES,
            debug_info={
                "total_sam_masks": len(mask_urls),
                "downloaded": len(np_masks),
                "assigned_classes": sorted(unique_classes),
            },
        )
