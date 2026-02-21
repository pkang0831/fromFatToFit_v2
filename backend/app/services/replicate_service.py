"""
Body transformation service using Replicate's FLUX Kontext Pro model.
Generates identity-preserving body transformations based on target body fat %.

Pipeline:
1. EXIF orientation fix
2. FLUX Kontext Pro/Max generation via curl subprocess
3. Post-processing: alpha blend + texture restoration from original

Uses curl subprocess for API calls to reliably work through corporate
proxies that interfere with Python HTTP libraries (httpx/requests).
"""

import asyncio
import base64
import io
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

BODY_BLEND_ALPHA = 0.6
TEXTURE_STRENGTH = 0.35
TEXTURE_BLUR_RADIUS = 4
MASK_BLUR_RADIUS = 50
TARGET_LONG_EDGE = 1440


def _fix_exif_and_resize(image_bytes: bytes) -> tuple[bytes, Image.Image]:
    """Apply EXIF orientation fix and resize for optimal model input."""
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)

    ratio = TARGET_LONG_EDGE / max(img.size)
    if ratio < 1.0:
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    if img.mode != "RGB":
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=92)
    return buf.getvalue(), img


def _build_prompt(current_bf: float, target_bf: float, gender: str) -> str:
    """Build a natural-sounding transformation prompt."""
    direction = "cutting" if target_bf < current_bf else "bulking"
    bf_diff = abs(current_bf - target_bf)

    if bf_diff <= 3:
        time_frame = "a few weeks"
        fat_desc = "very slightly"
    elif bf_diff <= 7:
        time_frame = "8 weeks"
        fat_desc = "slightly"
    else:
        time_frame = "3 months"
        fat_desc = "noticeably"

    preserve = (
        "Same person, same pose, same background, same lighting. "
        "Preserve all skin details: pores, body hair, moles, natural shadows, "
        "camera noise, and JPEG compression artifacts."
    )

    if gender == "female":
        if direction == "cutting":
            body_desc = (
                f"This woman after {time_frame} of consistent training and clean eating. "
                f"Her midsection is {fat_desc} leaner, with a slimmer waist. "
                "Existing muscle tone in arms and shoulders is slightly more visible. "
                "Natural, toned feminine physique."
            )
        else:
            body_desc = (
                f"This woman after {time_frame} of strength training. "
                f"Slightly fuller in the glutes and thighs with a more athletic build. "
                "Toned arms and a defined waist-to-hip ratio. "
                "Strong, curvy feminine physique."
            )
    else:
        if direction == "cutting":
            body_desc = (
                f"This man after {time_frame} of cutting diet and training. "
                f"His midsection is {fat_desc} leaner with the belly area flatter. "
                "Existing muscle definition in chest and arms is slightly more visible. "
                "Natural athletic look — no exaggerated or bodybuilder-level definition."
            )
        else:
            body_desc = (
                f"This man after {time_frame} of bulk training. "
                "Slightly broader shoulders, thicker arms and chest. "
                "A solid, powerful build while maintaining natural proportions. "
                "Strong and imposing but realistic physique."
            )

    return f"{body_desc} {preserve}"


def _create_body_mask(w: int, h: int) -> Image.Image:
    """
    Create a gradient mask for the torso region.
    White = transformed, Black = original.
    Gaussian blur creates smooth transitions.
    """
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)

    body_top = int(h * 0.30)
    body_bottom = int(h * 0.70)
    body_left = int(w * 0.18)
    body_right = int(w * 0.82)

    draw.rectangle([body_left, body_top, body_right, body_bottom], fill=255)
    return mask.filter(ImageFilter.GaussianBlur(radius=MASK_BLUR_RADIUS))


def _postprocess(original: Image.Image, transformed_bytes: bytes) -> bytes:
    """
    Post-process: blend body area with original to preserve naturalness.
    1. Alpha blend (keep face/background from original)
    2. Restore skin texture via high-pass filter from original
    """
    w, h = original.size
    transformed = Image.open(io.BytesIO(transformed_bytes)).resize((w, h), Image.LANCZOS)
    if transformed.mode != "RGB":
        transformed = transformed.convert("RGB")

    orig_arr = np.array(original, dtype=np.float32)
    trans_arr = np.array(transformed, dtype=np.float32)

    mask = _create_body_mask(w, h)
    mask_arr = np.array(mask, dtype=np.float32) / 255.0
    mask_arr = np.expand_dims(mask_arr, axis=2)

    # Alpha blend in body area
    blended = orig_arr * (1 - BODY_BLEND_ALPHA) + trans_arr * BODY_BLEND_ALPHA
    result = blended * mask_arr + orig_arr * (1.0 - mask_arr)

    # Restore skin texture from original via high-pass filter
    orig_blur = np.array(
        original.filter(ImageFilter.GaussianBlur(radius=TEXTURE_BLUR_RADIUS)),
        dtype=np.float32,
    )
    detail_layer = orig_arr - orig_blur
    result += detail_layer * mask_arr * TEXTURE_STRENGTH

    result = np.clip(result, 0, 255).astype(np.uint8)
    out_img = Image.fromarray(result)

    buf = io.BytesIO()
    out_img.save(buf, "JPEG", quality=95)
    return buf.getvalue()


def _curl_json(method: str, url: str, api_key: str, json_body: dict | None = None) -> dict:
    """Make an API call via curl subprocess (reliable through corporate proxies)."""
    cmd = [
        "curl", "-sk",
        "-X", method,
        url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
    ]

    tmp_file = None
    if json_body is not None:
        tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(json_body, tmp_file)
        tmp_file.close()
        cmd.extend(["-d", f"@{tmp_file.name}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr[:300]}")
        return json.loads(result.stdout)
    finally:
        if tmp_file is not None:
            os.unlink(tmp_file.name)


def _curl_download(url: str, dest_path: str) -> None:
    """Download a file via curl."""
    result = subprocess.run(
        ["curl", "-sk", "-o", dest_path, url],
        capture_output=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl download failed: {result.stderr[:200]}")


def _load_font(size: int):
    """Load a system font, falling back to PIL default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                from PIL import ImageFont
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    from PIL import ImageFont
    return ImageFont.load_default()


def _generate_progress_frames(
    original: Image.Image,
    transformed_bytes: bytes,
    current_bf: float,
    target_bf: float,
    direction: str,
    num_frames: int = 10,
) -> list[dict]:
    """
    Generate intermediate progress frames between original and transformed.
    Each frame has a date, week number, estimated BF%, and the blended image.

    Returns list of dicts with keys: date, week, bf_pct, image_b64
    """
    w, h = original.size
    transformed = Image.open(io.BytesIO(transformed_bytes)).resize((w, h), Image.LANCZOS)
    if transformed.mode != "RGB":
        transformed = transformed.convert("RGB")

    orig_arr = np.array(original, dtype=np.float32)
    trans_arr = np.array(transformed, dtype=np.float32)

    mask = _create_body_mask(w, h)
    mask_arr = np.array(mask, dtype=np.float32) / 255.0
    mask_arr = np.expand_dims(mask_arr, axis=2)

    orig_blur = np.array(
        original.filter(ImageFilter.GaussianBlur(radius=TEXTURE_BLUR_RADIUS)),
        dtype=np.float32,
    )
    detail_layer = orig_arr - orig_blur

    font_large = _load_font(36)
    font_small = _load_font(22)

    bf_diff = abs(current_bf - target_bf)
    if bf_diff <= 3:
        total_weeks = 4
    elif bf_diff <= 7:
        total_weeks = 8
    else:
        total_weeks = 12
    total_days = total_weeks * 7

    start_date = datetime.now()
    frames = []

    for i in range(num_frames):
        progress = (i + 1) / num_frames
        eased = progress ** 1.3

        alpha = eased * BODY_BLEND_ALPHA
        blended = orig_arr * (1 - alpha) + trans_arr * alpha
        result = blended * mask_arr + orig_arr * (1.0 - mask_arr)

        tex_strength = TEXTURE_STRENGTH * (1.0 - eased * 0.3)
        result += detail_layer * mask_arr * tex_strength
        result = np.clip(result, 0, 255).astype(np.uint8)

        frame = Image.fromarray(result)

        day_offset = int(total_days * progress)
        frame_date = start_date + timedelta(days=day_offset)
        date_str = frame_date.strftime("%b %d, %Y")
        week_num = day_offset // 7

        if direction == "cutting":
            frame_bf = current_bf - (bf_diff * eased)
        else:
            frame_bf = current_bf + (bf_diff * eased)

        # Overlay: semi-transparent bar with date, week, BF
        bar_height = 70
        overlay = Image.new("RGBA", (w, bar_height), (0, 0, 0, 160))
        frame_rgba = frame.convert("RGBA")
        frame_rgba.paste(overlay, (0, 0), overlay)
        frame = frame_rgba.convert("RGB")
        draw = ImageDraw.Draw(frame)

        draw.text((20, 10), date_str, fill=(255, 255, 255), font=font_large)
        draw.text(
            (20, 42),
            f"Week {week_num}  |  ~{frame_bf:.1f}% BF",
            fill=(200, 220, 255),
            font=font_small,
        )
        progress_label = f"{i + 1}/{num_frames}"
        bbox = draw.textbbox((0, 0), progress_label, font=font_large)
        draw.text(
            (w - (bbox[2] - bbox[0]) - 20, 10),
            progress_label,
            fill=(255, 255, 255),
            font=font_large,
        )

        buf = io.BytesIO()
        frame.save(buf, "JPEG", quality=90)
        frame_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        frames.append({
            "date": date_str,
            "week": week_num,
            "bf_pct": round(frame_bf, 1),
            "image_b64": f"data:image/jpeg;base64,{frame_b64}",
        })

    return frames


async def generate_body_transformation(
    image_base64: str,
    current_bf: float,
    target_bf: float,
    gender: str = "male",
) -> dict:
    """
    Generate a body transformation preview using FLUX Kontext Pro on Replicate.

    Pipeline:
    1. Fix EXIF orientation & resize
    2. Generate with FLUX Kontext Pro
    3. Post-process: alpha blend body area + texture restoration

    Returns dict with:
        - transformed_image_url: base64 data URL of the result
        - direction: "cutting" or "bulking"
        - muscle_gain_estimate: estimated kg range string
    """
    from ..config import settings

    api_key = getattr(settings, "replicate_api_key", None)
    if not api_key:
        raise RuntimeError("REPLICATE_API_KEY is not configured")

    direction = "cutting" if target_bf < current_bf else "bulking"
    prompt = _build_prompt(current_bf, target_bf, gender)

    if gender == "female":
        muscle_gain = "1-2 kg" if direction == "cutting" else "1.5-2.5 kg"
    else:
        muscle_gain = "2-3 kg" if direction == "cutting" else "3-4 kg"

    logger.info(
        f"Replicate transformation: gender={gender}, direction={direction}, "
        f"current_bf={current_bf:.1f}%, target_bf={target_bf:.1f}%"
    )

    # Step 1: EXIF fix + resize
    raw_bytes = base64.b64decode(image_base64)
    processed_bytes, original_img = _fix_exif_and_resize(raw_bytes)
    processed_b64 = base64.b64encode(processed_bytes).decode("utf-8")

    data_uri = f"data:image/jpeg;base64,{processed_b64}"

    payload = {
        "input": {
            "prompt": prompt,
            "input_image": data_uri,
            "aspect_ratio": "match_input_image",
            "output_format": "jpg",
            "output_quality": 95,
            "safety_tolerance": 2,
        },
    }

    loop = asyncio.get_event_loop()

    # Step 2: create prediction via FLUX Kontext Pro
    create_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions"
    pred = await loop.run_in_executor(None, _curl_json, "POST", create_url, api_key, payload)

    pred_status = pred.get("status")
    pred_id = pred.get("id")

    if pred_status == "failed":
        raise RuntimeError(f"Prediction failed: {pred.get('error')}")

    logger.info(f"Prediction created: {pred_id}, status={pred_status}")

    # Step 3: poll until done
    poll_url = pred.get("urls", {}).get("get", f"https://api.replicate.com/v1/predictions/{pred_id}")
    image_url = None

    for _ in range(90):
        await asyncio.sleep(2)
        poll_data = await loop.run_in_executor(None, _curl_json, "GET", poll_url, api_key, None)
        pred_status = poll_data.get("status")

        if pred_status == "succeeded":
            output = poll_data.get("output")
            image_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
            metrics = poll_data.get("metrics", {})
            logger.info(f"Prediction succeeded: {json.dumps(metrics)}")
            break
        elif pred_status in ("failed", "canceled"):
            raise RuntimeError(f"Prediction {pred_status}: {poll_data.get('error')}")

    if not image_url:
        raise RuntimeError("Prediction timed out after 180s")

    # Step 4: download raw result
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await loop.run_in_executor(None, _curl_download, image_url, tmp_path)
        with open(tmp_path, "rb") as f:
            raw_result = f.read()
    finally:
        os.unlink(tmp_path)

    # Step 5: post-process (alpha blend body + texture restoration)
    final_bytes = await loop.run_in_executor(
        None, _postprocess, original_img, raw_result
    )
    result_b64 = base64.b64encode(final_bytes).decode("utf-8")

    # Step 6: generate progress timeline frames
    progress_frames = await loop.run_in_executor(
        None,
        _generate_progress_frames,
        original_img,
        raw_result,
        current_bf,
        target_bf,
        direction,
    )

    return {
        "transformed_image_url": f"data:image/jpeg;base64,{result_b64}",
        "direction": direction,
        "muscle_gain_estimate": muscle_gain,
        "progress_frames": progress_frames,
    }
