from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from typing import Dict, Any
from ..schemas.payment_schemas import (
    CreateCheckoutSessionRequest, CheckoutSessionResponse,
    VerifyPurchaseRequest, SubscriptionResponse, UsageLimitResponse,
    BuyCreditPackRequest, CreditBalanceResponse,
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services.payment_service import (
    create_checkout_session, create_credit_pack_checkout,
    handle_stripe_webhook, verify_revenuecat_purchase, check_premium_status,
)
from ..services.usage_limiter import get_all_usage_limits, get_credit_balance
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


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
        is_valid = await verify_revenuecat_purchase(
            request.receipt_token,
            request.platform
        )
        
        if is_valid:
            # Update user's premium status
            supabase = get_supabase()
            from datetime import datetime
            supabase.table("user_profiles").update({
                "premium_status": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", current_user["id"]).execute()
            
            return {"status": "verified", "premium_status": True}
        else:
            return {"status": "invalid", "premium_status": False}
        
    except Exception as e:
        logger.error(f"Error verifying purchase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Purchase verification failed"
        )


@router.get("/subscription")
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Get user's current subscription status"""
    try:
        supabase = get_supabase()
        
        # Get active subscriptions
        result = supabase.table("user_subscriptions").select("*").eq("user_id", current_user["id"]).eq("status", "active").execute()
        
        is_premium = await check_premium_status(current_user["id"])
        
        if result.data:
            subscription = result.data[0]
            return SubscriptionResponse(**subscription)
        else:
            return {
                "premium_status": is_premium,
                "subscription_type": "free" if not is_premium else "premium",
                "status": "none"
            }
        
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
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
        is_premium = await check_premium_status(current_user["id"])
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credit purchase session"
        )
