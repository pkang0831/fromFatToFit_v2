"""Body-photo safety checks and body-fat estimation shared by body, guest, and transformation routes."""
from fastapi import HTTPException, status
import logging
from app.integrations.llm import anthropic_provider, gemini_provider, grok_provider, openai_provider
from app.vision.photo_quality import analyze_body_photo_quality
from app.vision.moderation import enforce_body_image_moderation
from app.core.upstream_errors import (
    ai_service_unavailable,
    body_model_service_unavailable,
    is_hf_or_body_model_unavailable,
    is_openai_unavailable,
    is_provider_rate_limited,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


def raise_body_unavailable(exc: Exception, *, default_detail: str) -> None:
    if is_hf_or_body_model_unavailable(exc):
        raise body_model_service_unavailable(
            "Body-analysis models are temporarily unavailable on this server."
        ) from exc
    if is_openai_unavailable(exc):
        raise ai_service_unavailable(
            "This body-analysis feature is temporarily unavailable because the AI service is not configured."
        ) from exc
    if is_provider_rate_limited(exc):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Body image generation is temporarily rate limited. Please try again shortly.",
        ) from exc
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=default_detail) from exc


def select_user_profile(supabase, user_id: str, columns: str):
    return supabase.table("user_profiles").select(columns).eq("user_id", user_id).execute()


def update_user_profile(supabase, user_id: str, data: dict):
    return supabase.table("user_profiles").update(data).eq("user_id", user_id).execute()


async def require_safe_body_photo(
    image_base64: str,
    *,
    route_name: str,
    framing: str = "upper_body",
    source: str = "authenticated",
    user_id: str | None = None,
    ownership_confirmed: bool = False,
    adult_confirmed: bool = False,
    stated_age: int | None = None,
):
    quality_result = await analyze_body_photo_quality(image_base64, framing=framing)
    if not quality_result.ok:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "body_photo_quality",
                "messages": quality_result.messages,
                "failure_codes": quality_result.failure_codes,
                "body_area_ratio": round(quality_result.body_area_ratio, 4),
                "bbox_area_ratio": round(quality_result.bbox_area_ratio, 4),
                "mask_fill_ratio": round(quality_result.mask_fill_ratio, 4),
                "is_front_facing": quality_result.is_front_facing,
                "pose_detected": quality_result.pose_detected,
                "is_shirtless": quality_result.is_shirtless,
                "brightness": round(quality_result.brightness, 1),
                "framing": quality_result.framing,
                "min_body_area_ratio": round(quality_result.min_body_area_ratio, 4),
                "min_mask_fill_ratio": round(quality_result.min_mask_fill_ratio, 4),
            },
        )

    await enforce_body_image_moderation(
        route_name=route_name,
        source=source,
        quality_result=quality_result,
        user_id=user_id,
        ownership_confirmed=ownership_confirmed,
        adult_confirmed=adult_confirmed,
        stated_age=stated_age,
    )
    return quality_result


async def estimate_body_fat_with_fallback(image_base64: str, gender: str, age: int):
    """
    Estimate body fat with AI provider fallback strategy
    Priority order: Gemini → OpenAI → Grok → Claude
    """
    primary_provider = settings.ai_provider.lower()
    
    # Define provider order based on primary
    if primary_provider == "gemini":
        providers = [
            ("Gemini", gemini_provider),
            ("OpenAI", openai_provider),
            ("Grok", grok_provider),
            ("Claude", anthropic_provider)
        ]
    elif primary_provider == "openai":
        providers = [
            ("OpenAI", openai_provider),
            ("Gemini", gemini_provider),
            ("Grok", grok_provider),
            ("Claude", anthropic_provider)
        ]
    elif primary_provider == "grok":
        providers = [
            ("Grok", grok_provider),
            ("Gemini", gemini_provider),
            ("OpenAI", openai_provider),
            ("Claude", anthropic_provider)
        ]
    elif primary_provider == "claude":
        providers = [
            ("Claude", anthropic_provider),
            ("Gemini", gemini_provider),
            ("OpenAI", openai_provider),
            ("Grok", grok_provider)
        ]
    else:  # default to gemini
        providers = [
            ("Gemini", gemini_provider),
            ("OpenAI", openai_provider),
            ("Grok", grok_provider),
            ("Claude", anthropic_provider)
        ]
    
    last_error = None
    
    # Try each provider in order
    for provider_name, provider_service in providers:
        try:
            logger.info(f"Trying {provider_name} for body fat estimation")
            return await provider_service.estimate_body_fat_percentage(image_base64, gender, age)
        except ValueError as e:
            error_msg = str(e).lower()
            # If AI declined to analyze, try next provider
            if "declined to analyze" in error_msg or "refused" in error_msg:
                logger.warning(f"{provider_name} refused analysis, trying next provider...")
                last_error = e
                continue
            else:
                # Other ValueError, raise immediately
                raise
        except Exception as e:
            logger.error(f"{provider_name} failed with error: {e}")
            last_error = e
            continue
    
    # If all providers failed, raise the last error
    if last_error:
        raise last_error
    else:
        raise ValueError("All AI providers failed to analyze the image")
