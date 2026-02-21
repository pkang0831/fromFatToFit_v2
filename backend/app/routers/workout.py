from fastapi import APIRouter, HTTPException, status, Depends
import logging
from datetime import date, datetime
from typing import List, Optional
from ..schemas.workout_schemas import (
    ExerciseLibraryItem, WorkoutLogCreate, WorkoutLogResponse,
    FormAnalysisRequest, FormAnalysisResponse, WorkoutTrendResponse
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services.openai_service import analyze_workout_form_video
from ..services.usage_limiter import check_usage_limit
from ..services.analytics import get_workout_trend_data
from ..services.payment_service import check_premium_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/exercises/library", response_model=List[ExerciseLibraryItem])
async def get_exercise_library(
    category: str = None,
    current_user: dict = Depends(get_current_user)
):
    """Get exercise library with form guides"""
    try:
        supabase = get_supabase()
        
        query = supabase.table("exercise_library").select("*")
        
        if category:
            query = query.ilike("category", category)
        
        result = query.order("name").execute()
        
        return [ExerciseLibraryItem(**ex) for ex in result.data]
        
    except Exception as e:
        logger.error(f"Error getting exercise library: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def calculate_workout_calories(
    user_id: str,
    exercise_id: str,
    sets: List,
    duration_minutes: Optional[int]
) -> float:
    """Calculate calories burned for a workout"""
    try:
        supabase = get_supabase()
        
        # Get user profile
        profile_result = supabase.table("user_profiles").select("weight_kg").eq("user_id", user_id).single().execute()
        
        if not profile_result.data or not profile_result.data.get('weight_kg'):
            weight_kg = 70.0  # Default weight
            logger.info(f"Using default weight 70kg for user {user_id}")
        else:
            weight_kg = float(profile_result.data['weight_kg'])
            logger.info(f"Using user weight: {weight_kg}kg")
        
        # Get exercise info
        exercise_result = supabase.table("exercise_library").select("met_value, exercise_type").eq("id", exercise_id).single().execute()
        
        if not exercise_result.data:
            logger.warning(f"No exercise found for id {exercise_id}, using default MET")
            met_value = 5.0
            exercise_type = 'strength'
        else:
            exercise = exercise_result.data
            met_value = float(exercise.get('met_value', 5.0))
            exercise_type = exercise.get('exercise_type', 'strength')
            logger.info(f"Exercise: type={exercise_type}, MET={met_value}")
        
        # Simple calorie calculation
        # Formula: Calories = MET × weight(kg) × time(hours)
        calories = 0.0
        
        if exercise_type == 'cardio':
            # Cardio: requires duration
            if duration_minutes and duration_minutes > 0:
                calories = met_value * weight_kg * (duration_minutes / 60.0)
                logger.info(f"Cardio calculation: {met_value} × {weight_kg} × {duration_minutes/60.0} = {calories}")
            else:
                logger.warning("Cardio exercise without duration")
        else:
            # Strength: estimate duration or use provided
            if not duration_minutes or duration_minutes <= 0:
                # Estimate: 3-5 minutes per set
                estimated_duration = len(sets) * 4 if sets else 15
            else:
                estimated_duration = duration_minutes
            
            calories = met_value * weight_kg * (estimated_duration / 60.0)
            logger.info(f"Strength calculation: {met_value} × {weight_kg} × {estimated_duration/60.0} = {calories}")
        
        return round(calories, 1)
        
    except Exception as e:
        logger.error(f"Error calculating calories: {e}", exc_info=True)
        return 0.0


@router.post("/log", response_model=WorkoutLogResponse, status_code=status.HTTP_201_CREATED)
async def log_workout(
    workout_log: WorkoutLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Log a workout session with automatic calorie calculation"""
    try:
        supabase = get_supabase()
        
        # Calculate calories burned
        calories_burned = await calculate_workout_calories(
            user_id=current_user["id"],
            exercise_id=workout_log.exercise_id,
            sets=[s.model_dump() for s in workout_log.sets],
            duration_minutes=workout_log.duration_minutes
        )
        
        log_data = {
            "user_id": current_user["id"],
            **workout_log.model_dump(),
            "date": workout_log.date.isoformat(),
            "sets": [s.model_dump() for s in workout_log.sets],
            "calories_burned": calories_burned,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("workout_logs").insert(log_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create workout log")
        
        created_log = result.data[0]
        return WorkoutLogResponse(**created_log)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging workout: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/logs/{target_date}", response_model=List[WorkoutLogResponse])
async def get_workout_logs(
    target_date: date,
    current_user: dict = Depends(get_current_user)
):
    """Get all workout logs for a specific date"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("workout_logs").select("*").eq("user_id", current_user["id"]).eq("date", target_date.isoformat()).order("created_at").execute()
        
        return [WorkoutLogResponse(**log) for log in result.data]
        
    except Exception as e:
        logger.error(f"Error getting workout logs: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/logs-range", response_model=List[WorkoutLogResponse])
async def get_workout_logs_range(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all workout logs for a date range (bulk query - 10x faster than individual calls)"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("workout_logs").select("*").eq(
            "user_id", current_user["id"]
        ).gte(
            "date", start_date
        ).lte(
            "date", end_date
        ).order(
            "date", desc=True
        ).order(
            "created_at", desc=False
        ).execute()
        
        logger.info(f"Fetched {len(result.data)} workout logs for date range {start_date} to {end_date}")
        return [WorkoutLogResponse(**log) for log in result.data]
        
    except Exception as e:
        logger.error(f"Error getting workout logs range: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/trends", response_model=WorkoutTrendResponse)
async def get_workout_trends(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get workout trends for specified days"""
    try:
        trend_data = await get_workout_trend_data(current_user["id"], days)
        
        total_workouts = sum(d["workout_count"] for d in trend_data)
        avg_per_week = (total_workouts / days) * 7 if days > 0 else 0
        
        return WorkoutTrendResponse(
            data=trend_data,
            total_workouts=total_workouts,
            average_per_week=round(avg_per_week, 1),
            days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting workout trends: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/analyze-form", response_model=FormAnalysisResponse)
async def analyze_workout_form(
    request: FormAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze workout form from video (Premium only)"""
    try:
        # This feature is premium only
        is_premium = await check_premium_status(current_user["id"])
        
        try:
            usage_info = await check_usage_limit(current_user["id"], "form_check", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Form analysis requires premium subscription"
            )
        
        # Analyze video with OpenAI
        analysis_result = await analyze_workout_form_video(request.video_base64, request.exercise_name)
        
        return FormAnalysisResponse(
            exercise_name=request.exercise_name,
            form_score=analysis_result["form_score"],
            issues_detected=analysis_result["issues_detected"],
            corrections=analysis_result["corrections"],
            overall_feedback=analysis_result["overall_feedback"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing form: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Form analysis failed")


@router.delete("/log/{log_id}")
async def delete_workout_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a workout log entry"""
    try:
        supabase = get_supabase()
        
        result = supabase.table("workout_logs").delete().eq("id", log_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout log not found")
        
        return {"message": "Workout log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workout log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
