import base64
import logging
import json
import re
from typing import Dict, Any
from openai import OpenAI
from ..config import settings

logger = logging.getLogger(__name__)

# Grok API is compatible with OpenAI SDK
grok_client = OpenAI(
    api_key=settings.grok_api_key,
    base_url="https://api.x.ai/v1"
)


async def estimate_body_fat_percentage(image_base64: str, gender: str, age: int) -> Dict[str, Any]:
    """
    Estimate body fat percentage from body image using Grok Vision API
    
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

        response = grok_client.chat.completions.create(
            model="grok-2-vision-1212",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        logger.info(f"Grok body fat response: {content}")
        
        if not content or content.strip() == "":
            raise ValueError("Grok returned empty response")
        
        # Check if Grok refused the request
        refusal_phrases = [
            "i'm sorry",
            "i can't help",
            "i cannot assist",
            "i'm unable to",
            "not appropriate"
        ]
        content_lower = content.lower()
        if any(phrase in content_lower for phrase in refusal_phrases):
            logger.warning(f"Grok refused body fat analysis: {content}")
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
        raise ValueError(f"Failed to parse Grok response: {str(e)}")
    except Exception as e:
        logger.error(f"Error estimating body fat with Grok: {e}")
        raise
