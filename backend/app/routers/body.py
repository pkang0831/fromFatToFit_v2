from fastapi import APIRouter, HTTPException, status, Depends
import logging
from datetime import datetime
from typing import List
from ..schemas.body_schemas import (
    BodyScanRequest, BodyFatEstimateResponse, PercentileResponse,
    TransformationResponse, EnhancementResponse, BodyScanHistoryItem
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services import openai_service, grok_service, claude_service, gemini_body_service
from ..services import replicate_service
from ..services.body_analysis import calculate_percentile, estimate_transformation_timeline, generate_recommendations
from ..services.usage_limiter import check_usage_limit, increment_usage
from ..services.payment_service import check_premium_status
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


async def estimate_body_fat_with_fallback(image_base64: str, gender: str, age: int):
    """
    Estimate body fat with AI provider fallback strategy
    Priority order: Gemini → OpenAI → Grok → Claude
    """
    primary_provider = settings.ai_provider.lower()
    
    # Define provider order based on primary
    if primary_provider == "gemini":
        providers = [
            ("Gemini", gemini_body_service),
            ("OpenAI", openai_service),
            ("Grok", grok_service),
            ("Claude", claude_service)
        ]
    elif primary_provider == "openai":
        providers = [
            ("OpenAI", openai_service),
            ("Gemini", gemini_body_service),
            ("Grok", grok_service),
            ("Claude", claude_service)
        ]
    elif primary_provider == "grok":
        providers = [
            ("Grok", grok_service),
            ("Gemini", gemini_body_service),
            ("OpenAI", openai_service),
            ("Claude", claude_service)
        ]
    elif primary_provider == "claude":
        providers = [
            ("Claude", claude_service),
            ("Gemini", gemini_body_service),
            ("OpenAI", openai_service),
            ("Grok", grok_service)
        ]
    else:  # default to gemini
        providers = [
            ("Gemini", gemini_body_service),
            ("OpenAI", openai_service),
            ("Grok", grok_service),
            ("Claude", claude_service)
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


@router.post("/estimate-bodyfat", response_model=BodyFatEstimateResponse)
async def estimate_bodyfat(
    request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Estimate body fat percentage from photo (1 free scan)"""
    try:
        if not request.gender or not request.age:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gender and age required")
        
        # Check if user is premium
        is_premium = await check_premium_status(current_user["id"])
        
        # Check usage limit
        try:
            usage_info = await check_usage_limit(current_user["id"], "body_fat_scan", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(usage_error)
            )
        
        # Analyze image with AI (with fallback)
        analysis_result = await estimate_body_fat_with_fallback(
            request.image_base64,
            request.gender,
            request.age
        )
        
        body_fat = analysis_result["body_fat_percentage"]
        
        # Generate recommendations
        recommendations = generate_recommendations(body_fat, request.gender)
        
        # Store scan result
        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "bodyfat",
            "result_data": {
                "body_fat_percentage": body_fat,
                "confidence": analysis_result["confidence"],
                "recommendations": recommendations
            },
            "ai_analysis": analysis_result,
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = result.data[0]["id"] if result.data else None
        
        # Increment usage count
        if not is_premium:
            await increment_usage(current_user["id"], "body_fat_scan")
        
        # Get updated usage info
        updated_usage = await check_usage_limit(current_user["id"], "body_fat_scan", is_premium)
        
        return BodyFatEstimateResponse(
            body_fat_percentage=body_fat,
            confidence=analysis_result["confidence"],
            recommendations=recommendations,
            scan_id=scan_id,
            usage_remaining=updated_usage["remaining"] if updated_usage["remaining"] != -1 else 999
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error estimating body fat: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Body fat estimation failed")


@router.post("/percentile", response_model=PercentileResponse)
async def calculate_body_percentile(
    request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calculate body fat percentile ranking (1 free scan)"""
    try:
        if not all([request.gender, request.age, request.ethnicity]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender, age, and ethnicity required"
            )
        
        # Check if user is premium
        is_premium = await check_premium_status(current_user["id"])
        
        # Check usage limit
        try:
            usage_info = await check_usage_limit(current_user["id"], "percentile_scan", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(usage_error)
            )
        
        # First, estimate body fat
        bf_analysis = await estimate_body_fat_with_fallback(
            request.image_base64,
            request.gender,
            request.age
        )
        
        body_fat = bf_analysis["body_fat_percentage"]
        
        # Calculate percentile
        percentile_data = calculate_percentile(
            body_fat,
            request.age,
            request.gender,
            request.ethnicity
        )
        
        # Store scan result
        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "percentile",
            "result_data": {
                "body_fat_percentage": body_fat,
                "percentile": percentile_data["percentile"],
                "rank_text": percentile_data["rank_text"]
            },
            "ai_analysis": bf_analysis,
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = result.data[0]["id"] if result.data else None
        
        # Increment usage count
        if not is_premium:
            await increment_usage(current_user["id"], "percentile_scan")
        
        # Get updated usage info
        updated_usage = await check_usage_limit(current_user["id"], "percentile_scan", is_premium)
        
        return PercentileResponse(
            percentile_data={
                "percentile": percentile_data["percentile"],
                "rank_text": percentile_data["rank_text"],
                "comparison_group": percentile_data["comparison_group"],
                "body_fat_percentage": body_fat
            },
            distribution_data=percentile_data["distribution_data"],
            scan_id=scan_id,
            usage_remaining=updated_usage["remaining"] if updated_usage["remaining"] != -1 else 999
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating percentile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Percentile calculation failed")


@router.post("/transformation", response_model=TransformationResponse)
async def generate_transformation_preview(
    request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate body transformation preview using Replicate FLUX Kontext Pro (Premium only)"""
    try:
        if not request.gender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender is required"
            )
        if not request.target_bf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target body fat percentage is required"
            )

        is_premium = await check_premium_status(current_user["id"])

        try:
            usage_info = await check_usage_limit(current_user["id"], "transformation", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Transformation preview requires premium subscription"
            )

        # Step 1: estimate current body fat via AI vision
        current_bf = None
        bf_analysis = {}
        try:
            bf_analysis = await estimate_body_fat_with_fallback(
                request.image_base64,
                request.gender,
                request.age or 30
            )
            current_bf = bf_analysis["body_fat_percentage"]
        except Exception as bf_err:
            logger.warning(f"Body fat estimation failed, using default: {bf_err}")

        # Fall back to a sensible default so transformation can still proceed
        estimated_bf = current_bf or (18.0 if request.gender == "male" else 25.0)
        target_bf = request.target_bf

        # Step 2: generate transformation image via Replicate
        result_data = await replicate_service.generate_body_transformation(
            image_base64=request.image_base64,
            current_bf=estimated_bf,
            target_bf=target_bf,
            gender=request.gender,
        )

        direction = result_data["direction"]
        timeline_weeks = estimate_transformation_timeline(estimated_bf, target_bf)

        if direction == "cutting":
            recommendations = [
                "Maintain calorie deficit of 300-500 kcal/day",
                "Aim for 0.5-1% bodyweight loss per week",
                "Increase protein intake to 0.8-1g per lb bodyweight",
                "Combine resistance training with cardio",
                "Track progress weekly with photos and measurements",
            ]
        else:
            recommendations = [
                "Maintain calorie surplus of 200-400 kcal/day",
                "Aim for 0.25-0.5% bodyweight gain per week",
                "Increase protein to 1-1.2g per lb bodyweight",
                "Focus on progressive overload in resistance training",
                "Track progress monthly with photos and strength benchmarks",
            ]

        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "transformation",
            "result_data": {
                "current_bf": estimated_bf,
                "target_bf": target_bf,
                "direction": direction,
                "muscle_gain_estimate": result_data["muscle_gain_estimate"],
                "timeline_weeks": timeline_weeks,
            },
            "ai_analysis": bf_analysis,
            "created_at": datetime.utcnow().isoformat(),
        }
        db_result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = db_result.data[0]["id"] if db_result.data else None

        return TransformationResponse(
            original_image_url="",
            transformed_image_url=result_data["transformed_image_url"],
            current_bf=estimated_bf,
            target_bf=target_bf,
            direction=direction,
            muscle_gain_estimate=result_data["muscle_gain_estimate"],
            estimated_timeline_weeks=timeline_weeks,
            recommendations=recommendations,
            progress_frames=result_data.get("progress_frames"),
            scan_id=scan_id,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating transformation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transformation generation failed")


@router.post("/enhancement", response_model=EnhancementResponse)
async def generate_body_enhancement(
    request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate professional body photo enhancement/retouching (Premium only)"""
    try:
        if not request.gender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender required"
            )

        is_premium = await check_premium_status(current_user["id"])

        try:
            usage_info = await check_usage_limit(current_user["id"], "enhancement", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Body enhancement requires premium subscription"
            )

        enhancement_level = request.enhancement_level or "natural"
        if enhancement_level not in ("subtle", "natural", "studio"):
            enhancement_level = "natural"

        enhanced_image_url = await openai_service.generate_body_enhancement(
            request.image_base64,
            gender=request.gender,
            enhancement_level=enhancement_level
        )

        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "enhancement",
            "result_data": {
                "enhancement_level": enhancement_level,
                "enhanced_image_url": enhanced_image_url[:100] + "..."
            },
            "ai_analysis": {"enhancement_level": enhancement_level},
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = result.data[0]["id"] if result.data else None

        return EnhancementResponse(
            original_image_url="",
            enhanced_image_url=enhanced_image_url,
            enhancement_level=enhancement_level,
            scan_id=scan_id
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating enhancement: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Body enhancement failed")


@router.get("/scans/history", response_model=List[BodyScanHistoryItem])
async def get_scan_history(
    current_user: dict = Depends(get_current_user)
):
    """Get user's body scan history"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("body_scans").select("id, scan_type, created_at, result_data, image_url").eq("user_id", current_user["id"]).order("created_at", desc=True).limit(20).execute()
        
        history = []
        for scan in result.data:
            result_data = scan.get("result_data", {})
            if scan["scan_type"] == "bodyfat":
                summary = f"{result_data.get('body_fat_percentage', 'N/A')}% body fat"
            elif scan["scan_type"] == "percentile":
                summary = f"{result_data.get('percentile', 'N/A')} percentile"
            elif scan["scan_type"] == "transformation":
                summary = f"Transformation: -{result_data.get('target_bf_reduction', 'N/A')}%"
            else:
                summary = f"Enhancement: {result_data.get('enhancement_level', 'natural')}"
            
            history.append(BodyScanHistoryItem(
                id=scan["id"],
                scan_type=scan["scan_type"],
                date=datetime.fromisoformat(scan["created_at"]),
                result_summary=summary,
                image_url=scan.get("image_url")
            ))
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting scan history: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
