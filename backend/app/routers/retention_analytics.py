import logging

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import settings
from ..middleware.auth_middleware import get_current_user
from ..schemas.home_schemas import RetentionEventRequest
from ..services.retention_event_service import list_funnel_view_rows, log_retention_event

router = APIRouter()
logger = logging.getLogger(__name__)
CLIENT_CAPTURED_RETENTION_EVENTS = {
    "reengagement_session",
    "history_viewed",
    "progress_proof_started",
    "progress_proof_completed",
    "proof_upload_failed",
    "progress_compare_viewed",
    "progress_checkin_started",
    "progress_checkin_completed",
    "progress_checkin_failed",
}


def _read_funnel_view(
    view_name: str,
    *,
    order_by: str | None = None,
    desc: bool = True,
):
    try:
        return list_funnel_view_rows(view_name, order_by=order_by, desc=desc)
    except Exception as exc:
        logger.error("Failed to load analytics view %s: %s", view_name, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load funnel analytics",
        ) from exc


def _require_analytics_admin(current_user: dict) -> None:
    if not settings.is_production:
        return

    email = str(current_user.get("email") or "").strip().lower()
    if email and email in settings.analytics_admin_emails_list:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Analytics access is restricted",
    )


def _mask_share_token(token: str | None) -> str | None:
    if not token:
        return None
    if len(token) <= 10:
        return f"{token[:3]}..."
    return f"{token[:6]}...{token[-4:]}"


@router.post("/retention")
async def capture_retention_event(
    body: RetentionEventRequest,
    current_user: dict = Depends(get_current_user),
):
    if body.event_name not in CLIENT_CAPTURED_RETENTION_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This retention event must be captured server-side",
        )

    await log_retention_event(
        current_user["id"],
        body.event_name,
        body.surface,
        body.properties,
    )
    return {"status": "ok"}


@router.get("/funnel/daily-snapshot")
async def get_daily_funnel_snapshot(current_user: dict = Depends(get_current_user)):
    _require_analytics_admin(current_user)
    return _read_funnel_view("analytics_daily_funnel_snapshot", order_by="snapshot_date")


@router.get("/funnel/weekly-cohort-by-source")
async def get_weekly_cohort_by_source(current_user: dict = Depends(get_current_user)):
    _require_analytics_admin(current_user)
    return _read_funnel_view("analytics_weekly_cohort_by_source", order_by="cohort_week")


@router.get("/funnel/entry-state-performance")
async def get_entry_state_performance(current_user: dict = Depends(get_current_user)):
    _require_analytics_admin(current_user)
    return _read_funnel_view("analytics_entry_state_performance", order_by="reengagement_sessions")


@router.get("/funnel/reminder-open-to-proof")
async def get_reminder_open_to_proof(current_user: dict = Depends(get_current_user)):
    _require_analytics_admin(current_user)
    return _read_funnel_view("analytics_reminder_open_to_proof", order_by="opened_date")


@router.get("/funnel/share-view-to-register")
async def get_share_view_to_register(current_user: dict = Depends(get_current_user)):
    _require_analytics_admin(current_user)
    rows = _read_funnel_view("analytics_share_view_to_try_to_register", order_by="share_views")
    return [
        {
            **{key: value for key, value in row.items() if key != "share_token"},
            "share_token_preview": _mask_share_token(row.get("share_token")),
        }
        for row in rows
    ]
