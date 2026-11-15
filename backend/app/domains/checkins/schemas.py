from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


QualityFlag = Literal[
    "mirror_selfie",
    "phone_occlusion",
    "uneven_lighting",
    "different_distance",
    "different_pose",
    "cropped_body",
    "low_resolution",
    "none",
]

WeeklyStatus = Literal["improved", "stable", "regressed", "low_confidence"]
RegionStatus = Literal["improved", "stable", "regressed"]
HighlightRegion = Literal["abdomen", "chest", "arms", "whole"]


class WeeklyCheckinCreateRequest(BaseModel):
    image_base64: str
    notes: str = ""
    weight_kg: Optional[float] = None
    ownership_confirmed: bool = False
    prioritize_leanness: Optional[float] = Field(default=None, ge=0, le=1)
    prioritize_definition: Optional[float] = Field(default=None, ge=0, le=1)


class ImageQualityObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frontal_pose: float = Field(..., ge=0, le=1)
    body_visibility: float = Field(..., ge=0, le=1)
    lighting_consistency: float = Field(..., ge=0, le=1)
    pose_consistency: float = Field(..., ge=0, le=1)
    comparison_confidence: float = Field(..., ge=0, le=1)
    quality_flags: List[QualityFlag] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_flags(self):
        if not self.quality_flags:
            self.quality_flags = ["none"]
        if "none" in self.quality_flags and len(self.quality_flags) > 1:
            self.quality_flags = [flag for flag in self.quality_flags if flag != "none"]
        return self


class VisualObservations(BaseModel):
    model_config = ConfigDict(extra="forbid")

    abdomen_softness: float = Field(..., ge=0, le=10)
    lower_abdomen_protrusion: float = Field(..., ge=0, le=10)
    ab_definition: float = Field(..., ge=0, le=10)
    chest_definition: float = Field(..., ge=0, le=10)
    arm_definition: float = Field(..., ge=0, le=10)
    shoulder_roundness: float = Field(..., ge=0, le=10)
    v_taper_visibility: float = Field(..., ge=0, le=10)
    overall_visual_leanness: float = Field(..., ge=0, le=10)


class EstimatedBodyFatRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body_fat_percent_min: float = Field(..., ge=3, le=45)
    body_fat_percent_max: float = Field(..., ge=3, le=45)
    body_fat_confidence: float = Field(..., ge=0, le=1)

    @model_validator(mode="after")
    def normalize_bounds(self):
        if self.body_fat_percent_max < self.body_fat_percent_min:
            self.body_fat_percent_min, self.body_fat_percent_max = (
                self.body_fat_percent_max,
                self.body_fat_percent_min,
            )
        return self


class RegionNotes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    abdomen: str
    chest: str
    arms: str
    shoulders: str


class BodyObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_quality: ImageQualityObservation
    observations: VisualObservations
    estimated_ranges: EstimatedBodyFatRange
    qualitative_summary: List[str] = Field(..., min_length=2, max_length=5)
    region_notes: RegionNotes


class GoalWeighting(BaseModel):
    prioritize_leanness: float = Field(default=0.55, ge=0, le=1)
    prioritize_definition: float = Field(default=0.30, ge=0, le=1)
    target_body_fat: Optional[float] = Field(default=None, ge=3, le=45)

    @property
    def prioritize_proportion(self) -> float:
        return max(0.0, 1.0 - self.prioritize_leanness - self.prioritize_definition)

    @model_validator(mode="after")
    def ensure_weight_budget(self):
        if self.prioritize_leanness + self.prioritize_definition > 1:
            total = self.prioritize_leanness + self.prioritize_definition
            self.prioritize_leanness = self.prioritize_leanness / total
            self.prioritize_definition = self.prioritize_definition / total
        return self


class DerivedScores(BaseModel):
    leanness_score: float = Field(..., ge=0, le=100)
    definition_score: float = Field(..., ge=0, le=100)
    proportion_score: float = Field(..., ge=0, le=100)
    goal_proximity_score: float = Field(..., ge=0, le=100)


class WeeklyDelta(BaseModel):
    abdomen_softness: float = 0
    lower_abdomen_protrusion: float = 0
    ab_definition: float = 0
    chest_definition: float = 0
    arm_definition: float = 0
    overall_visual_leanness: float = 0
    goal_proximity_score: float = 0


class RegionVisualization(BaseModel):
    region: HighlightRegion
    label: str
    value: str
    note: str
    status: RegionStatus
    intensity: float = Field(..., ge=0, le=1)


class HologramVisualization(BaseModel):
    glow_intensity: float = Field(..., ge=0, le=1)
    body_clarity: float = Field(..., ge=0, le=1)
    pedestal_progress: float = Field(..., ge=0, le=1)


class WeeklyCheckinAnalysisResponse(BaseModel):
    id: str
    progress_photo_id: str
    previous_checkin_id: Optional[str] = None
    created_at: datetime
    taken_at: datetime
    analysis_version: str
    image_quality: ImageQualityObservation
    observations: VisualObservations
    estimated_ranges: EstimatedBodyFatRange
    qualitative_summary: List[str]
    region_notes: RegionNotes
    derived_scores: DerivedScores
    delta_from_previous: Optional[WeeklyDelta] = None
    comparison_confidence: float = Field(..., ge=0, le=1)
    weekly_status: WeeklyStatus
    is_first_checkin: bool = False
    regional_visualization: List[RegionVisualization] = Field(default_factory=list, max_length=3)
    hologram_visualization: HologramVisualization


class HomeWeeklyAnalysisSummary(BaseModel):
    latest: Optional[WeeklyCheckinAnalysisResponse] = None
