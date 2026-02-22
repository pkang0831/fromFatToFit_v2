from fastapi import APIRouter, Depends
from datetime import date, timedelta
from supabase import Client
from app.dependencies import get_current_user, get_user_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/streaks", tags=["streaks"])

@router.get("")
async def get_streak(
    current_user: dict = Depends(get_current_user),
    user_db: Client = Depends(get_user_db),
):
    """Get user's current streak data."""
    user_id = current_user["id"]

    result = user_db.table("user_streaks").select("*").eq("user_id", user_id).execute()

    if not result.data:
        streak_data = {
            "user_id": user_id,
            "current_streak": 0,
            "longest_streak": 0,
            "last_active_date": None,
            "total_active_days": 0,
            "streak_freezes": 1,
        }
        user_db.table("user_streaks").insert(streak_data).execute()
        return streak_data

    streak = result.data[0]

    today = date.today()
    last_active = streak.get("last_active_date")

    if last_active:
        from datetime import datetime
        if isinstance(last_active, str):
            last_active = datetime.strptime(last_active, "%Y-%m-%d").date()

        days_since = (today - last_active).days

        if days_since > 1:
            streak["current_streak"] = 0
            user_db.table("user_streaks").update({
                "current_streak": 0
            }).eq("user_id", user_id).execute()

    return streak

@router.post("/check-in")
async def check_in(
    current_user: dict = Depends(get_current_user),
    user_db: Client = Depends(get_user_db),
):
    """Record daily activity to maintain/extend streak."""
    user_id = current_user["id"]
    today = str(date.today())

    result = user_db.table("user_streaks").select("*").eq("user_id", user_id).execute()

    if not result.data:
        streak_data = {
            "user_id": user_id,
            "current_streak": 1,
            "longest_streak": 1,
            "last_active_date": today,
            "total_active_days": 1,
            "streak_freezes": 1,
        }
        user_db.table("user_streaks").insert(streak_data).execute()
        return {"streak": 1, "is_new": True, "message": "Streak started!"}

    streak = result.data[0]
    last_active = streak.get("last_active_date")

    if last_active == today:
        return {
            "streak": streak["current_streak"],
            "is_new": False,
            "message": "Already checked in today!"
        }

    from datetime import datetime
    if isinstance(last_active, str) and last_active:
        last_active_date = datetime.strptime(last_active, "%Y-%m-%d").date()
        days_since = (date.today() - last_active_date).days
    else:
        days_since = 999

    if days_since == 1:
        new_streak = streak["current_streak"] + 1
    elif days_since > 1:
        new_streak = 1
    else:
        new_streak = streak["current_streak"]

    longest = max(new_streak, streak.get("longest_streak", 0))
    total_days = streak.get("total_active_days", 0) + 1

    update_data = {
        "current_streak": new_streak,
        "longest_streak": longest,
        "last_active_date": today,
        "total_active_days": total_days,
    }

    user_db.table("user_streaks").update(update_data).eq("user_id", user_id).execute()

    milestones = {7: "1 Week", 14: "2 Weeks", 30: "1 Month", 60: "2 Months", 100: "100 Days", 365: "1 Year"}
    milestone_hit = milestones.get(new_streak)

    return {
        "streak": new_streak,
        "longest": longest,
        "total_days": total_days,
        "is_new": True,
        "milestone": milestone_hit,
        "message": f"{'🎉 ' + milestone_hit + ' milestone! ' if milestone_hit else ''}Day {new_streak}!"
    }
