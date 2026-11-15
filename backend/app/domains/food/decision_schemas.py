"""
Schemas for food decision and recommendation features
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date


# Should I Eat Request/Response
class ShouldIEatRequest(BaseModel):
    """Request to analyze if user should eat the food"""
    image_base64: str = Field(..., description="Base64 encoded food image")


class DecisionReason(BaseModel):
    """Reason for the decision"""
    type: Literal["calorie", "macro", "sodium", "sugar", "timing", "allergy"]
    message: str
    severity: Literal["info", "warning", "critical"]


class FoodItemAnalysis(BaseModel):
    """Individual food item from AI analysis"""
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: Optional[str] = None
    sodium: Optional[float] = None
    sugar: Optional[float] = None


class ImpactAnalysis(BaseModel):
    """Impact of eating this food"""
    calories_used_percentage: float
    remaining_calories: float
    remaining_protein: float
    remaining_carbs: float
    remaining_fat: float


class CurrentDailyStats(BaseModel):
    """Current day's nutrition stats"""
    consumed_calories: float
    consumed_protein: float
    consumed_carbs: float
    consumed_fat: float
    calorie_goal: float
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None


class AlternativeFood(BaseModel):
    """Alternative food suggestion"""
    food_id: str
    name: str
    category: str
    calories: float
    protein: float
    carbs: float
    fat: float
    reason: str


class ShouldIEatResponse(BaseModel):
    """Response with decision and recommendations"""
    # Decision
    decision: Literal["green", "yellow", "red"]
    decision_text: str
    
    # Food Analysis
    food_items: List[FoodItemAnalysis]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_sodium: Optional[float] = None
    total_sugar: Optional[float] = None
    
    # Impact Analysis
    impact: ImpactAnalysis
    reasons: List[DecisionReason]
    
    # Recommendations
    ai_advice: str
    alternatives: Optional[List[AlternativeFood]] = None
    
    # Context
    current_stats: CurrentDailyStats
    confidence: str


# Food Recommendation Request/Response
class RecommendationRequest(BaseModel):
    """Request for food recommendations"""
    just_ate_food_id: Optional[str] = None
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"]
    target_date: Optional[date] = None


class FoodRecommendation(BaseModel):
    """Individual food recommendation"""
    food_id: str
    food_name: str
    category: str
    calories: float
    protein: float
    carbs: float
    fat: float
    serving_size: str
    reason: str
    match_score: float


class RemainingMacros(BaseModel):
    """Remaining macros for the day"""
    calories: float
    protein: float
    carbs: float
    fat: float


class RecommendationResponse(BaseModel):
    """Response with food recommendations"""
    meal_type: str
    remaining: RemainingMacros
    recommendations: List[FoodRecommendation]
    ai_explanation: str


# User Preferences
class UserFoodPreferences(BaseModel):
    """User food preferences and restrictions"""
    favorite_foods: List[str] = Field(default_factory=list)
    disliked_foods: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    avoid_high_sodium: bool = False
    avoid_high_sugar: bool = False
    prefer_high_protein: bool = False


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences"""
    favorite_foods: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    avoid_high_sodium: Optional[bool] = None
    avoid_high_sugar: Optional[bool] = None
    prefer_high_protein: Optional[bool] = None
