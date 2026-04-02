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


async def generate_transformation_image(
    image_base64: str,
    prompt: str,
) -> dict:
    """Generate a single 'after' transformation image via FLUX Kontext Pro.

    Returns dict with keys: ``image_data_uri``, ``latency_ms``.
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

    t0 = time.monotonic()
    logger.info("Creating FLUX Kontext Pro prediction for transformation")

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
        retry_after = prediction.get("retry_after", 12)
        if prediction.get("status") == 429:
            logger.info(f"Rate limited, waiting {retry_after}s")
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
            raise RuntimeError(f"No poll URL: {prediction}")

    result = await poll_prediction(poll_url, api_key, max_polls=60, interval=3.0)
    output = result.get("output")
    output_url = (
        output if isinstance(output, str)
        else output[0] if isinstance(output, list)
        else None
    )
    if not output_url:
        raise RuntimeError(f"Unexpected output: {output}")

    transformed_b64 = download_to_base64(output_url)
    transformed_b64 = _match_orientation(transformed_b64, orig_w, orig_h)
    latency = round((time.monotonic() - t0) * 1000, 1)
    logger.info(f"Transformation completed in {latency}ms")

    return {
        "image_data_uri": image_to_data_uri(transformed_b64, "jpeg"),
        "latency_ms": latency,
    }


REALVIS_MODEL = "pkang0831/realvis-v5-lightning"

_replicate_semaphore: asyncio.Semaphore | None = None


def _get_replicate_semaphore() -> asyncio.Semaphore:
    """Lazy-init semaphore to cap concurrent Replicate requests."""
    global _replicate_semaphore
    if _replicate_semaphore is None:
        _replicate_semaphore = asyncio.Semaphore(4)
    return _replicate_semaphore


_realvis_version_cache: dict[str, tuple[str, float]] = {}
_REALVIS_VERSION_TTL = 300  # 5 minutes


def _get_realvis_version(api_key: str) -> str:
    """Get model version ID with a 5-minute TTL cache."""
    import time as _t
    now = _t.monotonic()
    cached = _realvis_version_cache.get("version")
    if cached and (now - cached[1]) < _REALVIS_VERSION_TTL:
        return cached[0]

    model_url = f"{REPLICATE_MODELS_API}/{REALVIS_MODEL}"
    model_info = curl_json("GET", model_url, api_key)
    version_id = (model_info.get("latest_version") or {}).get("id")
    if not version_id:
        raise RuntimeError(f"No version found for model {REALVIS_MODEL}")

    _realvis_version_cache["version"] = (version_id, now)
    logger.info(f"Cached RealVis version: {version_id[:12]}...")
    return version_id


async def run_realvis_img2img(
    image: "Image.Image",
    prompt: str,
    negative_prompt: str = "",
    strength: float = 0.3,
    num_inference_steps: int = 10,
    guidance_scale: float = 2.2,
    seed: int = 42,
) -> "Image.Image":
    """Run RealVisXL V5.0 Lightning img2img on Replicate.

    Uses our custom Cog model with the exact same pipeline as the Colab notebook.
    Guarded by a semaphore to prevent overwhelming Replicate with concurrent requests.
    """
    import time as _time

    sem = _get_replicate_semaphore()
    async with sem:
        return await _run_realvis_img2img_inner(
            image, prompt, negative_prompt, strength,
            num_inference_steps, guidance_scale, seed,
        )


async def _run_realvis_img2img_inner(
    image: "Image.Image",
    prompt: str,
    negative_prompt: str,
    strength: float,
    num_inference_steps: int,
    guidance_scale: float,
    seed: int,
) -> "Image.Image":
    import time as _time

    api_key = get_replicate_api_key()

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=92)
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    data_uri = f"data:image/jpeg;base64,{img_b64}"

    create_url = "https://api.replicate.com/v1/predictions"

    t0 = _time.monotonic()
    logger.info(
        f"RealVis img2img: strength={strength:.2f} steps={num_inference_steps} "
        f"cfg={guidance_scale} seed={seed}"
    )

    version_id = _get_realvis_version(api_key)

    payload = {
        "version": version_id,
        "input": {
            "image": data_uri,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "strength": float(strength),
            "num_inference_steps": int(num_inference_steps),
            "guidance_scale": float(guidance_scale),
            "seed": int(seed),
            "output_format": "jpg",
            "output_quality": 92,
        },
    }

    for attempt in range(5):
        prediction = curl_json("POST", create_url, api_key, payload)
        if prediction.get("status") == 429:
            wait = prediction.get("retry_after", 10)
            logger.info(f"Rate limited, waiting {wait}s (attempt {attempt + 1}/5)")
            await asyncio.sleep(wait + 1)
            continue
        break

    poll_url = prediction.get("urls", {}).get("get")
    if not poll_url:
        raise RuntimeError(f"No poll URL from RealVis prediction: {prediction}")

    result = await poll_prediction(poll_url, api_key, max_polls=180, interval=3.0)

    output = result.get("output")
    output_url = (
        output if isinstance(output, str)
        else output[0] if isinstance(output, list)
        else None
    )
    if not output_url:
        raise RuntimeError(f"No output from RealVis: {output}")

    out_b64 = download_to_base64(output_url)
    latency = round((_time.monotonic() - t0) * 1000, 1)
    logger.info(f"RealVis img2img completed in {latency}ms")

    raw = base64.b64decode(out_b64)
    out_img = Image.open(io.BytesIO(raw)).convert("RGB")
    return out_img.resize(image.size, Image.LANCZOS)


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
