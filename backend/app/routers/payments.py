from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from typing import Dict, Any
from ..schemas.payment_schemas import (
    CreateCheckoutSessionRequest, CheckoutSessionResponse,
    VerifyPurchaseRequest, SubscriptionResponse, UsageLimitResponse,
    BuyCreditPackRequest, CreditBalanceResponse,
    SubscriptionDiagnosticsResponse, BillingPortalSessionRequest,
    BillingPortalSessionResponse,
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services.payment_service import (
    create_checkout_session, create_credit_pack_checkout,
    handle_stripe_webhook, verify_revenuecat_purchase, check_premium_status,
    get_subscription_diagnostics, create_billing_portal_session,
    _upsert_external_subscription,
)
from ..services.retention_event_service import log_retention_event
from ..services.usage_limiter import get_all_usage_limits, get_credit_balance
from ..services.service_availability import is_stripe_unavailable, is_stripe_bad_request, payment_service_unavailable
from ..rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
@limiter.limit("5/minute")
async def create_checkout(
    request: Request,
    checkout_request: CreateCheckoutSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription purchase"""
    try:
        session_data = await create_checkout_session(
            user_id=current_user["id"],
            price_id=checkout_request.price_id,
            success_url=checkout_request.success_url,
            cancel_url=checkout_request.cancel_url
        )
        
        return CheckoutSessionResponse(**session_data)
        
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        if is_stripe_bad_request(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        if is_stripe_unavailable(e):
            raise payment_service_unavailable("Payments are temporarily unavailable on this server.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create checkout session")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing stripe signature"
            )
        
        result = await handle_stripe_webhook(payload, signature)
        return result
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )


@router.post("/verify-purchase")
async def verify_purchase(
    request: VerifyPurchaseRequest,
    current_user: dict = Depends(get_current_user)
):
    """Verify in-app purchase via RevenueCat"""
    try:
        verification = await verify_revenuecat_purchase(
            request.receipt_token,
            request.platform,
            request.app_user_id,
        )
        if verification.get("status") == "verification_error":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Purchase verification is temporarily unavailable. Please try again.",
            )

        provider = "revenuecat_ios" if request.platform == "ios" else "revenuecat_android"
        subscription_id = f"revenuecat:{request.platform}:{current_user['id']}:{verification.get('entitlement_id', 'premium_access')}"
        await _upsert_external_subscription(
            user_id=current_user["id"],
            provider=provider,
            subscription_id=subscription_id,
            status=verification.get("status", "invalid"),
            start_date=verification.get("start_date"),
            end_date=verification.get("end_date"),
            auto_renew=bool(verification.get("auto_renew", False)),
        )

        diagnostics = await get_subscription_diagnostics(current_user["id"])
        if verification.get("is_valid"):
            dedupe_key = ":".join([
                provider,
                subscription_id,
                str(verification.get("start_date") or verification.get("end_date") or "unknown"),
            ])
            await log_retention_event(
                current_user["id"],
                "purchase_completed",
                "revenuecat_verification",
                {
                    "payment_provider": provider,
                    "purchase_type": "subscription",
                    "dedupe_key": dedupe_key,
                },
            )
        return {
            "status": "verified" if verification.get("is_valid") else verification.get("status", "invalid"),
            "premium_status": diagnostics.get("premium_status", False),
            "deletion_blocked": diagnostics.get("deletion_blocked", False),
            "deletion_block_reason": diagnostics.get("deletion_block_reason"),
            "entitlement_source": diagnostics.get("entitlement_source", "none"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying purchase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Purchase verification failed"
        )


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get user's current subscription status"""
    try:
        diagnostics = await get_subscription_diagnostics(current_user["id"])
        return SubscriptionResponse(**{
            "subscription_id": diagnostics.get("subscription_id"),
            "user_id": diagnostics.get("user_id"),
            "subscription_type": diagnostics.get("subscription_type", "free"),
            "status": diagnostics.get("status", "none"),
            "start_date": diagnostics.get("start_date"),
            "end_date": diagnostics.get("end_date"),
            "payment_provider": diagnostics.get("payment_provider"),
            "auto_renew": diagnostics.get("auto_renew", False),
            "premium_status": diagnostics.get("premium_status", False),
            "deletion_blocked": diagnostics.get("deletion_blocked", False),
            "deletion_block_reason": diagnostics.get("deletion_block_reason"),
            "billing_portal_available": diagnostics.get("billing_portal_available", False),
        })

    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
        )


@router.get("/subscription-diagnostics", response_model=SubscriptionDiagnosticsResponse)
async def get_subscription_debug(current_user: dict = Depends(get_current_user)):
    """Expose subscription reconciliation diagnostics for support/debugging."""
    try:
        diagnostics = await get_subscription_diagnostics(current_user["id"])
        return SubscriptionDiagnosticsResponse(**{
            "subscription_id": diagnostics.get("subscription_id"),
            "user_id": diagnostics.get("user_id"),
            "subscription_type": diagnostics.get("subscription_type", "free"),
            "status": diagnostics.get("status", "none"),
            "start_date": diagnostics.get("start_date"),
            "end_date": diagnostics.get("end_date"),
            "payment_provider": diagnostics.get("payment_provider"),
            "auto_renew": diagnostics.get("auto_renew", False),
            "premium_status": diagnostics.get("premium_status", False),
            "deletion_blocked": diagnostics.get("deletion_blocked", False),
            "deletion_block_reason": diagnostics.get("deletion_block_reason"),
            "billing_portal_available": diagnostics.get("billing_portal_available", False),
            "stripe_customer_id": diagnostics.get("stripe_customer_id"),
            "profile_premium_status": diagnostics.get("profile_premium_status", False),
            "entitlement_source": diagnostics.get("entitlement_source", "none"),
            "cancel_at_period_end": diagnostics.get("cancel_at_period_end", False),
            "last_stripe_event_id": diagnostics.get("last_stripe_event_id"),
            "last_stripe_event_type": diagnostics.get("last_stripe_event_type"),
            "last_webhook_processed_at": diagnostics.get("last_webhook_processed_at"),
        })
    except Exception as e:
        logger.error(f"Error getting subscription diagnostics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription diagnostics"
        )


@router.post("/billing-portal", response_model=BillingPortalSessionResponse)
async def create_billing_portal(
    portal_request: BillingPortalSessionRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a Stripe billing portal session for self-serve cancellation."""
    try:
        portal = await create_billing_portal_session(
            current_user["id"],
            portal_request.return_url,
        )
        return BillingPortalSessionResponse(**portal)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating billing portal session: {e}")
        if is_stripe_unavailable(e):
            raise payment_service_unavailable("Billing portal is temporarily unavailable on this server.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create billing portal session"
        )


@router.get("/usage-limits")
async def get_usage_limits(current_user: dict = Depends(get_current_user)):
    """Get user's feature usage limits"""
    try:
        is_premium = await check_premium_status(current_user["id"])
        usage_data = await get_all_usage_limits(current_user["id"], is_premium)
        
        return {
            "is_premium": is_premium,
            "limits": usage_data
        }
        
    except Exception as e:
        logger.error(f"Error getting usage limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get usage limits"
        )


@router.get("/credits", response_model=CreditBalanceResponse)
async def get_credits(current_user: dict = Depends(get_current_user)):
    """Get user's credit balance"""
    try:
        is_premium = bool(current_user.get("premium_status", False))
        balance = await get_credit_balance(current_user["id"], is_premium)
        return CreditBalanceResponse(**balance)
    except Exception as e:
        logger.error(f"Error getting credits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get credit balance"
        )


@router.post("/buy-credits", response_model=CheckoutSessionResponse)
@limiter.limit("5/minute")
async def buy_credits(
    request: Request,
    credit_request: BuyCreditPackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Purchase a credit pack"""
    try:
        session_data = await create_credit_pack_checkout(
            user_id=current_user["id"],
            pack_size=credit_request.pack_size,
            success_url=credit_request.success_url,
            cancel_url=credit_request.cancel_url,
        )
        return CheckoutSessionResponse(**session_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error buying credits: {e}")
        if is_stripe_unavailable(e):
            raise payment_service_unavailable("Credit purchases are temporarily unavailable on this server.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create credit purchase session")
