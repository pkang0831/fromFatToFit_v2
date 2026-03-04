"""
SAM-2 segmentation service for body part selection.

Strategy:
1. Call meta/sam-2 to auto-segment the entire image into individual masks
2. Download each mask and check which one contains the user's click point
3. Return the best-matching mask (smallest area that contains the click)
"""

import asyncio
import base64
import io
import logging
import os
import tempfile

from PIL import Image

from .replicate_utils import (
    curl_json,
    curl_download,
    get_replicate_api_key,
    image_to_data_uri,
    poll_prediction,
)

logger = logging.getLogger(__name__)

SAM2_PREDICTIONS_URL = "https://api.replicate.com/v1/predictions"
SAM2_VERSION = "fe97b453a6455861e3bac769b441ca1f1086110da7466dbb65cf1eecfd60dc83"

BODY_PART_Y_RANGES = [
    (0.00, 0.15, "head"),
    (0.15, 0.30, "shoulders"),
    (0.30, 0.45, "chest"),
    (0.45, 0.62, "abdomen"),
    (0.62, 0.78, "thighs"),
    (0.78, 1.00, "legs"),
]


def _guess_body_part(click_y_norm: float, click_x_norm: float) -> str:
    for y_min, y_max, part in BODY_PART_Y_RANGES:
        if y_min <= click_y_norm < y_max:
            if part == "shoulders" and (click_x_norm < 0.25 or click_x_norm > 0.75):
                return "arms"
            return part
    return "body"


def _mask_contains_click(mask_img: Image.Image, click_x_px: int, click_y_px: int) -> bool:
    """Check if the mask has a white pixel at the click location."""
    if mask_img.mode != "L":
        mask_img = mask_img.convert("L")
    x = min(click_x_px, mask_img.width - 1)
    y = min(click_y_px, mask_img.height - 1)
    return mask_img.getpixel((x, y)) > 128


def _mask_white_count(mask_img: Image.Image) -> int:
    """Count white pixels in a mask."""
    if mask_img.mode != "L":
        mask_img = mask_img.convert("L")
    return sum(1 for p in mask_img.getdata() if p > 128)


def _download_mask(url: str) -> Image.Image:
    """Download a mask URL and return as PIL Image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        curl_download(url, tmp_path)
        return Image.open(tmp_path).copy()
    finally:
        os.unlink(tmp_path)


async def segment_body_part(
    image_base64: str,
    click_x_norm: float,
    click_y_norm: float,
) -> dict:
    """
    Segment a body part using SAM-2 auto-segmentation + click selection.

    1. SAM-2 auto-segments the entire image
    2. Find which mask contains the click point
    3. Return the smallest matching mask (most precise)
    """
    api_key = get_replicate_api_key()

    img_bytes = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(img_bytes))
    w, h = img.size

    click_x_px = int(click_x_norm * w)
    click_y_px = int(click_y_norm * h)

    logger.info(f"SAM-2 segment: click=({click_x_px},{click_y_px}) on {w}x{h}")

    data_uri = image_to_data_uri(image_base64, "jpeg")

    payload = {
        "version": SAM2_VERSION,
        "input": {
            "image": data_uri,
            "points_per_side": 32,
            "pred_iou_thresh": 0.88,
            "stability_score_thresh": 0.95,
            "use_m2m": True,
        }
    }

    loop = asyncio.get_event_loop()
    pred = await loop.run_in_executor(
        None, curl_json, "POST", SAM2_PREDICTIONS_URL, api_key, payload,
    )

    pred_status = pred.get("status")
    pred_id = pred.get("id")

    if not pred_id:
        error_detail = pred.get("detail", str(pred)[:300])
        raise RuntimeError(f"SAM-2 failed to create prediction: {error_detail}")

    logger.info(f"SAM-2 prediction: {pred_id}, status={pred_status}")

    if pred_status not in ("succeeded",):
        poll_url = pred.get("urls", {}).get(
            "get", f"https://api.replicate.com/v1/predictions/{pred_id}",
        )
        pred = await poll_prediction(poll_url, api_key, max_polls=90, interval=2.0)

    output = pred.get("output", {})
    mask_urls = output.get("individual_masks", [])
    combined_url = output.get("combined_mask")

    if not mask_urls:
        if combined_url:
            mask_urls = [combined_url]
        else:
            raise RuntimeError("SAM-2 returned no masks")

    logger.info(f"SAM-2 returned {len(mask_urls)} individual masks, finding click match...")

    # Download all masks and find the one containing the click point
    candidates = []

    for i, url in enumerate(mask_urls):
        try:
            mask_img = await loop.run_in_executor(None, _download_mask, url)
            if _mask_contains_click(mask_img, click_x_px, click_y_px):
                white_count = _mask_white_count(mask_img)
                candidates.append((white_count, mask_img, i))
        except Exception as e:
            logger.warning(f"Failed to download mask {i}: {e}")
            continue

    if not candidates:
        logger.warning("No mask contains the click point, using combined mask")
        if combined_url:
            mask_img = await loop.run_in_executor(None, _download_mask, combined_url)
            candidates.append((_mask_white_count(mask_img), mask_img, -1))
        else:
            raise RuntimeError("No SAM-2 mask matches the clicked area")

    # Pick the smallest mask that contains the click (most specific segment)
    candidates.sort(key=lambda c: c[0])
    best_count, best_mask, best_idx = candidates[0]

    # Convert to base64
    if best_mask.mode != "L":
        best_mask = best_mask.convert("L")

    buf = io.BytesIO()
    best_mask.save(buf, "PNG")
    mask_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    total_pixels = best_mask.width * best_mask.height
    area_pct = round(best_count / total_pixels * 100, 1) if total_pixels > 0 else 0.0

    body_part = _guess_body_part(click_y_norm, click_x_norm)

    logger.info(
        f"SAM-2 segment complete: part={body_part}, area={area_pct}%, "
        f"mask_idx={best_idx}, candidates={len(candidates)}/{len(mask_urls)}"
    )

    return {
        "mask_base64": mask_b64,
        "body_part_guess": body_part,
        "mask_area_pct": area_pct,
    }
