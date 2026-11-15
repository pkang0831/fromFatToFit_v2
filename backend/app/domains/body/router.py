from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from datetime import datetime, timezone
from typing import List
from app.domains.body.schemas import (
    BodyScanRequest,
    BodyFatEstimateResponse,
    PercentileResponse,
    BodyScanHistoryItem,
    GapToGoalResponse,
    ScanHistoryPoint,
    SaveGoalRequest,
    BodyPhotoQualityRequest,
    BodyPhotoQualityResponse,
)
from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.vision.photo_quality import analyze_body_photo_quality
from app.domains.body.analysis import calculate_percentile, generate_recommendations
from app.domains.billing.usage import check_usage_limit, increment_usage, get_credit_balance
from app.domains.billing.service import check_premium_status, deduct_credits
from app.domains.analytics.events import log_retention_event
from app.core.rate_limit import limiter

from app.domains.body.common import (
    estimate_body_fat_with_fallback,
    raise_body_unavailable,
    require_safe_body_photo,
    select_user_profile,
    update_user_profile,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/validate-photo", response_model=BodyPhotoQualityResponse)
@limiter.limit("20/minute")
async def validate_body_photo(
    request: Request,
    body: BodyPhotoQualityRequest,
    current_user: dict = Depends(get_current_user),
):
    """Check framing (segmentation area) and frontal pose; no credits charged."""
    try:
        result = await analyze_body_photo_quality(
            body.image_base64,
            framing=body.framing,
        )
        d = result.to_dict()
        return BodyPhotoQualityResponse(
            ok=d["ok"],
            body_area_ratio=d["body_area_ratio"],
            bbox_area_ratio=d["bbox_area_ratio"],
            mask_fill_ratio=d["mask_fill_ratio"],
            is_front_facing=d["is_front_facing"],
            pose_detected=d["pose_detected"],
            is_shirtless=d["is_shirtless"],
            brightness=d["brightness"],
            failure_codes=d["failure_codes"],
            messages=d["messages"],
            width=d["width"],
            height=d["height"],
            framing=d["framing"],
            min_body_area_ratio=d["min_body_area_ratio"],
            min_mask_fill_ratio=d["min_mask_fill_ratio"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"validate-photo error: {e}", exc_info=True)
        raise_body_unavailable(e, default_detail="Photo validation failed. Please try again.")


@router.post("/estimate-bodyfat", response_model=BodyFatEstimateResponse)
@limiter.limit("5/minute")
async def estimate_bodyfat(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Estimate body fat percentage from photo (1 free scan, then credits)"""
    try:
        if not scan_request.gender or not scan_request.age:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Gender and age required")

        await require_safe_body_photo(
            scan_request.image_base64,
            route_name="estimate_bodyfat",
            user_id=current_user["id"],
            ownership_confirmed=scan_request.ownership_confirmed,
            stated_age=scan_request.age,
        )

        # Check if user is premium
        is_premium = await check_premium_status(current_user["id"])
        
        # Check usage limit — if free scans exhausted, try credit deduction
        used_credits = False
        try:
            await check_usage_limit(current_user["id"], "body_fat_scan", is_premium)
        except Exception:
            credit_info = await get_credit_balance(current_user["id"], is_premium)
            cost = credit_info["credit_costs"].get("body_fat_scan", 10)
            await deduct_credits(current_user["id"], cost, "body_fat_scan")
            used_credits = True
        
        # Analyze image with AI (with fallback)
        analysis_result = await estimate_body_fat_with_fallback(
            scan_request.image_base64,
            scan_request.gender,
            scan_request.age
        )
        
        body_fat = analysis_result["body_fat_percentage"]
        
        # Generate recommendations
        recommendations = generate_recommendations(body_fat, scan_request.gender)
        
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
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = result.data[0]["id"] if result.data else None

        await log_retention_event(
            current_user["id"],
            "scan_success",
            "body_scan_api",
            {
                "scan_id": scan_id,
                "scan_type": "bodyfat",
                "source": scan_request.source,
                "session_id": scan_request.session_id,
                "reminder_event_id": scan_request.reminder_event_id,
                "entry_state": scan_request.reentry_state,
                "reentry_state": scan_request.reentry_state,
                "surface_state": scan_request.surface_state,
                "used_credits": used_credits,
                "is_premium": is_premium,
            },
        )
        
        # Increment usage count (only for free scans, credits already deducted)
        if not is_premium and not used_credits:
            await increment_usage(current_user["id"], "body_fat_scan")
        
        # Get updated usage info
        try:
            updated_usage = await check_usage_limit(current_user["id"], "body_fat_scan", is_premium)
        except Exception:
            updated_usage = {"remaining": 0}
        
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
        raise_body_unavailable(e, default_detail="Body fat estimation failed")


@router.post("/percentile", response_model=PercentileResponse)
@limiter.limit("5/minute")
async def calculate_body_percentile(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calculate body fat percentile ranking (1 free scan, then credits)"""
    try:
        if not all([scan_request.gender, scan_request.age, scan_request.ethnicity]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender, age, and ethnicity required"
            )

        await require_safe_body_photo(
            scan_request.image_base64,
            route_name="percentile",
            user_id=current_user["id"],
            ownership_confirmed=scan_request.ownership_confirmed,
            stated_age=scan_request.age,
        )

        # Check if user is premium
        is_premium = await check_premium_status(current_user["id"])
        
        # Check usage limit — if free scans exhausted, try credit deduction
        used_credits = False
        try:
            await check_usage_limit(current_user["id"], "percentile_scan", is_premium)
        except Exception:
            credit_info = await get_credit_balance(current_user["id"], is_premium)
            cost = credit_info["credit_costs"].get("percentile_scan", 10)
            await deduct_credits(current_user["id"], cost, "percentile_scan")
            used_credits = True
        
        # First, estimate body fat
        bf_analysis = await estimate_body_fat_with_fallback(
            scan_request.image_base64,
            scan_request.gender,
            scan_request.age
        )
        
        body_fat = bf_analysis["body_fat_percentage"]
        
        # Calculate percentile
        percentile_data = calculate_percentile(
            body_fat,
            scan_request.age,
            scan_request.gender,
            scan_request.ethnicity
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
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = result.data[0]["id"] if result.data else None

        await log_retention_event(
            current_user["id"],
            "scan_success",
            "body_scan_api",
            {
                "scan_id": scan_id,
                "scan_type": "percentile",
                "source": scan_request.source,
                "session_id": scan_request.session_id,
                "reminder_event_id": scan_request.reminder_event_id,
                "entry_state": scan_request.reentry_state or ("weekly_scan" if scan_request.source == "weekly_reminder" else None),
                "reentry_state": scan_request.reentry_state or ("weekly_scan" if scan_request.source == "weekly_reminder" else None),
                "surface_state": scan_request.surface_state or ("weekly_scan" if scan_request.source == "weekly_reminder" else None),
                "used_credits": used_credits,
                "is_premium": is_premium,
            },
        )
        
        # Increment usage count (only for free scans, credits already deducted)
        if not is_premium and not used_credits:
            await increment_usage(current_user["id"], "percentile_scan")
        
        # Get updated usage info
        try:
            updated_usage = await check_usage_limit(current_user["id"], "percentile_scan", is_premium)
        except Exception:
            updated_usage = {"remaining": 0}
        
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
        raise_body_unavailable(e, default_detail="Percentile calculation failed")


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


@router.get("/gap-to-goal", response_model=GapToGoalResponse)
async def get_gap_to_goal(
    current_user: dict = Depends(get_current_user)
):
    """Get gap-to-goal data: current BF, target, goal image, scan history trend"""
    try:
        supabase = get_supabase()

        # Get user profile for target BF and goal image
        try:
            profile_result = select_user_profile(
                supabase,
                current_user["id"],
                "target_body_fat_percentage, goal_image_url",
            )
            profile = profile_result.data[0] if profile_result.data else {}
        except Exception:
            # goal_image_url column may not exist yet
            try:
                profile_result = select_user_profile(
                    supabase,
                    current_user["id"],
                    "target_body_fat_percentage",
                )
                profile = profile_result.data[0] if profile_result.data else {}
            except Exception:
                profile = {}

        target_bf = profile.get("target_body_fat_percentage")
        goal_image_url = profile.get("goal_image_url")
        if target_bf is not None:
            target_bf = float(target_bf)

        # Get all bodyfat/percentile scans ordered by date
        scans_result = supabase.table("body_scans").select(
            "created_at, result_data, scan_type"
        ).eq("user_id", current_user["id"]).in_(
            "scan_type", ["bodyfat", "percentile"]
        ).order("created_at", desc=False).execute()

        scan_history: list[ScanHistoryPoint] = []
        current_bf = None
        last_scan_date = None

        for scan in (scans_result.data or []):
            rd = scan.get("result_data", {})
            bf = rd.get("body_fat_percentage")
            if bf is None and "percentile" in rd:
                bf = rd.get("body_fat_percentage")
            if bf is not None:
                bf = float(bf)
                scan_date = scan["created_at"][:10]
                scan_history.append(ScanHistoryPoint(date=scan_date, bf=bf))
                current_bf = bf
                last_scan_date = scan_date

        gap = None
        if current_bf is not None and target_bf is not None:
            gap = round(current_bf - target_bf, 1)

        return GapToGoalResponse(
            current_bf=current_bf,
            target_bf=target_bf,
            goal_image_url=goal_image_url,
            gap=gap,
            scan_count=len(scan_history),
            last_scan_date=last_scan_date,
            scan_history=scan_history,
        )

    except Exception as e:
        logger.error(f"Error getting gap-to-goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get gap-to-goal data"
        )


@router.patch("/save-goal")
async def save_goal(
    goal_request: SaveGoalRequest,
    current_user: dict = Depends(get_current_user)
):
    """Save transformation goal image and target body fat to user profile"""
    try:
        supabase = get_supabase()
        update_user_profile(supabase, current_user["id"], {
            "goal_image_url": goal_request.goal_image_url,
            "target_body_fat_percentage": goal_request.target_bf,
        })

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error saving goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save goal"
        )
