import logging
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from ..database import get_supabase
from .calorie_calculator import CalorieCalculator

logger = logging.getLogger(__name__)


async def get_food_trend_data(user_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Get food/calorie trend data for specified number of days
    
    Args:
        user_id: User's ID
        days: Number of days to retrieve
        
    Returns:
        List of daily data points
    """
    try:
        supabase = get_supabase()
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get daily summaries
        result = supabase.table("daily_summaries").select("*").eq("user_id", user_id).gte('"date"', start_date.isoformat()).lte('"date"', end_date.isoformat()).order('"date"').execute()
        
        # Get user's calorie goal
        user_result = supabase.table("user_profiles").select("calorie_goal").eq("user_id", user_id).execute()
        calorie_goal = user_result.data[0].get("calorie_goal") if user_result.data and len(user_result.data) > 0 else 2000
        
        trend_data = []
        for day_data in result.data:
            trend_data.append({
                "date": day_data["date"],
                "calories": day_data["total_calories"],
                "protein": day_data["total_protein"],
                "carbs": day_data["total_carbs"],
                "fat": day_data["total_fat"],
                "goal": calorie_goal
            })
        
        # Fill in missing days with zero values
        all_dates = [start_date + timedelta(days=x) for x in range(days)]
        existing_dates = {datetime.fromisoformat(item["date"]).date() for item in trend_data}
        
        for check_date in all_dates:
            if check_date not in existing_dates:
                trend_data.append({
                    "date": check_date.isoformat(),
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "goal": calorie_goal
                })
        
        # Sort by date
        trend_data.sort(key=lambda x: x["date"])
        
        return trend_data
        
    except Exception as e:
        logger.error(f"Error getting food trend data: {e}")
        raise


async def get_workout_trend_data(user_id: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get workout trend data for specified number of days
    
    Args:
        user_id: User's ID
        days: Number of days to retrieve
        
    Returns:
        List of daily workout data points
    """
    try:
        supabase = get_supabase()
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get workout logs
        result = supabase.table("workout_logs").select("*").eq("user_id", user_id).gte('"date"', start_date.isoformat()).lte('"date"', end_date.isoformat()).execute()
        
        # Aggregate by date
        daily_data = {}
        for workout in result.data:
            workout_date = workout["date"]
            if workout_date not in daily_data:
                daily_data[workout_date] = {
                    "date": workout_date,
                    "workout_count": 0,
                    "total_volume": 0,
                    "duration_minutes": 0,
                    "calories_burned": 0
                }
            
            daily_data[workout_date]["workout_count"] += 1
            
            # Calculate volume (weight x reps for all sets)
            sets = workout.get("sets", [])
            for set_data in sets:
                volume = set_data.get("weight", 0) * set_data.get("reps", 0)
                daily_data[workout_date]["total_volume"] += volume
            
            if workout.get("duration_minutes"):
                daily_data[workout_date]["duration_minutes"] += workout["duration_minutes"]
            
            # Add calories burned
            if workout.get("calories_burned"):
                daily_data[workout_date]["calories_burned"] += float(workout["calories_burned"])
        
        # Fill in missing days
        all_dates = [start_date + timedelta(days=x) for x in range(days)]
        trend_data = []
        
        for check_date in all_dates:
            date_str = check_date.isoformat()
            if date_str in daily_data:
                trend_data.append(daily_data[date_str])
            else:
                trend_data.append({
                    "date": date_str,
                    "workout_count": 0,
                    "total_volume": 0,
                    "duration_minutes": 0,
                    "calories_burned": 0
                })
        
        return trend_data
        
    except Exception as e:
        logger.error(f"Error getting workout trend data: {e}")
        raise


async def get_calorie_balance_trend(user_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Get calorie balance trend combining food intake, TDEE, workout burn, and deficit
    
    Formula: Calorie Delta = Consumed - (TDEE + Workout Calories)
    - Positive delta = Surplus (gaining weight)
    - Negative delta = Deficit (losing weight)
    
    TDEE = BMR × Activity Factor (from activity_level)
    Total Burned = TDEE + Workout Calories
    
    Averages are calculated based on actual active days:
    - If user registered < days ago: use actual days since registration
    - If user registered >= days ago: use full requested days (rolling basis)
    
    Args:
        user_id: User's ID
        days: Number of days to retrieve
        
    Returns:
        Dictionary with trend data and summary statistics
    """
    try:
        supabase = get_supabase()
        
        # Get user profile with all necessary fields for TDEE calculation
        user_profile = supabase.table("user_profiles").select(
            "created_at, calorie_goal, weight_kg, height_cm, age, gender, activity_level"
        ).eq("user_id", user_id).execute()
        
        if not user_profile.data or len(user_profile.data) == 0:
            raise ValueError(f"User profile not found for user_id: {user_id}")
        
        profile = user_profile.data[0]
        calorie_goal = profile.get("calorie_goal", 2000)
        registration_date = datetime.fromisoformat(profile["created_at"]).date()
        today = date.today()
        
        # Calculate TDEE (daily baseline energy expenditure)
        weight_kg = profile.get("weight_kg", 70.0)
        height_cm = profile.get("height_cm", 170.0)
        age = profile.get("age", 30)
        gender = profile.get("gender", "male")
        activity_level = profile.get("activity_level", "moderate")
        
        tdee = CalorieCalculator.calculate_tdee(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            gender=gender,
            activity_level=activity_level
        )
        
        logger.info(f"User TDEE: {tdee} kcal/day (BMR + activity factor for {activity_level})")
        
        # Calculate actual active days
        days_since_registration = (today - registration_date).days + 1  # +1 to include today
        
        # Determine the actual period for averaging
        # If user is newer than requested period, use actual days since registration
        actual_days_for_average = min(days_since_registration, days)
        
        logger.info(f"User registered: {registration_date}, Days since: {days_since_registration}, Using {actual_days_for_average} days for average")
        
        # Get food and workout trends (still fetch full requested days for chart)
        food_trend = await get_food_trend_data(user_id, days)
        workout_trend = await get_workout_trend_data(user_id, days)
        
        # Create a map for quick lookup
        food_map = {item["date"]: item["calories"] for item in food_trend}
        workout_map = {item["date"]: item["calories_burned"] for item in workout_trend}
        
        # Generate all dates in the period (to include days with no data)
        date_map = {}
        for i in range(actual_days_for_average):
            current_date = today - timedelta(days=actual_days_for_average - 1 - i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            date_map[date_str] = {
                "date": date_str,
                "consumed": food_map.get(date_str, 0),
                "workout_calories": workout_map.get(date_str, 0),
                "goal": calorie_goal
            }
        
        # Calculate net and deficit for each day
        # Formula: consumed - (TDEE + workout_calories)
        trend_data = []
        for date_str in sorted(date_map.keys()):
            data = date_map[date_str]
            
            # Total burned = TDEE (baseline) + workout calories (active)
            total_burned = tdee + data["workout_calories"]
            
            # Net calories (positive = surplus, negative = deficit)
            net = data["consumed"] - total_burned
            
            # Deficit = total_burned - consumed
            # Positive deficit = burning more than eating (losing weight)
            # Negative deficit = eating more than burning (gaining weight)
            deficit = total_burned - data["consumed"]
            
            trend_data.append({
                "date": data["date"],
                "consumed": round(data["consumed"], 1),
                "burned": round(total_burned, 1),  # TDEE + workout
                "tdee": round(tdee, 1),
                "workout_calories": round(data["workout_calories"], 1),
                "net": round(net, 1),
                "goal": calorie_goal,
                "deficit": round(deficit, 1)
            })
        
        # Calculate summary statistics using actual_days_for_average as denominator
        total_consumed = sum(d["consumed"] for d in trend_data)
        total_burned = sum(d["burned"] for d in trend_data)
        total_deficit = sum(d["deficit"] for d in trend_data)
        
        # Use actual_days_for_average (not len(trend_data)) for proper daily average
        avg_consumed = total_consumed / actual_days_for_average if actual_days_for_average > 0 else 0
        avg_burned = total_burned / actual_days_for_average if actual_days_for_average > 0 else 0
        avg_deficit = total_deficit / actual_days_for_average if actual_days_for_average > 0 else 0
        
        return {
            "data": trend_data,
            "summary": {
                "avg_consumed": round(avg_consumed, 1),
                "avg_burned": round(avg_burned, 1),
                "avg_deficit": round(avg_deficit, 1),
                "total_deficit": round(total_deficit, 1),
                "days_used_for_average": actual_days_for_average,
                "days_since_registration": days_since_registration,
                "tdee": round(tdee, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting calorie balance trend: {e}")
        raise


async def calculate_daily_summary(user_id: str, target_date: date) -> Dict[str, Any]:
    """
    Calculate or update daily nutritional summary
    
    Args:
        user_id: User's ID
        target_date: Date to calculate summary for
        
    Returns:
        Dictionary with daily totals
    """
    try:
        supabase = get_supabase()
        
        # Get all food logs for the date
        result = supabase.table("food_logs").select("*").eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()
        
        # Calculate totals (default to 0 if no data)
        total_calories = sum(float(item.get("calories", 0)) for item in result.data) if result.data else 0
        total_protein = sum(float(item.get("protein", 0)) for item in result.data) if result.data else 0
        total_carbs = sum(float(item.get("carbs", 0)) for item in result.data) if result.data else 0
        total_fat = sum(float(item.get("fat", 0)) for item in result.data) if result.data else 0
        
        # Get workout count for the day
        workout_result = supabase.table("workout_logs").select("id").eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()
        workout_count = len(workout_result.data) if workout_result.data else 0
        
        # Get user's calorie goal
        user_result = supabase.table("user_profiles").select("calorie_goal").eq("user_id", user_id).execute()
        calorie_goal = user_result.data[0].get("calorie_goal") if user_result.data and len(user_result.data) > 0 else 2000
        
        summary_data = {
            "user_id": user_id,
            "date": target_date.isoformat(),
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "workout_count": workout_count,
            "calorie_goal": calorie_goal,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Upsert daily summary
        existing = supabase.table("daily_summaries").select("id").eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()
        
        if existing.data and len(existing.data) > 0:
            supabase.table("daily_summaries").update(summary_data).eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()
        else:
            summary_data["created_at"] = datetime.utcnow().isoformat()
            supabase.table("daily_summaries").insert(summary_data).execute()
        
        return summary_data
        
    except Exception as e:
        logger.error(f"Error calculating daily summary: {e}")
        raise


async def get_dashboard_stats(user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive dashboard statistics for user
    
    Args:
        user_id: User's ID
        
    Returns:
        Dictionary with dashboard data
    """
    try:
        today = date.today()
        
        # Get today's summary
        daily_summary = await calculate_daily_summary(user_id, today)
        
        # Get 7-day trends
        food_trend_7d = await get_food_trend_data(user_id, 7)
        
        # Get 30-day workout trends
        workout_trend_30d = await get_workout_trend_data(user_id, 30)
        
        # Calculate averages
        avg_calories_7d = sum(d["calories"] for d in food_trend_7d) / len(food_trend_7d) if food_trend_7d else 0
        total_workouts_30d = sum(d["workout_count"] for d in workout_trend_30d)
        avg_workouts_per_week = (total_workouts_30d / 30) * 7
        
        return {
            "today": daily_summary,
            "food_trend_7d": food_trend_7d,
            "workout_trend_30d": workout_trend_30d,
            "stats": {
                "avg_calories_7d": round(avg_calories_7d, 1),
                "total_workouts_30d": total_workouts_30d,
                "avg_workouts_per_week": round(avg_workouts_per_week, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise
