import json
import logging
from typing import Dict, Any, List
from openai import AsyncOpenAI
from ..config import settings
from .cost_tracker import track_ai_cost

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

FACE_ANALYSIS_PROMPT = """You are a professional beauty consultant and personal color analyst.
Analyze this selfie photo and provide a comprehensive beauty analysis in JSON format.

Return ONLY valid JSON with this exact structure:
{
  "face_shape": "oval|round|square|heart|oblong|diamond|triangle",
  "face_shape_description": "Brief explanation of their face shape characteristics",
  "forehead_ratio": "narrow|average|wide",
  "cheekbone_ratio": "narrow|average|wide",
  "jawline_ratio": "narrow|average|wide",
  "skin_tone": "fair|light|medium|olive|tan|dark|deep",
  "skin_undertone": "warm|cool|neutral",
  "personal_color_season": "spring_warm|summer_cool|autumn_warm|winter_cool",
  "personal_color_sub": "light_spring|bright_spring|warm_spring|light_summer|cool_summer|soft_summer|warm_autumn|deep_autumn|soft_autumn|bright_winter|cool_winter|deep_winter",
  "personal_color_description": "Explanation of their seasonal color type",
  "best_colors": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5", "#hex6"],
  "avoid_colors": ["#hex1", "#hex2", "#hex3"],
  "hairstyle_recommendations": [
    {"style": "style name", "reason": "why it suits them"},
    {"style": "style name", "reason": "why it suits them"},
    {"style": "style name", "reason": "why it suits them"},
    {"style": "style name", "reason": "why it suits them"}
  ],
  "hair_color_recommendations": [
    {"color": "color name", "hex": "#hex", "reason": "why it suits them"},
    {"color": "color name", "hex": "#hex", "reason": "why it suits them"},
    {"color": "color name", "hex": "#hex", "reason": "why it suits them"},
    {"color": "color name", "hex": "#hex", "reason": "why it suits them"}
  ],
  "makeup_recommendations": {
    "foundation_tone": "description",
    "lip_colors": ["color1", "color2", "color3"],
    "eye_shadow": ["color1", "color2", "color3"],
    "blush": "description"
  },
  "skincare_recommendations": [
    "recommendation 1",
    "recommendation 2",
    "recommendation 3"
  ],
  "styling_suggestions": [
    {"title": "Style 1 name", "description": "detailed description for image generation"},
    {"title": "Style 2 name", "description": "detailed description for image generation"},
    {"title": "Style 3 name", "description": "detailed description for image generation"},
    {"title": "Style 4 name", "description": "detailed description for image generation"}
  ]
}

Be specific with hex color codes. For styling_suggestions, describe each look in detail (hair, makeup, accessories) so it can be used as an image generation prompt."""


async def analyze_face(image_base64: str, gender: str = "female") -> Dict[str, Any]:
    """Analyze a face photo using GPT-4o Vision."""
    try:
        if image_base64.startswith("data:"):
            image_url = image_base64
        else:
            image_url = f"data:image/jpeg;base64,{image_base64}"

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": FACE_ANALYSIS_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this {gender} person's face for a comprehensive beauty consultation."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url, "detail": "high"}
                        }
                    ]
                }
            ],
            max_tokens=2000,
            temperature=0.7,
        )

        track_ai_cost("openai_gpt4o", "beauty_analysis", "system")

        content = response.choices[0].message.content or ""
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse beauty analysis JSON: {e}")
        raise ValueError("Failed to parse AI analysis results")
    except Exception as e:
        logger.error(f"Beauty analysis failed: {e}")
        raise


async def generate_styled_images(
    image_base64: str,
    styling_suggestions: List[Dict[str, str]],
    gender: str = "female"
) -> List[Dict[str, Any]]:
    """Generate styled images using GPT image editing.
    Returns list of {title, description, image_url}."""
    results = []

    if image_base64.startswith("data:"):
        image_data = image_base64
    else:
        image_data = f"data:image/jpeg;base64,{image_base64}"

    for suggestion in styling_suggestions[:4]:
        try:
            prompt = (
                f"Transform this {gender} person's appearance to match this style: "
                f"{suggestion['description']}. "
                f"Keep the person's face and identity recognizable. "
                f"Apply the hairstyle, hair color, and makeup changes naturally. "
                f"Professional photography quality, studio lighting."
            )

            response = await client.images.edit(
                model="gpt-image-1",
                image=image_data,
                prompt=prompt,
                n=1,
                size="1024x1024",
            )

            track_ai_cost("openai_gpt_image", "beauty_styling", "system")

            image_url = f"data:image/png;base64,{response.data[0].b64_json}"

            results.append({
                "title": suggestion["title"],
                "description": suggestion["description"],
                "image_url": image_url,
            })

        except Exception as e:
            logger.error(f"Failed to generate styled image '{suggestion['title']}': {e}")
            results.append({
                "title": suggestion["title"],
                "description": suggestion["description"],
                "image_url": None,
                "error": str(e),
            })

    return results
