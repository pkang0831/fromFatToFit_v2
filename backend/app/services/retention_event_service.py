import json
import logging
from datetime import datetime, timezone
from typing import Any

from ..database import get_supabase

logger = logging.getLogger(__name__)
FUNNEL_EVENTS_TABLE = "funnel_events"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _sanitize_properties(properties: dict[str, Any] | None) -> dict[str, Any]:
    return json.loads(json.dumps(properties or {}, default=str))


def _find_existing_deduped_event(
    user_id: str | None,
    event_name: str,
    dedupe_key: str | None,
) -> dict[str, Any] | None:
    if not user_id or not dedupe_key:
        return None

    result = (
        get_supabase()
        .table(FUNNEL_EVENTS_TABLE)
        .select("*")
        .eq("user_id", user_id)
        .eq("event_name", event_name)
        .contains("properties", {"dedupe_key": dedupe_key})
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def _extract_source(properties: dict[str, Any]) -> str | None:
    return _coerce_string(
        properties.get("source")
        or properties.get("ref")
        or properties.get("attribution_source")
    )


def _extract_share_token(properties: dict[str, Any]) -> str | None:
    return _coerce_string(
        properties.get("share_token")
        or properties.get("share")
        or properties.get("source_token")
        or properties.get("attribution_token")
    )


def _extract_reentry_state(properties: dict[str, Any]) -> str | None:
    return _coerce_string(
        properties.get("reentry_state")
        or properties.get("entry_state")
    )


def _extract_surface_state(properties: dict[str, Any]) -> str | None:
    return _coerce_string(
        properties.get("surface_state")
        or properties.get("entry_state")
        or properties.get("reentry_state")
    )


def list_funnel_view_rows(
    view_name: str,
    *,
    order_by: str | None = None,
    desc: bool = True,
) -> list[dict[str, Any]]:
    supabase = get_supabase()
    query = supabase.table(view_name).select("*")
    if order_by:
        query = query.order(order_by, desc=desc)
    result = query.execute()
    return result.data or []


async def log_retention_event(
    user_id: str | None,
    event_name: str,
    surface: str,
    properties: dict[str, Any] | None = None,
) -> dict[str, Any]:
    normalized_properties = _sanitize_properties(properties)
    dedupe_key = _coerce_string(normalized_properties.get("dedupe_key"))
    existing_event = None

    try:
        existing_event = _find_existing_deduped_event(user_id, event_name, dedupe_key)
    except Exception as exc:
        logger.error(
            "Failed to check funnel event dedupe for %s/%s: %s",
            event_name,
            user_id,
            exc,
        )

    if existing_event:
        logger.info("retention_event_deduped=%s", json.dumps(existing_event, sort_keys=True, default=str))
        return existing_event

    event = {
        "timestamp": _utcnow().isoformat(),
        "user_id": user_id,
        "event_name": event_name,
        "surface": surface,
        "source": _extract_source(normalized_properties),
        "entry_state": _extract_reentry_state(normalized_properties),
        "reentry_state": _extract_reentry_state(normalized_properties),
        "surface_state": _extract_surface_state(normalized_properties),
        "event_origin": _coerce_string(normalized_properties.get("event_origin")),
        "session_id": _coerce_string(normalized_properties.get("session_id")),
        "reminder_event_id": _coerce_string(normalized_properties.get("reminder_event_id")),
        "share_id": _coerce_string(normalized_properties.get("share_id")),
        "share_token": _extract_share_token(normalized_properties),
        "properties": normalized_properties,
    }
    try:
        get_supabase().table(FUNNEL_EVENTS_TABLE).insert({
            "user_id": user_id,
            "event_name": event_name,
            "surface": surface,
            "source": event["source"],
            "entry_state": event["entry_state"],
            "reentry_state": event["reentry_state"],
            "surface_state": event["surface_state"],
            "event_origin": event["event_origin"],
            "session_id": event["session_id"],
            "reminder_event_id": event["reminder_event_id"],
            "share_id": event["share_id"],
            "share_token": event["share_token"],
            "properties": normalized_properties,
            "event_at": event["timestamp"],
            "created_at": event["timestamp"],
        }).execute()
    except Exception as exc:
        logger.error(
            "Failed to persist funnel event %s for user %s: %s",
            event_name,
            user_id,
            exc,
        )
    logger.info("retention_event=%s", json.dumps(event, sort_keys=True, default=str))
    return event
