from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from datetime import datetime
from typing import List
from ..schemas.body_schemas import (
    BodyScanRequest, BodyFatEstimateResponse, PercentileResponse,
    TransformationResponse, EnhancementResponse, BodyScanHistoryItem,
    SegmentRequest, SegmentResponse,
    RegionTransformRequest, RegionTransformResponse,
    GapToGoalResponse, ScanHistoryPoint, SaveGoalRequest,
    TransformationJourneyResponse, TransformationStageResponse,
    StageDescriptorResponse, NutritionPlanResponse, WorkoutPlanResponse,
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services import openai_service, grok_service, claude_service, gemini_body_service
from ..services import replicate_service
from ..services.sam_service import segment_body_part
from ..services.body_analysis import calculate_percentile, generate_recommendations
from ..services.transformation_planner import build_plan
from ..services.transformation_types import MuscleGainSpec
from ..services.journey_telemetry import (
    JourneyRequestRecord, start_timer, elapsed_ms, record_journey, get_counters,
)
from ..services.usage_limiter import check_usage_limit, increment_usage, get_credit_balance
from ..services.payment_service import check_premium_status, deduct_credits
from ..config import settings
from ..rate_limit import limiter

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
@limiter.limit("5/minute")
async def estimate_bodyfat(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Estimate body fat percentage from photo (1 free scan)"""
    try:
        if not scan_request.gender or not scan_request.age:
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
@limiter.limit("5/minute")
async def calculate_body_percentile(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Calculate body fat percentile ranking (1 free scan)"""
    try:
        if not all([scan_request.gender, scan_request.age, scan_request.ethnicity]):
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


@router.post("/transformation", response_model=TransformationJourneyResponse)
@limiter.limit("3/minute")
async def generate_transformation_journey(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user),
):
    """Generate a multi-stage body transformation journey with diet + workout plans."""
    t_start = start_timer()
    rec = JourneyRequestRecord(user_id=current_user.get("id", ""))
    try:
        if not scan_request.gender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender is required",
            )
        if not scan_request.target_bf:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target body fat percentage is required",
            )

        is_premium = await check_premium_status(current_user["id"])
        JOURNEY_COST = 30

        balance = await get_credit_balance(current_user["id"], is_premium)
        if not is_premium and balance["total_credits"] < JOURNEY_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Not enough credits. Need {JOURNEY_COST}, have {balance['total_credits']}.",
            )

        # 1. Estimate current body fat via AI vision
        current_bf = None
        bf_analysis: dict = {}
        try:
            bf_analysis = await estimate_body_fat_with_fallback(
                scan_request.image_base64,
                scan_request.gender,
                scan_request.age or 30,
            )
            current_bf = bf_analysis["body_fat_percentage"]
        except Exception as bf_err:
            logger.warning(f"Body fat estimation failed, using default: {bf_err}")

        estimated_bf = current_bf or (18.0 if scan_request.gender == "male" else 25.0)

        # 2. Build muscle gain spec from request
        mg = MuscleGainSpec()
        if scan_request.muscle_gains:
            mg = MuscleGainSpec(
                arms_kg=scan_request.muscle_gains.arms,
                chest_kg=scan_request.muscle_gains.chest,
                back_kg=scan_request.muscle_gains.back,
                shoulders_kg=scan_request.muscle_gains.shoulders,
                legs_kg=scan_request.muscle_gains.legs,
                core_kg=scan_request.muscle_gains.core,
            )

        # 3. Build the structured transformation plan
        plan = build_plan(
            current_bf=estimated_bf,
            target_bf=scan_request.target_bf,
            gender=scan_request.gender,
            muscle_gains=mg,
            weight_kg=scan_request.weight_kg,
            height_cm=scan_request.height_cm,
            age=scan_request.age,
            activity_level=scan_request.activity_level,
        )

        # 4. Collect prompts for generated stages (1-4)
        stage_prompts = [
            (s.stage_number, s.prompt)
            for s in plan.stages if s.stage_number > 0 and s.prompt
        ]

        if not stage_prompts:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No stages to generate — goal may be too close to current state.",
            )

        # 5. Generate stage images via Replicate (parallel, original as input)
        stage_images = await replicate_service.generate_journey_images(
            scan_request.image_base64, stage_prompts,
        )

        succeeded_nums = {si["stage_number"] for si in stage_images}
        all_nums = {n for n, _ in stage_prompts}
        rec.stages_requested = len(stage_prompts)
        rec.stages_succeeded = len(stage_images)
        rec.stages_failed = len(stage_prompts) - len(stage_images)
        rec.failed_stage_numbers = sorted(all_nums - succeeded_nums)
        rec.stage_latencies_ms = {si["stage_number"]: si.get("latency_ms", 0) for si in stage_images}
        rec.mode = plan.mode.value
        rec.stage_count = len(plan.stages)

        MIN_REQUIRED_STAGES = 3
        if len(stage_images) < MIN_REQUIRED_STAGES:
            rec.outcome = "below_threshold"
            rec.total_latency_ms = elapsed_ms(t_start)
            record_journey(rec)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Only {len(stage_images)} of {len(stage_prompts)} stage images "
                    f"generated successfully. No credits were charged. Please try again."
                ),
            )

        if len(stage_images) < len(stage_prompts):
            plan.warnings.append(
                f"{len(stage_prompts) - len(stage_images)} of {len(stage_prompts)} "
                f"stage image(s) failed to generate."
            )

        image_map = {si["stage_number"]: si["image_data_uri"] for si in stage_images}

        # 6. Deduct credits (only after enough stages succeeded)
        await deduct_credits(current_user["id"], JOURNEY_COST, "transformation_journey")

        # 7. Persist to body_scans
        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "transformation",
            "result_data": {
                "mode": plan.mode.value,
                "current_bf": estimated_bf,
                "target_bf": plan.target_bf,
                "total_weeks": plan.total_weeks,
                "stage_count": len(plan.stages),
                "warnings": plan.warnings,
            },
            "ai_analysis": bf_analysis,
            "created_at": datetime.utcnow().isoformat(),
        }
        db_result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = db_result.data[0]["id"] if db_result.data else None

        # 8. Auto-save final stage goal image
        final_image = image_map.get(4)
        if final_image:
            try:
                supabase.table("user_profiles").update({
                    "goal_image_url": final_image,
                    "target_body_fat_percentage": plan.target_bf,
                }).eq("id", current_user["id"]).execute()
            except Exception:
                pass

        # 9. Build response
        stages_out: list[TransformationStageResponse] = []
        for s in plan.stages:
            stages_out.append(TransformationStageResponse(
                stage_number=s.stage_number,
                label=s.label,
                week=s.week,
                bf_pct=s.bf_pct,
                weight_kg=s.weight_kg,
                lean_mass_delta_kg=s.lean_mass_delta_kg,
                fat_mass_delta_kg=s.fat_mass_delta_kg,
                body_state=StageDescriptorResponse(
                    face=s.body_state.face,
                    waist=s.body_state.waist,
                    abdomen=s.body_state.abdomen,
                    chest=s.body_state.chest,
                    arms=s.body_state.arms,
                    shoulders=s.body_state.shoulders,
                    legs=s.body_state.legs,
                    overall=s.body_state.overall,
                ),
                image_url=image_map.get(s.stage_number),
                warnings=s.warnings,
            ))

        nutrition_out = NutritionPlanResponse(
            daily_calories=plan.nutrition.daily_calories,
            protein_g=plan.nutrition.protein_g,
            carbs_g_min=plan.nutrition.carbs_g_min,
            carbs_g_max=plan.nutrition.carbs_g_max,
            fat_g_min=plan.nutrition.fat_g_min,
            fat_g_max=plan.nutrition.fat_g_max,
            meal_structure=plan.nutrition.meal_structure,
            weekly_adjustment=plan.nutrition.weekly_adjustment,
            checkin_cadence=plan.nutrition.checkin_cadence,
            stage_notes={str(k): v for k, v in plan.nutrition.stage_notes.items()},
            assumptions=plan.nutrition.assumptions,
            disclaimer=plan.nutrition.disclaimer,
        )

        workout_out = WorkoutPlanResponse(
            split_type=plan.workout.split_type,
            sessions_per_week=plan.workout.sessions_per_week,
            exercises=plan.workout.exercises,
            sets_reps_guidance=plan.workout.sets_reps_guidance,
            progression_scheme=plan.workout.progression_scheme,
            cardio_guidance=plan.workout.cardio_guidance,
            recovery_notes=plan.workout.recovery_notes,
            deload_protocol=plan.workout.deload_protocol,
            stage_adjustments={str(k): v for k, v in plan.workout.stage_adjustments.items()},
        )

        rec.outcome = "partial" if rec.stages_failed > 0 else "success"
        rec.credits_charged = JOURNEY_COST
        rec.warnings = list(plan.warnings)
        rec.total_latency_ms = elapsed_ms(t_start)
        record_journey(rec)

        return TransformationJourneyResponse(
            mode=plan.mode.value,
            current_bf=estimated_bf,
            target_bf=plan.target_bf,
            target_bf_clamped=plan.target_bf_clamped,
            total_weeks=plan.total_weeks,
            stages=stages_out,
            nutrition=nutrition_out,
            workout=workout_out,
            warnings=plan.warnings,
            disclaimer=plan.disclaimer,
            scan_id=scan_id,
        )

    except HTTPException:
        raise
    except ValueError as e:
        rec.outcome = "error"
        rec.error_detail = str(e)
        rec.total_latency_ms = elapsed_ms(t_start)
        record_journey(rec)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        rec.outcome = "error"
        rec.error_detail = str(e)
        rec.total_latency_ms = elapsed_ms(t_start)
        record_journey(rec)
        logger.error(f"Transformation journey error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transformation generation failed. Please try again.",
        )


@router.post("/enhancement", response_model=EnhancementResponse)
@limiter.limit("5/minute")
async def generate_body_enhancement(
    request: Request,
    scan_request: BodyScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate professional body photo enhancement/retouching (Premium only)"""
    try:
        if not scan_request.gender:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender required"
            )

        is_premium = await check_premium_status(current_user["id"])
        ENHANCEMENT_COST = 50

        balance = await get_credit_balance(current_user["id"], is_premium)
        if not is_premium and balance["total_credits"] < ENHANCEMENT_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Not enough credits. Need {ENHANCEMENT_COST}, have {balance['total_credits']}.",
            )

        enhancement_level = scan_request.enhancement_level or "natural"
        if enhancement_level not in ("subtle", "natural", "studio"):
            enhancement_level = "natural"

        enhanced_image_url = await openai_service.generate_body_enhancement(
            scan_request.image_base64,
            gender=scan_request.gender,
            enhancement_level=enhancement_level
        )

        await deduct_credits(current_user["id"], ENHANCEMENT_COST, "enhancement")

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


# ---------------------------------------------------------------------------
# Gap-to-Goal Retention Loop
# ---------------------------------------------------------------------------

@router.get("/gap-to-goal", response_model=GapToGoalResponse)
async def get_gap_to_goal(
    current_user: dict = Depends(get_current_user)
):
    """Get gap-to-goal data: current BF, target, goal image, scan history trend"""
    try:
        supabase = get_supabase()

        # Get user profile for target BF and goal image
        try:
            profile_result = supabase.table("user_profiles").select(
                "target_body_fat_percentage, goal_image_url"
            ).eq("id", current_user["id"]).execute()
            profile = profile_result.data[0] if profile_result.data else {}
        except Exception:
            # goal_image_url column may not exist yet
            try:
                profile_result = supabase.table("user_profiles").select(
                    "target_body_fat_percentage"
                ).eq("id", current_user["id"]).execute()
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
        supabase.table("user_profiles").update({
            "goal_image_url": goal_request.goal_image_url,
            "target_body_fat_percentage": goal_request.target_bf,
        }).eq("id", current_user["id"]).execute()

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error saving goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save goal"
        )


# ---------------------------------------------------------------------------
# SAM Segmentation & Region-Specific Transformation
# ---------------------------------------------------------------------------

@router.post("/segment", response_model=SegmentResponse)
@limiter.limit("10/minute")
async def segment_body(
    request: Request,
    seg_request: SegmentRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Segment a body part using SAM-2. User clicks on the image and receives
    a binary mask for that region. Free to call (no credits deducted).
    """
    try:
        result = await segment_body_part(
            image_base64=seg_request.image_base64,
            click_x_norm=seg_request.click_x,
            click_y_norm=seg_request.click_y,
        )
        return SegmentResponse(**result)

    except Exception as e:
        logger.error(f"SAM segmentation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Body segmentation failed. Please try clicking a different area.",
        )


@router.post("/transform-region", response_model=RegionTransformResponse)
@limiter.limit("5/minute")
async def transform_body_region(
    request: Request,
    transform_request: RegionTransformRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Transform a specific body region using ControlNet + SAM mask compositing.
    Credits are deducted for this operation.
    """
    try:
        is_premium = await check_premium_status(current_user["id"])
        REGION_TRANSFORM_COST = 15

        balance = await get_credit_balance(current_user["id"], is_premium)
        if not is_premium and balance["total_credits"] < REGION_TRANSFORM_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Not enough credits. Need {REGION_TRANSFORM_COST}, have {balance['total_credits']}.",
            )

        result = await replicate_service.controlnet_transform_region(
            image_base64=transform_request.image_base64,
            mask_base64=transform_request.mask_base64,
            body_part=transform_request.body_part,
            goal=transform_request.goal,
            gender=transform_request.gender,
            intensity=transform_request.intensity,
        )

        supabase = get_supabase()
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "region_transform",
            "result_data": {
                "body_part": result["body_part"],
                "goal": result["goal"],
                "direction": result["direction"],
            },
            "ai_analysis": {
                "body_part": result["body_part"],
                "goal": result["goal"],
                "intensity": transform_request.intensity,
            },
            "created_at": datetime.utcnow().isoformat(),
        }
        supabase.table("body_scans").insert(scan_data).execute()

        await deduct_credits(current_user["id"], REGION_TRANSFORM_COST, "region_transform")

        return RegionTransformResponse(
            transformed_image_url=result["transformed_image_url"],
            body_part=result["body_part"],
            goal=result["goal"],
            direction=result["direction"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Region transform error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Region transformation failed. Please try again.",
        )


# ---------------------------------------------------------------------------
# Dev/staging-only telemetry endpoint
# ---------------------------------------------------------------------------

@router.get("/journey-telemetry")
async def get_journey_telemetry(
    current_user: dict = Depends(get_current_user),
):
    """Return in-process journey telemetry counters (dev/staging only)."""
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found")
    return get_counters()
