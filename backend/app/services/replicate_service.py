"""
Body transformation service using Replicate's FLUX Kontext Pro model.
Generates identity-preserving body transformations based on target body fat %.
"""

import base64
import logging
import httpx
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

    async with httpx.AsyncClient(timeout=120.0) as client:
        # Create prediction
        create_resp = await client.post(
            "https://api.replicate.com/v1/models/black-forest-labs/flux-kontext-pro/predictions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Prefer": "wait=90",
            },
            json={
                "input": {
                    "prompt": prompt,
                    "input_image": data_uri,
                    "aspect_ratio": "match_input_image",
                    "output_format": "png",
                    "safety_tolerance": 2,
                },
            },
        )

        if create_resp.status_code not in (200, 201):
            body = create_resp.text
            logger.error(f"Replicate create prediction failed ({create_resp.status_code}): {body}")
            raise RuntimeError(f"Replicate API error: {create_resp.status_code}")

        prediction = create_resp.json()
        pred_status = prediction.get("status")
        output = prediction.get("output")

        # If the "Prefer: wait" header resolved it synchronously, output is already here
        if pred_status == "succeeded" and output:
            image_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
        else:
            # Poll until done
            poll_url = prediction.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{prediction['id']}"
            for _ in range(60):
                import asyncio
                await asyncio.sleep(2)
                poll_resp = await client.get(
                    poll_url,
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                poll_data = poll_resp.json()
                pred_status = poll_data.get("status")

                if pred_status == "succeeded":
                    output = poll_data.get("output")
                    image_url = output if isinstance(output, str) else output[0] if isinstance(output, list) else None
                    break
                elif pred_status in ("failed", "canceled"):
                    err = poll_data.get("error", "Unknown error")
                    logger.error(f"Replicate prediction failed: {err}")
                    raise RuntimeError(f"Image generation failed: {err}")
            else:
                raise RuntimeError("Replicate prediction timed out after 120s")

        if not image_url:
            raise RuntimeError("No output image URL from Replicate")

        # Download the result image and convert to base64
        img_resp = await client.get(image_url)
        img_resp.raise_for_status()
        result_b64 = base64.b64encode(img_resp.content).decode("utf-8")

    return {
        "transformed_image_url": f"data:image/png;base64,{result_b64}",
        "direction": direction,
        "muscle_gain_estimate": muscle_gain,
    }
