from fastapi import APIRouter, HTTPException, Request, status, Depends
import logging
from typing import Dict, Any
from ..middleware.auth_middleware import get_current_user
from ..services.analytics import get_dashboard_stats, get_calorie_balance_trend
from ..rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
@limiter.limit("60/minute")
async def get_dashboard(request: Request, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        dashboard_data = await get_dashboard_stats(current_user["id"])
        return {
            "user": {
                "name": current_user.get("full_name", "User"),
                "email": current_user["email"],
                "premium_status": current_user.get("premium_status", False),
                "calorie_goal": current_user.get("calorie_goal")
            },
            "today": dashboard_data["today"],
            "trends": {
                "food_7d": dashboard_data["food_trend_7d"],
                "workout_30d": dashboard_data["workout_trend_30d"]
            },
            "stats": dashboard_data["stats"]
        }
    except Exception as e:
        logger.error(f"Error getting dashboard: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load dashboard data")


@router.get("/quick-stats")
@limiter.limit("60/minute")
async def get_quick_stats(request: Request, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    try:
        from datetime import date, timedelta
        from ..services.analytics import calculate_daily_summary
        from ..services.calorie_calculator import CalorieCalculator
        from ..database import get_supabase

        today = date.today()
        supabase = get_supabase()
        daily_summary = await calculate_daily_summary(current_user["id"], today)

        profile_result = supabase.table("user_profiles").select(
            "weight_kg, height_cm, age, gender, activity_level"
        ).eq("user_id", current_user["id"]).single().execute()

        tdee = 0.0
        if profile_result.data:
            p = profile_result.data
            tdee = CalorieCalculator.calculate_tdee(
                p.get('weight_kg', 70.0), p.get('height_cm', 170.0),
                p.get('age', 30), p.get('gender', 'male'), p.get('activity_level', 'moderate')
            )

        workout_calories_result = supabase.table("workout_logs").select(
            "calories_burned"
        ).eq("user_id", current_user["id"]).eq('"date"', today.isoformat()).execute()

        workout_calories = sum(
            float(log.get('calories_burned', 0) or 0) for log in workout_calories_result.data
        ) if workout_calories_result.data else 0.0

        total_burned = tdee + workout_calories

        week_start = today - timedelta(days=today.weekday())
        workout_result = supabase.table("workout_logs").select("id").eq(
            "user_id", current_user["id"]
        ).gte('"date"', week_start.isoformat()).execute()
        workouts_this_week = len(workout_result.data) if workout_result.data else 0

        calorie_goal = float(current_user.get("calorie_goal") or 2000)
        total_calories = float(daily_summary.get("total_calories", 0))
        calorie_progress = (total_calories / calorie_goal * 100) if calorie_goal > 0 else 0

        return {
            "today_calories": total_calories,
            "calorie_goal": calorie_goal,
            "calorie_progress": min(100, round(calorie_progress, 1)),
            "today_protein": float(daily_summary.get("total_protein", 0)),
            "workouts_this_week": workouts_this_week,
            "tdee": round(tdee, 1),
            "workout_calories": round(workout_calories, 1),
            "total_burned": round(total_burned, 1),
            "premium_status": current_user.get("premium_status", False)
        }
    except Exception as e:
        logger.error(f"Error getting quick stats: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load quick stats")


@router.get("/calorie-balance-trend")
@limiter.limit("30/minute")
async def get_calorie_balance_trend_endpoint(
    request: Request, days: int = 7, current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    try:
        trend_data = await get_calorie_balance_trend(current_user["id"], days)
        return trend_data
    except Exception as e:
        logger.error(f"Error getting calorie balance trend: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to load calorie balance trend")
