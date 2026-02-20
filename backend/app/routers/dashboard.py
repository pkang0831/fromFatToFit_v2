from fastapi import APIRouter, HTTPException, status, Depends
import logging
from typing import Dict, Any
from ..middleware.auth_middleware import get_current_user
from ..services.analytics import get_dashboard_stats, get_calorie_balance_trend

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def get_dashboard(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get comprehensive dashboard data with today's stats and trends"""
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data"
        )


@router.get("/quick-stats")
async def get_quick_stats(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get quick stats for home screen widgets"""
    try:
        from datetime import date
        from ..services.analytics import calculate_daily_summary
        from ..services.calorie_calculator import CalorieCalculator
        from ..database import get_supabase
        
        today = date.today()
        supabase = get_supabase()
        
        # Get today's summary
        daily_summary = await calculate_daily_summary(current_user["id"], today)
        
        # Get user profile for TDEE calculation
        profile_result = supabase.table("user_profiles").select(
            "weight_kg, height_cm, age, gender, activity_level"
        ).eq("user_id", current_user["id"]).single().execute()
        
        # Calculate TDEE if profile data is available
        tdee = 0.0
        if profile_result.data:
            profile = profile_result.data
            weight = profile.get('weight_kg', 70.0)
            height = profile.get('height_cm', 170.0)
            age = profile.get('age', 30)
            gender = profile.get('gender', 'male')
            activity_level = profile.get('activity_level', 'moderate')
            
            tdee = CalorieCalculator.calculate_tdee(
                weight, height, age, gender, activity_level
            )
        
        # Get today's workout calories burned
        workout_calories_result = supabase.table("workout_logs").select(
            "calories_burned"
        ).eq("user_id", current_user["id"]).eq('"date"', today.isoformat()).execute()
        
        workout_calories = sum(
            float(log.get('calories_burned', 0) or 0) 
            for log in workout_calories_result.data
        ) if workout_calories_result.data else 0.0
        
        # Total calories burned today = TDEE + workout calories
        total_burned = tdee + workout_calories
        
        # Get this week's workout count
        from datetime import timedelta
        week_start = today - timedelta(days=today.weekday())
        
        workout_result = supabase.table("workout_logs").select("id").eq("user_id", current_user["id"]).gte('"date"', week_start.isoformat()).execute()
        
        workouts_this_week = len(workout_result.data) if workout_result.data else 0
        
        # Calculate calorie progress
        calorie_goal = current_user.get("calorie_goal") or 2000
        calorie_goal = float(calorie_goal) if calorie_goal else 2000
        total_calories = float(daily_summary.get("total_calories", 0))
        calorie_progress = (total_calories / calorie_goal * 100) if calorie_goal and calorie_goal > 0 else 0
        
        return {
            "today_calories": float(daily_summary.get("total_calories", 0)),
            "calorie_goal": float(calorie_goal),
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load quick stats"
        )


@router.get("/calorie-balance-trend")
async def get_calorie_balance_trend_endpoint(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get calorie intake/burn/deficit trend for specified days"""
    try:
        trend_data = await get_calorie_balance_trend(current_user["id"], days)
        return trend_data
        
    except Exception as e:
        logger.error(f"Error getting calorie balance trend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load calorie balance trend"
        )
