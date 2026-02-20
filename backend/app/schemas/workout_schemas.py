from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ExerciseLibraryItem(BaseModel):
    id: str
    name: str
    category: str
    muscle_groups: List[str]
    form_instructions: str
    demo_image_url: Optional[str]
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    met_value: Optional[float] = Field(default=None, description="MET (Metabolic Equivalent of Task) value")
    exercise_type: Optional[str] = Field(default="strength", description="cardio or strength")


class WorkoutSetLog(BaseModel):
    set_number: int
    reps: int
    weight: Optional[float] = None


class WorkoutLogCreate(BaseModel):
    date: date
    exercise_id: str
    exercise_name: str
    sets: List[WorkoutSetLog]
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    id: str
    user_id: str
    date: date
    exercise_id: str
    exercise_name: str
    sets: List[WorkoutSetLog]
    duration_minutes: Optional[int]
    notes: Optional[str]
    calories_burned: Optional[float] = Field(default=None, description="Calories burned during workout")
    created_at: datetime


class FormAnalysisRequest(BaseModel):
    video_base64: str = Field(..., description="Base64 encoded video")
    exercise_name: str


class FormAnalysisResponse(BaseModel):
    exercise_name: str
    form_score: int = Field(..., ge=0, le=100, description="Score out of 100")
    issues_detected: List[str]
    corrections: List[str]
    overall_feedback: str


class WorkoutTrendDataPoint(BaseModel):
    date: date
    workout_count: int
    total_volume: float = Field(description="Total weight x reps")
    duration_minutes: int


class WorkoutTrendResponse(BaseModel):
    data: List[WorkoutTrendDataPoint]
    total_workouts: int
    average_per_week: float
    days: int
