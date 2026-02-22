import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from ..database import get_supabase

logger = logging.getLogger(__name__)

CREDIT_COSTS: Dict[str, int] = {
    "food_scan": 1,
    "food_recommendation": 2,
    "body_fat_scan": 10,
    "percentile_scan": 10,
    "form_check": 3,
    "transformation": 30,
    "enhancement": 50,
    "chat_message": 0,
}

FREE_MONTHLY_CREDITS = 10
PRO_MONTHLY_CREDITS = 100


class InsufficientCredits(Exception):
    """Raised when user does not have enough credits"""
    def __init__(self, required: int, available: int, feature: str):
        self.required = required
        self.available = available
        self.feature = feature
        super().__init__(
            f"Not enough credits for {feature}. "
            f"Required: {required}, available: {available}. "
            f"Purchase more credits or upgrade to Pro."
        )


async def _get_or_create_credit_record(user_id: str, is_premium: bool = False) -> Dict[str, Any]:
    supabase = get_supabase()
    result = supabase.table("user_credits").select("*").eq("user_id", user_id).execute()

    now = datetime.utcnow()

    if result.data:
        record = result.data[0]
        reset_date = datetime.fromisoformat(record["reset_date"].replace("Z", "+00:00")).replace(tzinfo=None)
        if now >= reset_date:
            monthly = PRO_MONTHLY_CREDITS if is_premium else FREE_MONTHLY_CREDITS
            new_reset = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
            bonus = record.get("bonus_credits", 0)
            supabase.table("user_credits").update({
                "monthly_credits": monthly,
                "reset_date": new_reset.isoformat(),
                "updated_at": now.isoformat(),
            }).eq("user_id", user_id).execute()
            record["monthly_credits"] = monthly
            record["bonus_credits"] = bonus
            record["reset_date"] = new_reset.isoformat()
        return record
    else:
        monthly = PRO_MONTHLY_CREDITS if is_premium else FREE_MONTHLY_CREDITS
        new_reset = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
        new_record = {
            "user_id": user_id,
            "monthly_credits": monthly,
            "bonus_credits": 0,
            "reset_date": new_reset.isoformat(),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        supabase.table("user_credits").insert(new_record).execute()
        return new_record


async def get_credit_balance(user_id: str, is_premium: bool = False) -> Dict[str, Any]:
    record = await _get_or_create_credit_record(user_id, is_premium)
    monthly = record.get("monthly_credits", 0)
    bonus = record.get("bonus_credits", 0)
    return {
        "monthly_credits": monthly,
        "bonus_credits": bonus,
        "total_credits": monthly + bonus,
        "reset_date": record.get("reset_date"),
        "credit_costs": CREDIT_COSTS,
    }


async def check_credits(user_id: str, feature_type: str, is_premium: bool = False) -> Dict[str, Any]:
    cost = CREDIT_COSTS.get(feature_type, 1)
    balance = await get_credit_balance(user_id, is_premium)
    total = balance["total_credits"]

    if total < cost:
        raise InsufficientCredits(required=cost, available=total, feature=feature_type)

    return {
        "allowed": True,
        "cost": cost,
        "remaining_after": total - cost,
        "total_credits": total,
    }


async def deduct_credits(user_id: str, feature_type: str, is_premium: bool = False) -> Dict[str, Any]:
    cost = CREDIT_COSTS.get(feature_type, 1)
    if cost == 0:
        balance = await get_credit_balance(user_id, is_premium)
        return {
            "credits_used": 0,
            "monthly_credits": balance["monthly_credits"],
            "bonus_credits": balance["bonus_credits"],
            "total_credits": balance["total_credits"],
        }

    # Ensure the credit record exists (and resets monthly credits if needed)
    await _get_or_create_credit_record(user_id, is_premium)

    supabase = get_supabase()
    try:
        result = supabase.rpc('deduct_user_credits', {
            'p_user_id': user_id,
            'p_amount': cost,
        }).execute()

        data = result.data
        if data and data.get('success'):
            logger.info(
                f"Deducted {cost} credits from user {user_id} for {feature_type}. "
                f"Remaining: {data.get('total')}"
            )
            return {
                "credits_used": cost,
                "monthly_credits": data["monthly_credits"],
                "bonus_credits": data["bonus_credits"],
                "total_credits": data["total"],
            }
        else:
            error = data.get('error', 'Unknown error') if data else 'RPC returned no data'
            if error == 'Insufficient credits':
                total = data.get('total', 0) if data else 0
                raise InsufficientCredits(required=cost, available=total, feature=feature_type)
            raise Exception(f"Credit deduction RPC failed: {error}")
    except InsufficientCredits:
        raise
    except Exception as e:
        logger.error(f"Credit deduction error for user {user_id}: {e}")
        raise


async def add_credits(user_id: str, amount: int, credit_type: str = "bonus") -> Dict[str, Any]:
    record = await _get_or_create_credit_record(user_id)
    supabase = get_supabase()

    if credit_type == "monthly":
        new_val = record.get("monthly_credits", 0) + amount
        supabase.table("user_credits").update({
            "monthly_credits": new_val,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("user_id", user_id).execute()
    else:
        new_val = record.get("bonus_credits", 0) + amount
        supabase.table("user_credits").update({
            "bonus_credits": new_val,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("user_id", user_id).execute()

    logger.info(f"Added {amount} {credit_type} credits to user {user_id}")
    return await get_credit_balance(user_id)


# Backward-compatible wrappers for existing code
async def check_usage_limit(user_id: str, feature_type: str, is_premium: bool = False) -> Dict[str, Any]:
    try:
        result = await check_credits(user_id, feature_type, is_premium)
        return {
            "allowed": True,
            "current_count": 0,
            "limit": -1 if is_premium else result["total_credits"],
            "remaining": result["remaining_after"],
        }
    except InsufficientCredits:
        raise UsageLimitExceeded(
            f"Not enough credits for {feature_type}. Purchase more credits or upgrade to Pro."
        )


async def increment_usage(user_id: str, feature_type: str, is_premium: bool = False) -> int:
    result = await deduct_credits(user_id, feature_type, is_premium)
    return result["credits_used"]


async def get_all_usage_limits(user_id: str, is_premium: bool = False) -> Dict[str, Dict[str, Any]]:
    balance = await get_credit_balance(user_id, is_premium)
    total = balance["total_credits"]

    return {
        feature: {
            "credit_cost": cost,
            "can_afford": total >= cost,
            "total_credits": total,
        }
        for feature, cost in CREDIT_COSTS.items()
    }


class UsageLimitExceeded(Exception):
    pass
