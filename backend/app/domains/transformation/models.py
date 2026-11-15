"""Domain types for the body transformation journey engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TransformationMode(str, Enum):
    CUT = "cut"
    RECOMP = "recomp"
    LEAN_BULK = "lean_bulk"
    MASS_GAIN = "mass_gain"
    UNSUPPORTED = "unsupported"


@dataclass
class MuscleGainSpec:
    arms_kg: float = 0.0
    chest_kg: float = 0.0
    back_kg: float = 0.0
    shoulders_kg: float = 0.0
    legs_kg: float = 0.0
    core_kg: float = 0.0

    @property
    def total_kg(self) -> float:
        return (
            self.arms_kg + self.chest_kg + self.back_kg
            + self.shoulders_kg + self.legs_kg + self.core_kg
        )


@dataclass
class BodyStateDescriptor:
    """Visual description of body composition at a given BF%."""
    face: str
    waist: str
    abdomen: str
    chest: str
    arms: str
    shoulders: str
    legs: str
    overall: str


@dataclass
class StageNutritionSnapshot:
    """Per-stage calorie/protein target."""
    daily_calories: int
    protein_g: int

@dataclass
class TransformationStage:
    stage_number: int
    label: str
    week: int
    bf_pct: float
    weight_kg: Optional[float]
    lean_mass_delta_kg: float
    fat_mass_delta_kg: float
    body_state: BodyStateDescriptor
    prompt: str
    warnings: list[str] = field(default_factory=list)
    stage_nutrition: Optional[StageNutritionSnapshot] = None
    stage_exercises: list[str] = field(default_factory=list)


@dataclass
class NutritionPlan:
    daily_calories: int
    protein_g: int
    carbs_g_min: int
    carbs_g_max: int
    fat_g_min: int
    fat_g_max: int
    meal_structure: list[str]
    weekly_adjustment: str
    checkin_cadence: str
    stage_notes: dict[int, str]
    assumptions: list[str]
    disclaimer: str


@dataclass
class WorkoutPlan:
    split_type: str
    sessions_per_week: int
    exercises: list[dict]
    sets_reps_guidance: str
    progression_scheme: str
    cardio_guidance: str
    recovery_notes: str
    deload_protocol: str
    stage_adjustments: dict[int, str]


@dataclass
class TransformationPlan:
    mode: TransformationMode
    current_bf: float
    target_bf: float
    target_bf_clamped: Optional[float]
    total_weeks: int
    stages: list[TransformationStage]
    nutrition: NutritionPlan
    workout: WorkoutPlan
    warnings: list[str]
    disclaimer: str


@dataclass
class JourneyResult:
    plan: TransformationPlan
    stage_images: list[dict]
    scan_id: Optional[str] = None
