import logging
from typing import Dict, Any
from google import genai
from google.genai import types
from ..config import settings
from .prompts import FOOD_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

# Configure Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def analyze_food_image_gemini(image_base64: str) -> Dict[str, Any]:
    """
    Analyze food image using Google Gemini to estimate nutritional content
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        Dictionary with food items and nutritional breakdown
    """
    try:
        prompt = FOOD_ANALYSIS_PROMPT

        # Prepare image data
        import base64
        
        # Use Gemini 2.5 Flash (latest stable) for cost efficiency
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part.from_text(text=prompt),
                        types.Part.from_bytes(
                            data=base64.b64decode(image_base64),
                            mime_type='image/jpeg'
                        )
                    ]
                )
            ]
        )
        
        content = response.text
        
        logger.info(f"Gemini food analysis response: {content}")
        
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
            "confidence": result.get("confidence", "medium"),
            "provider": "gemini"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing food image with Gemini: {e}")
        raise
