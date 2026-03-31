"""Pydantic schemas for the Goal Planner wizard endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Any


# ── Tier comparison ──────────────────────────────────────────────────────────

class TierRequest(BaseModel):
    current_weight_kg: float = Field(..., gt=0)
    current_bf_pct: float = Field(..., ge=3, le=60)
    target_weight_kg: Optional[float] = Field(None, gt=0)
    target_bf_pct: float = Field(..., ge=3, le=60)
    gender: Literal["male", "female"]
    age: int = Field(..., ge=10, le=100)
    height_cm: float = Field(..., gt=0)
    activity_level: Literal[
        "sedentary", "light", "moderate", "active", "very_active"
    ] = "moderate"


class MonthMilestone(BaseModel):
    month: int
    projected_weight_kg: float
    projected_bf_pct: float
    fat_lost_kg: float
    lean_mass_kg: float


class TierInfo(BaseModel):
    deficit_or_surplus: int = Field(description="Positive = surplus, negative = deficit")
    daily_calories: int
    weekly_change_kg: float = Field(description="Negative = loss, positive = gain")
    weeks_to_goal: int
    monthly_milestones: List[MonthMilestone]
    safety_note: str


class TierComparisonResponse(BaseModel):
    tdee: int
    bmr: int
    direction: Literal["deficit", "surplus"]
    tiers: List[TierInfo]


# ── Macro split ──────────────────────────────────────────────────────────────

class MacroRequest(BaseModel):
    daily_calories: int = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    preset: Optional[Literal[
        "balanced", "high_protein", "keto", "low_fat"
    ]] = None
    carb_pct: Optional[float] = Field(None, ge=0, le=100)
    protein_pct: Optional[float] = Field(None, ge=0, le=100)
    fat_pct: Optional[float] = Field(None, ge=0, le=100)


class MacroBreakdown(BaseModel):
    carb_pct: float
    protein_pct: float
    fat_pct: float
    carb_g: int
    protein_g: int
    fat_g: int
    calories_check: int = Field(description="Recalculated cal from grams")


class MacroResponse(BaseModel):
    preset_used: Optional[str]
    breakdown: MacroBreakdown


# ── Food suggestions ─────────────────────────────────────────────────────────

class FoodSuggestionRequest(BaseModel):
    protein_g: int = Field(..., ge=0)
    carb_g: int = Field(..., ge=0)
    fat_g: int = Field(..., ge=0)
    priority: Literal["protein", "carb", "fat", "balanced"] = "balanced"
    categories: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)


class FoodItem(BaseModel):
    id: str
    name: str
    category: str
    calories_per_100g: float
    protein_per_100g: float
    carb_per_100g: float
    fat_per_100g: float
    density_score: float = Field(description="Score based on priority macro per calorie")
    common_serving: Optional[str] = None
    common_serving_g: Optional[float] = None


class FoodSuggestionResponse(BaseModel):
    priority: str
    foods: List[FoodItem]
    total_available: int


# ── Dish composition ─────────────────────────────────────────────────────────

class DishIngredient(BaseModel):
    food_id: str
    amount_g: float = Field(..., gt=0)


class DishRequest(BaseModel):
    ingredients: List[DishIngredient]
    target_calories: Optional[int] = None
    target_protein_g: Optional[int] = None
    target_carb_g: Optional[int] = None
    target_fat_g: Optional[int] = None
    meals_per_day: int = Field(3, ge=1, le=8)


class IngredientNutrition(BaseModel):
    food_id: str
    food_name: str
    amount_g: float
    calories: float
    protein_g: float
    carb_g: float
    fat_g: float


class MealSuggestion(BaseModel):
    meal_label: str
    ingredients: List[IngredientNutrition]
    total_calories: float
    total_protein_g: float
    total_carb_g: float
    total_fat_g: float


class DishResponse(BaseModel):
    meals: List[MealSuggestion]
    day_total_calories: float
    day_total_protein_g: float
    day_total_carb_g: float
    day_total_fat_g: float
    target_diff: Optional[dict] = Field(
        None, description="Difference vs targets {calories, protein_g, carb_g, fat_g}"
    )


# ── Auto meal-plan recommendation ────────────────────────────────────────────

class MealPlanRequest(BaseModel):
    daily_calories: int = Field(..., gt=0)
    protein_g: int = Field(..., ge=0)
    carb_g: int = Field(..., ge=0)
    fat_g: int = Field(..., ge=0)
    meals_per_day: int = Field(3, ge=2, le=5)


class MealPlanResponse(BaseModel):
    meals: List[MealSuggestion]
    day_total_calories: float
    day_total_protein_g: float
    day_total_carb_g: float
    day_total_fat_g: float
    target_diff: Optional[dict] = None


# ── Exercise routine ─────────────────────────────────────────────────────────

class ExerciseRoutineRequest(BaseModel):
    mode: Literal["cut", "lean_bulk", "mass_gain", "recomp"]
    gender: Literal["male", "female"]
    experience: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    available_equipment: Optional[List[str]] = None
    sessions_per_week: Optional[int] = Field(None, ge=1, le=7)


class ExerciseDetail(BaseModel):
    name: str
    muscle_group: str
    equipment: str
    exercise_type: Literal["compound", "isolation"]
    sets: int
    reps_min: int
    reps_max: int
    rest_seconds: int
    tempo: Optional[str] = Field(None, description="e.g. 3-1-2-0")
    notes: Optional[str] = None


class WorkoutDay(BaseModel):
    day_label: str
    focus: str
    exercises: List[ExerciseDetail]
    estimated_duration_min: int


class ExerciseRoutineResponse(BaseModel):
    split_type: str
    sessions_per_week: int
    days: List[WorkoutDay]
    progression_scheme: str
    deload_note: str


# ── Cardio plan ──────────────────────────────────────────────────────────────

class CardioRequest(BaseModel):
    weight_kg: float = Field(..., gt=0)
    gender: Literal["male", "female"]
    height_cm: float = Field(..., gt=0)
    age: int = Field(..., ge=10, le=100)
    target_calories: int = Field(..., gt=0)
    preferred_activities: Optional[List[str]] = None


class CardioOption(BaseModel):
    activity: str
    met_value: float
    duration_minutes: int
    calories_burned: int
    intensity: str


class CardioResponse(BaseModel):
    target_calories: int
    options: List[CardioOption]


# ── Persisted wizard state (Supabase saved_goal_plans.plan_data) ─────────────

class SaveGoalPlanRequest(BaseModel):
    plan: dict[str, Any]


class SaveGoalPlanResponse(BaseModel):
    status: Literal["ok"] = "ok"
    updated_at: str


class GetSavedGoalPlanResponse(BaseModel):
    plan: dict[str, Any]
    updated_at: str
