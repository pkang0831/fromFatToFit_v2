"""Goal Planner wizard endpoints.

Each endpoint corresponds to a step in the interactive goal-planning wizard.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status, Depends
import logging

from ..middleware.auth_middleware import get_current_user
from ..rate_limit import limiter
from ..database import get_supabase, get_user_supabase
from ..schemas.goal_plan_schemas import (
    TierRequest, TierComparisonResponse,
    MacroRequest, MacroResponse,
    FoodSuggestionRequest, FoodSuggestionResponse,
    DishRequest, DishResponse,
    MealPlanRequest, MealPlanResponse,
    ExerciseRoutineRequest, ExerciseRoutineResponse,
    CardioRequest, CardioResponse,
    SaveGoalPlanRequest, SaveGoalPlanResponse, GetSavedGoalPlanResponse,
)
from ..services.goal_plan_service import (
    calculate_tier_comparison,
    calculate_macro_split,
    suggest_whole_foods,
    compose_dishes,
    auto_recommend_meal_plan,
)
from ..services.exercise_plan_service import (
    build_structured_routine,
    calculate_cardio_duration,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/tiers", response_model=TierComparisonResponse)
@limiter.limit("30/minute")
async def compare_tiers(
    body: TierRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 2: Compare 4 caloric tiers (300/500/700/1000 cal deficit or surplus)."""
    try:
        result = calculate_tier_comparison(
            current_weight_kg=body.current_weight_kg,
            current_bf_pct=body.current_bf_pct,
            target_bf_pct=body.target_bf_pct,
            gender=body.gender,
            age=body.age,
            height_cm=body.height_cm,
            activity_level=body.activity_level,
            target_weight_kg=body.target_weight_kg,
        )
        return result
    except Exception as e:
        logger.error(f"Tier comparison failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/macros", response_model=MacroResponse)
@limiter.limit("30/minute")
async def macro_breakdown(
    body: MacroRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 4: Calculate macro grams from daily calories + C/P/F ratio."""
    try:
        result = calculate_macro_split(
            daily_calories=body.daily_calories,
            weight_kg=body.weight_kg,
            preset=body.preset,
            carb_pct=body.carb_pct,
            protein_pct=body.protein_pct,
            fat_pct=body.fat_pct,
        )
        return result
    except Exception as e:
        logger.error(f"Macro breakdown failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/foods", response_model=FoodSuggestionResponse)
@limiter.limit("30/minute")
async def suggest_foods(
    body: FoodSuggestionRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 5a: Suggest whole foods matching macro targets."""
    try:
        result = suggest_whole_foods(
            protein_g=body.protein_g,
            carb_g=body.carb_g,
            fat_g=body.fat_g,
            priority=body.priority,
            categories=body.categories,
            limit=body.limit,
        )
        return result
    except Exception as e:
        logger.error(f"Food suggestion failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/dishes", response_model=DishResponse)
@limiter.limit("30/minute")
async def compose_dish(
    body: DishRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 6: Compose dishes from selected foods and show per-meal nutrition."""
    try:
        ingredients = [{"food_id": i.food_id, "amount_g": i.amount_g} for i in body.ingredients]
        result = compose_dishes(
            ingredients=ingredients,
            meals_per_day=body.meals_per_day,
            target_calories=body.target_calories,
            target_protein_g=body.target_protein_g,
            target_carb_g=body.target_carb_g,
            target_fat_g=body.target_fat_g,
        )
        return result
    except Exception as e:
        logger.error(f"Dish composition failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/recommend-meals", response_model=MealPlanResponse)
@limiter.limit("30/minute")
async def recommend_meals(
    body: MealPlanRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Auto-recommend a full day meal plan matching macro targets."""
    try:
        result = auto_recommend_meal_plan(
            daily_calories=body.daily_calories,
            protein_g=body.protein_g,
            carb_g=body.carb_g,
            fat_g=body.fat_g,
            meals_per_day=body.meals_per_day,
        )
        return result
    except Exception as e:
        logger.error(f"Meal recommendation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/exercise", response_model=ExerciseRoutineResponse)
@limiter.limit("30/minute")
async def exercise_routine(
    body: ExerciseRoutineRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 5b: Generate structured exercise routine with sets/reps/equipment."""
    try:
        result = build_structured_routine(
            mode=body.mode,
            gender=body.gender,
            experience=body.experience,
            available_equipment=body.available_equipment,
            sessions_per_week=body.sessions_per_week,
        )
        return result
    except Exception as e:
        logger.error(f"Exercise routine failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/cardio", response_model=CardioResponse)
@limiter.limit("30/minute")
async def cardio_plan(
    body: CardioRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Step 7: Calculate cardio durations for target calorie burn."""
    try:
        result = calculate_cardio_duration(
            weight_kg=body.weight_kg,
            gender=body.gender,
            height_cm=body.height_cm,
            age=body.age,
            target_calories=body.target_calories,
            preferred_activities=body.preferred_activities,
        )
        return result
    except Exception as e:
        logger.error(f"Cardio plan failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/saved-plan", response_model=SaveGoalPlanResponse)
@limiter.limit("20/minute")
async def save_goal_plan(
    body: SaveGoalPlanRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Upsert the user's full goal planner snapshot to `saved_goal_plans`."""
    user_id = current_user["id"]
    now = datetime.now(timezone.utc).isoformat()
    supabase = get_user_supabase(current_user["access_token"])
    try:
        existing = (
            supabase.table("saved_goal_plans")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            supabase.table("saved_goal_plans").update(
                {"plan_data": body.plan, "updated_at": now}
            ).eq("user_id", user_id).execute()
        else:
            supabase.table("saved_goal_plans").insert(
                {"user_id": user_id, "plan_data": body.plan, "updated_at": now}
            ).execute()
        return SaveGoalPlanResponse(updated_at=now)
    except Exception as e:
        logger.error(f"Save goal plan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save goal plan",
        )


@router.get("/saved-plan", response_model=GetSavedGoalPlanResponse)
@limiter.limit("60/minute")
async def get_saved_goal_plan(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """Return the user's saved planner JSON, or 404 if none."""
    user_id = current_user["id"]
    supabase = get_user_supabase(current_user["access_token"])
    try:
        result = (
            supabase.table("saved_goal_plans")
            .select("plan_data, updated_at")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No saved goal plan",
            )
        row = result.data[0]
        return GetSavedGoalPlanResponse(
            plan=row["plan_data"],
            updated_at=row["updated_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get goal plan failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load saved goal plan",
        )
