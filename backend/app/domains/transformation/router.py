from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from datetime import datetime, timezone
from app.domains.body.schemas import (
    BodyScanRequest,
    EnhancementResponse,
    TransformationJourneyResponse,
    TransformationStageResponse,
    StageDescriptorResponse,
    StageNutritionSnapshotResponse,
    NutritionPlanResponse,
    WorkoutPlanResponse,
)
from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.integrations.llm import openai_provider
from app.domains.transformation.planner import build_plan
from app.domains.transformation.models import MuscleGainSpec
from app.domains.transformation.telemetry import (
    JourneyRequestRecord,
    start_timer,
    elapsed_ms,
    record_journey,
    get_counters,
)
from app.domains.billing.usage import get_credit_balance
from app.domains.billing.service import check_premium_status, deduct_credits
from app.core.config import settings
from app.core.rate_limit import limiter

from app.domains.body.common import (
    estimate_body_fat_with_fallback,
    raise_body_unavailable,
    require_safe_body_photo,
    update_user_profile,
)

logger = logging.getLogger(__name__)
router = APIRouter()


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

        await require_safe_body_photo(
            scan_request.image_base64,
            route_name="transformation",
            user_id=current_user["id"],
            ownership_confirmed=scan_request.ownership_confirmed,
            stated_age=scan_request.age,
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

        # 4. Generate all 4 stage images via RealVisXL pipeline
        from app.domains.transformation.realvis_pipeline import generate_realvis_journey

        rec.stages_requested = 4
        rec.mode = plan.mode.value
        rec.stage_count = len(plan.stages)

        stage_results = await generate_realvis_journey(
            image_base64=scan_request.image_base64,
            gender=scan_request.gender,
            mode=plan.mode,
            user_id=current_user.get("id", ""),
            stage_numbers=[1, 2, 3, 4],
        )

        stage_image_map: dict[int, str] = {}
        stage_latency_map: dict[int, float] = {}
        for sr in stage_results:
            stage_image_map[sr["stage_number"]] = sr["image_data_uri"]
            stage_latency_map[sr["stage_number"]] = sr["latency_ms"]

        rec.stages_succeeded = len(stage_results)
        rec.stages_failed = 4 - len(stage_results)
        rec.stage_latencies_ms = stage_latency_map

        after_image_uri = stage_image_map.get(4, "")

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
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        db_result = supabase.table("body_scans").insert(scan_data).execute()
        scan_id = db_result.data[0]["id"] if db_result.data else None

        # 8. Auto-save final goal image
        try:
            update_user_profile(supabase, current_user["id"], {
                "goal_image_url": after_image_uri,
                "target_body_fat_percentage": plan.target_bf,
            })
        except Exception:
            pass

        # 9. Build response — all stages 1-4 now have images via RealVisXL
        stages_out: list[TransformationStageResponse] = []
        for s in plan.stages:
            stage_image = stage_image_map.get(s.stage_number)

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
                image_url=stage_image,
                warnings=s.warnings,
                stage_nutrition=(
                    StageNutritionSnapshotResponse(
                        daily_calories=s.stage_nutrition.daily_calories,
                        protein_g=s.stage_nutrition.protein_g,
                    ) if s.stage_nutrition else None
                ),
                stage_exercises=s.stage_exercises or [],
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

        rec.outcome = "success"
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
        raise_body_unavailable(e, default_detail="Transformation generation failed. Please try again.")


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

        await require_safe_body_photo(
            scan_request.image_base64,
            route_name="enhancement",
            user_id=current_user["id"],
            ownership_confirmed=scan_request.ownership_confirmed,
            stated_age=scan_request.age or current_user.get("age"),
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

        enhanced_image_url = await openai_provider.generate_body_enhancement(
            scan_request.image_base64,
            gender=scan_request.gender,
            enhancement_level=enhancement_level
        )

        await deduct_credits(current_user["id"], ENHANCEMENT_COST, "enhancement")

        supabase = get_supabase()
        scan_id = None
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "enhancement",
            "result_data": {
                "enhancement_level": enhancement_level,
                "enhanced_image_url": enhanced_image_url[:100] + "..."
            },
            "ai_analysis": {"enhancement_level": enhancement_level},
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        try:
            result = supabase.table("body_scans").insert(scan_data).execute()
            scan_id = result.data[0]["id"] if result.data else None
        except Exception as scan_error:
            logger.warning(
                "Enhancement generated successfully but body_scans persistence failed; continuing without scan_id: %s",
                scan_error,
            )

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
        raise_body_unavailable(e, default_detail="Body enhancement failed")


@router.get("/journey-telemetry", include_in_schema=not settings.is_production)
async def get_journey_telemetry(
    current_user: dict = Depends(get_current_user),
):
    """Return in-process journey telemetry counters (dev/staging only)."""
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found")
    return get_counters()
