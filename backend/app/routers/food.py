from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
import logging
from datetime import date, datetime
from typing import List
import base64
from ..schemas.food_schemas import (
    FoodLogCreate, FoodLogResponse, FoodAnalysisRequest, FoodAnalysisResponse,
    DailySummaryResponse, TrendResponse
)
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..services.ai_vision_service import analyze_food_image
from ..services.usage_limiter import check_usage_limit, increment_usage
from ..services.analytics import get_food_trend_data, calculate_daily_summary
from ..services.payment_service import check_premium_status

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/log", response_model=FoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_food(
    food_log: FoodLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Log a food entry manually"""
    try:
        supabase = get_supabase()
        
        log_data = {
            "user_id": current_user["id"],
            **food_log.model_dump(),
            "date": food_log.date.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("food_logs").insert(log_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create food log")
        
        # Recalculate daily summary
        await calculate_daily_summary(current_user["id"], food_log.date)
        
        created_log = result.data[0]
        return FoodLogResponse(**created_log)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging food: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/analyze-photo", response_model=FoodAnalysisResponse)
async def analyze_food_photo(
    request: FoodAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze food photo using AI (usage-limited for free users)"""
    try:
        # Check if user is premium
        is_premium = await check_premium_status(current_user["id"])
        
        # Check usage limit
        try:
            usage_info = await check_usage_limit(current_user["id"], "food_scan", is_premium)
        except Exception as usage_error:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(usage_error)
            )
        
        # Analyze image with AI (hybrid strategy based on user tier)
        user_tier = "premium" if is_premium else "free"
        analysis_result = await analyze_food_image(request.image_base64, user_tier=user_tier)
        
        # Increment usage count
        if not is_premium:
            await increment_usage(current_user["id"], "food_scan")
        
        # Get updated usage info
        updated_usage = await check_usage_limit(current_user["id"], "food_scan", is_premium)
        
        return FoodAnalysisResponse(
            items=analysis_result["items"],
            total_calories=analysis_result["total_calories"],
            total_protein=analysis_result["total_protein"],
            total_carbs=analysis_result["total_carbs"],
            total_fat=analysis_result["total_fat"],
            analysis_confidence=analysis_result.get("confidence", "medium"),
            usage_remaining=updated_usage["remaining"] if updated_usage["remaining"] != -1 else 999
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing food photo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Food analysis failed")


@router.get("/daily/{target_date}", response_model=DailySummaryResponse)
async def get_daily_food(
    target_date: date,
    current_user: dict = Depends(get_current_user)
):
    """Get all food logs and summary for a specific date"""
    try:
        supabase = get_supabase()
        
        # Get food logs
        result = supabase.table("food_logs").select("*").eq("user_id", current_user["id"]).eq("date", target_date.isoformat()).order("created_at").execute()
        
        meals = [FoodLogResponse(**log) for log in result.data]
        
        # Calculate totals
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        
        return DailySummaryResponse(
            date=target_date,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fat=total_fat,
            calorie_goal=current_user.get("calorie_goal"),
            meals=meals
        )
        
    except Exception as e:
        logger.error(f"Error getting daily food: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/trends", response_model=TrendResponse)
async def get_food_trends(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    """Get food/calorie trends for specified days"""
    try:
        trend_data = await get_food_trend_data(current_user["id"], days)
        
        avg_calories = sum(d["calories"] for d in trend_data) / len(trend_data) if trend_data else 0
        
        return TrendResponse(
            data=trend_data,
            average_calories=round(avg_calories, 1),
            days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting food trends: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/recent")
async def get_recent_foods(
    days: int = 7,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recent unique food items for quick logging"""
    try:
        supabase = get_supabase()
        from datetime import timedelta
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get recent food logs
        result = supabase.table("food_logs").select("*").eq(
            "user_id", current_user["id"]
        ).gte(
            '"date"', start_date.isoformat()
        ).order(
            "created_at", desc=True
        ).execute()
        
        if not result.data:
            return {"recent_foods": []}
        
        # Track unique foods by name (keep most recent occurrence)
        seen_foods = {}
        for log in result.data:
            food_name = log.get("food_name", "")
            if food_name and food_name not in seen_foods:
                seen_foods[food_name] = {
                    "food_name": log.get("food_name"),
                    "calories": log.get("calories"),
                    "protein": log.get("protein"),
                    "carbs": log.get("carbs"),
                    "fat": log.get("fat"),
                    "serving_size": log.get("serving_size"),
                    "meal_type": log.get("meal_type"),
                    "last_logged": log.get("created_at")
                }
                
                if len(seen_foods) >= limit:
                    break
        
        recent_foods = list(seen_foods.values())
        
        return {"recent_foods": recent_foods}
        
    except Exception as e:
        logger.error(f"Error getting recent foods: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/log/{log_id}", response_model=FoodLogResponse)
async def update_food_log(
    log_id: str,
    food_log: FoodLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update a food log entry"""
    try:
        supabase = get_supabase()
        
        # Verify the log exists and belongs to the user
        existing_log = supabase.table("food_logs").select("*").eq("id", log_id).eq("user_id", current_user["id"]).execute()
        
        if not existing_log.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food log not found")
        
        # Update the log
        update_data = {
            **food_log.model_dump(),
            "date": food_log.date.isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("food_logs").update(update_data).eq("id", log_id).eq("user_id", current_user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update food log")
        
        # Recalculate daily summary for the date
        await calculate_daily_summary(current_user["id"], food_log.date)
        
        updated_log = result.data[0]
        return FoodLogResponse(**updated_log)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating food log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/log/{log_id}")
async def delete_food_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a food log entry"""
    try:
        supabase = get_supabase()
        
        # Get the log to find its date
        log_result = supabase.table("food_logs").select("date").eq("id", log_id).eq("user_id", current_user["id"]).execute()
        
        if not log_result.data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food log not found")
        
        log_date = date.fromisoformat(log_result.data[0]["date"])
        
        # Delete the log
        supabase.table("food_logs").delete().eq("id", log_id).eq("user_id", current_user["id"]).execute()
        
        # Recalculate daily summary
        await calculate_daily_summary(current_user["id"], log_date)
        
        return {"message": "Food log deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting food log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
