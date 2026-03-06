import json
import logging
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from ..config import settings
from .cost_tracker import track_ai_cost

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

FASHION_PROMPT = """You are a professional fashion stylist.
Based on the user's body data and personal color analysis, recommend seasonal outfit styles.

User data:
- Gender: {gender}
- Height: {height_cm}cm
- Body type notes: {body_notes}
- Personal color season: {personal_color}
- Best colors: {best_colors}

For the "{season}" season, provide exactly 4 outfit recommendations.

Return ONLY valid JSON:
{{
  "season": "{season}",
  "outfits": [
    {{
      "style_name": "e.g. Smart Casual",
      "top": "specific top description",
      "bottom": "specific bottom description",
      "outerwear": "specific outerwear or null",
      "accessories": ["accessory1", "accessory2"],
      "color_palette": ["#hex1", "#hex2", "#hex3"],
      "color_reasoning": "why these colors work",
      "occasion": "when to wear this",
      "image_prompt": "detailed description of full outfit on a person for image generation"
    }}
  ]
}}

Be specific about materials, fits, and colors. Use the person's personal color palette."""


async def recommend_outfits(
    gender: str,
    season: str,
    height_cm: Optional[float] = None,
    body_notes: str = "",
    personal_color: str = "",
    best_colors: str = "",
) -> Dict[str, Any]:
    """Generate seasonal outfit recommendations using GPT-4o."""
    try:
        prompt = FASHION_PROMPT.format(
            gender=gender,
            height_cm=height_cm or "unknown",
            body_notes=body_notes or "not provided",
            personal_color=personal_color or "not analyzed yet",
            best_colors=best_colors or "not analyzed yet",
            season=season,
        )

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Give me 4 {season} outfit recommendations."},
            ],
            max_tokens=2000,
            temperature=0.8,
        )

        track_ai_cost("openai_gpt4o", "fashion_recommendation", "system")

        content = response.choices[0].message.content or ""
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        return json.loads(content.strip())

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse fashion JSON: {e}")
        raise ValueError("Failed to parse AI fashion results")
    except Exception as e:
        logger.error(f"Fashion recommendation failed: {e}")
        raise


async def generate_outfit_images(
    image_base64: Optional[str],
    outfits: List[Dict[str, Any]],
    gender: str = "female",
) -> List[Dict[str, Any]]:
    """Generate outfit images using GPT image editing.
    If no user image is provided, generates standalone outfit images."""
    results = []

    for outfit in outfits[:4]:
        try:
            prompt = outfit.get("image_prompt", "")
            if not prompt:
                prompt = (
                    f"A {gender} person wearing: {outfit.get('top', '')}, "
                    f"{outfit.get('bottom', '')}, {outfit.get('outerwear', '')}. "
                    f"Colors: {', '.join(outfit.get('color_palette', []))}. "
                    f"Professional fashion photography, full body shot, studio background."
                )

            if image_base64:
                if image_base64.startswith("data:"):
                    image_data = image_base64
                else:
                    image_data = f"data:image/jpeg;base64,{image_base64}"

                response = await client.images.edit(
                    model="gpt-image-1",
                    image=image_data,
                    prompt=f"Dress this person in: {prompt}. Keep face recognizable. Professional fashion photo.",
                    n=1,
                    size="1024x1024",
                )
            else:
                response = await client.images.generate(
                    model="gpt-image-1",
                    prompt=f"Fashion photo: {prompt}",
                    n=1,
                    size="1024x1024",
                )

            track_ai_cost("openai_gpt_image", "fashion_styling", "system")

            image_url = f"data:image/png;base64,{response.data[0].b64_json}"

            results.append({
                **outfit,
                "image_url": image_url,
            })

        except Exception as e:
            logger.error(f"Failed to generate outfit image '{outfit.get('style_name', '')}': {e}")
            results.append({
                **outfit,
                "image_url": None,
                "error": str(e),
            })

    return results
