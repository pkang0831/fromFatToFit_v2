import base64
import io
import json
import re
import logging
from typing import Dict, Any, List
from openai import OpenAI
from ..config import settings
from .prompts import FOOD_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)


async def analyze_food_image(image_base64: str) -> Dict[str, Any]:
    """
    Analyze food image using GPT-4 Vision to estimate nutritional content
    
    Args:
        image_base64: Base64 encoded image string
        
    Returns:
        Dictionary with food items and nutritional breakdown
    """
    try:
        prompt = FOOD_ANALYSIS_PROMPT

        response = client.chat.completions.create(
            model="gpt-4o",
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
            max_tokens=1000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        logger.info(f"OpenAI food analysis response: {content}")
        
        content_clean = content.strip()
        if content_clean.startswith("```"):
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content_clean, re.DOTALL)
            if match:
                content_clean = match.group(1)
            else:
                match = re.search(r'\{.*\}', content_clean, re.DOTALL)
                if match:
                    content_clean = match.group(0)
        
        result = json.loads(content_clean)
        
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
            "provider": "openai"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing food image: {e}")
        raise


async def analyze_workout_form_video(video_base64: str, exercise_name: str) -> Dict[str, Any]:
    """
    Analyze workout form from video frames using GPT-4 Vision
    
    Args:
        video_base64: Base64 encoded video (we'll extract frames)
        exercise_name: Name of the exercise being performed
        
    Returns:
        Dictionary with form analysis and corrections
    """
    try:
        # Note: For MVP, we'll analyze a single frame or a few frames
        # In production, you'd extract multiple frames from the video
        
        prompt = f"""Analyze this workout form for {exercise_name}.

Evaluate:
1. Body positioning and alignment
2. Range of motion
3. Common form mistakes for this exercise
4. Safety concerns

Return ONLY a valid JSON object (no markdown):
{{
  "form_score": 0-100,
  "issues_detected": ["issue1", "issue2"],
  "corrections": ["correction1", "correction2"],
  "overall_feedback": "detailed feedback"
}}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{video_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"Error analyzing workout form: {e}")
        raise


async def estimate_body_fat_percentage(image_base64: str, gender: str, age: int) -> Dict[str, Any]:
    """
    Estimate body fat percentage from body image using GPT-4 Vision
    
    Args:
        image_base64: Base64 encoded body image
        gender: User's gender
        age: User's age
        
    Returns:
        Dictionary with body fat estimate and recommendations
    """
    try:
        prompt = f"""You are a certified fitness coach AI used in a health & wellness app.
The user has uploaded a gym/fitness progress photo for body composition tracking.
This is standard practice in fitness coaching — similar to what personal trainers review.

User info: {gender}, age {age}

Analyze visible fitness indicators (muscle definition, waist-to-shoulder ratio, visible vascularity, abdominal definition) and estimate an approximate body fat percentage range.

This is for educational fitness tracking only, not medical advice.

Return ONLY valid JSON (no markdown):
{{
  "body_fat_percentage": 15.5,
  "confidence": "medium",
  "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}"""

        # Try gpt-4o-mini first (less restrictive), fallback to gpt-4o
        models_to_try = ["gpt-4o-mini", "gpt-4o"]
        content = None
        
        for model_name in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a certified fitness coach AI in a health tracking app. You help users estimate body composition from gym progress photos. Always respond with valid JSON only."
                        },
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
                logger.info(f"OpenAI ({model_name}) body fat response: {content}")
                
                content_lower = (content or "").lower()
                if any(p in content_lower for p in ["i'm sorry", "i can't", "i cannot", "i'm unable", "not appropriate"]):
                    logger.warning(f"OpenAI ({model_name}) refused, trying next model...")
                    continue
                break
            except Exception as model_err:
                logger.warning(f"OpenAI ({model_name}) failed: {model_err}")
                continue
        
        if not content or content.strip() == "":
            raise ValueError("OpenAI returned empty response")
        
        # Check if OpenAI refused the request
        refusal_phrases = [
            "i'm sorry",
            "i can't help",
            "i cannot assist",
            "i'm unable to",
            "not appropriate"
        ]
        content_lower = content.lower()
        if any(phrase in content_lower for phrase in refusal_phrases):
            logger.warning(f"OpenAI refused body fat analysis: {content}")
            raise ValueError(
                "AI service declined to analyze this image. "
                "Please ensure the photo shows clear body composition indicators. "
                "For best results: use good lighting, wear form-fitting clothes, and capture full body in frame."
            )
        
        # Remove markdown code blocks if present
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
        raise ValueError(f"Failed to parse OpenAI response: {str(e)}")
    except Exception as e:
        logger.error(f"Error estimating body fat: {e}")
        raise


async def generate_body_transformation(
    image_base64: str,
    target_bf_reduction: float,
    gender: str = "male"
) -> str:
    """
    Generate body transformation preview using GPT Image (gpt-image-1).
    Uses image editing to realistically modify the user's actual photo.
    
    Args:
        image_base64: Base64 encoded current body image
        target_bf_reduction: Target body fat % reduction
        gender: User's gender for context-aware editing
        
    Returns:
        Base64 data URL of the transformed image
    """
    try:
        intensity = "subtly" if target_bf_reduction <= 3 else "moderately" if target_bf_reduction <= 6 else "noticeably"
        
        muscle_detail = (
            "Define abdominal muscles and obliques clearly with realistic lighting and shadows. "
            "Enhance muscle separation in arms, shoulders, and chest."
        ) if gender == "male" else (
            "Define a toned, athletic midsection with subtle muscle definition. "
            "Enhance overall body tone in arms, shoulders, and waist."
        )

        prompt = (
            f"This is a professional fitness coaching visualization for health tracking purposes. "
            f"Keep the exact same person, face, skin tone, hair, clothing, pose, and background environment. "
            f"Reduce body fat {intensity} — approximately {target_bf_reduction}% body fat reduction. "
            f"Reduce subcutaneous fat especially in the midsection and waist area. "
            f"{muscle_detail} "
            f"Keep proportions believable and anatomically correct. "
            f"Maintain the exact same lighting, camera angle, and photo quality. "
            f"Do NOT change the face, skin color, tattoos, or any background elements. "
            f"The result must look like a realistic fitness progress photo of the same person."
        )

        image_bytes = base64.b64decode(image_base64)
        image_file = io.BytesIO(image_bytes)
        image_file.name = "body_photo.png"

        response = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
            quality="high",
        )

        result_b64 = response.data[0].b64_json
        return f"data:image/png;base64,{result_b64}"

    except Exception as e:
        error_str = str(e).lower()
        if "moderation" in error_str or "safety" in error_str or "blocked" in error_str:
            raise ValueError(
                "The image was flagged by OpenAI's safety filter. "
                "Try a photo with a shirt/tank top on, or taken from a different angle."
            )
        logger.error(f"Error generating transformation: {e}")
        raise


async def generate_body_enhancement(
    image_base64: str,
    gender: str = "male",
    enhancement_level: str = "natural"
) -> str:
    """
    Professional body profile photo retouching using GPT Image (gpt-image-1).
    Enhances existing physique with studio-quality retouching — no body shape changes.
    
    Args:
        image_base64: Base64 encoded body image
        gender: User's gender for context-aware editing
        enhancement_level: 'subtle', 'natural', or 'studio'
        
    Returns:
        Base64 data URL of the enhanced image
    """
    try:
        shadow_intensity = {
            "subtle": "slightly deepen shadows in muscle grooves for mild definition enhancement",
            "natural": "enhance shadows and highlights in muscle grooves for clear but natural-looking definition",
            "studio": "professionally enhance muscle definition with deep shadows and crisp highlights, similar to magazine-quality retouching"
        }.get(enhancement_level, "enhance shadows and highlights in muscle grooves for clear but natural-looking definition")

        skin_instruction = (
            "Smooth skin texture slightly while preserving natural pores and body hair. "
            "Even out skin tone and reduce blemishes, redness, or uneven patches."
        )

        gender_detail = (
            "Enhance definition in abs, obliques, chest striations, deltoid separation, and arm vascularity where already visible."
        ) if gender == "male" else (
            "Enhance tone and definition in abs, waist taper, shoulder caps, and arm definition while maintaining a feminine aesthetic."
        )

        prompt = (
            f"This is a professional fitness photography retouching job for health coaching purposes. "
            f"Keep the EXACT same person, face, body shape, proportions, pose, clothing, and background. "
            f"Do NOT change body fat level, muscle size, or body proportions — only enhance how they look in the photo. "
            f"{shadow_intensity}. "
            f"{gender_detail} "
            f"{skin_instruction} "
            f"Apply subtle color grading: slightly warmer skin tones, improved contrast. "
            f"Maintain the exact same camera angle, focal length, and composition. "
            f"Do NOT change the face, hairstyle, skin color, tattoos, or any background elements. "
            f"The result should look like professional fitness photography retouching — the same photo, just polished."
        )

        image_bytes = base64.b64decode(image_base64)
        image_file = io.BytesIO(image_bytes)
        image_file.name = "body_photo.png"

        response = client.images.edit(
            model="gpt-image-1",
            image=image_file,
            prompt=prompt,
            size="1024x1024",
            quality="high",
        )

        result_b64 = response.data[0].b64_json
        return f"data:image/png;base64,{result_b64}"

    except Exception as e:
        error_str = str(e).lower()
        if "moderation" in error_str or "safety" in error_str or "blocked" in error_str:
            raise ValueError(
                "The image was flagged by OpenAI's safety filter. "
                "Try a photo with a shirt/tank top on, or taken from a different angle."
            )
        logger.error(f"Error generating body enhancement: {e}")
        raise


async def simple_completion(prompt: str, max_tokens: int = 150) -> str:
    """
    Simple text completion for food recommendations and advice
    Uses gpt-4o-mini for cost efficiency
    
    Args:
        prompt: The prompt to send to the model
        max_tokens: Maximum tokens in response
        
    Returns:
        The generated text response
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper for simple tasks
            messages=[
                {"role": "system", "content": "You are a friendly and encouraging nutrition coach. Provide concise, motivating advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error in simple completion: {e}")
        # Return a friendly fallback message
        return "Great choice! You're maintaining a good nutritional balance."
