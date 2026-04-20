import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

from ..config import settings
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..rate_limit import limiter
from ..schemas.weekly_checkin_schemas import (
    BodyObservation,
    GoalWeighting,
    WeeklyCheckinAnalysisResponse,
    WeeklyCheckinCreateRequest,
)
from ..services.body_image_moderation import enforce_body_image_moderation
from ..services.body_photo_quality import analyze_body_photo_quality
from ..services.openai_body_checkin_service import analyze_weekly_checkin_image
from ..services.payment_service import check_premium_status
from ..services.progress_photo_storage import delete_progress_image, upload_progress_image
from ..services.service_availability import body_model_service_unavailable, is_hf_or_body_model_unavailable, is_openai_unavailable
from ..services.usage_limiter import UsageLimitExceeded, check_usage_limit, increment_usage
from ..services.weekly_checkin_scoring import (
    build_hologram_visualization,
    build_regional_visualization,
    classify_weekly_status,
    compute_derived_scores,
    compute_weekly_delta,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/weekly-checkins", tags=["weekly-checkins"])


async def _execute(builder):
    return await asyncio.to_thread(builder.execute)


async def _ensure_safe_weekly_photo(
    image_base64: str,
    *,
    user_id: str,
    ownership_confirmed: bool,
) -> None:
    quality_result = await analyze_body_photo_quality(image_base64, framing="full_body")
    if not quality_result.ok:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "body_photo_quality",
                "messages": quality_result.messages,
                "failure_codes": quality_result.failure_codes,
                "framing": quality_result.framing,
            },
        )

    await enforce_body_image_moderation(
        route_name="weekly_checkin_analysis",
        source="authenticated",
        quality_result=quality_result,
        user_id=user_id,
        ownership_confirmed=ownership_confirmed,
        adult_confirmed=True,
        stated_age=None,
    )


async def _load_goal_weighting(user_id: str, request_body: WeeklyCheckinCreateRequest) -> GoalWeighting:
    profile_result, saved_plan_result = await asyncio.gather(
        _execute(
            get_supabase()
            .table("user_profiles")
            .select("target_body_fat_percentage")
            .eq("user_id", user_id)
            .limit(1)
        ),
        _execute(
            get_supabase()
            .table("saved_goal_plans")
            .select("plan_data")
            .eq("user_id", user_id)
            .limit(1)
        ),
    )

    profile = profile_result.data[0] if profile_result.data else {}
    saved_plan = saved_plan_result.data[0]["plan_data"] if saved_plan_result.data else {}

    target_bf = profile.get("target_body_fat_percentage")
    if target_bf is None:
        try:
            target_bf = (saved_plan.get("goals") or {}).get("targetBf")
        except AttributeError:
            target_bf = None

    weekly_weights = {}
    if isinstance(saved_plan, dict):
        weekly_weights = (
            saved_plan.get("weeklyCheckinWeights")
            or saved_plan.get("analysisWeights")
            or {}
        )

    prioritize_leanness = request_body.prioritize_leanness
    if prioritize_leanness is None:
        prioritize_leanness = weekly_weights.get("prioritizeLeanness")

    prioritize_definition = request_body.prioritize_definition
    if prioritize_definition is None:
        prioritize_definition = weekly_weights.get("prioritizeDefinition")

    return GoalWeighting(
        target_body_fat=float(target_bf) if target_bf is not None else None,
        prioritize_leanness=float(prioritize_leanness) if prioritize_leanness is not None else 0.55,
        prioritize_definition=float(prioritize_definition) if prioritize_definition is not None else 0.30,
    )


async def _load_previous_checkin(user_id: str) -> dict[str, Any] | None:
    result = await _execute(
        get_supabase()
        .table("weekly_checkins")
        .select("*")
        .eq("user_id", user_id)
        .order("taken_at", desc=True)
        .limit(1)
    )
    return result.data[0] if result.data else None


def _build_response(row: dict[str, Any]) -> WeeklyCheckinAnalysisResponse:
    return WeeklyCheckinAnalysisResponse.model_validate(row)


@router.get("/latest", response_model=WeeklyCheckinAnalysisResponse)
async def get_latest_weekly_checkin(current_user: dict = Depends(get_current_user)):
    try:
        latest = await _load_previous_checkin(current_user["id"])
    except Exception as exc:
        message = str(exc).lower()
        if "weekly_checkins" in message and ("relation" in message or "does not exist" in message):
            raise HTTPException(
                status_code=503,
                detail="Weekly check-in storage is not provisioned yet. Apply backend/supabase_weekly_checkins.sql first.",
            ) from exc
        logger.error("Failed to load latest weekly check-in: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load weekly check-in") from exc

    if not latest:
        raise HTTPException(status_code=404, detail="No weekly check-in yet")

    return _build_response(latest)


@router.post("/analyze", response_model=WeeklyCheckinAnalysisResponse)
@limiter.limit("6/minute")
async def analyze_weekly_checkin(
    request: Request,
    body: WeeklyCheckinCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    is_premium = False

    try:
        is_premium = await check_premium_status(user_id)
        if not is_premium:
            try:
                await check_usage_limit(user_id, "body_fat_scan", is_premium)
            except UsageLimitExceeded as exc:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Weekly check-in free limit reached. Upgrade to premium to continue.",
                ) from exc

        await _ensure_safe_weekly_photo(
            body.image_base64,
            user_id=user_id,
            ownership_confirmed=body.ownership_confirmed,
        )
        observation = await analyze_weekly_checkin_image(body.image_base64)
        goal = await _load_goal_weighting(user_id, body)
        derived_scores = compute_derived_scores(observation, goal)

        previous_row = await _load_previous_checkin(user_id)
        previous_id = None
        delta = None
        comparison_confidence = observation.image_quality.comparison_confidence
        weekly_status = "stable"
        is_first_checkin = previous_row is None

        if previous_row:
            previous_id = previous_row["id"]
            previous_model = WeeklyCheckinAnalysisResponse.model_validate(
                {
                    **previous_row,
                    "is_first_checkin": previous_row.get("is_first_checkin", False),
                }
            )
            previous_observation = BodyObservation(
                image_quality=previous_model.image_quality,
                observations=previous_model.observations,
                estimated_ranges=previous_model.estimated_ranges,
                qualitative_summary=previous_model.qualitative_summary,
                region_notes=previous_model.region_notes,
            )
            delta, comparison_confidence = compute_weekly_delta(
                previous_observation,
                observation,
                previous_model.derived_scores,
                derived_scores,
            )
            weekly_status = classify_weekly_status(delta.goal_proximity_score, comparison_confidence)

        regional_visualization = build_regional_visualization(observation, delta)
        hologram_visualization = build_hologram_visualization(derived_scores, comparison_confidence)

        storage = upload_progress_image(user_id, body.image_base64)
        supabase = get_supabase()
        photo_row = None

        try:
            photo_result = await _execute(
                supabase.table("progress_photos").insert(
                    {
                        "user_id": user_id,
                        "image_base64": None,
                        "storage_bucket": storage["storage_bucket"],
                        "storage_key": storage["storage_key"],
                        "notes": body.notes,
                        "weight_kg": body.weight_kg,
                        "body_fat_pct": None,
                        "taken_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
            )
            if not photo_result.data:
                raise HTTPException(status_code=500, detail="Failed to save progress photo")
            photo_row = photo_result.data[0]

            record = {
                "user_id": user_id,
                "progress_photo_id": photo_row["id"],
                "previous_checkin_id": previous_id,
                "analysis_version": settings.weekly_checkin_analysis_version,
                "taken_at": photo_row["taken_at"],
                "image_quality": observation.image_quality.model_dump(),
                "observations": observation.observations.model_dump(),
                "estimated_ranges": observation.estimated_ranges.model_dump(),
                "qualitative_summary": observation.qualitative_summary,
                "region_notes": observation.region_notes.model_dump(),
                "derived_scores": derived_scores.model_dump(),
                "delta_from_previous": delta.model_dump() if delta else None,
                "comparison_confidence": comparison_confidence,
                "weekly_status": weekly_status,
                "is_first_checkin": is_first_checkin,
                "regional_visualization": [item.model_dump() for item in regional_visualization],
                "hologram_visualization": hologram_visualization.model_dump(),
            }

            insert_result = await _execute(
                supabase.table("weekly_checkins").insert(record)
            )
            if not insert_result.data:
                raise HTTPException(status_code=500, detail="Failed to save weekly check-in analysis")
            if not is_premium:
                await increment_usage(user_id, "body_fat_scan")
            return _build_response(insert_result.data[0])
        except Exception:
            if photo_row:
                try:
                    await _execute(
                        supabase.table("progress_photos").delete().eq("id", photo_row["id"]).eq("user_id", user_id)
                    )
                except Exception:
                    logger.warning("Failed to clean up progress photo row after weekly analysis insert failure", exc_info=True)
            try:
                delete_progress_image(storage["storage_key"], storage["storage_bucket"])
            except Exception:
                logger.warning("Failed to clean up progress photo object after weekly analysis error", exc_info=True)
            raise
    except HTTPException:
        raise
    except Exception as exc:
        message = str(exc).lower()
        if "weekly_checkins" in message and ("relation" in message or "does not exist" in message):
            raise HTTPException(
                status_code=503,
                detail="Weekly check-in storage is not provisioned yet. Apply backend/supabase_weekly_checkins.sql first.",
            ) from exc
        if is_hf_or_body_model_unavailable(exc) or is_openai_unavailable(exc):
            raise body_model_service_unavailable("Weekly check-in analysis is temporarily unavailable because required AI models are not available on this server.")
        logger.error("Weekly check-in analysis failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Weekly check-in analysis failed") from exc
