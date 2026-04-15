import asyncio
import json
import logging
from typing import Any, Dict

from openai import OpenAI

from ..config import settings
from ..schemas.weekly_checkin_schemas import BodyObservation

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


BODY_CHECKIN_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "image_quality",
        "observations",
        "estimated_ranges",
        "qualitative_summary",
        "region_notes",
    ],
    "properties": {
        "image_quality": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "frontal_pose",
                "body_visibility",
                "lighting_consistency",
                "pose_consistency",
                "comparison_confidence",
                "quality_flags",
            ],
            "properties": {
                "frontal_pose": {"type": "number", "minimum": 0, "maximum": 1},
                "body_visibility": {"type": "number", "minimum": 0, "maximum": 1},
                "lighting_consistency": {"type": "number", "minimum": 0, "maximum": 1},
                "pose_consistency": {"type": "number", "minimum": 0, "maximum": 1},
                "comparison_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "quality_flags": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "mirror_selfie",
                            "phone_occlusion",
                            "uneven_lighting",
                            "different_distance",
                            "different_pose",
                            "cropped_body",
                            "low_resolution",
                            "none",
                        ],
                    },
                },
            },
        },
        "observations": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "abdomen_softness",
                "lower_abdomen_protrusion",
                "ab_definition",
                "chest_definition",
                "arm_definition",
                "shoulder_roundness",
                "v_taper_visibility",
                "overall_visual_leanness",
            ],
            "properties": {
                "abdomen_softness": {"type": "number", "minimum": 0, "maximum": 10},
                "lower_abdomen_protrusion": {"type": "number", "minimum": 0, "maximum": 10},
                "ab_definition": {"type": "number", "minimum": 0, "maximum": 10},
                "chest_definition": {"type": "number", "minimum": 0, "maximum": 10},
                "arm_definition": {"type": "number", "minimum": 0, "maximum": 10},
                "shoulder_roundness": {"type": "number", "minimum": 0, "maximum": 10},
                "v_taper_visibility": {"type": "number", "minimum": 0, "maximum": 10},
                "overall_visual_leanness": {"type": "number", "minimum": 0, "maximum": 10},
            },
        },
        "estimated_ranges": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "body_fat_percent_min",
                "body_fat_percent_max",
                "body_fat_confidence",
            ],
            "properties": {
                "body_fat_percent_min": {"type": "number", "minimum": 3, "maximum": 45},
                "body_fat_percent_max": {"type": "number", "minimum": 3, "maximum": 45},
                "body_fat_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
        },
        "qualitative_summary": {
            "type": "array",
            "minItems": 2,
            "maxItems": 5,
            "items": {"type": "string"},
        },
        "region_notes": {
            "type": "object",
            "additionalProperties": False,
            "required": ["abdomen", "chest", "arms", "shoulders"],
            "properties": {
                "abdomen": {"type": "string"},
                "chest": {"type": "string"},
                "arms": {"type": "string"},
                "shoulders": {"type": "string"},
            },
        },
    },
}


SYSTEM_PROMPT = """You are analyzing physique progress photos for visual change tracking.

Your job is not to diagnose, not to provide medical certainty, and not to claim exact body composition.
You must only extract consistent visual observations from the image.

Return JSON only and strictly follow the provided schema.

Scoring rules:
- Use a 0 to 10 scale for visual observations.
- 0 means nearly absent or not visually apparent.
- 10 means very strong or very visually prominent.
- Be conservative and consistent.
- If image quality is weak, lower comparison_confidence rather than hallucinating certainty.
- Estimate body fat only as a visual range, never as a single exact truth.
- Focus on visible appearance only:
  abdomen softness,
  lower abdomen protrusion,
  abdominal definition,
  chest definition,
  arm definition,
  shoulder roundness,
  v-taper visibility,
  overall visual leanness.

Quality rules:
- Penalize inconsistent lighting, changed pose, partial occlusion, cropping, or different camera distance.
- Mirror selfies are acceptable but may reduce confidence if phone blocks anatomy.

Writing rules:
- qualitative_summary should be short, factual, and comparative-ready.
- region_notes should describe what is visually noticeable in each region.
- Do not mention morality, attractiveness, or identity.
- Do not fabricate hidden anatomy or exact measurements."""


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key or None)
    return _client


def _build_user_prompt() -> str:
    return "Analyze this weekly physique progress photo and extract only visible observations."


async def analyze_weekly_checkin_image(image_base64: str) -> BodyObservation:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for weekly check-in analysis")

    image_url = image_base64
    if not image_url.startswith("data:"):
        image_url = f"data:image/jpeg;base64,{image_base64}"

    def _request():
        return _get_client().responses.create(
            model=settings.openai_body_checkin_model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": _build_user_prompt()},
                        {
                            "type": "input_image",
                            "image_url": image_url,
                            "detail": "high",
                        },
                    ],
                },
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "body_checkin_analysis",
                    "strict": True,
                    "schema": BODY_CHECKIN_SCHEMA,
                }
            },
        )

    response = await asyncio.to_thread(_request)
    raw_text = response.output_text

    if not raw_text:
        raise RuntimeError("OpenAI returned an empty weekly check-in analysis response")

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse weekly check-in analysis JSON: %s", raw_text[:400])
        raise RuntimeError("OpenAI returned invalid weekly check-in JSON") from exc

    return BodyObservation.model_validate(payload)
