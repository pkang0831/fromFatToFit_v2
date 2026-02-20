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


class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    subscription_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    payment_provider: str
    auto_renew: bool


class UsageLimitResponse(BaseModel):
    feature_type: str
    current_count: int
    limit: int
    remaining: int
    is_premium: bool


class WebhookEvent(BaseModel):
    type: str
    data: Dict[str, Any]
