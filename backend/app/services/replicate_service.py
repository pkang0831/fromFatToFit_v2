"""
Body transformation service using Replicate's FLUX Kontext Pro model.
Generates identity-preserving body transformations based on target body fat %.

Uses curl subprocess for API calls to reliably work through corporate
proxies that interfere with Python HTTP libraries (httpx/requests).
"""

import asyncio
import base64
import json
import logging
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)


def _build_prompt(current_bf: float, target_bf: float, gender: str) -> str:
    """Build a transformation prompt based on direction (cutting/bulking) and gender."""
    direction = "cutting" if target_bf < current_bf else "bulking"
    bf_diff = abs(current_bf - target_bf)

    preserve = (
        "Keep the exact same person, face, skin tone, hair, tattoos, clothing, "
        "background environment, pose, and camera angle. "
        "The result must be a realistic, believable photo of the same individual."
    )

    if gender == "female":
        if direction == "cutting":
            body_desc = (
                f"Reduce body fat to approximately {target_bf:.0f}%. "
                "Create a toned, athletic physique with subtle muscle definition in arms and midsection. "
                "Add approximately 1-2 kg of lean muscle. "
                "Slim waist, defined but feminine legs and shoulders. "
                "The body should look fit, lean, and naturally athletic."
            )
        else:
            body_desc = (
                f"Transform the physique to approximately {target_bf:.0f}% body fat with a curvy, athletic build. "
                "Add approximately 1.5-2.5 kg of muscle with fuller glutes, thighs, and toned arms. "
                "The body should look strong and curvy with a feminine aesthetic — "
                "wider hips, rounded glutes, and a defined waist-to-hip ratio."
            )
    else:
        if direction == "cutting":
            body_desc = (
                f"Reduce body fat to approximately {target_bf:.0f}%. "
                "Make the physique leaner with visible abdominal definition, oblique lines, "
                "and clear muscle separation in arms, shoulders, and chest. "
                "Add approximately 2-3 kg of lean muscle mass. "
                "The body should look athletic, defined, and naturally lean."
            )
        else:
            body_desc = (
                f"Transform the physique to approximately {target_bf:.0f}% body fat with a powerful, muscular build. "
                "Add approximately 3-4 kg of muscle mass with broader shoulders, thicker arms and chest, "
                "and a solid, imposing core. "
                "The body should look strong, bulky, and imposing while maintaining natural proportions."
            )

    intensity = "subtly" if bf_diff <= 3 else "moderately" if bf_diff <= 7 else "noticeably"

    return (
        f"Professional fitness coaching visualization. "
        f"{preserve} "
        f"{intensity.capitalize()} transform the body: {body_desc} "
        f"Maintain the exact same lighting and photo quality."
    )


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
            import os
            os.unlink(tmp_file.name)


def _curl_download(url: str, dest_path: str) -> None:
    """Download a file via curl."""
    result = subprocess.run(
        ["curl", "-sk", "-o", dest_path, url],
        capture_output=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl download failed: {result.stderr[:200]}")


async def generate_body_transformation(
    image_base64: str,
    current_bf: float,
    target_bf: float,
    gender: str = "male",
) -> dict:
    """
    Generate a body transformation preview using FLUX Kontext Pro on Replicate.

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

    data_uri = f"data:image/jpeg;base64,{image_base64}"

    payload = {
        "input": {
            "prompt": prompt,
            "input_image": data_uri,
            "aspect_ratio": "match_input_image",
            "output_format": "png",
            "safety_tolerance": 2,
        },
    }

    loop = asyncio.get_event_loop()

    # Step 1: create prediction
    create_url = "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions"
    pred = await loop.run_in_executor(None, _curl_json, "POST", create_url, api_key, payload)

    pred_status = pred.get("status")
    pred_id = pred.get("id")

    if pred_status == "failed":
        raise RuntimeError(f"Prediction failed: {pred.get('error')}")

    logger.info(f"Prediction created: {pred_id}, status={pred_status}")

    # Step 2: poll until done
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

    # Step 3: download result and convert to base64
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await loop.run_in_executor(None, _curl_download, image_url, tmp_path)
        with open(tmp_path, "rb") as f:
            result_b64 = base64.b64encode(f.read()).decode("utf-8")
    finally:
        import os
        os.unlink(tmp_path)

    return {
        "transformed_image_url": f"data:image/png;base64,{result_b64}",
        "direction": direction,
        "muscle_gain_estimate": muscle_gain,
    }
