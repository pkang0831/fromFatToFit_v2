"""
Replicate service for body transformation using FLUX Kontext Pro.
Generates body transformation previews by editing the uploaded photo.
"""

import asyncio
import base64
import io
import logging

from PIL import Image, ImageOps

from .replicate_utils import (
    curl_json,
    poll_prediction,
    image_to_data_uri,
    download_to_base64,
    get_replicate_api_key,
)

logger = logging.getLogger(__name__)

REPLICATE_MODELS_API = "https://api.replicate.com/v1/models"
FLUX_KONTEXT_MODEL = "black-forest-labs/flux-kontext-pro"


def _normalize_image(image_base64: str) -> tuple[str, int, int]:
    """
    Strip EXIF orientation, re-encode as JPEG, and return
    (clean_base64, width, height) so aspect ratio is deterministic.
    """
    raw = base64.b64decode(image_base64)
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img) or img
    img = img.convert("RGB")
    w, h = img.size
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    clean_b64 = base64.b64encode(buf.getvalue()).decode()
    return clean_b64, w, h


def _match_orientation(transformed_b64: str, target_w: int, target_h: int) -> str:
    """
    If the output image orientation doesn't match the original,
    rotate it to match.
    """
    raw = base64.b64decode(transformed_b64)
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img) or img
    img = img.convert("RGB")
    ow, oh = img.size

    original_is_portrait = target_h > target_w
    output_is_portrait = oh > ow

    if original_is_portrait != output_is_portrait:
        logger.info(
            f"Orientation mismatch: original {target_w}x{target_h}, "
            f"output {ow}x{oh} — rotating output"
        )
        img = img.rotate(90 if original_is_portrait else -90, expand=True)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode()


async def _generate_single_image(
    data_uri: str, prompt: str, aspect: str,
    orig_w: int, orig_h: int, api_key: str,
) -> str:
    """Single FLUX Kontext Pro image generation. Returns base64 data URI."""
    create_url = f"{REPLICATE_MODELS_API}/{FLUX_KONTEXT_MODEL}/predictions"
    prediction = curl_json("POST", create_url, api_key, {
        "input": {
            "prompt": prompt,
            "input_image": data_uri,
            "aspect_ratio": aspect,
            "safety_tolerance": 5,
            "output_format": "jpg",
            "output_quality": 90,
        },
    })

    poll_url = prediction.get("urls", {}).get("get")
    if not poll_url:
        raise RuntimeError(f"No poll URL in prediction response: {prediction}")

    result = await poll_prediction(poll_url, api_key, max_polls=60, interval=3.0)

    output = result.get("output")
    if not output:
        raise RuntimeError("No output from FLUX Kontext")

    output_url = (
        output if isinstance(output, str)
        else output[0] if isinstance(output, list)
        else None
    )
    if not output_url:
        raise RuntimeError(f"Unexpected output format: {type(output)}")

    transformed_b64 = download_to_base64(output_url)
    transformed_b64 = _match_orientation(transformed_b64, orig_w, orig_h)
    return image_to_data_uri(transformed_b64, "jpeg")


async def generate_journey_images(
    image_base64: str,
    stage_prompts: list[tuple[int, str]],
) -> list[dict]:
    """Generate transformation images for stages 1-4.

    Uses the original uploaded image as input for every stage to preserve
    identity.  Returns list of dicts with keys:
    ``stage_number``, ``image_data_uri``, ``latency_ms``.
    """
    import time

    api_key = get_replicate_api_key()

    clean_b64, orig_w, orig_h = _normalize_image(image_base64)
    data_uri = image_to_data_uri(clean_b64)

    if orig_h > orig_w:
        aspect = "3:4"
    elif orig_w > orig_h:
        aspect = "4:3"
    else:
        aspect = "1:1"

    # Stagger prediction creation to avoid Replicate burst rate limits.
    # Each prediction is created sequentially (the POST is fast), then
    # all polls run concurrently.
    create_url = f"{REPLICATE_MODELS_API}/{FLUX_KONTEXT_MODEL}/predictions"
    pending: list[tuple[int, str, float]] = []  # (stage_num, poll_url, t0)

    for stage_num, prompt in stage_prompts:
        t0 = time.monotonic()
        logger.info(f"Creating prediction for stage {stage_num}")
        prediction = curl_json("POST", create_url, api_key, {
            "input": {
                "prompt": prompt,
                "input_image": data_uri,
                "aspect_ratio": aspect,
                "safety_tolerance": 5,
                "output_format": "jpg",
                "output_quality": 90,
            },
        })
        poll_url = prediction.get("urls", {}).get("get")
        if not poll_url:
            logger.error(f"Stage {stage_num}: no poll URL: {prediction}")
            # If rate-limited, wait and retry once
            retry_after = prediction.get("retry_after", 12)
            if prediction.get("status") == 429:
                logger.info(f"Stage {stage_num}: rate limited, waiting {retry_after}s")
                await asyncio.sleep(retry_after)
                prediction = curl_json("POST", create_url, api_key, {
                    "input": {
                        "prompt": prompt,
                        "input_image": data_uri,
                        "aspect_ratio": aspect,
                        "safety_tolerance": 5,
                        "output_format": "jpg",
                        "output_quality": 90,
                    },
                })
                poll_url = prediction.get("urls", {}).get("get")
            if not poll_url:
                logger.error(f"Stage {stage_num}: still no poll URL after retry")
                continue
        pending.append((stage_num, poll_url, t0))
        await asyncio.sleep(1)  # 1s stagger between creations

    # Poll all predictions concurrently
    async def _poll_one(stage_num: int, poll_url: str, t0: float) -> dict:
        result = await poll_prediction(poll_url, api_key, max_polls=60, interval=3.0)
        output = result.get("output")
        output_url = (
            output if isinstance(output, str)
            else output[0] if isinstance(output, list)
            else None
        )
        if not output_url:
            raise RuntimeError(f"Stage {stage_num}: unexpected output: {output}")
        transformed_b64 = download_to_base64(output_url)
        transformed_b64 = _match_orientation(transformed_b64, orig_w, orig_h)
        latency = round((time.monotonic() - t0) * 1000, 1)
        logger.info(f"Stage {stage_num} completed in {latency}ms")
        return {"stage_number": stage_num, "image_data_uri": image_to_data_uri(transformed_b64, "jpeg"), "latency_ms": latency}

    poll_tasks = [_poll_one(sn, pu, t0) for sn, pu, t0 in pending]
    results = await asyncio.gather(*poll_tasks, return_exceptions=True)

    stage_images: list[dict] = []
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Stage generation failed: {r}")
            continue
        stage_images.append(r)

    stage_images.sort(key=lambda x: x["stage_number"])
    return stage_images


async def controlnet_transform_region(
    image_base64: str,
    mask_base64: str,
    body_part: str,
    goal: str,
    gender: str,
    intensity: str = "moderate",
) -> dict:
    """Region-specific transformation using FLUX Kontext with targeted prompt."""
    api_key = get_replicate_api_key()

    clean_b64, orig_w, orig_h = _normalize_image(image_base64)
    data_uri = image_to_data_uri(clean_b64)

    intensity_map = {"subtle": "slightly", "moderate": "noticeably", "dramatic": "significantly"}
    level = intensity_map.get(intensity, "noticeably")

    goal_map = {
        "bigger": f"Make the {body_part} {level} bigger and more muscular",
        "leaner": f"Make the {body_part} {level} leaner and more defined",
        "more_defined": f"Make the {body_part} {level} more defined with visible muscle striations",
        "slimmer": f"Make the {body_part} {level} slimmer and more toned",
    }

    prompt = (
        f"{goal_map.get(goal, f'Transform the {body_part}')}. "
        f"Keep everything else exactly the same — same person, same face, pose, clothing, background. "
        f"Realistic photo edit."
    )

    direction_map = {
        "bigger": "muscle_gain",
        "leaner": "fat_loss",
        "more_defined": "definition",
        "slimmer": "fat_loss",
    }

    if orig_h > orig_w:
        aspect = "3:4"
    elif orig_w > orig_h:
        aspect = "4:3"
    else:
        aspect = "1:1"

    create_url = f"{REPLICATE_MODELS_API}/{FLUX_KONTEXT_MODEL}/predictions"
    prediction = curl_json("POST", create_url, api_key, {
        "input": {
            "prompt": prompt,
            "input_image": data_uri,
            "aspect_ratio": aspect,
            "safety_tolerance": 5,
            "output_format": "jpg",
            "output_quality": 90,
        },
    })

    poll_url = prediction.get("urls", {}).get("get")
    if not poll_url:
        raise RuntimeError(f"No poll URL: {prediction}")

    result = await poll_prediction(poll_url, api_key, max_polls=60, interval=3.0)

    output = result.get("output")
    output_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
    if not output_url:
        raise RuntimeError("No output from region transform")

    transformed_b64 = download_to_base64(output_url)
    transformed_b64 = _match_orientation(transformed_b64, orig_w, orig_h)
    transformed_data_uri = image_to_data_uri(transformed_b64, "jpeg")

    return {
        "transformed_image_url": transformed_data_uri,
        "body_part": body_part,
        "goal": goal,
        "direction": direction_map.get(goal, "definition"),
    }
