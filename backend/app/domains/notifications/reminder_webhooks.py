"""Resend delivery webhooks for weekly proof reminder emails."""
import logging
import json
import hmac
import hashlib
import base64
from typing import Dict, Any, Mapping
from datetime import datetime, timezone, timedelta
from math import floor
from email.utils import parseaddr
from uuid import uuid4
from app.core.database import get_supabase
from app.core.config import settings
from app.domains.notifications.reminders import (
    WEEKLY_PROOF_REMINDER_CHANNEL,
    WEEKLY_PROOF_REMINDER_TYPE,
    _disable_weekly_proof_reminders_for_user,
    _is_unique_violation,
    _update_reminder_event,
    _utcnow,
)

logger = logging.getLogger(__name__)

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
