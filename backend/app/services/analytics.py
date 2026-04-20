import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from ..database import get_supabase, get_user_supabase
from .calorie_calculator import CalorieCalculator

logger = logging.getLogger(__name__)

_calorie_balance_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_CALORIE_BALANCE_CACHE_TTL_SECONDS = 60


def _coerce_float(value: Any, default: float) -> float:
    try:
        if value is None:
            raise ValueError("missing")
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int) -> int:
    try:
        if value is None:
            raise ValueError("missing")
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_str(value: Any, default: str) -> str:
    if value is None:
        return default
    normalized = str(value).strip()
    return normalized or default


def _coerce_created_at_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str) and value.strip():
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            pass

    return date.today()


def _calorie_balance_cache_key(user_id: str, days: int) -> str:
    return f"{user_id}:{days}"


def _read_calorie_balance_cache(user_id: str, days: int) -> Optional[Dict[str, Any]]:
    key = _calorie_balance_cache_key(user_id, days)
    cached = _calorie_balance_cache.get(key)
    if not cached:
        return None
    stored_at, response = cached
    if time.time() - stored_at > _CALORIE_BALANCE_CACHE_TTL_SECONDS:
        _calorie_balance_cache.pop(key, None)
        return None
    return response


def _write_calorie_balance_cache(user_id: str, days: int, response: Dict[str, Any]) -> None:
    _calorie_balance_cache[_calorie_balance_cache_key(user_id, days)] = (time.time(), response)


def invalidate_calorie_balance_cache(user_id: str) -> None:
    keys_to_delete = [key for key in _calorie_balance_cache if key.startswith(f"{user_id}:")]
    for key in keys_to_delete:
        _calorie_balance_cache.pop(key, None)


def _normalize_date_key(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, str) and value.strip():
        raw = value.strip()
        try:
            return date.fromisoformat(raw[:10])
        except ValueError:
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
            except ValueError:
                return None

    return None


def _is_degraded_daily_summary_row(row: Dict[str, Any]) -> bool:
    return any(
        row.get(field) is None
        for field in ("total_calories", "total_protein", "total_carbs", "total_fat")
    )


def _aggregate_food_log_rows(rows: List[Dict[str, Any]]) -> Dict[date, Dict[str, float]]:
    aggregated: Dict[date, Dict[str, float]] = {}

    for row in rows:
        row_date = _normalize_date_key(row.get("date"))
        if row_date is None:
            continue

        bucket = aggregated.setdefault(
            row_date,
            {
                "calories": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
            },
        )
        bucket["calories"] += _coerce_float(row.get("calories"), 0.0)
        bucket["protein"] += _coerce_float(row.get("protein"), 0.0)
        bucket["carbs"] += _coerce_float(row.get("carbs"), 0.0)
        bucket["fat"] += _coerce_float(row.get("fat"), 0.0)

    return aggregated


async def get_food_trend_data(
    user_id: str,
    days: int = 7,
    calorie_goal_override: float | None = None,
) -> List[Dict[str, Any]]:
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

        all_dates = [start_date + timedelta(days=x) for x in range(days)]
        daily_summary_rows: List[Dict[str, Any]] = []
        food_log_rollups: Dict[date, Dict[str, float]] = {}
        needs_food_log_fallback = False

        # Get daily summaries first; if they are missing, partial, or degraded for the
        # requested window we can repair the read with food_logs instead of returning
        # stale / zero-heavy data.
        try:
            result = supabase.table("daily_summaries").select("*").eq("user_id", user_id).gte('"date"', start_date.isoformat()).lte('"date"', end_date.isoformat()).order('"date"').execute()
            daily_summary_rows = result.data or []
        except Exception as summary_error:
            logger.warning(
                "Daily summaries unavailable for user %s (%s to %s); falling back to food logs: %s",
                user_id,
                start_date.isoformat(),
                end_date.isoformat(),
                summary_error,
            )
            needs_food_log_fallback = True

        daily_summaries_by_date: Dict[date, Dict[str, Any]] = {}
        for row in daily_summary_rows:
            row_date = _normalize_date_key(row.get("date"))
            if row_date is None or row_date < start_date or row_date > end_date:
                continue
            daily_summaries_by_date[row_date] = row

        if len(daily_summaries_by_date) < len(all_dates):
            needs_food_log_fallback = True

        if any(_is_degraded_daily_summary_row(row) for row in daily_summaries_by_date.values()):
            needs_food_log_fallback = True

        if needs_food_log_fallback:
            food_logs_result = supabase.table("food_logs").select("date, calories, protein, carbs, fat").eq("user_id", user_id).gte('"date"', start_date.isoformat()).lte('"date"', end_date.isoformat()).execute()
            food_log_rollups = _aggregate_food_log_rows(food_logs_result.data or [])

        # Get user's calorie goal only when it was not already loaded by caller.
        if calorie_goal_override is not None:
            calorie_goal = calorie_goal_override
        else:
            user_result = supabase.table("user_profiles").select("calorie_goal").eq("user_id", user_id).execute()
            calorie_goal = user_result.data[0].get("calorie_goal") if user_result.data and len(user_result.data) > 0 else 2000

        trend_data = []
        for current_date in all_dates:
            summary_row = daily_summaries_by_date.get(current_date)
            fallback_row = food_log_rollups.get(current_date, {})
            prefer_food_log_rollup = needs_food_log_fallback and bool(fallback_row)

            trend_data.append({
                "date": current_date.isoformat(),
                "calories": _coerce_float(
                    None if prefer_food_log_rollup else (summary_row.get("total_calories") if summary_row else None),
                    _coerce_float(fallback_row.get("calories"), 0.0),
                ),
                "protein": _coerce_float(
                    None if prefer_food_log_rollup else (summary_row.get("total_protein") if summary_row else None),
                    _coerce_float(fallback_row.get("protein"), 0.0),
                ),
                "carbs": _coerce_float(
                    None if prefer_food_log_rollup else (summary_row.get("total_carbs") if summary_row else None),
                    _coerce_float(fallback_row.get("carbs"), 0.0),
                ),
                "fat": _coerce_float(
                    None if prefer_food_log_rollup else (summary_row.get("total_fat") if summary_row else None),
                    _coerce_float(fallback_row.get("fat"), 0.0),
                ),
                "goal": calorie_goal,
            })

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


async def get_calorie_balance_trend(
    user_id: str,
    days: int = 7,
    profile: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
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
        cached = _read_calorie_balance_cache(user_id, days)
        if cached is not None:
            return cached

        profile_data = profile

        if not profile_data:
            supabase = get_supabase()
            user_profile = supabase.table("user_profiles").select(
                "created_at, calorie_goal, weight_kg, height_cm, age, gender, activity_level"
            ).eq("user_id", user_id).execute()

            if not user_profile.data or len(user_profile.data) == 0:
                raise ValueError(f"User profile not found for user_id: {user_id}")

            profile_data = user_profile.data[0]

        if not profile_data:
            raise ValueError(f"User profile not found for user_id: {user_id}")

        calorie_goal = _coerce_float(profile_data.get("calorie_goal"), 2000.0)
        registration_date = _coerce_created_at_date(profile_data.get("created_at"))
        today = date.today()
        
        # Calculate TDEE (daily baseline energy expenditure)
        weight_kg = _coerce_float(profile_data.get("weight_kg"), 70.0)
        height_cm = _coerce_float(profile_data.get("height_cm"), 170.0)
        age = _coerce_int(profile_data.get("age"), 30)
        gender = _coerce_str(profile_data.get("gender"), "male")
        activity_level = _coerce_str(profile_data.get("activity_level"), "moderate")
        
        tdee = CalorieCalculator.calculate_tdee(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            gender=gender,
            activity_level=activity_level
        )
        
        # Calculate actual active days
        days_since_registration = (today - registration_date).days + 1  # +1 to include today
        
        # Determine the actual period for averaging
        # If user is newer than requested period, use actual days since registration
        actual_days_for_average = min(days_since_registration, days)
        
        # Get food and workout trends (still fetch full requested days for chart)
        food_trend, workout_trend = await asyncio.gather(
            get_food_trend_data(user_id, days, calorie_goal_override=calorie_goal),
            get_workout_trend_data(user_id, days),
        )
        
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
        
        response = {
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
        _write_calorie_balance_cache(user_id, days, response)
        return response
        
    except Exception as e:
        logger.error(f"Error getting calorie balance trend: {e}")
        raise


async def calculate_daily_summary(
    user_id: str,
    target_date: date,
    access_token: str | None = None,
) -> Dict[str, Any]:
    """
    Calculate or update daily nutritional summary
    
    Args:
        user_id: User's ID
        target_date: Date to calculate summary for
        
    Returns:
        Dictionary with daily totals
    """
    try:
        supabase = get_user_supabase(access_token) if access_token else get_supabase()
        
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
        
        # Upsert daily summary. Some local/dev environments run with a less-privileged
        # Supabase key, so persistence may fail under RLS even though the computed
        # summary itself is still perfectly usable for the dashboard response.
        try:
            existing = supabase.table("daily_summaries").select("id").eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()

            if existing.data and len(existing.data) > 0:
                supabase.table("daily_summaries").update(summary_data).eq("user_id", user_id).eq('"date"', target_date.isoformat()).execute()
            else:
                summary_data["created_at"] = datetime.utcnow().isoformat()
                supabase.table("daily_summaries").insert(summary_data).execute()
        except Exception as persistence_error:
            logger.warning(
                "Daily summary persistence degraded for user %s on %s: %s",
                user_id,
                target_date.isoformat(),
                persistence_error,
            )
        
        return summary_data
        
    except Exception as e:
        logger.error(f"Error calculating daily summary: {e}")
        raise


async def get_dashboard_stats(
    user_id: str,
    access_token: str | None = None,
) -> Dict[str, Any]:
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
        daily_summary = await calculate_daily_summary(
            user_id,
            today,
            access_token=access_token,
        )
        
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
