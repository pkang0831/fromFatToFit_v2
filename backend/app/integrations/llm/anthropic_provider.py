"""Anthropic Claude vision calls: food photo nutrition and body-fat estimates."""
import json
import logging
import re
from typing import Any, Dict

from anthropic import Anthropic

from app.core.config import settings
from app.integrations.llm.prompts import FOOD_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key or None)
    return _client


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
        response = _get_client().messages.create(
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


async def estimate_body_fat_percentage(image_base64: str, gender: str, age: int) -> Dict[str, Any]:
    """
    Estimate body fat percentage from body image using Claude Vision API
    
    Args:
        image_base64: Base64 encoded body image
        gender: User's gender
        age: User's age
        
    Returns:
        Dictionary with body fat estimate and recommendations
    """
    try:
        prompt = f"""You are a fitness assessment AI helping users track their fitness progress.

Analyze this fitness progress photo to provide an educational body composition estimate for health tracking purposes.

User context:
- Gender: {gender}
- Age: {age}

Based on visible indicators like muscle definition, body composition markers, and typical ranges for this demographic, provide an educational estimate.

Important: This is for personal fitness tracking, not medical diagnosis.

Return ONLY a valid JSON object (no markdown, no code blocks):
{{
  "body_fat_percentage": 15.5,
  "confidence": "medium",
  "recommendations": ["Focus on progressive overload", "Maintain protein intake at 1.6-2.2g/kg", "Track measurements weekly"]
}}

Response:"""

        # Claude API only supports synchronous calls
        response = _get_client().messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Extract Claude's response
        content = response.content[0].text
        logger.info(f"Claude body fat response: {content}")
        
        if not content or content.strip() == "":
            raise ValueError("Claude returned empty response")
        
        # Check if Claude refused the request
        refusal_phrases = [
            "i'm sorry",
            "i can't help",
            "i cannot assist",
            "i'm unable to",
            "not appropriate",
            "i can't provide",
            "i cannot provide"
        ]
        content_lower = content.lower()
        if any(phrase in content_lower for phrase in refusal_phrases):
            logger.warning(f"Claude refused body fat analysis: {content}")
            raise ValueError(
                "AI service declined to analyze this image. "
                "Please ensure the photo shows clear body composition indicators. "
                "For best results: use good lighting, wear form-fitting clothes, and capture full body in frame."
            )
        
        # Handle markdown code blocks if present
        content_clean = content.strip()
        if content_clean.startswith("```"):
            # Extract JSON from markdown code block
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content_clean, re.DOTALL)
            if match:
                content_clean = match.group(1)
            else:
                # Try to find JSON object
                match = re.search(r'\{.*\}', content_clean, re.DOTALL)
                if match:
                    content_clean = match.group(0)
        
        result = json.loads(content_clean)
        
        # Validate response structure
        if "body_fat_percentage" not in result:
            raise ValueError("Invalid response format: missing body_fat_percentage")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}, Content: {content[:200] if content else 'None'}")
        raise ValueError(f"Failed to parse Claude response: {str(e)}")
    except Exception as e:
        logger.error(f"Error estimating body fat with Claude: {e}")
        raise
