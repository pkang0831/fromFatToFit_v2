import logging
import json
import asyncio
import smtplib
import hmac
import hashlib
import base64
from typing import Dict, Any, List, Optional, Mapping
from datetime import datetime, timezone, timedelta
from math import floor
from email.message import EmailMessage
from email.utils import make_msgid, parseaddr
from urllib.parse import quote
from uuid import UUID, uuid4
from ..database import get_supabase, get_user_supabase
from ..config import settings
from .proof_loop_handoff import (
    WEEKLY_REMINDER_SOURCE,
    append_query_params_to_path,
    build_progress_upload_handoff_path,
    build_weekly_scan_journey_handoff_path,
    extract_query_param,
    resolve_surface_state,
)
from .retention_event_service import log_retention_event

logger = logging.getLogger(__name__)

WEEKLY_PROOF_REMINDER_TYPE = "weekly_proof"
WEEKLY_PROOF_REMINDER_CHANNEL = "email"
WEEKLY_PROOF_ELIGIBLE_STATES = {"progress_proof", "weekly_scan"}
WEEKLY_PROOF_NON_DELIVERABLE_STATUSES = {"bounced", "suppressed", "complained", "unsubscribed"}
WEEKLY_PROOF_COOLDOWN_STATUSES = {"queued", "sending", "sent", "delivered", "opened", "clicked"}
WEEKLY_PROOF_PROVIDER_EVENTS = {
    "email.sent",
    "email.delivered",
    "email.delivery_delayed",
    "email.bounced",
    "email.failed",
    "email.suppressed",
    "email.opened",
    "email.clicked",
    "email.complained",
    "contact.updated",
}

DEFAULT_PREFERENCES = {
    "email_weekly_summary": True,
    "email_inactivity_reminder": True,
    "email_credit_low": True,
    "push_meal_reminder": True,
    "push_workout_reminder": True,
    "push_daily_summary": False,
    "push_weekly_body_scan": True,
    "meal_reminder_time": "12:00",
    "workout_reminder_days": ["monday", "wednesday", "friday"],
}

LEGACY_DEFAULT_PREFERENCES = {
    "email_enabled": True,
    "push_enabled": True,
    "weekly_report": True,
}


def _strip_metadata(row: Dict[str, Any]) -> Dict[str, Any]:
    cleaned = dict(row)
    cleaned.pop("id", None)
    cleaned.pop("created_at", None)
    cleaned.pop("updated_at", None)
    return cleaned


def _normalize_preferences(row: Dict[str, Any]) -> Dict[str, Any]:
    stripped = _strip_metadata(row)
    normalized = dict(DEFAULT_PREFERENCES)

    if any(key in stripped for key in DEFAULT_PREFERENCES):
        for key, default in DEFAULT_PREFERENCES.items():
            value = stripped.get(key, default)
            normalized[key] = default if value is None else value
        return normalized

    email_enabled = bool(stripped.get("email_enabled", True))
    push_enabled = bool(stripped.get("push_enabled", True))
    weekly_report = bool(stripped.get("weekly_report", True))

    normalized.update({
        "email_weekly_summary": weekly_report,
        "email_inactivity_reminder": email_enabled,
        "email_credit_low": email_enabled,
        "push_meal_reminder": push_enabled,
        "push_workout_reminder": push_enabled,
        "push_weekly_body_scan": push_enabled,
        "push_daily_summary": False,
    })
    return normalized


def _build_latest_preferences_record(user_id: str) -> Dict[str, Any]:
    now = _utcnow().isoformat()
    return {
        "user_id": user_id,
        **DEFAULT_PREFERENCES,
        "created_at": now,
        "updated_at": now,
    }


def _build_legacy_preferences_record(user_id: str) -> Dict[str, Any]:
    now = _utcnow().isoformat()
    return {
        "user_id": user_id,
        **LEGACY_DEFAULT_PREFERENCES,
        "created_at": now,
        "updated_at": now,
    }


def _to_legacy_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
    legacy_updates: Dict[str, Any] = {}

    email_fields = {
        "email_weekly_summary",
        "email_inactivity_reminder",
        "email_credit_low",
    }
    if any(field in updates for field in email_fields):
        legacy_updates["email_enabled"] = any(bool(updates.get(field)) for field in email_fields if field in updates)
        if "email_weekly_summary" in updates:
            legacy_updates["weekly_report"] = bool(updates["email_weekly_summary"])

    push_fields = {
        "push_meal_reminder",
        "push_workout_reminder",
        "push_daily_summary",
        "push_weekly_body_scan",
    }
    if any(field in updates for field in push_fields):
        legacy_updates["push_enabled"] = any(bool(updates.get(field)) for field in push_fields if field in updates)

    return legacy_updates


async def get_notification_preferences(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase()
    try:
        result = supabase.table("notification_preferences").select("*").eq("user_id", user_id).execute()
    except Exception as select_error:
        logger.error("notification_preferences unavailable; returning defaults: %s", select_error)
        return dict(DEFAULT_PREFERENCES)

    if result.data:
        return _normalize_preferences(result.data[0])

    latest_record = _build_latest_preferences_record(user_id)
    try:
        insert_result = supabase.table("notification_preferences").insert(latest_record).execute()
        if insert_result.data:
            return _normalize_preferences(insert_result.data[0])
        return _normalize_preferences(latest_record)
    except Exception as latest_insert_error:
        logger.warning(
            "notification_preferences insert failed with latest schema; retrying with legacy columns: %s",
            latest_insert_error,
        )

    legacy_record = _build_legacy_preferences_record(user_id)
    try:
        insert_result = supabase.table("notification_preferences").insert(legacy_record).execute()
        if insert_result.data:
            return _normalize_preferences(insert_result.data[0])
        return _normalize_preferences(legacy_record)
    except Exception as legacy_insert_error:
        logger.error("notification_preferences legacy insert unavailable; returning defaults: %s", legacy_insert_error)
        return dict(DEFAULT_PREFERENCES)


async def update_notification_preferences(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase()
    await get_notification_preferences(user_id)

    allowed = set(DEFAULT_PREFERENCES.keys())
    filtered = {k: v for k, v in updates.items() if k in allowed}
    filtered["updated_at"] = _utcnow().isoformat()

    try:
        supabase.table("notification_preferences").update(filtered).eq("user_id", user_id).execute()
    except Exception as latest_update_error:
        logger.warning(
            "notification_preferences update failed with latest schema; retrying with legacy columns: %s",
            latest_update_error,
        )
        legacy_updates = _to_legacy_updates(filtered)
        if not legacy_updates:
            return await get_notification_preferences(user_id)
        legacy_updates["updated_at"] = filtered["updated_at"]
        try:
            supabase.table("notification_preferences").update(legacy_updates).eq("user_id", user_id).execute()
        except Exception as legacy_update_error:
            logger.error(
                "notification_preferences update unavailable; returning in-memory fallback: %s",
                legacy_update_error,
            )
            current = await get_notification_preferences(user_id)
            current.update({k: v for k, v in filtered.items() if k in DEFAULT_PREFERENCES})
            return current

    return await get_notification_preferences(user_id)


async def save_push_subscription(
    user_id: str,
    subscription: Dict[str, Any],
    access_token: str | None = None,
) -> Dict[str, Any]:
    supabase = get_user_supabase(access_token) if access_token else get_supabase()
    endpoint = subscription.get("endpoint", "")

    existing = supabase.table("push_subscriptions").select("id").eq("user_id", user_id).eq("endpoint", endpoint).execute()

    if existing.data:
        supabase.table("push_subscriptions").update({
            "subscription_data": json.dumps(subscription),
            "updated_at": _utcnow().isoformat(),
        }).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("push_subscriptions").insert({
            "user_id": user_id,
            "endpoint": endpoint,
            "subscription_data": json.dumps(subscription),
            "active": True,
            "created_at": _utcnow().isoformat(),
            "updated_at": _utcnow().isoformat(),
        }).execute()

    logger.info(f"Saved push subscription for user {user_id}")
    return {"status": "subscribed"}


async def remove_push_subscription(
    user_id: str,
    endpoint: str,
    access_token: str | None = None,
) -> Dict[str, Any]:
    supabase = get_user_supabase(access_token) if access_token else get_supabase()
    supabase.table("push_subscriptions").update({
        "active": False,
        "updated_at": _utcnow().isoformat(),
    }).eq("user_id", user_id).eq("endpoint", endpoint).execute()

    return {"status": "unsubscribed"}


async def get_push_subscriptions(user_id: str, access_token: str | None = None) -> List[Dict[str, Any]]:
    supabase = get_user_supabase(access_token) if access_token else get_supabase()
    result = supabase.table("push_subscriptions").select("*").eq("user_id", user_id).eq("active", True).execute()
    return result.data or []


async def check_weekly_scan_reminder(user_id: str) -> bool:
    """
    Check if user should receive a weekly body scan reminder.
    Returns True if reminder was sent.
    """
    try:
        prefs = await get_notification_preferences(user_id)
        if not prefs.get("push_weekly_body_scan", True):
            return False

        supabase = get_supabase()
        scans = supabase.table("body_scans").select("created_at").eq(
            "user_id", user_id
        ).in_("scan_type", ["bodyfat", "percentile"]).order(
            "created_at", desc=True
        ).limit(1).execute()

        if not scans.data:
            return False

        last_scan = datetime.fromisoformat(scans.data[0]["created_at"].replace("Z", "+00:00"))
        days_since = (datetime.now(last_scan.tzinfo) - last_scan).days

        if days_since >= 7:
            await send_push_notification(
                user_id,
                "Your weekly scan is ready!",
                "Come back and see how your gap to goal has changed.",
                {"action": "body-scan"},
            )
            return True

        return False
    except Exception as e:
        logger.error(f"Error checking scan reminder for {user_id}: {e}")
        return False


def _vapid_ready() -> bool:
    return bool(settings.vapid_private_key and settings.vapid_public_key)


def _send_webpush(sub_data: Dict[str, Any], payload_str: str) -> None:
    from pywebpush import webpush, WebPushException  # type: ignore[import]

    webpush(
        subscription_info=sub_data,
        data=payload_str,
        vapid_private_key=settings.vapid_private_key,
        vapid_claims={"sub": settings.vapid_claims_email},
    )


async def send_push_notification(user_id: str, title: str, body: str, data: Optional[Dict] = None) -> int:
    """
    Send push notification to all active subscriptions for a user via pywebpush.
    Silently skips if VAPID keys are not configured.
    """
    if not _vapid_ready():
        logger.debug("Push skipped for %s: VAPID keys not configured", user_id)
        return 0

    subs = await get_push_subscriptions(user_id)
    payload = json.dumps({"title": title, "body": body, **(data or {})})
    sent = 0
    for sub in subs:
        try:
            sub_data = json.loads(sub["subscription_data"])
            await asyncio.to_thread(_send_webpush, sub_data, payload)
            sent += 1
        except Exception as e:
            logger.warning("Failed to send push to %s: %s", user_id, e)
    return sent


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _is_local_url(url: str | None) -> bool:
    if not url:
        return True
    lowered = url.lower()
    return "localhost" in lowered or "127.0.0.1" in lowered


def get_weekly_proof_reminder_status() -> Dict[str, Any]:
    if not settings.enable_weekly_proof_reminders:
        return {
            "active": False,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "reason": "disabled_by_flag",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    if settings.weekly_proof_reminder_channel != WEEKLY_PROOF_REMINDER_CHANNEL:
        return {
            "active": False,
            "channel": settings.weekly_proof_reminder_channel,
            "reason": "unsupported_channel",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    if not settings.weekly_proof_reminder_provider_ready:
        return {
            "active": False,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "reason": "provider_not_ready",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    if (
        not settings.smtp_host
        or not settings.smtp_username
        or not settings.smtp_password
        or not settings.smtp_from_email
    ):
        return {
            "active": False,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "reason": "email_not_configured",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    if not settings.resend_webhook_secret:
        return {
            "active": False,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "reason": "webhook_not_configured",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    if _is_local_url(settings.public_app_url) or _is_local_url(settings.public_api_url):
        return {
            "active": False,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "reason": "public_urls_not_configured",
            "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
        }

    return {
        "active": True,
        "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
        "reason": None,
        "cooldown_hours": settings.weekly_proof_reminder_cooldown_hours,
    }


def _get_weekly_proof_profile(user_id: str) -> Dict[str, Any]:
    supabase = get_supabase()
    result = (
        supabase.table("user_profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else {"user_id": user_id, "email": "", "onboarding_completed": False}


async def get_weekly_proof_reminder_status_for_user(user_id: str) -> Dict[str, Any]:
    system_status = get_weekly_proof_reminder_status()
    prefs = await get_notification_preferences(user_id)
    profile = _get_weekly_proof_profile(user_id)

    response: Dict[str, Any] = {
        **system_status,
        "system_active": system_status["active"],
        "eligible": False,
        "effective_active": False,
        "effective_reason": system_status["reason"] if not system_status["active"] else None,
        "eligibility_reason": None,
        "preferences_enabled": bool(prefs.get("email_weekly_summary", True)),
        "onboarding_completed": bool(profile.get("onboarding_completed", True)),
        "email_present": bool(profile.get("email")),
        "entry_state": None,
        "surface_state": None,
        "scan_count": 0,
        "proof_photo_count": 0,
        "next_path": None,
        "last_event_status": None,
        "last_event_at": None,
    }

    user_reason: str | None = None

    if profile.get("deleted_at") or profile.get("blocked_at") or profile.get("disabled_at"):
        user_reason = "account_inactive"
    elif not response["email_present"]:
        user_reason = "email_missing"
    elif not response["onboarding_completed"]:
        user_reason = "onboarding_incomplete"
    elif not response["preferences_enabled"]:
        user_reason = "preferences_disabled"
    else:
        try:
            summary = await _get_home_summary_for_user(user_id)
        except Exception as exc:
            logger.error("Failed to load home summary for weekly reminder status %s: %s", user_id, exc)
            user_reason = "summary_unavailable"
        else:
            entry_state = getattr(summary, "entry_state", None)
            response["entry_state"] = entry_state

            if entry_state not in WEEKLY_PROOF_ELIGIBLE_STATES:
                user_reason = "not_ready_for_weekly_proof"
            else:
                scan_summary = getattr(summary, "scan_summary", None)
                scan_count = int(getattr(scan_summary, "scan_count", 0) or 0)
                response["scan_count"] = scan_count

                if scan_count <= 0:
                    user_reason = "no_scan_data"
                else:
                    progress_summary = getattr(summary, "progress_summary", None)
                    proof_photo_count = int(getattr(progress_summary, "photo_count", 0) or 0)
                    response["proof_photo_count"] = proof_photo_count

                    surface_state = resolve_surface_state(
                        source=WEEKLY_REMINDER_SOURCE,
                        reentry_state=entry_state,
                        proof_photo_count=proof_photo_count,
                        enabled=settings.weekly_scan_upload_first_handoff_enabled,
                    )
                    response["surface_state"] = surface_state
                    response["next_path"] = build_weekly_proof_reminder_path(
                        entry_state,
                        progress_photo_count=proof_photo_count,
                    )

                    last_event = _get_latest_weekly_reminder_event(user_id)
                    last_status = ((last_event or {}).get("status") or "").lower() or None
                    last_touch = (
                        _parse_iso_datetime((last_event or {}).get("sent_at"))
                        or _parse_iso_datetime((last_event or {}).get("created_at"))
                    )
                    response["last_event_status"] = last_status
                    response["last_event_at"] = last_touch.isoformat() if last_touch else None

                    if last_status in WEEKLY_PROOF_NON_DELIVERABLE_STATUSES:
                        user_reason = "deliverability_blocked"
                    elif (
                        last_status in WEEKLY_PROOF_COOLDOWN_STATUSES
                        and last_touch
                        and _utcnow() - last_touch < timedelta(hours=settings.weekly_proof_reminder_cooldown_hours)
                    ):
                        user_reason = "cooldown_active"
                    else:
                        response["eligible"] = True

    response["eligibility_reason"] = user_reason
    response["effective_active"] = bool(system_status["active"] and response["eligible"])
    response["effective_reason"] = (
        system_status["reason"]
        if not system_status["active"]
        else user_reason
    )
    return response


def build_weekly_proof_reminder_path(
    entry_state: str,
    *,
    progress_photo_count: int = 0,
) -> str:
    surface_state = resolve_surface_state(
        source=WEEKLY_REMINDER_SOURCE,
        reentry_state=entry_state,
        proof_photo_count=progress_photo_count,
        enabled=settings.weekly_scan_upload_first_handoff_enabled,
    )
    if surface_state == "progress_proof":
        return build_progress_upload_handoff_path(
            source=WEEKLY_REMINDER_SOURCE,
            reentry_state=entry_state,
            surface_state=surface_state,
        )
    if entry_state == "weekly_scan":
        return build_weekly_scan_journey_handoff_path(
            source=WEEKLY_REMINDER_SOURCE,
            reentry_state=entry_state,
            surface_state=surface_state,
        )
    raise ValueError(f"Unsupported reminder entry_state: {entry_state}")


def build_weekly_proof_tracking_url(reminder_event_id: str, next_path: str) -> str:
    encoded_next = quote(_sanitize_frontend_path(next_path), safe="")
    return (
        f"{settings.public_api_url.rstrip('/')}"
        f"/notifications/reminders/open/{reminder_event_id}?next={encoded_next}"
    )


def build_weekly_proof_unsubscribe_url(reminder_event_id: str) -> str:
    return (
        f"{settings.public_api_url.rstrip('/')}"
        f"/notifications/reminders/unsubscribe/{reminder_event_id}"
    )


def _sanitize_frontend_path(next_path: str | None) -> str:
    if not next_path or not next_path.startswith("/"):
        return "/home"
    if next_path.startswith("//") or "://" in next_path:
        return "/home"
    return next_path


def _build_weekly_proof_subject(reentry_state: str, surface_state: str) -> str:
    if reentry_state == "weekly_scan" and surface_state == "weekly_scan":
        return "Your weekly proof check-in is ready"
    return "Add this week’s progress proof before the next scan"


def _build_weekly_proof_copy(reentry_state: str, surface_state: str) -> tuple[str, str]:
    if reentry_state == "weekly_scan" and surface_state == "weekly_scan":
        return (
            "Your weekly check-in window is open.",
            "Open your journey, compare the latest proof, and run the next check-in while the change is still fresh.",
        )
    if reentry_state == "weekly_scan" and surface_state == "progress_proof":
        return (
            "Your next weekly check-in needs one more proof photo first.",
            "Start with an upload-first proof handoff now so your next compare is grounded in real evidence, not just scan history.",
        )
    return (
        "You already have scan data. Now lock it with proof.",
        "Upload one progress photo so this week is grounded in something you can compare later, not just a number.",
    )


def _build_weekly_proof_candidate(
    *,
    profile: Dict[str, Any],
    prefs: Dict[str, Any],
    summary: Any,
    last_event: Dict[str, Any] | None,
    now: datetime,
) -> Dict[str, Any] | None:
    if not profile.get("user_id") or not profile.get("email"):
        return None

    if profile.get("deleted_at") or profile.get("blocked_at") or profile.get("disabled_at"):
        return None

    if not profile.get("onboarding_completed", True):
        return None

    if not prefs.get("email_weekly_summary", True):
        return None

    entry_state = getattr(summary, "entry_state", None)
    if entry_state not in WEEKLY_PROOF_ELIGIBLE_STATES:
        return None

    scan_summary = getattr(summary, "scan_summary", None)
    if not scan_summary or getattr(scan_summary, "scan_count", 0) <= 0:
        return None

    last_status = ((last_event or {}).get("status") or "").lower()
    last_touch = (
        _parse_iso_datetime((last_event or {}).get("sent_at"))
        or _parse_iso_datetime((last_event or {}).get("created_at"))
    )
    if last_status in WEEKLY_PROOF_NON_DELIVERABLE_STATUSES:
        return None
    if (
        last_status in WEEKLY_PROOF_COOLDOWN_STATUSES
        and last_touch
        and now - last_touch < timedelta(hours=settings.weekly_proof_reminder_cooldown_hours)
    ):
        return None

    progress_summary = getattr(summary, "progress_summary", None)
    proof_photo_count = int(getattr(progress_summary, "photo_count", 0) or 0)
    surface_state = resolve_surface_state(
        source=WEEKLY_REMINDER_SOURCE,
        reentry_state=entry_state,
        proof_photo_count=proof_photo_count,
        enabled=settings.weekly_scan_upload_first_handoff_enabled,
    )
    next_path = build_weekly_proof_reminder_path(
        entry_state,
        progress_photo_count=proof_photo_count,
    )
    headline, body = _build_weekly_proof_copy(entry_state, surface_state)
    return {
        "user_id": profile["user_id"],
        "email": profile["email"],
        "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
        "entry_state": entry_state,
        "reentry_state": entry_state,
        "surface_state": surface_state,
        "proof_photo_count": proof_photo_count,
        "next_path": next_path,
        "subject": _build_weekly_proof_subject(entry_state, surface_state),
        "headline": headline,
        "body": body,
    }


def _send_email_message(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


async def _send_weekly_proof_email(candidate: Dict[str, Any], reminder_event_id: str) -> str:
    tracking_url = build_weekly_proof_tracking_url(reminder_event_id, candidate["next_path"])
    unsubscribe_url = build_weekly_proof_unsubscribe_url(reminder_event_id)
    message = EmailMessage()
    message["To"] = candidate["email"]
    message["From"] = settings.smtp_from_email
    message["Subject"] = candidate["subject"]
    message["Message-ID"] = make_msgid("denevira")
    message["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    message["X-Denevira-Reminder-Id"] = reminder_event_id
    message["Auto-Submitted"] = "auto-generated"

    text_body = (
        f"{candidate['headline']}\n\n"
        f"{candidate['body']}\n\n"
        f"Open Denevira: {tracking_url}\n"
        f"Unsubscribe from weekly proof reminders: {unsubscribe_url}\n"
    )
    html_body = (
        f"<p>{candidate['headline']}</p>"
        f"<p>{candidate['body']}</p>"
        f"<p><a href=\"{tracking_url}\">Open Denevira</a></p>"
        f"<p style=\"font-size:12px;color:#666;\">"
        f"<a href=\"{unsubscribe_url}\">Unsubscribe from weekly proof reminders</a>"
        f"</p>"
    )
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    await asyncio.to_thread(_send_email_message, message)
    return str(message["Message-ID"])


def _list_candidate_profiles() -> List[Dict[str, Any]]:
    supabase = get_supabase()
    result = (
        supabase.table("user_profiles")
        .select("user_id, email, onboarding_completed")
        .execute()
    )
    return result.data or []


def _get_latest_weekly_reminder_event(user_id: str) -> Dict[str, Any] | None:
    supabase = get_supabase()
    result = (
        supabase.table("reminder_events")
        .select("id, sent_at, created_at, status, opened_at, recipient_email, provider_email_id")
        .eq("user_id", user_id)
        .eq("channel", WEEKLY_PROOF_REMINDER_CHANNEL)
        .eq("reminder_type", WEEKLY_PROOF_REMINDER_TYPE)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _build_job_key(now: datetime) -> str:
    interval_minutes = max(5, settings.weekly_proof_reminder_job_interval_minutes)
    bucket = int(now.timestamp() // (interval_minutes * 60))
    return f"{WEEKLY_PROOF_REMINDER_TYPE}:{bucket}"


def _is_unique_violation(exc: Exception) -> bool:
    message = str(exc).lower()
    return "duplicate key" in message or "23505" in message


def _claim_weekly_proof_job_run(job_key: str, now: datetime) -> Dict[str, Any] | None:
    supabase = get_supabase()
    payload = {
        "job_key": job_key,
        "job_name": WEEKLY_PROOF_REMINDER_TYPE,
        "status": "running",
        "started_at": now.isoformat(),
        "completed_at": None,
        "lease_owner": str(uuid4()),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    try:
        result = supabase.table("reminder_job_runs").insert(payload).execute()
    except Exception as exc:
        if _is_unique_violation(exc):
            return None
        raise
    return result.data[0] if result.data else payload


def _finish_weekly_proof_job_run(job_key: str, updates: Dict[str, Any]) -> None:
    supabase = get_supabase()
    payload = {**updates, "updated_at": _utcnow().isoformat()}
    supabase.table("reminder_job_runs").update(payload).eq("job_key", job_key).execute()


def _create_reminder_event(candidate: Dict[str, Any], job_key: str) -> Dict[str, Any]:
    supabase = get_supabase()
    now = _utcnow().isoformat()
    payload = {
        "id": str(uuid4()),
        "user_id": candidate["user_id"],
        "recipient_email": candidate["email"],
        "channel": candidate["channel"],
        "reminder_type": WEEKLY_PROOF_REMINDER_TYPE,
        "entry_state": candidate["entry_state"],
        "deep_link": candidate["next_path"],
        "job_key": job_key,
        "status": "queued",
        "provider_message_id": None,
        "sent_at": None,
        "opened_at": None,
        "created_at": now,
        "updated_at": now,
    }
    result = supabase.table("reminder_events").insert(payload).execute()
    return result.data[0] if result.data else payload


def _update_reminder_event(reminder_event_id: str, updates: Dict[str, Any]) -> None:
    supabase = get_supabase()
    payload = {
        **updates,
        "updated_at": _utcnow().isoformat(),
    }
    supabase.table("reminder_events").update(payload).eq("id", reminder_event_id).execute()


def _is_valid_uuid(value: str) -> bool:
    try:
        UUID(str(value))
        return True
    except (TypeError, ValueError):
        return False


def _get_reminder_event(reminder_event_id: str) -> Dict[str, Any] | None:
    if not _is_valid_uuid(reminder_event_id):
        return None
    supabase = get_supabase()
    result = (
        supabase.table("reminder_events")
        .select("*")
        .eq("id", reminder_event_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _get_latest_weekly_reminder_event_by_email(recipient_email: str) -> Dict[str, Any] | None:
    supabase = get_supabase()
    result = (
        supabase.table("reminder_events")
        .select("*")
        .eq("channel", WEEKLY_PROOF_REMINDER_CHANNEL)
        .eq("reminder_type", WEEKLY_PROOF_REMINDER_TYPE)
        .eq("recipient_email", recipient_email)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _get_weekly_reminder_event_by_provider_email_id(provider_email_id: str) -> Dict[str, Any] | None:
    supabase = get_supabase()
    result = (
        supabase.table("reminder_events")
        .select("*")
        .eq("channel", WEEKLY_PROOF_REMINDER_CHANNEL)
        .eq("reminder_type", WEEKLY_PROOF_REMINDER_TYPE)
        .eq("provider_email_id", provider_email_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _record_reminder_webhook_event(
    *,
    svix_id: str,
    event_type: str,
    payload: Dict[str, Any],
    recipient_email: str | None,
    provider_email_id: str | None,
) -> Dict[str, Any] | None:
    supabase = get_supabase()
    record = {
        "svix_id": svix_id,
        "event_type": event_type,
        "recipient_email": recipient_email,
        "provider_email_id": provider_email_id,
        "processing_status": "processing",
        "payload": payload,
        "last_error": None,
        "created_at": _utcnow().isoformat(),
        "processed_at": None,
    }
    try:
        result = supabase.table("reminder_webhook_events").insert(record).execute()
    except Exception as exc:
        if _is_unique_violation(exc):
            return None
        raise
    return result.data[0] if result.data else record


def _update_reminder_webhook_event(svix_id: str, updates: Dict[str, Any]) -> None:
    supabase = get_supabase()
    supabase.table("reminder_webhook_events").update(updates).eq("svix_id", svix_id).execute()


def _normalize_email_address(value: Any) -> str | None:
    if isinstance(value, list):
        value = value[0] if value else None
    if not value:
        return None
    if isinstance(value, dict):
        value = value.get("email") or value.get("address")
    _, parsed = parseaddr(str(value))
    normalized = parsed.strip().lower()
    return normalized or None


def _extract_provider_email_id(payload: Dict[str, Any]) -> str | None:
    data = payload.get("data") or {}
    return data.get("email_id") or data.get("id") or payload.get("email_id")


def _extract_recipient_email(payload: Dict[str, Any]) -> str | None:
    data = payload.get("data") or {}
    return (
        _normalize_email_address(data.get("to"))
        or _normalize_email_address(data.get("email"))
        or _normalize_email_address(payload.get("to"))
    )


def _extract_webhook_timestamp(payload: Dict[str, Any]) -> str:
    data = payload.get("data") or {}
    for key in ("created_at", "updated_at", "timestamp"):
        if payload.get(key):
            return str(payload[key])
        if data.get(key):
            return str(data[key])
    return _utcnow().isoformat()


def _resolve_reminder_event_for_webhook(
    *,
    recipient_email: str | None,
    provider_email_id: str | None,
) -> Dict[str, Any] | None:
    if provider_email_id:
        reminder_event = _get_weekly_reminder_event_by_provider_email_id(provider_email_id)
        if reminder_event:
            return reminder_event
    if recipient_email:
        return _get_latest_weekly_reminder_event_by_email(recipient_email)
    return None


def _find_user_id_by_email(email: str | None) -> str | None:
    if not email:
        return None
    supabase = get_supabase()
    result = (
        supabase.table("user_profiles")
        .select("user_id")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None
    return result.data[0].get("user_id")


async def _disable_weekly_proof_reminders_for_user(user_id: str) -> None:
    await update_notification_preferences(
        user_id,
        {
            "email_weekly_summary": False,
            "email_inactivity_reminder": False,
            "email_credit_low": False,
        },
    )


def _build_provider_transition_updates(
    *,
    current_event: Dict[str, Any],
    event_type: str,
    payload: Dict[str, Any],
    recipient_email: str | None,
    provider_email_id: str | None,
) -> Dict[str, Any]:
    timestamp = _extract_webhook_timestamp(payload)
    current_status = (current_event.get("status") or "").lower()
    updates: Dict[str, Any] = {
        "last_provider_event_type": event_type,
    }
    if recipient_email:
        updates["recipient_email"] = recipient_email
    if provider_email_id:
        updates["provider_email_id"] = provider_email_id

    if event_type == "email.sent":
        updates["status"] = "sent"
        updates["sent_at"] = current_event.get("sent_at") or timestamp
    elif event_type == "email.delivered":
        updates["status"] = "delivered" if current_status not in {"opened", "clicked"} else current_status
        updates["delivered_at"] = timestamp
    elif event_type == "email.delivery_delayed":
        updates["status"] = current_status or "sent"
        updates["last_error"] = "delivery_delayed"
    elif event_type == "email.bounced":
        updates["status"] = "bounced"
        updates["bounced_at"] = timestamp
        updates["last_error"] = (payload.get("data") or {}).get("message") or "bounced"
    elif event_type == "email.failed":
        updates["status"] = "failed"
        updates["failed_at"] = timestamp
        updates["last_error"] = (payload.get("data") or {}).get("message") or "failed"
    elif event_type == "email.suppressed":
        updates["status"] = "suppressed"
        updates["suppressed_at"] = timestamp
        updates["last_error"] = (payload.get("data") or {}).get("message") or "suppressed"
    elif event_type == "email.opened":
        updates["status"] = "opened" if current_status != "clicked" else current_status
        updates["opened_at"] = current_event.get("opened_at") or timestamp
    elif event_type == "email.clicked":
        updates["status"] = "clicked"
        updates["clicked_at"] = timestamp
        updates["opened_at"] = current_event.get("opened_at") or timestamp
    elif event_type == "email.complained":
        updates["status"] = "complained"
        updates["complained_at"] = timestamp
        updates["last_error"] = "complained"
    elif event_type == "contact.updated" and (payload.get("data") or {}).get("unsubscribed"):
        updates["status"] = "unsubscribed"
        updates["unsubscribed_at"] = timestamp
        updates["last_error"] = "provider_unsubscribed"

    return updates


def verify_resend_webhook(payload: str, headers: Mapping[str, str]) -> Dict[str, Any]:
    header_id = (
        headers.get("svix-id")
        or headers.get("webhook-id")
        or headers.get("id")
        or ""
    )
    header_timestamp = (
        headers.get("svix-timestamp")
        or headers.get("webhook-timestamp")
        or headers.get("timestamp")
        or ""
    )
    header_signature = (
        headers.get("svix-signature")
        or headers.get("webhook-signature")
        or headers.get("signature")
        or ""
    )
    svix_headers = {
        "svix-id": header_id,
        "svix-timestamp": header_timestamp,
        "svix-signature": header_signature,
    }
    try:
        if not all(svix_headers.values()):
            raise ValueError("Missing required headers")

        try:
            timestamp = datetime.fromtimestamp(float(header_timestamp), tz=timezone.utc)
        except Exception as exc:
            raise ValueError("Invalid Signature Headers") from exc

        tolerance = timedelta(minutes=5)
        now = datetime.now(tz=timezone.utc)
        if timestamp < (now - tolerance):
            raise ValueError("Message timestamp too old")
        if timestamp > (now + tolerance):
            raise ValueError("Message timestamp too new")

        secret = settings.resend_webhook_secret or ""
        if secret.startswith("whsec_"):
            secret = secret[len("whsec_"):]
        if not secret:
            raise ValueError("Webhook secret is empty")

        secret_bytes = base64.b64decode(secret)
        timestamp_str = str(floor(timestamp.replace(tzinfo=timezone.utc).timestamp()))
        to_sign = f"{header_id}.{timestamp_str}.{payload}".encode("utf-8")
        expected_sig = hmac.new(secret_bytes, to_sign, hashlib.sha256).digest()

        verified = None
        for versioned_sig in header_signature.split(" "):
            try:
                version, signature = versioned_sig.split(",", 1)
            except ValueError:
                continue
            if version != "v1":
                continue
            try:
                sig_bytes = base64.b64decode(signature)
            except Exception:
                continue
            if hmac.compare_digest(expected_sig, sig_bytes):
                verified = json.loads(payload)
                break

        if verified is None:
            raise ValueError("No matching signature found")
    except Exception as exc:
        logger.warning(
            "Resend webhook verification failed: error=%s headers_present=%s header_sources=%s payload_len=%s secret_len=%s",
            str(exc),
            {
                "svix-id": bool(svix_headers["svix-id"]),
                "svix-timestamp": bool(svix_headers["svix-timestamp"]),
                "svix-signature": bool(svix_headers["svix-signature"]),
            },
            {
                "id": "svix-id" if headers.get("svix-id") else "webhook-id" if headers.get("webhook-id") else "id" if headers.get("id") else "missing",
                "timestamp": "svix-timestamp" if headers.get("svix-timestamp") else "webhook-timestamp" if headers.get("webhook-timestamp") else "timestamp" if headers.get("timestamp") else "missing",
                "signature": "svix-signature" if headers.get("svix-signature") else "webhook-signature" if headers.get("webhook-signature") else "signature" if headers.get("signature") else "missing",
            },
            len(payload),
            len(settings.resend_webhook_secret or ""),
        )
        raise
    return verified


async def process_resend_webhook(payload: str, headers: Mapping[str, str]) -> Dict[str, Any]:
    try:
        verified = verify_resend_webhook(payload, headers)
    except Exception as exc:
        raise ValueError(f"invalid_webhook_signature:{type(exc).__name__}:{exc}") from exc
    event_type = verified.get("type")
    if event_type not in WEEKLY_PROOF_PROVIDER_EVENTS:
        return {"status": "ignored", "reason": "unsupported_event", "event_type": event_type}

    svix_id = headers.get("svix-id") or str(uuid4())
    recipient_email = _extract_recipient_email(verified)
    provider_email_id = _extract_provider_email_id(verified)
    webhook_event = _record_reminder_webhook_event(
        svix_id=svix_id,
        event_type=event_type,
        payload=verified,
        recipient_email=recipient_email,
        provider_email_id=provider_email_id,
    )
    if webhook_event is None:
        return {"status": "duplicate", "event_type": event_type}

    reminder_event = _resolve_reminder_event_for_webhook(
        recipient_email=recipient_email,
        provider_email_id=provider_email_id,
    )
    user_id = reminder_event.get("user_id") if reminder_event else _find_user_id_by_email(recipient_email)

    try:
        if reminder_event:
            updates = _build_provider_transition_updates(
                current_event=reminder_event,
                event_type=event_type,
                payload=verified,
                recipient_email=recipient_email,
                provider_email_id=provider_email_id,
            )
            if updates:
                _update_reminder_event(reminder_event["id"], updates)

        if user_id and (
            event_type == "email.complained"
            or event_type == "email.suppressed"
            or (event_type == "contact.updated" and (verified.get("data") or {}).get("unsubscribed"))
        ):
            await _disable_weekly_proof_reminders_for_user(user_id)

        _update_reminder_webhook_event(
            svix_id,
            {
                "processing_status": "processed",
                "processed_at": _utcnow().isoformat(),
                "reminder_event_id": reminder_event.get("id") if reminder_event else None,
            },
        )
        return {
            "status": "processed",
            "event_type": event_type,
            "reminder_event_id": reminder_event.get("id") if reminder_event else None,
        }
    except Exception as exc:
        _update_reminder_webhook_event(
            svix_id,
            {
                "processing_status": "failed",
                "last_error": str(exc),
                "processed_at": _utcnow().isoformat(),
                "reminder_event_id": reminder_event.get("id") if reminder_event else None,
            },
        )
        raise


async def unsubscribe_weekly_proof_reminder(reminder_event_id: str) -> Dict[str, Any]:
    event = _get_reminder_event(reminder_event_id)
    if not event:
        return {"status": "not_found"}

    updates = {
        "status": "unsubscribed",
        "unsubscribed_at": _utcnow().isoformat(),
        "last_error": "user_unsubscribed",
    }
    if not event.get("opened_at"):
        updates["opened_at"] = _utcnow().isoformat()
    _update_reminder_event(reminder_event_id, updates)
    await _disable_weekly_proof_reminders_for_user(event["user_id"])
    return {"status": "unsubscribed", "user_id": event["user_id"]}


async def _get_home_summary_for_user(user_id: str):
    from ..routers.home import get_home_summary

    return await get_home_summary({"id": user_id})


async def evaluate_weekly_proof_reminder_candidates(now: datetime | None = None) -> List[Dict[str, Any]]:
    reminder_status = get_weekly_proof_reminder_status()
    if not reminder_status["active"]:
        return []

    current_time = now or _utcnow()
    candidates: List[Dict[str, Any]] = []
    for profile in _list_candidate_profiles():
        try:
            prefs = await get_notification_preferences(profile["user_id"])
            summary = await _get_home_summary_for_user(profile["user_id"])
            last_event = _get_latest_weekly_reminder_event(profile["user_id"])
            candidate = _build_weekly_proof_candidate(
                profile=profile,
                prefs=prefs,
                summary=summary,
                last_event=last_event,
                now=current_time,
            )
            if candidate:
                candidates.append(candidate)
        except Exception as exc:
            logger.error("Failed to evaluate weekly proof reminder candidate %s: %s", profile.get("user_id"), exc)
    return candidates


async def run_weekly_proof_reminder_job(now: datetime | None = None) -> Dict[str, Any]:
    reminder_status = get_weekly_proof_reminder_status()
    if not reminder_status["active"]:
        logger.info("Weekly proof reminder job inactive: %s", reminder_status["reason"])
        return {"active": False, "reason": reminder_status["reason"], "sent": 0, "failed": 0}

    current_time = now or _utcnow()
    job_key = _build_job_key(current_time)
    job_run = _claim_weekly_proof_job_run(job_key, current_time)
    if job_run is None:
        logger.info("Weekly proof reminder job skipped; already claimed for %s", job_key)
        return {
            "active": True,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "sent": 0,
            "failed": 0,
            "evaluated": 0,
            "skipped": True,
            "reason": "job_already_claimed",
        }

    sent = 0
    failed = 0
    candidates: List[Dict[str, Any]] = []
    try:
        candidates = await evaluate_weekly_proof_reminder_candidates(now=current_time)
        for candidate in candidates:
            reminder_event = _create_reminder_event(candidate, job_key)
            try:
                _update_reminder_event(reminder_event["id"], {"status": "sending"})
                provider_message_id = await _send_weekly_proof_email(candidate, reminder_event["id"])
                _update_reminder_event(
                    reminder_event["id"],
                    {
                        "status": "sent",
                        "provider_message_id": provider_message_id,
                        "sent_at": current_time.isoformat(),
                        "recipient_email": candidate["email"],
                        "last_provider_event_type": "email.sent",
                    },
                )
                try:
                    await send_push_notification(
                        candidate["user_id"],
                        candidate["subject"],
                        candidate["body"],
                        {"action": "weekly_proof", "path": candidate["next_path"]},
                    )
                except Exception as push_exc:
                    logger.warning("Push notification failed for %s: %s", candidate["user_id"], push_exc)
                await log_retention_event(
                    candidate["user_id"],
                    "notification_sent",
                    "weekly_proof_reminder_email",
                    {
                        "channel": candidate["channel"],
                        "entry_state": candidate["reentry_state"],
                        "reentry_state": candidate["reentry_state"],
                        "surface_state": candidate["surface_state"],
                        "reminder_event_id": reminder_event["id"],
                        "source": WEEKLY_REMINDER_SOURCE,
                        "event_origin": "live",
                        "proof_photo_count": candidate["proof_photo_count"],
                    },
                )
                sent += 1
            except Exception as exc:
                failed += 1
                _update_reminder_event(
                    reminder_event["id"],
                    {
                        "status": "failed",
                        "failed_at": _utcnow().isoformat(),
                        "last_error": str(exc),
                    },
                )
                logger.error("Failed to send weekly proof reminder to %s: %s", candidate["user_id"], exc)
        _finish_weekly_proof_job_run(
            job_key,
            {
                "status": "completed" if failed == 0 else "completed_with_failures",
                "completed_at": _utcnow().isoformat(),
            },
        )
        return {
            "active": True,
            "channel": WEEKLY_PROOF_REMINDER_CHANNEL,
            "sent": sent,
            "failed": failed,
            "evaluated": len(candidates),
        }
    except Exception:
        _finish_weekly_proof_job_run(
            job_key,
            {
                "status": "failed",
                "completed_at": _utcnow().isoformat(),
            },
        )
        raise


async def run_weekly_proof_reminder_scheduler() -> None:
    interval_seconds = max(300, settings.weekly_proof_reminder_job_interval_minutes * 60)
    while True:
        try:
            await run_weekly_proof_reminder_job()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Weekly proof reminder scheduler error: %s", exc, exc_info=True)
        await asyncio.sleep(interval_seconds)


async def mark_weekly_proof_reminder_opened(reminder_event_id: str, next_path: str | None) -> str:
    safe_path = _sanitize_frontend_path(next_path)
    event = _get_reminder_event(reminder_event_id)
    if not event:
        raise LookupError("Reminder link is invalid or expired")
    surface_state = extract_query_param(safe_path, "surface_state")
    reentry_state = extract_query_param(safe_path, "reentry_state")
    opened_at = _utcnow().isoformat()
    _update_reminder_event(
        reminder_event_id,
        {
            "status": "clicked",
            "opened_at": event.get("opened_at") or opened_at,
            "clicked_at": event.get("clicked_at") or opened_at,
        },
    )
    await log_retention_event(
        event["user_id"],
        "notification_opened",
        "weekly_proof_reminder_email",
        {
            "channel": event.get("channel", WEEKLY_PROOF_REMINDER_CHANNEL),
            "entry_state": event.get("entry_state"),
            "reentry_state": reentry_state or event.get("entry_state"),
            "surface_state": surface_state or event.get("entry_state"),
            "reminder_event_id": reminder_event_id,
            "source": WEEKLY_REMINDER_SOURCE,
        },
    )
    annotated_path = append_query_params_to_path(
        safe_path,
        {"reminder_event_id": reminder_event_id},
    )
    return f"{settings.public_app_url.rstrip('/')}{annotated_path}"
