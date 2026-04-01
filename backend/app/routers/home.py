from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
import logging

from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..config import settings
from ..services.proof_loop_handoff import (
    WEEKLY_REMINDER_SOURCE,
    build_progress_upload_handoff_path,
    build_weekly_scan_journey_handoff_path,
    resolve_surface_state,
)
from ..schemas.home_schemas import (
    HomeChallengeSummary,
    HomeGoalSummary,
    HomePrimaryCta,
    HomeProgressSummary,
    HomeScanSummary,
    HomeSummaryResponse,
    HomeTransformationSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_test_home_summary() -> HomeSummaryResponse:
    return HomeSummaryResponse(
        entry_state="progress_proof",
        reentry_state="progress_proof",
        surface_state="progress_proof",
        goal_summary=HomeGoalSummary(
            has_saved_plan=True,
            plan_updated_at=datetime.now(timezone.utc),
            current_bf=18.4,
            target_bf=14.0,
            goal_image_url=None,
            gap=4.4,
            selected_tier_calories=2100,
        ),
        scan_summary=HomeScanSummary(
            scan_count=3,
            last_scan_date=datetime.now(timezone.utc).isoformat(),
            prompt_state="too_early",
            latest_transformation=HomeTransformationSummary(
                id="transform-test-1",
                date=datetime.now(timezone.utc),
                result_summary="Transformation: -4%",
                image_url="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn4m0QAAAAASUVORK5CYII=",
            ),
            next_check_in_label="5 days",
        ),
        challenge_summary=HomeChallengeSummary(
            is_active=False,
            checked_in_today=False,
            day_index=None,
        ),
        progress_summary=HomeProgressSummary(
            photo_count=1,
            latest_photo_date=datetime.now(timezone.utc).isoformat(),
            compare_ready=False,
        ),
        primary_cta=HomePrimaryCta(
            state="progress_proof",
            href="/progress?tab=photos&focus=upload&from=home_progress_proof",
            label="Upload progress proof",
            title="You have data, but no proof yet",
            description="Add a progress photo so the journey is not just estimates and future previews.",
        ),
    )


def _build_upload_first_weekly_reminder_cta(*, reentry_state: str) -> HomePrimaryCta:
    return HomePrimaryCta(
        state="progress_proof",
        href=build_progress_upload_handoff_path(
            source=WEEKLY_REMINDER_SOURCE,
            reentry_state=reentry_state,
        ),
        label="Upload progress proof",
        title="Start with proof before the next weekly scan",
        description="You already have enough scan history. Add the next proof photo first so the next compare has something real to show.",
    )


def _build_weekly_scan_weekly_reminder_cta(*, reentry_state: str, surface_state: str) -> HomePrimaryCta:
    return HomePrimaryCta(
        state="weekly_scan",
        href=build_weekly_scan_journey_handoff_path(
            source=WEEKLY_REMINDER_SOURCE,
            reentry_state=reentry_state,
            surface_state=surface_state,
        ),
        label="Open weekly check-in",
        title="Review the journey, then run this week's scan",
        description="Use the weekly reminder flow to review the latest journey context before you start the next check-in.",
    )


def _days_since(value: str) -> int:
    return max(
        0,
        (datetime.now(timezone.utc).date() - datetime.fromisoformat(value.replace("Z", "+00:00")).date()).days,
    )


def _get_prompt_state(scan_count: int, last_scan_date: str | None) -> str:
    if scan_count == 0 or not last_scan_date:
        return "first_scan"
    days = _days_since(last_scan_date)
    if days < 5:
        return "too_early"
    if days <= 10:
        return "ready"
    return "overdue"


def _format_date_label(value: str | None) -> str:
    if not value:
        return "Not yet"
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%b %-d")


def _get_saved_target_bf(saved_plan: dict | None) -> float | None:
    if not saved_plan:
        return None
    goals = saved_plan.get("goals") or {}
    value = goals.get("targetBf")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _get_selected_tier_calories(saved_plan: dict | None) -> int | None:
    if not saved_plan:
        return None
    selected_tier = saved_plan.get("selectedTier")
    tier_data = saved_plan.get("tierData") or {}
    tiers = tier_data.get("tiers") or []
    try:
        index = int(selected_tier)
    except (TypeError, ValueError):
        return None
    if index < 0 or index >= len(tiers):
        return None
    calories = tiers[index].get("daily_calories")
    return calories if isinstance(calories, int) else None


def _summarize_transformation(scan: dict) -> str:
    result_data = scan.get("result_data") or {}
    target_reduction = result_data.get("target_bf_reduction")
    if target_reduction is not None:
        return f"Transformation: -{target_reduction}%"
    target_bf = result_data.get("target_body_fat_percentage") or result_data.get("target_bf")
    if target_bf is not None:
        return f"Transformation target: {target_bf}%"
    return "Transformation saved"


def _build_primary_cta(
    *,
    has_saved_plan: bool,
    challenge_active: bool,
    checked_in_today: bool,
    challenge_day_index: int | None,
    prompt_state: str,
    progress_photo_count: int,
) -> HomePrimaryCta:
    if not has_saved_plan:
        return HomePrimaryCta(
            state="plan_setup",
            href="/goal-planner",
            label="Save your plan",
            title="Set the plan before chasing the result",
            description="Your goal is not saved yet. Lock the target and calorie tier first so the rest of the journey has a reference point.",
        )

    if challenge_active and not checked_in_today:
        return HomePrimaryCta(
            state="challenge_checkin",
            href="/challenge",
            label="Check in today",
            title="Your 7-day loop is waiting",
            description=f"Day {challenge_day_index or '—'} is open. Log today before you leave so the loop stays real.",
        )

    if prompt_state == "first_scan":
        return HomePrimaryCta(
            state="first_scan",
            href="/body-scan?tab=scan",
            label="Start first scan",
            title="You still need a baseline",
            description="The planner exists, but your weekly loop does not start until you log the first body scan.",
        )

    if prompt_state in {"ready", "overdue"}:
        return HomePrimaryCta(
            state="weekly_scan",
            href="/body-scan?tab=scan",
            label="Do weekly check-in",
            title="You are overdue for this week’s check-in" if prompt_state == "overdue" else "Your weekly check-in is ready",
            description="Run the scan now so your trend stays current and the next decision is based on real data, not memory.",
        )

    if progress_photo_count == 0:
        return HomePrimaryCta(
            state="progress_proof",
            href="/progress?tab=photos&focus=upload&from=home_progress_proof",
            label="Upload progress proof",
            title="You have data, but no proof yet",
            description="Add a progress photo so the journey is not just estimates and future previews.",
        )

    return HomePrimaryCta(
        state="review_progress",
        href="/progress?tab=photos&focus=compare&from=home_review_progress",
        label="Review your proof",
        title="Your next check-in is scheduled. Use the meantime well.",
        description="Look at your latest proof and journey before the next weekly scan so you know what actually changed.",
    )


@router.get("/summary", response_model=HomeSummaryResponse)
async def get_home_summary(
    current_user: dict = Depends(get_current_user),
    source: str | None = None,
):
    user_id = current_user["id"]

    if settings.test_login_stub_mode and user_id == settings.test_login_stub_user_id:
        return _build_test_home_summary()

    supabase = get_supabase()

    try:
        profile_result = (
            supabase.table("user_profiles")
            .select("target_body_fat_percentage, goal_image_url")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        profile = profile_result.data[0] if profile_result.data else {}

        saved_plan_result = (
            supabase.table("saved_goal_plans")
            .select("plan_data, updated_at")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        saved_plan_row = saved_plan_result.data[0] if saved_plan_result.data else None
        saved_plan = saved_plan_row.get("plan_data") if saved_plan_row else None

        bodyfat_scans_result = (
            supabase.table("body_scans")
            .select("created_at, result_data, scan_type")
            .eq("user_id", user_id)
            .in_("scan_type", ["bodyfat", "percentile"])
            .order("created_at", desc=False)
            .execute()
        )

        transformation_result = (
            supabase.table("body_scans")
            .select("id, scan_type, created_at, result_data, image_url")
            .eq("user_id", user_id)
            .eq("scan_type", "transformation")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        progress_result = (
            supabase.table("progress_photos")
            .select("taken_at")
            .eq("user_id", user_id)
            .order("taken_at", desc=True)
            .execute()
        )

        challenge_result = (
            supabase.table("seven_day_challenges")
            .select("id, status, started_at")
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        current_bf = None
        last_scan_date = None
        for scan in bodyfat_scans_result.data or []:
            result_data = scan.get("result_data") or {}
            body_fat = result_data.get("body_fat_percentage")
            if body_fat is None:
                continue
            current_bf = float(body_fat)
            last_scan_date = scan["created_at"]

        target_bf = profile.get("target_body_fat_percentage")
        if target_bf is not None:
            target_bf = float(target_bf)
        else:
            target_bf = _get_saved_target_bf(saved_plan)

        gap = round(current_bf - target_bf, 1) if current_bf is not None and target_bf is not None else None
        prompt_state = _get_prompt_state(len(bodyfat_scans_result.data or []), last_scan_date)

        latest_transformation = None
        if transformation_result.data:
            transformation = transformation_result.data[0]
            latest_transformation = HomeTransformationSummary(
                id=transformation["id"],
                date=datetime.fromisoformat(transformation["created_at"].replace("Z", "+00:00")),
                result_summary=_summarize_transformation(transformation),
                image_url=transformation.get("image_url"),
            )

        progress_rows = progress_result.data or []
        latest_photo_date = progress_rows[0]["taken_at"] if progress_rows else None

        challenge_row = challenge_result.data[0] if challenge_result.data else None
        challenge_active = bool(challenge_row)
        checked_in_today = False
        challenge_day_index = None

        if challenge_row:
            started_at = challenge_row.get("started_at")
            if started_at:
                started_date = datetime.fromisoformat(started_at.replace("Z", "+00:00")).date()
                challenge_day_index = max(1, min((date.today() - started_date).days + 1, 7))

            checkins_result = (
                supabase.table("seven_day_checkins")
                .select("calendar_date")
                .eq("challenge_id", challenge_row["id"])
                .execute()
            )
            checked_in_today = any(
                row.get("calendar_date") == date.today().isoformat()
                for row in (checkins_result.data or [])
            )

        next_check_in_label = (
            "Today"
            if challenge_active and not checked_in_today
            else "After your first scan"
            if prompt_state == "first_scan"
            else f"{max(0, 7 - _days_since(last_scan_date))} day{'s' if max(0, 7 - _days_since(last_scan_date)) != 1 else ''}"
            if prompt_state == "too_early" and last_scan_date
            else "Now"
        )

        primary_cta = _build_primary_cta(
            has_saved_plan=bool(saved_plan_row),
            challenge_active=challenge_active,
            checked_in_today=checked_in_today,
            challenge_day_index=challenge_day_index,
            prompt_state=prompt_state,
            progress_photo_count=len(progress_rows),
        )
        reentry_state = primary_cta.state
        surface_state = resolve_surface_state(
            source=source,
            reentry_state=reentry_state,
            proof_photo_count=len(progress_rows),
            enabled=settings.weekly_scan_upload_first_handoff_enabled,
        )
        if source == WEEKLY_REMINDER_SOURCE and reentry_state == "weekly_scan":
            if surface_state == "progress_proof":
                primary_cta = _build_upload_first_weekly_reminder_cta(reentry_state=reentry_state)
            else:
                primary_cta = _build_weekly_scan_weekly_reminder_cta(
                    reentry_state=reentry_state,
                    surface_state=surface_state,
                )

        return HomeSummaryResponse(
            entry_state=reentry_state,
            reentry_state=reentry_state,
            surface_state=surface_state,
            goal_summary=HomeGoalSummary(
                has_saved_plan=bool(saved_plan_row),
                plan_updated_at=saved_plan_row["updated_at"] if saved_plan_row else None,
                current_bf=current_bf,
                target_bf=target_bf,
                goal_image_url=profile.get("goal_image_url"),
                gap=gap,
                selected_tier_calories=_get_selected_tier_calories(saved_plan),
            ),
            scan_summary=HomeScanSummary(
                scan_count=len(bodyfat_scans_result.data or []),
                last_scan_date=last_scan_date,
                prompt_state=prompt_state,
                latest_transformation=latest_transformation,
                next_check_in_label=next_check_in_label,
            ),
            challenge_summary=HomeChallengeSummary(
                is_active=challenge_active,
                checked_in_today=checked_in_today,
                day_index=challenge_day_index,
            ),
            progress_summary=HomeProgressSummary(
                photo_count=len(progress_rows),
                latest_photo_date=latest_photo_date,
                compare_ready=len(progress_rows) >= 2,
            ),
            primary_cta=primary_cta,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error building home summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to load home summary")
