import logging
from datetime import datetime, timezone
from typing import Any, Dict

import stripe

from ..config import settings
from ..database import get_supabase
from .retention_event_service import log_retention_event

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


CREDIT_PACK_PRICES = {
    50: 499,   # $4.99
    100: 899,  # $8.99
    200: 1599, # $15.99
}

ENTITLED_SUBSCRIPTION_STATUSES = {"active", "trialing", "past_due"}
DELETION_BLOCKING_STATUSES = {"active", "trialing", "past_due", "unpaid", "incomplete"}
TERMINAL_SUBSCRIPTION_STATUSES = {"canceled", "expired", "incomplete_expired"}

ACTIVE_BILLING_BLOCK_REASON = "active_billing_requires_cancellation"
UNRESOLVED_BILLING_BLOCK_REASON = "unresolved_billing_requires_resolution"
MISMATCH_BLOCK_REASON = "billing_state_mismatch_requires_reconciliation"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _now().isoformat()


def _normalize_status(status: Any) -> str:
    if not status:
        return "none"

    normalized = str(status).strip().lower()
    if normalized == "cancelled":
        return "canceled"
    return normalized


def _stripe_timestamp_to_iso(timestamp: Any) -> str | None:
    if not timestamp:
        return None

    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc).isoformat()


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    return None


def _get_primary_row(rows: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    if rows:
        return rows[0]
    return None


def _subscription_is_entitled(subscription: dict[str, Any], now: datetime | None = None) -> bool:
    status = _normalize_status(subscription.get("status"))
    if status not in ENTITLED_SUBSCRIPTION_STATUSES:
        return False

    end_date = _parse_datetime(subscription.get("end_date"))
    if end_date and end_date <= (now or _now()) and status != "past_due":
        return False

    return True


def _subscription_blocks_deletion(subscription: dict[str, Any], now: datetime | None = None) -> bool:
    status = _normalize_status(subscription.get("status"))
    if status not in DELETION_BLOCKING_STATUSES:
        return False

    if status in {"active", "trialing"} and not subscription.get("auto_renew", True):
        return False

    end_date = _parse_datetime(subscription.get("end_date"))
    if status in {"active", "trialing"} and end_date and end_date <= (now or _now()):
        return False

    return True


def _block_reason_for_subscription(subscription: dict[str, Any]) -> str | None:
    if not _subscription_blocks_deletion(subscription):
        return None

    status = _normalize_status(subscription.get("status"))
    if status in {"past_due", "unpaid", "incomplete"}:
        return UNRESOLVED_BILLING_BLOCK_REASON

    return ACTIVE_BILLING_BLOCK_REASON


def _subscription_score(subscription: dict[str, Any], now: datetime | None = None) -> tuple[int, float, float]:
    reference = now or _now()
    end_date = _parse_datetime(subscription.get("end_date")) or reference
    updated_at = _parse_datetime(subscription.get("updated_at")) or _parse_datetime(subscription.get("start_date")) or reference

    if _subscription_blocks_deletion(subscription, reference):
        status_rank = 3
    elif _subscription_is_entitled(subscription, reference):
        status_rank = 2
    elif _normalize_status(subscription.get("status")) in TERMINAL_SUBSCRIPTION_STATUSES:
        status_rank = 0
    else:
        status_rank = 1

    return status_rank, end_date.timestamp(), updated_at.timestamp()


def _pick_canonical_subscription(subscriptions: list[dict[str, Any]], now: datetime | None = None) -> dict[str, Any] | None:
    if not subscriptions:
        return None

    return max(subscriptions, key=lambda subscription: _subscription_score(subscription, now))


def _derive_subscription_diagnostics(
    profile: dict[str, Any] | None,
    subscriptions: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    profile = profile or {}
    reference = now or _now()
    canonical = _pick_canonical_subscription(subscriptions, reference)
    stripe_customer_id = profile.get("stripe_customer_id") or (canonical or {}).get("stripe_customer_id")

    diagnostics: dict[str, Any] = {
        "subscription_id": None,
        "user_id": profile.get("user_id"),
        "subscription_type": "free",
        "status": "none",
        "start_date": None,
        "end_date": None,
        "payment_provider": None,
        "auto_renew": False,
        "premium_status": False,
        "deletion_blocked": False,
        "deletion_block_reason": None,
        "billing_portal_available": bool(stripe_customer_id),
        "stripe_customer_id": stripe_customer_id,
        "profile_premium_status": bool(profile.get("premium_status")),
        "entitlement_source": "none",
        "cancel_at_period_end": False,
        "last_stripe_event_id": None,
        "last_stripe_event_type": None,
        "last_webhook_processed_at": None,
        "should_sync_profile": True,
    }

    if canonical:
        diagnostics.update({
            "subscription_id": canonical.get("subscription_id"),
            "user_id": canonical.get("user_id") or diagnostics["user_id"],
            "subscription_type": canonical.get("subscription_type") or "premium",
            "status": _normalize_status(canonical.get("status")),
            "start_date": canonical.get("start_date"),
            "end_date": canonical.get("end_date"),
            "payment_provider": canonical.get("payment_provider"),
            "auto_renew": bool(canonical.get("auto_renew", True)),
            "premium_status": _subscription_is_entitled(canonical, reference),
            "deletion_blocked": _subscription_blocks_deletion(canonical, reference),
            "deletion_block_reason": _block_reason_for_subscription(canonical),
            "entitlement_source": "subscription_record",
            "cancel_at_period_end": bool(canonical.get("cancel_at_period_end", False)),
            "last_stripe_event_id": canonical.get("last_stripe_event_id"),
            "last_stripe_event_type": canonical.get("last_stripe_event_type"),
            "last_webhook_processed_at": canonical.get("last_webhook_processed_at"),
        })
        return diagnostics

    if diagnostics["profile_premium_status"]:
        diagnostics.update({
            "subscription_type": "premium",
            "status": "mismatch",
            "premium_status": True,
            "deletion_blocked": True,
            "deletion_block_reason": MISMATCH_BLOCK_REASON,
            "entitlement_source": "profile_fallback_mismatch",
            "should_sync_profile": False,
        })

    return diagnostics


def _get_user_profile(supabase: Any, user_id: str) -> dict[str, Any]:
    result = (
        supabase.table("user_profiles")
        .select("user_id, email, full_name, premium_status, stripe_customer_id")
        .eq("user_id", user_id)
        .execute()
    )
    return _get_primary_row(result.data) or {"user_id": user_id, "premium_status": False}


def _get_user_subscriptions(supabase: Any, user_id: str) -> list[dict[str, Any]]:
    result = (
        supabase.table("user_subscriptions")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    return result.data or []


def _sync_profile_subscription_state(supabase: Any, user_id: str, profile: dict[str, Any], diagnostics: dict[str, Any]) -> None:
    if not diagnostics.get("should_sync_profile", True):
        return

    updates: dict[str, Any] = {}
    if bool(profile.get("premium_status")) != bool(diagnostics["premium_status"]):
        updates["premium_status"] = bool(diagnostics["premium_status"])

    if diagnostics.get("stripe_customer_id") and profile.get("stripe_customer_id") != diagnostics["stripe_customer_id"]:
        updates["stripe_customer_id"] = diagnostics["stripe_customer_id"]

    if not updates:
        return

    updates["updated_at"] = _now_iso()
    supabase.table("user_profiles").update(updates).eq("user_id", user_id).execute()


async def get_subscription_diagnostics(user_id: str) -> dict[str, Any]:
    supabase = get_supabase()
    profile = _get_user_profile(supabase, user_id)
    subscriptions = _get_user_subscriptions(supabase, user_id)
    diagnostics = _derive_subscription_diagnostics(profile, subscriptions)
    _sync_profile_subscription_state(supabase, user_id, profile, diagnostics)
    return diagnostics


def _link_stripe_customer_to_user(supabase: Any, user_id: str, stripe_customer_id: str | None) -> None:
    if not stripe_customer_id:
        return

    supabase.table("user_profiles").update({
        "stripe_customer_id": stripe_customer_id,
        "updated_at": _now_iso(),
    }).eq("user_id", user_id).execute()


def _ensure_stripe_customer(user_id: str) -> str:
    supabase = get_supabase()
    profile = _get_user_profile(supabase, user_id)

    existing_customer_id = profile.get("stripe_customer_id")
    if existing_customer_id:
        return existing_customer_id

    customer = stripe.Customer.create(
        email=profile.get("email"),
        name=profile.get("full_name"),
        metadata={"user_id": user_id},
    )
    _link_stripe_customer_to_user(supabase, user_id, customer.id)
    return customer.id


def _resolve_user_id_for_subscription(supabase: Any, subscription_data: dict[str, Any], fallback_user_id: str | None = None) -> str | None:
    if fallback_user_id:
        return fallback_user_id

    metadata = subscription_data.get("metadata") or {}
    if metadata.get("user_id"):
        return metadata["user_id"]

    customer_id = subscription_data.get("customer")
    if customer_id:
        result = (
            supabase.table("user_profiles")
            .select("user_id")
            .eq("stripe_customer_id", customer_id)
            .execute()
        )
        row = _get_primary_row(result.data)
        if row:
            return row["user_id"]

    return None


async def _upsert_subscription_from_stripe(
    subscription_data: dict[str, Any],
    *,
    fallback_user_id: str | None = None,
    event_id: str | None = None,
    event_type: str | None = None,
    event_created: Any = None,
) -> str | None:
    supabase = get_supabase()
    user_id = _resolve_user_id_for_subscription(supabase, subscription_data, fallback_user_id=fallback_user_id)

    if not user_id:
        logger.warning("Unable to reconcile Stripe subscription %s to a Denevira user", subscription_data.get("id"))
        return None

    customer_id = subscription_data.get("customer")
    _link_stripe_customer_to_user(supabase, user_id, customer_id)

    normalized_status = _normalize_status(subscription_data.get("status"))
    cancel_at_period_end = bool(subscription_data.get("cancel_at_period_end", False))

    payload = {
        "user_id": user_id,
        "subscription_id": subscription_data["id"],
        "subscription_type": "premium",
        "status": normalized_status,
        "payment_provider": "stripe",
        "stripe_customer_id": customer_id,
        "start_date": _stripe_timestamp_to_iso(subscription_data.get("start_date")) or _stripe_timestamp_to_iso(subscription_data.get("current_period_start")) or _now_iso(),
        "current_period_start": _stripe_timestamp_to_iso(subscription_data.get("current_period_start")),
        "end_date": _stripe_timestamp_to_iso(subscription_data.get("current_period_end")),
        "auto_renew": not cancel_at_period_end and normalized_status not in TERMINAL_SUBSCRIPTION_STATUSES,
        "cancel_at_period_end": cancel_at_period_end,
        "canceled_at": _stripe_timestamp_to_iso(subscription_data.get("canceled_at")),
        "last_stripe_event_id": event_id,
        "last_stripe_event_type": event_type,
        "last_webhook_processed_at": _stripe_timestamp_to_iso(event_created) or _now_iso(),
        "updated_at": _now_iso(),
    }
    supabase.table("user_subscriptions").upsert(payload, on_conflict="subscription_id").execute()
    await get_subscription_diagnostics(user_id)
    return user_id


async def _upsert_external_subscription(
    *,
    user_id: str,
    provider: str,
    subscription_id: str,
    status: str,
    start_date: str | None,
    end_date: str | None,
    auto_renew: bool,
) -> None:
    supabase = get_supabase()
    payload = {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "subscription_type": "premium",
        "status": _normalize_status(status),
        "payment_provider": provider,
        "start_date": start_date or _now_iso(),
        "end_date": end_date,
        "auto_renew": auto_renew,
        "updated_at": _now_iso(),
    }
    supabase.table("user_subscriptions").upsert(payload, on_conflict="subscription_id").execute()
    await get_subscription_diagnostics(user_id)


def _record_webhook_event(
    supabase: Any,
    *,
    event_id: str,
    event_type: str,
    stripe_customer_id: str | None,
    stripe_subscription_id: str | None,
) -> tuple[bool, dict[str, Any] | None]:
    existing = (
        supabase.table("stripe_webhook_events")
        .select("*")
        .eq("event_id", event_id)
        .execute()
    )
    existing_row = _get_primary_row(existing.data)
    if existing_row and existing_row.get("processing_status") == "processed":
        return False, existing_row

    payload = {
        "event_id": event_id,
        "event_type": event_type,
        "stripe_customer_id": stripe_customer_id,
        "stripe_subscription_id": stripe_subscription_id,
        "processing_status": "processing",
        "error_message": None,
        "processed_at": None,
        "created_at": _now_iso(),
    }
    supabase.table("stripe_webhook_events").upsert(payload, on_conflict="event_id").execute()
    return True, existing_row


def _finalize_webhook_event(supabase: Any, event_id: str, *, processing_status: str, error_message: str | None = None) -> None:
    supabase.table("stripe_webhook_events").update({
        "processing_status": processing_status,
        "error_message": error_message,
        "processed_at": _now_iso() if processing_status == "processed" else None,
    }).eq("event_id", event_id).execute()


async def create_checkout_session(user_id: str, price_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
    try:
        customer_id = _ensure_stripe_customer(user_id)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            customer=customer_id,
            client_reference_id=user_id,
            metadata={'user_id': user_id, 'purchase_type': 'subscription'},
            subscription_data={
                'metadata': {'user_id': user_id},
            },
        )

        return {
            "session_id": session.id,
            "checkout_url": session.url
        }

    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise


async def create_credit_pack_checkout(user_id: str, pack_size: int, success_url: str, cancel_url: str) -> Dict[str, Any]:
    price_cents = CREDIT_PACK_PRICES.get(pack_size)
    if not price_cents:
        raise ValueError(f"Invalid pack size: {pack_size}. Available: {list(CREDIT_PACK_PRICES.keys())}")

    customer_id = _ensure_stripe_customer(user_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'{pack_size} Credit Pack',
                    'description': f'{pack_size} credits for Devenira AI features (never expire)',
                },
                'unit_amount': price_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        customer=customer_id,
        client_reference_id=user_id,
        metadata={
            'user_id': user_id,
            'purchase_type': 'credit_pack',
            'credit_amount': str(pack_size),
        }
    )

    return {
        "session_id": session.id,
        "checkout_url": session.url
    }


async def handle_stripe_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
    """
    Handle Stripe webhook events

    Args:
        payload: Raw webhook payload
        signature: Stripe signature header

    Returns:
        Dictionary with processing result
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, settings.stripe_webhook_secret
        )

        event_id = event["id"]
        event_type = event['type']
        event_data = event['data']['object']
        event_created = event.get("created")

        supabase = get_supabase()
        should_process, existing_row = _record_webhook_event(
            supabase,
            event_id=event_id,
            event_type=event_type,
            stripe_customer_id=event_data.get("customer"),
            stripe_subscription_id=event_data.get("id") if event_type.startswith("customer.subscription") else event_data.get("subscription"),
        )
        if not should_process:
            return {
                "status": "duplicate",
                "event_id": event_id,
                "event_type": event_type,
                "processed_at": existing_row.get("processed_at") if existing_row else None,
            }

        try:
            if event_type == 'checkout.session.completed':
                await handle_checkout_completed(event_data, event_id=event_id, event_created=event_created)
            elif event_type == 'customer.subscription.created':
                await handle_subscription_created(event_data, event_id=event_id, event_created=event_created)
            elif event_type == 'customer.subscription.updated':
                await handle_subscription_updated(event_data, event_id=event_id, event_created=event_created)
            elif event_type == 'customer.subscription.deleted':
                await handle_subscription_deleted(event_data, event_id=event_id, event_created=event_created)

            _finalize_webhook_event(supabase, event_id, processing_status="processed")
        except Exception as handler_error:
            _finalize_webhook_event(supabase, event_id, processing_status="failed", error_message=str(handler_error))
            raise

        return {"status": "processed", "event_id": event_id, "event_type": event_type}

    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        raise


async def handle_checkout_completed(
    session_data: Dict[str, Any],
    *,
    event_id: str | None = None,
    event_created: Any = None,
):
    """Handle successful checkout completion."""
    from .usage_limiter import add_credits, PRO_MONTHLY_CREDITS, FREE_MONTHLY_CREDITS

    user_id = session_data.get('client_reference_id')
    metadata = session_data.get('metadata', {})
    purchase_type = metadata.get('purchase_type', 'subscription')
    stripe_customer_id = session_data.get("customer")

    if not user_id:
        logger.error(f"Checkout completed but no user_id found in session: {session_data.get('id', 'unknown')}")
        return

    supabase = get_supabase()
    _link_stripe_customer_to_user(supabase, user_id, stripe_customer_id)

    if purchase_type == 'credit_pack':
        credit_amount = int(metadata.get('credit_amount', 0))
        if credit_amount > 0:
            await add_credits(user_id, credit_amount, credit_type="bonus")
            logger.info(f"Added {credit_amount} bonus credits for user {user_id}")
        await log_retention_event(
            user_id,
            "purchase_completed",
            "stripe_checkout_webhook",
            {
                "purchase_type": "credit_pack",
                "credit_amount": credit_amount,
                "payment_provider": "stripe",
                "stripe_customer_id": stripe_customer_id,
                "checkout_session_id": session_data.get("id"),
                "source": metadata.get("source"),
            },
        )
        return

    subscription_id = session_data.get("subscription")
    if subscription_id:
        subscription = stripe.Subscription.retrieve(subscription_id)
        await _upsert_subscription_from_stripe(
            subscription,
            fallback_user_id=user_id,
            event_id=event_id or session_data.get("id"),
            event_type="checkout.session.completed",
            event_created=event_created or session_data.get("created"),
        )

    diagnostics = await get_subscription_diagnostics(user_id)
    if diagnostics["premium_status"]:
        upgrade_credits = PRO_MONTHLY_CREDITS - FREE_MONTHLY_CREDITS
        await add_credits(user_id, upgrade_credits, credit_type="monthly")
        logger.info(f"Checkout completed for user {user_id}, added {upgrade_credits} monthly credits")

    await log_retention_event(
        user_id,
        "purchase_completed",
        "stripe_checkout_webhook",
        {
            "purchase_type": purchase_type,
            "payment_provider": "stripe",
            "stripe_customer_id": stripe_customer_id,
            "subscription_id": subscription_id,
            "checkout_session_id": session_data.get("id"),
            "premium_status": diagnostics.get("premium_status"),
            "source": metadata.get("source"),
        },
    )


async def handle_subscription_created(
    subscription_data: Dict[str, Any],
    *,
    event_id: str | None = None,
    event_created: Any = None,
):
    """Handle new subscription creation."""
    user_id = await _upsert_subscription_from_stripe(
        subscription_data,
        event_id=event_id or subscription_data.get("id"),
        event_type="customer.subscription.created",
        event_created=event_created,
    )
    if user_id:
        logger.info(f"Subscription created for user {user_id}")


async def handle_subscription_updated(
    subscription_data: Dict[str, Any],
    *,
    event_id: str | None = None,
    event_created: Any = None,
):
    """Handle subscription updates."""
    await _upsert_subscription_from_stripe(
        subscription_data,
        event_id=event_id or subscription_data.get("id"),
        event_type="customer.subscription.updated",
        event_created=event_created,
    )
    logger.info(f"Subscription {subscription_data['id']} updated to {_normalize_status(subscription_data.get('status'))}")


async def handle_subscription_deleted(
    subscription_data: Dict[str, Any],
    *,
    event_id: str | None = None,
    event_created: Any = None,
):
    """Handle subscription cancellation."""
    await _upsert_subscription_from_stripe(
        subscription_data,
        event_id=event_id or subscription_data.get("id"),
        event_type="customer.subscription.deleted",
        event_created=event_created,
    )
    logger.info(f"Subscription {subscription_data['id']} canceled")


async def create_billing_portal_session(user_id: str, return_url: str) -> Dict[str, str]:
    diagnostics = await get_subscription_diagnostics(user_id)
    customer_id = diagnostics.get("stripe_customer_id")

    if not customer_id:
        raise ValueError("No Stripe customer is linked to this account")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return {"url": session.url}


async def verify_revenuecat_purchase(receipt_token: str, platform: str) -> dict[str, Any]:
    """
    Verify purchase with RevenueCat

    Args:
        receipt_token: Receipt/purchase token
        platform: ios or android

    Returns:
        True if purchase is valid
    """
    try:
        import httpx

        headers = {
            "Authorization": f"Bearer {settings.revenuecat_api_key}",
            "Content-Type": "application/json"
        }

        # RevenueCat API endpoint
        url = "https://api.revenuecat.com/v1/receipts"

        data = {
            "app_user_id": receipt_token,
            "fetch_token": receipt_token,
            "platform": platform
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)

            if response.status_code == 200:
                result = response.json()
                subscriber = result.get("subscriber", {})
                entitlements = subscriber.get("entitlements", {})
                entitlement = entitlements.get("premium_access") or {}
                expires_date = entitlement.get("expires_date")
                purchase_date = entitlement.get("purchase_date")
                expires_at = _parse_datetime(expires_date)
                is_valid = bool(expires_at and expires_at > _now())

                return {
                    "is_valid": is_valid,
                    "status": "active" if is_valid else "expired",
                    "start_date": purchase_date,
                    "end_date": expires_date,
                    "auto_renew": bool(entitlement.get("will_renew", True)) if is_valid else False,
                    "entitlement_id": entitlement.get("product_identifier") or "premium_access",
                }

            return {
                "is_valid": False,
                "status": "invalid",
                "start_date": None,
                "end_date": None,
                "auto_renew": False,
                "entitlement_id": "premium_access",
            }

    except Exception as e:
        logger.error(f"Error verifying RevenueCat purchase: {e}")
        return {
            "is_valid": False,
            "status": "verification_error",
            "start_date": None,
            "end_date": None,
            "auto_renew": False,
            "entitlement_id": "premium_access",
        }


async def _ensure_credit_record(user_id: str, is_premium: bool = False) -> None:
    """Create a credit record for the user if one doesn't exist."""
    from .usage_limiter import ensure_credit_record
    await ensure_credit_record(user_id, is_premium=is_premium)


async def _deduct_credits_fallback(user_id: str, amount: int, feature: str = "unknown") -> Dict[str, Any]:
    """Fallback deduction path when the RPC or schema contract is unavailable."""
    from fastapi import HTTPException

    supabase = get_supabase()
    result = supabase.table("user_credits").select("*").eq("user_id", user_id).execute()
    row = result.data[0] if result.data else None

    if not row:
        raise HTTPException(status_code=402, detail="No credit record found")

    now = _now_iso()

    if "monthly_credits" in row or "bonus_credits" in row:
        monthly = int(row.get("monthly_credits", 0))
        bonus = int(row.get("bonus_credits", 0))
        total = monthly + bonus
        if total < amount:
            raise HTTPException(status_code=402, detail="Insufficient credits")

        deduct_monthly = min(monthly, amount)
        deduct_bonus = amount - deduct_monthly
        monthly -= deduct_monthly
        bonus -= deduct_bonus

        supabase.table("user_credits").update({
            "monthly_credits": monthly,
            "bonus_credits": bonus,
            "updated_at": now,
        }).eq("user_id", user_id).execute()

        logger.warning(f"Used fallback credit deduction for {user_id} ({feature})")
        return {
            "success": True,
            "monthly_credits": monthly,
            "bonus_credits": bonus,
            "total": monthly + bonus,
        }

    balance = int(row.get("balance", 0))
    if balance < amount:
        raise HTTPException(status_code=402, detail="Insufficient credits")

    balance -= amount
    supabase.table("user_credits").update({
        "balance": balance,
        "updated_at": now,
    }).eq("user_id", user_id).execute()

    logger.warning(f"Used legacy-balance fallback deduction for {user_id} ({feature})")
    return {
        "success": True,
        "monthly_credits": balance,
        "bonus_credits": 0,
        "total": balance,
    }


async def deduct_credits(user_id: str, amount: int, feature: str = "unknown") -> Dict[str, Any]:
    """Atomically deduct credits from a user's balance via Supabase RPC."""
    try:
        supabase = get_supabase()
        is_premium = await check_premium_status(user_id)
        await _ensure_credit_record(user_id, is_premium=is_premium)

        try:
            result = supabase.rpc("deduct_user_credits", {
                "p_user_id": user_id,
                "p_amount": amount,
            }).execute()
        except Exception as rpc_error:
            logger.warning(f"Credit RPC unavailable for {user_id}, falling back: {rpc_error}")
            return await _deduct_credits_fallback(user_id, amount, feature)

        data = result.data if result.data else {}
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        if isinstance(data, str):
            import json
            data = json.loads(data)

        if not data.get("success"):
            error_msg = data.get("error", "Credit deduction failed")
            logger.warning(f"Credit deduction failed for {user_id}: {error_msg} (feature={feature})")
            from fastapi import HTTPException
            raise HTTPException(status_code=402, detail=error_msg)

        logger.info(f"Deducted {amount} credits from {user_id} for {feature}. Remaining: {data.get('total')}")
        return data

    except Exception as e:
        if "HTTPException" in type(e).__name__:
            raise
        logger.error(f"Error deducting credits: {e}")
        raise


async def check_premium_status(user_id: str) -> bool:
    """
    Check if user has active premium subscription

    Args:
        user_id: User's ID

    Returns:
        True if user has premium
    """
    try:
        diagnostics = await get_subscription_diagnostics(user_id)
        return bool(diagnostics["premium_status"])

    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False
