"""
Gemini service for body composition analysis with privacy-optimized prompts
"""
import logging
import json
import re
import base64
from typing import Dict, Any
from google import genai
from google.genai import types
from ..config import settings

logger = logging.getLogger(__name__)

# Configure Gemini client
client = genai.Client(api_key=settings.gemini_api_key)


async def estimate_body_fat_percentage(image_base64: str, gender: str, age: int) -> Dict[str, Any]:
    """
    Estimate body fat percentage using Google Gemini with privacy-optimized prompt
    
    Args:
        image_base64: Base64 encoded image string
        gender: User's gender (male/female)
        age: User's age
        
    Returns:
        Dictionary with body_fat_percentage, confidence, and recommendations
    """
    try:
        # Privacy-optimized prompt that focuses on educational/research context
        prompt = f"""You are a fitness research AI analyzing body composition for educational purposes.

Context: {gender.capitalize()}, ~{age} years old. Educational fitness tracking (NOT medical diagnosis).

Task: Estimate body composition based on visual markers:
- Muscle definition (abdominal, shoulder, deltoid)
- Subcutaneous tissue distribution
- Vascular prominence

Reference ranges:
- Athletes: 6-13% (M), 14-20% (F)
- Fitness: 14-17% (M), 21-24% (F)
- Average: 18-24% (M), 25-31% (F)

Disclaimer: Visual estimate for personal tracking only. Limitations exist vs clinical methods (DEXA).

Output ONLY valid JSON (no markdown):
{{"body_fat_percentage": <number>, "confidence": "low|medium|high", "recommendations": ["tip1", "tip2", "tip3"]}}

Response:"""

        # Prepare image data
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
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1000,
            )
        )
        
        content = response.text
        logger.info(f"Gemini body fat response: {content}")
        
        if not content or content.strip() == "":
            raise ValueError("Gemini returned empty response")
        
        # Check for refusal phrases
        refusal_phrases = [
            "i'm sorry", "i can't help", "i cannot assist",
            "i'm unable to", "not appropriate", "cannot provide",
            "i apologize", "i do not feel comfortable"
        ]
        content_lower = content.lower()
        if any(phrase in content_lower for phrase in refusal_phrases):
            logger.warning(f"Gemini refused body fat analysis: {content}")
            raise ValueError(
                "AI service declined to analyze this image. "
                "Please ensure the photo shows clear body composition indicators. "
                "For best results: use good lighting, wear form-fitting clothes, and capture full body in frame."
            )
        
        # Remove markdown code blocks if present
        content_clean = re.sub(r'```(?:json)?\s*|\s*```', '', content).strip()
        
        try:
            result = json.loads(content_clean)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {content_clean}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        
        # Validate response structure
        if "body_fat_percentage" not in result:
            raise ValueError("Missing body_fat_percentage in response")
        
        # Ensure confidence is set
        if "confidence" not in result:
            result["confidence"] = "medium"
        
        # Ensure recommendations exist
        if "recommendations" not in result or not result["recommendations"]:
            result["recommendations"] = [
                "Continue with progressive resistance training",
                "Maintain adequate protein intake (1.6-2.2g/kg)",
                "Track progress with regular measurements"
            ]
        
        logger.info(f"Gemini analysis successful: {result['body_fat_percentage']}% (confidence: {result['confidence']})")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing body fat with Gemini: {e}")
        raise
