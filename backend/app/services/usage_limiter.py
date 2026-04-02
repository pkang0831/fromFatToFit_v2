import logging
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from ..database import get_supabase

logger = logging.getLogger(__name__)

FREE_MONTHLY_CREDITS = 10
PRO_MONTHLY_CREDITS = 100

# Feature usage limits for free tier (after first month)
USAGE_LIMITS = {
    "food_scan": 5,
    "body_fat_scan": 1,
    "percentile_scan": 1,
    "form_check": 0,  # Premium only
    "transformation": 0  # Premium only
}

# Boosted limits for first 30 days after signup
FIRST_MONTH_USAGE_LIMITS = {
    "food_scan": 10,
    "body_fat_scan": 3,
    "percentile_scan": 3,
    "form_check": 0,
    "transformation": 0
}

FIRST_MONTH_DAYS = 30


class UsageLimitExceeded(Exception):
    """Raised when user exceeds their usage limit"""
    pass


def _next_reset_date_iso() -> str:
    now = datetime.now(timezone.utc)
    next_month = (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)).replace(day=1)
    return next_month.isoformat()


def _build_credit_costs(is_premium: bool = False) -> Dict[str, int]:
    return {
        "food_scan": 1,
        "body_fat_scan": 0 if is_premium else 10,
        "percentile_scan": 0 if is_premium else 10,
        "transformation": 30,
        "journey": 100,
        "enhancement": 50,
        "region_transform": 15,
        "beauty_scan": 10,
        "beauty_styling": 30,
        "fashion_recommend": 5,
        "fashion_images": 15,
    }


def _normalize_credit_row(row: Dict[str, Any] | None, is_premium: bool = False) -> Dict[str, Any]:
    default_monthly = PRO_MONTHLY_CREDITS if is_premium else FREE_MONTHLY_CREDITS

    if not row:
        return {
            "monthly_credits": default_monthly,
            "bonus_credits": 0,
            "total_credits": default_monthly,
            "reset_date": None,
            "credit_costs": _build_credit_costs(is_premium),
        }

    if "monthly_credits" in row or "bonus_credits" in row:
        monthly = int(row.get("monthly_credits", default_monthly if is_premium else FREE_MONTHLY_CREDITS))
        bonus = int(row.get("bonus_credits", 0))
        total = int(row.get("total_credits", monthly + bonus))
        return {
            "monthly_credits": monthly,
            "bonus_credits": bonus,
            "total_credits": total,
            "reset_date": row.get("reset_date"),
            "credit_costs": _build_credit_costs(is_premium),
        }

    balance = int(row.get("balance", default_monthly))
    return {
        "monthly_credits": balance,
        "bonus_credits": 0,
        "total_credits": balance,
        "reset_date": row.get("reset_date"),
        "credit_costs": _build_credit_costs(is_premium),
    }


async def ensure_credit_record(user_id: str, is_premium: bool = False) -> Dict[str, Any]:
    supabase = get_supabase()
    result = supabase.table("user_credits").select("*").eq("user_id", user_id).execute()
    existing = result.data[0] if result.data else None
    if existing:
        return existing

    default_monthly = PRO_MONTHLY_CREDITS if is_premium else FREE_MONTHLY_CREDITS
    now = datetime.now(timezone.utc).isoformat()

    try:
        insert_result = supabase.table("user_credits").insert({
            "user_id": user_id,
            "monthly_credits": default_monthly,
            "bonus_credits": 0,
            "reset_date": _next_reset_date_iso(),
            "created_at": now,
            "updated_at": now,
        }).execute()
        if insert_result.data:
            return insert_result.data[0]
    except Exception:
        # Support legacy schemas that still use a single balance column.
        insert_result = supabase.table("user_credits").insert({
            "user_id": user_id,
            "balance": default_monthly,
            "created_at": now,
            "updated_at": now,
        }).execute()
        if insert_result.data:
            return insert_result.data[0]

    return {
        "user_id": user_id,
        "monthly_credits": default_monthly,
        "bonus_credits": 0,
        "reset_date": _next_reset_date_iso(),
    }


async def add_credits(user_id: str, amount: int, credit_type: str = "bonus") -> Dict[str, Any]:
    if amount <= 0:
        return _normalize_credit_row(await ensure_credit_record(user_id))

    supabase = get_supabase()
    row = await ensure_credit_record(user_id)
    now = datetime.now(timezone.utc).isoformat()

    if "monthly_credits" in row or "bonus_credits" in row:
        monthly = int(row.get("monthly_credits", FREE_MONTHLY_CREDITS))
        bonus = int(row.get("bonus_credits", 0))

        if credit_type == "monthly":
            monthly += amount
        else:
            bonus += amount

        supabase.table("user_credits").update({
            "monthly_credits": monthly,
            "bonus_credits": bonus,
            "updated_at": now,
        }).eq("user_id", user_id).execute()

        return {
            "monthly_credits": monthly,
            "bonus_credits": bonus,
            "total_credits": monthly + bonus,
            "reset_date": row.get("reset_date"),
        }

    balance = int(row.get("balance", FREE_MONTHLY_CREDITS)) + amount
    supabase.table("user_credits").update({
        "balance": balance,
        "updated_at": now,
    }).eq("user_id", user_id).execute()

    return {
        "monthly_credits": balance,
        "bonus_credits": 0,
        "total_credits": balance,
        "reset_date": row.get("reset_date"),
    }


async def _is_first_month(user_id: str) -> bool:
    """Check if user signed up within the last FIRST_MONTH_DAYS days."""
    try:
        supabase = get_supabase()
        result = supabase.table("user_profiles").select("created_at").eq("id", user_id).execute()
        if not result.data:
            return False
        created_str = result.data[0].get("created_at")
        if not created_str:
            return False
        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - created).days < FIRST_MONTH_DAYS
    except Exception as e:
        logger.warning("Failed to check account age for first-month boost: %s", e)
        return False


async def check_usage_limit(user_id: str, feature_type: str, is_premium: bool = False) -> Dict[str, Any]:
    """
    Check if user has remaining usage for a feature.
    Free users get boosted limits during their first 30 days.
    """
    try:
        if is_premium:
            return {
                "allowed": True,
                "current_count": 0,
                "limit": -1,
                "remaining": -1
            }

        base_limit = USAGE_LIMITS.get(feature_type, 0)

        if base_limit == 0:
            raise UsageLimitExceeded(f"{feature_type} requires premium subscription")

        # Check if user qualifies for first-month boosted limits
        first_month_limit = FIRST_MONTH_USAGE_LIMITS.get(feature_type, base_limit)
        if first_month_limit > base_limit and await _is_first_month(user_id):
            limit = first_month_limit
        else:
            limit = base_limit

        supabase = get_supabase()
        result = supabase.table("usage_limits").select("*").eq("user_id", user_id).eq("feature_type", feature_type).execute()

        current_count = result.data[0]["count"] if result.data else 0
        remaining = limit - current_count

        if remaining <= 0:
            raise UsageLimitExceeded(f"Usage limit exceeded for {feature_type}. Upgrade to premium for unlimited access.")

        return {
            "allowed": True,
            "current_count": current_count,
            "limit": limit,
            "remaining": remaining
        }

    except UsageLimitExceeded:
        raise
    except Exception as e:
        logger.error(f"Error checking usage limit: {e}")
        raise


async def increment_usage(user_id: str, feature_type: str) -> int:
    """
    Increment usage count for a feature
    
    Args:
        user_id: User's ID
        feature_type: Type of feature
        
    Returns:
        New usage count
    """
    try:
        supabase = get_supabase()
        
        # Check if record exists
        result = supabase.table("usage_limits").select("*").eq("user_id", user_id).eq("feature_type", feature_type).execute()
        
        if result.data:
            # Update existing record
            new_count = result.data[0]["count"] + 1
            supabase.table("usage_limits").update({
                "count": new_count,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).eq("feature_type", feature_type).execute()
        else:
            # Create new record
            new_count = 1
            supabase.table("usage_limits").insert({
                "user_id": user_id,
                "feature_type": feature_type,
                "count": new_count,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
        
        return new_count
        
    except Exception as e:
        logger.error(f"Error incrementing usage: {e}")
        raise


async def get_all_usage_limits(user_id: str, is_premium: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Get all usage limits for a user
    
    Args:
        user_id: User's ID
        is_premium: Whether user has premium subscription
        
    Returns:
        Dictionary of feature usage data
    """
    try:
        if is_premium:
            return {
                feature: {
                    "current_count": 0,
                    "limit": -1,
                    "remaining": -1,
                    "is_premium": True
                }
                for feature in USAGE_LIMITS.keys()
            }
        
        supabase = get_supabase()
        result = supabase.table("usage_limits").select("*").eq("user_id", user_id).execute()
        
        usage_data = {}
        for feature_type, limit in USAGE_LIMITS.items():
            current = next((item for item in result.data if item["feature_type"] == feature_type), None)
            current_count = current["count"] if current else 0
            
            usage_data[feature_type] = {
                "current_count": current_count,
                "limit": limit,
                "remaining": max(0, limit - current_count),
                "is_premium": False
            }
        
        return usage_data
        
    except Exception as e:
        logger.error(f"Error getting usage limits: {e}")
        raise


async def get_credit_balance(user_id: str, is_premium: bool = False) -> Dict[str, Any]:
    """
    Get user's credit balance (monthly + bonus = total).
    Returns dict suitable for CreditBalanceResponse.
    """
    try:
        supabase = get_supabase()
        result = supabase.table("user_credits").select("*").eq("user_id", user_id).execute()
        row = result.data[0] if result.data else None
        return _normalize_credit_row(row, is_premium)
    except Exception as e:
        logger.error(f"Error getting credit balance: {e}")
        return _normalize_credit_row(None, is_premium)
