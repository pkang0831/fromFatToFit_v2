from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BodyScanRequest(BaseModel):
    image_base64: str
    scan_type: str = Field(..., description="bodyfat, percentile, transformation, or enhancement")
    gender: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    height_cm: Optional[float] = None
    target_bf: Optional[float] = Field(None, description="Absolute target body fat % for transformation")
    target_bf_reduction: Optional[float] = Field(None, description="Legacy: relative BF reduction")
    enhancement_level: Optional[str] = Field(None, description="subtle, natural, or studio")


class BodyFatEstimateResponse(BaseModel):
    body_fat_percentage: float
    confidence: str = Field(description="low, medium, high")
    recommendations: List[str]
    scan_id: str
    usage_remaining: int


class PercentileData(BaseModel):
    percentile: float = Field(..., ge=0, le=100)
    rank_text: str = Field(description="e.g., 'top 15%'")
    comparison_group: str
    body_fat_percentage: float


class PercentileResponse(BaseModel):
    percentile_data: PercentileData
    distribution_data: Dict[str, Any] = Field(description="Data for bell curve visualization")
    scan_id: str
    usage_remaining: int


class TransformationResponse(BaseModel):
    original_image_url: str
    transformed_image_url: str
    current_bf: Optional[float] = None
    target_bf: Optional[float] = None
    direction: Optional[str] = None
    muscle_gain_estimate: Optional[str] = None
    estimated_timeline_weeks: int
    recommendations: List[str]
    scan_id: str


class EnhancementResponse(BaseModel):
    original_image_url: str
    enhanced_image_url: str
    enhancement_level: str
    scan_id: str


class BodyScanHistoryItem(BaseModel):
    id: str
    scan_type: str
    date: datetime
    result_summary: str
    image_url: Optional[str]


class UserProfileUpdate(BaseModel):
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    activity_level: Optional[str] = None
    calorie_goal: Optional[float] = None
