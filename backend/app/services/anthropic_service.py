import logging
from typing import Dict, Any
import base64
from anthropic import Anthropic
from ..config import settings
from .prompts import FOOD_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.anthropic_api_key)


async def analyze_food_image_claude(image_base64: str) -> Dict[str, Any]:
    """
    Analyze food image using Claude to estimate nutritional content
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        Dictionary with food items and nutritional breakdown
    """
    try:
        prompt = FOOD_ANALYSIS_PROMPT

        # Detect image type from base64
        image_type = "image/jpeg"
        if image_base64.startswith("iVBOR"):
            image_type = "image/png"
        elif image_base64.startswith("/9j/"):
            image_type = "image/jpeg"
        elif image_base64.startswith("R0lGOD"):
            image_type = "image/gif"
        elif image_base64.startswith("UklGR"):
            image_type = "image/webp"

        # Use Claude Sonnet for high accuracy
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_type,
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        content = response.content[0].text
        logger.info(f"Claude food analysis response: {content}")
        
        # Parse JSON response
        import json
        # Remove markdown code blocks if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        result = json.loads(content)
        
        # Calculate totals
        total_calories = sum(item.get("calories", 0) for item in result["items"])
        total_protein = sum(item.get("protein", 0) for item in result["items"])
        total_carbs = sum(item.get("carbs", 0) for item in result["items"])
        total_fat = sum(item.get("fat", 0) for item in result["items"])
        
        return {
            "items": result["items"],
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "confidence": result.get("confidence", "high"),
            "provider": "claude"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing food image with Claude: {e}")
        raise
