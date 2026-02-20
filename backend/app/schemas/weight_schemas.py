"""
Weight Tracking Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class WeightLogCreate(BaseModel):
    """Schema for creating a weight log entry"""
    date: date
    weight_kg: float = Field(..., gt=0, le=500)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class WeightLogUpdate(BaseModel):
    """Schema for updating a weight log entry"""
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class WeightLogResponse(BaseModel):
    """Schema for weight log response"""
    id: str
    user_id: str
    date: date
    weight_kg: float
    body_fat_percentage: Optional[float]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class GoalUpdate(BaseModel):
    """Schema for updating weight/body fat goals"""
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    target_body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)


class MovingAveragePoint(BaseModel):
    """Single point in moving average trend"""
    date: date
    weight_kg: float
    body_fat_percentage: Optional[float]
    moving_avg_weight: float
    moving_avg_body_fat: Optional[float]


class ProjectionPoint(BaseModel):
    """Single point in goal projection"""
    date: date
    projected_weight: float
    projected_body_fat: Optional[float]
    is_goal_reached: bool


class GoalProjectionResponse(BaseModel):
    """Complete goal projection response"""
    current_weight: float
    current_body_fat: Optional[float]
    target_weight: Optional[float]
    target_body_fat: Optional[float]
    
    # 3-day moving averages
    moving_avg_weight: float
    moving_avg_body_fat: Optional[float]
    
    # Daily rate of change (based on 3-day MA)
    daily_weight_change: float  # kg/day
    daily_body_fat_change: Optional[float]  # %/day
    
    # Calorie deficit info
    avg_daily_deficit: float  # kcal/day
    
    # Projection
    estimated_days_to_goal: Optional[int]
    estimated_goal_date: Optional[date]
    
    # Historical trend
    historical_data: List[MovingAveragePoint]
    
    # Future projection
    projection_data: List[ProjectionPoint]
    
    # Status
    on_track: bool
    message: str
