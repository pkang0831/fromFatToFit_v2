import logging
from typing import Dict, Any, Literal
from ..config import settings
from .openai_service import analyze_food_image as analyze_food_image_openai
from .gemini_service import analyze_food_image_gemini
from .anthropic_service import analyze_food_image_claude

logger = logging.getLogger(__name__)

AIProvider = Literal["openai", "gemini", "claude", "hybrid"]


async def analyze_food_image(
    image_base64: str, 
    user_tier: str = "free",
    provider: AIProvider = None
) -> Dict[str, Any]:
    """
    Analyze food image using the appropriate AI provider based on user tier
    
    Hybrid Strategy:
    - Free users: Gemini Flash (cheapest, fast)
    - Premium users: Claude Sonnet (highest accuracy)
    - Fallback: OpenAI GPT-4o (most stable)
    
    Args:
        image_base64: Base64 encoded image string
        user_tier: User subscription tier ("free", "premium", etc.)
        provider: Force specific provider (overrides hybrid logic)
        
    Returns:
        Dictionary with food items and nutritional breakdown
    """
    
    # Determine provider based on strategy
    if provider is None:
        if settings.ai_provider == "hybrid":
            # Hybrid strategy based on user tier
            if user_tier == "premium":
                provider = "claude"  # Best accuracy for premium users
                logger.info(f"🏆 Using Claude Sonnet for premium user")
            else:
                provider = "gemini"  # Most cost-effective for free users
                logger.info(f"💰 Using Gemini Flash for free user")
        else:
            provider = settings.ai_provider
            logger.info(f"🔧 Using configured provider: {provider}")
    else:
        logger.info(f"🎯 Using forced provider: {provider}")
    
    # Try primary provider with fallback
    try:
        if provider == "gemini":
            return await analyze_food_image_gemini(image_base64)
        elif provider == "claude":
            return await analyze_food_image_claude(image_base64)
        elif provider == "openai":
            return await analyze_food_image_openai(image_base64)
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
            
    except Exception as e:
        logger.error(f"Error with {provider} provider: {e}")
        
        # Fallback to OpenAI if primary provider fails
        if provider != "openai":
            logger.warning(f"⚠️ Falling back to OpenAI GPT-4o")
            try:
                result = await analyze_food_image_openai(image_base64)
                result["provider"] = f"{provider}_fallback_openai"
                return result
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                raise fallback_error
        else:
            raise e


async def get_provider_stats() -> Dict[str, Any]:
    """
    Get statistics about AI provider usage and costs
    
    Returns:
        Dictionary with provider statistics
    """
    return {
        "current_strategy": settings.ai_provider,
        "providers": {
            "openai": {
                "name": "OpenAI GPT-4o",
                "cost_per_image": 0.003,
                "speed": "medium",
                "accuracy": "high"
            },
            "gemini": {
                "name": "Google Gemini Flash",
                "cost_per_image": 0.0005,
                "speed": "fast",
                "accuracy": "high"
            },
            "claude": {
                "name": "Anthropic Claude Sonnet",
                "cost_per_image": 0.004,
                "speed": "medium",
                "accuracy": "very_high"
            }
        }
    }
