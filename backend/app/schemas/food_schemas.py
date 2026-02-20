from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class FoodLogCreate(BaseModel):
    date: date
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack")
    food_name: str
    calories: float
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    serving_size: Optional[str] = None
    source: str = Field(default="manual", description="manual or ai")
    image_url: Optional[str] = None


class FoodLogResponse(BaseModel):
    id: str
    user_id: str
    date: date
    meal_type: str
    food_name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: Optional[str]
    source: str
    image_url: Optional[str]
    created_at: datetime


class FoodAnalysisRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image")


class FoodItem(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: Optional[str] = None


class FoodAnalysisResponse(BaseModel):
    items: List[FoodItem]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    analysis_confidence: str = Field(default="medium", description="low, medium, high")
    usage_remaining: int


class DailySummaryResponse(BaseModel):
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    calorie_goal: Optional[float]
    meals: List[FoodLogResponse]


class TrendDataPoint(BaseModel):
    date: date
    calories: float
    protein: float
    carbs: float
    fat: float
    goal: Optional[float]


class TrendResponse(BaseModel):
    data: List[TrendDataPoint]
    average_calories: float
    days: int
