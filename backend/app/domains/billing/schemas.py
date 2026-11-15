from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CreateCheckoutSessionRequest(BaseModel):
    price_id: str = Field(..., description="Stripe price ID")
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    session_id: str
    checkout_url: str


class VerifyPurchaseRequest(BaseModel):
    receipt_token: str = Field(..., description="RevenueCat receipt token")
    platform: str = Field(..., description="ios or android")
    app_user_id: Optional[str] = Field(default=None, description="RevenueCat app user ID when available")


class SubscriptionResponse(BaseModel):
    subscription_id: Optional[str] = None
    user_id: Optional[str] = None
    subscription_type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime]
    payment_provider: Optional[str] = None
    auto_renew: bool = False
    premium_status: bool
    deletion_blocked: bool = False
    deletion_block_reason: Optional[str] = None
    billing_portal_available: bool = False


class SubscriptionDiagnosticsResponse(BaseModel):
    subscription_id: Optional[str] = None
    user_id: Optional[str] = None
    subscription_type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    payment_provider: Optional[str] = None
    auto_renew: bool = False
    premium_status: bool
    deletion_blocked: bool = False
    deletion_block_reason: Optional[str] = None
    billing_portal_available: bool = False
    stripe_customer_id: Optional[str] = None
    profile_premium_status: bool = False
    entitlement_source: str
    cancel_at_period_end: bool = False
    last_stripe_event_id: Optional[str] = None
    last_stripe_event_type: Optional[str] = None
    last_webhook_processed_at: Optional[datetime] = None


class BillingPortalSessionRequest(BaseModel):
    return_url: str


class BillingPortalSessionResponse(BaseModel):
    url: str


class UsageLimitResponse(BaseModel):
    feature_type: str
    current_count: int
    limit: int
    remaining: int
    is_premium: bool


class CreditBalanceResponse(BaseModel):
    monthly_credits: int
    bonus_credits: int
    total_credits: int
    reset_date: Optional[str] = None
    credit_costs: Dict[str, int]


class BuyCreditPackRequest(BaseModel):
    pack_size: int = Field(..., description="Number of credits to purchase (50, 100, 200)")
    success_url: str
    cancel_url: str


class WebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
