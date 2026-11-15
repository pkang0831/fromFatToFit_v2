"""Per-user notification preferences (current and legacy table shapes)."""
import logging
from typing import Dict, Any
from datetime import datetime, timezone
from app.core.database import get_supabase

logger = logging.getLogger(__name__)

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
    now = datetime.now(timezone.utc).isoformat()
    return {
        "user_id": user_id,
        **DEFAULT_PREFERENCES,
        "created_at": now,
        "updated_at": now,
    }


def _build_legacy_preferences_record(user_id: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
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
    filtered["updated_at"] = datetime.now(timezone.utc).isoformat()

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
