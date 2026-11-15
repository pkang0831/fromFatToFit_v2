"""Web Push subscriptions and VAPID delivery."""
import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.core.database import get_supabase, get_user_supabase
from app.core.config import settings

logger = logging.getLogger(__name__)

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
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", existing.data[0]["id"]).execute()
    else:
        supabase.table("push_subscriptions").insert({
            "user_id": user_id,
            "endpoint": endpoint,
            "subscription_data": json.dumps(subscription),
            "active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
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
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("user_id", user_id).eq("endpoint", endpoint).execute()

    return {"status": "unsubscribed"}


async def get_push_subscriptions(user_id: str, access_token: str | None = None) -> List[Dict[str, Any]]:
    supabase = get_user_supabase(access_token) if access_token else get_supabase()
    result = supabase.table("push_subscriptions").select("*").eq("user_id", user_id).eq("active", True).execute()
    return result.data or []


def _vapid_ready() -> bool:
    return bool(settings.vapid_private_key and settings.vapid_public_key)


def _send_webpush(sub_data: Dict[str, Any], payload_str: str) -> None:
    from pywebpush import webpush  # type: ignore[import]

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
