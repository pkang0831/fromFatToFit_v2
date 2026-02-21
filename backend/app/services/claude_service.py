import base64
import logging
import json
import re
from typing import Dict, Any
from anthropic import Anthropic
from ..config import settings

logger = logging.getLogger(__name__)

# Claude client
claude_client = Anthropic(api_key=settings.anthropic_api_key)


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
        response = claude_client.messages.create(
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
