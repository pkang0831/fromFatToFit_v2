"""Structured transformation planner.

Converts (current body state + goal) into a multi-stage plan with
conservative timelines, mode-specific visual descriptors, and warnings.
"""

from __future__ import annotations

import logging
from typing import Optional

from .transformation_types import (
    TransformationMode,
    MuscleGainSpec,
    BodyStateDescriptor,
    TransformationStage,
    TransformationPlan,
)
from .transformation_prompts import render_stage_prompt
from .nutrition_planner import build_nutrition_plan
from .workout_planner import build_workout_plan

logger = logging.getLogger(__name__)

# ── Safety limits ───────────────────────────────────────────────────────────

MIN_BF_MALE = 6.0
MIN_BF_FEMALE = 14.0
MAX_BF = 45.0

# Non-linear progress fractions per stage [0..4].
# Cuts are front-loaded (early water/glycogen loss, later metabolic adaptation).
CUT_PROGRESS = [0.0, 0.30, 0.55, 0.78, 1.0]
GAIN_PROGRESS = [0.0, 0.25, 0.50, 0.75, 1.0]

STAGE_LABELS = ["Original", "Early", "Mid", "Late", "Final"]
NUM_STAGES = 5


# ── 1. Mode classification ─────────────────────────────────────────────────

def classify_mode(
    current_bf: float,
    target_bf: float,
    muscle_gain_kg: float,
    gender: str,
) -> TransformationMode:
    min_bf = MIN_BF_MALE if gender == "male" else MIN_BF_FEMALE

    if target_bf < min_bf or target_bf > MAX_BF:
        return TransformationMode.UNSUPPORTED

    bf_delta = target_bf - current_bf  # negative = losing fat

    if bf_delta < -2:
        return TransformationMode.RECOMP if muscle_gain_kg > 2 else TransformationMode.CUT
    if -2 <= bf_delta <= 2:
        if muscle_gain_kg > 0:
            return TransformationMode.RECOMP
        return TransformationMode.CUT if bf_delta <= 0 else TransformationMode.LEAN_BULK
    if bf_delta <= 5:
        return TransformationMode.LEAN_BULK
    return TransformationMode.MASS_GAIN


# ── 2. Timeline ────────────────────────────────────────────────────────────

def estimate_timeline_weeks(
    mode: TransformationMode,
    current_bf: float,
    target_bf: float,
    muscle_gain_kg: float,
) -> int:
    bf_diff = abs(target_bf - current_bf)

    if mode == TransformationMode.CUT:
        months = bf_diff / 0.6
    elif mode == TransformationMode.RECOMP:
        bf_months = bf_diff / 0.25 if bf_diff > 0 else 0
        muscle_months = muscle_gain_kg / 0.35 if muscle_gain_kg > 0 else 0
        months = max(bf_months, muscle_months, 3)
    elif mode == TransformationMode.LEAN_BULK:
        months = max(
            bf_diff / 0.3 if bf_diff > 0 else 3,
            muscle_gain_kg / 0.5 if muscle_gain_kg > 0 else 3,
        )
    elif mode == TransformationMode.MASS_GAIN:
        months = bf_diff / 1.0
    else:
        months = 12

    weeks = int(months * 4.33)
    return max(8, min(weeks, 104))


# ── 3. Weight / body-composition at each stage ─────────────────────────────

def _weight_at_stage(
    mode: TransformationMode,
    current_bf: float,
    stage_bf: float,
    current_weight: Optional[float],
    muscle_gain_kg: float,
    progress_frac: float,
) -> tuple[Optional[float], float, float]:
    """Return (weight_kg, lean_delta_kg, fat_delta_kg) for one stage."""
    if current_weight is None:
        return None, 0.0, 0.0

    current_fat = current_weight * current_bf / 100
    current_lean = current_weight - current_fat

    if mode == TransformationMode.CUT:
        final_lean = current_lean * 0.97
        lean_at_stage = current_lean + (final_lean - current_lean) * progress_frac
        weight = lean_at_stage / (1 - stage_bf / 100) if stage_bf < 100 else current_weight
        fat_at_stage = weight - lean_at_stage
        return (
            round(weight, 1),
            round(lean_at_stage - current_lean, 1),
            round(fat_at_stage - current_fat, 1),
        )

    if mode == TransformationMode.RECOMP:
        lean_gain = muscle_gain_kg * progress_frac
        new_lean = current_lean + lean_gain
        bf_frac = stage_bf / 100
        weight = new_lean / (1 - bf_frac) if bf_frac < 1 else current_weight
        new_fat = weight - new_lean
        return (
            round(weight, 1),
            round(lean_gain, 1),
            round(new_fat - current_fat, 1),
        )

    # LEAN_BULK / MASS_GAIN
    lean_gain = muscle_gain_kg * progress_frac
    new_lean = current_lean + lean_gain
    bf_frac = stage_bf / 100
    weight = new_lean / (1 - bf_frac) if bf_frac < 1 else current_weight
    new_fat = weight - new_lean
    return (
        round(weight, 1),
        round(lean_gain, 1),
        round(new_fat - current_fat, 1),
    )


# ── 4. Mode-specific visual descriptors ────────────────────────────────────

def _scale_word(bf_change: float) -> str:
    if bf_change <= 1.5:
        return "very slightly"
    if bf_change <= 3.5:
        return "slightly"
    if bf_change <= 6:
        return "noticeably"
    return "significantly"


def _cut_visuals(current_bf: float, stage_bf: float, gender: str) -> BodyStateDescriptor:
    delta = current_bf - stage_bf
    sw = _scale_word(delta)
    is_male = gender == "male"

    if is_male:
        if stage_bf > 22:
            abdomen = f"{sw} less soft, still no visible ab definition"
        elif stage_bf > 18:
            abdomen = f"{sw} flatter, faint upper-ab outline may be visible"
        elif stage_bf > 14:
            abdomen = "flatter midsection with visible upper-ab outline"
        elif stage_bf > 10:
            abdomen = "visible ab definition with moderate separation"
        else:
            abdomen = "deep ab definition with clear 6-pack separation"
    else:
        if stage_bf > 28:
            abdomen = f"{sw} less soft, still rounded"
        elif stage_bf > 23:
            abdomen = f"{sw} flatter, smoother midsection"
        elif stage_bf > 18:
            abdomen = "flat midsection with subtle toning"
        else:
            abdomen = "toned, defined midsection"

    return BodyStateDescriptor(
        face=f"{sw} leaner jawline and cheeks" if delta > 2 else "unchanged",
        waist=f"{sw} narrower" if delta > 1 else "unchanged",
        abdomen=abdomen,
        chest="same muscle size, less soft tissue over pectorals" if delta > 2 else "unchanged",
        arms="same size, slightly more vein visibility" if delta > 3 else "unchanged",
        shoulders="same size, slightly more visible contour" if delta > 3 else "unchanged",
        legs="same size, slightly more defined" if delta > 3 else "unchanged",
        overall=f"{sw} leaner overall — fat reduction only, no added muscle size",
    )


def _mass_gain_visuals(current_bf: float, stage_bf: float, gender: str) -> BodyStateDescriptor:
    delta = stage_bf - current_bf
    sw = _scale_word(delta)

    return BodyStateDescriptor(
        face=f"{sw} fuller and rounder" if delta > 1.5 else "unchanged",
        waist=f"{sw} wider with more subcutaneous fat" if delta > 1 else "unchanged",
        abdomen=f"{sw} softer, any prior definition hidden under fat layer",
        chest=f"{sw} thicker but softer, no added muscular definition",
        arms=f"{sw} thicker and smoother, reduced vein visibility" if delta > 2 else "unchanged",
        shoulders=f"{sw} thicker but softer, no new definition" if delta > 2 else "unchanged",
        legs=f"{sw} thicker with a softer appearance" if delta > 2 else "unchanged",
        overall=f"{sw} softer and heavier — weight gain, NOT added muscularity",
    )


def _lean_bulk_visuals(current_bf: float, stage_bf: float, gender: str) -> BodyStateDescriptor:
    delta = abs(stage_bf - current_bf)
    sw = _scale_word(delta)

    return BodyStateDescriptor(
        face="very slightly fuller" if delta > 1 else "unchanged",
        waist="marginally wider" if delta > 1 else "unchanged",
        abdomen="slightly less defined as thin fat layer covers abs" if delta > 1 else "unchanged",
        chest=f"{sw} broader and slightly rounder — subtle muscle size increase",
        arms=f"{sw} bigger — modest size increase" if delta > 1 else "very slightly bigger",
        shoulders=f"{sw} broader and slightly rounder" if delta > 1 else "very slightly bigger",
        legs="slightly thicker with maintained definition" if delta > 1 else "unchanged",
        overall=f"{sw} bigger and slightly fuller — controlled lean mass gain",
    )


def _recomp_visuals(current_bf: float, stage_bf: float, gender: str) -> BodyStateDescriptor:
    return BodyStateDescriptor(
        face="very slightly leaner" if current_bf > stage_bf else "unchanged",
        waist="very slightly tighter" if current_bf > stage_bf else "unchanged",
        abdomen="very slightly more toned, subtle definition improvement",
        chest="same size, very slightly better definition",
        arms="same size, very slightly better definition",
        shoulders="same size, very slightly better definition",
        legs="same size, very slightly better definition",
        overall="subtle improvement — slightly leaner with marginally better muscle definition",
    )


_VISUAL_DISPATCH = {
    TransformationMode.CUT: _cut_visuals,
    TransformationMode.MASS_GAIN: _mass_gain_visuals,
    TransformationMode.LEAN_BULK: _lean_bulk_visuals,
    TransformationMode.RECOMP: _recomp_visuals,
}


def _generate_visuals(
    current_bf: float,
    stage_bf: float,
    mode: TransformationMode,
    gender: str,
    progress_frac: float,
) -> BodyStateDescriptor:
    if progress_frac == 0:
        return BodyStateDescriptor(
            face="unchanged", waist="unchanged", abdomen="unchanged",
            chest="unchanged", arms="unchanged", shoulders="unchanged",
            legs="unchanged", overall="current state",
        )
    fn = _VISUAL_DISPATCH.get(mode, _cut_visuals)
    return fn(current_bf, stage_bf, gender)


# ── 5. Stage generation ────────────────────────────────────────────────────

def _build_stages(
    mode: TransformationMode,
    current_bf: float,
    target_bf: float,
    current_weight: Optional[float],
    muscle_gain_kg: float,
    gender: str,
    timeline_weeks: int,
) -> list[TransformationStage]:
    bf_diff = target_bf - current_bf
    is_losing = bf_diff < 0
    progress_curve = CUT_PROGRESS if is_losing else GAIN_PROGRESS
    min_bf = MIN_BF_MALE if gender == "male" else MIN_BF_FEMALE

    stages: list[TransformationStage] = []
    for i in range(NUM_STAGES):
        frac = progress_curve[i]
        stage_bf = round(current_bf + bf_diff * frac, 1)
        stage_week = round(timeline_weeks * frac) if i > 0 else 0

        weight_kg, lean_delta, fat_delta = _weight_at_stage(
            mode, current_bf, stage_bf, current_weight, muscle_gain_kg, frac,
        )
        body_state = _generate_visuals(current_bf, stage_bf, mode, gender, frac)

        warnings: list[str] = []
        if stage_bf < min_bf:
            warnings.append(
                f"Body fat below {min_bf}% is difficult to sustain and may harm health."
            )

        stages.append(TransformationStage(
            stage_number=i,
            label=STAGE_LABELS[i],
            week=stage_week,
            bf_pct=stage_bf,
            weight_kg=weight_kg,
            lean_mass_delta_kg=lean_delta,
            fat_mass_delta_kg=fat_delta,
            body_state=body_state,
            prompt="",
            warnings=warnings,
        ))
    return stages


# ── 6. Top-level entry point ───────────────────────────────────────────────

_DISCLAIMER = (
    "This is an AI-generated visual estimate and plan for illustrative "
    "purposes only. It is not medical, nutritional, or fitness advice. "
    "Individual results vary widely based on genetics, adherence, health "
    "conditions, and many other factors. Consult a qualified professional "
    "before starting any diet or exercise programme."
)


def build_plan(
    current_bf: float,
    target_bf: float,
    gender: str,
    muscle_gains: Optional[MuscleGainSpec] = None,
    weight_kg: Optional[float] = None,
    height_cm: Optional[float] = None,
    age: Optional[int] = None,
    activity_level: Optional[str] = None,
) -> TransformationPlan:
    if muscle_gains is None:
        muscle_gains = MuscleGainSpec()
    mg_total = muscle_gains.total_kg

    mode = classify_mode(current_bf, target_bf, mg_total, gender)

    min_bf = MIN_BF_MALE if gender == "male" else MIN_BF_FEMALE
    clamped_target = target_bf
    target_bf_clamped: Optional[float] = None
    warnings: list[str] = []

    if mode == TransformationMode.UNSUPPORTED:
        if target_bf < min_bf:
            clamped_target = min_bf
            target_bf_clamped = clamped_target
            warnings.append(
                f"Target body fat {target_bf:.1f}% is below the safe minimum "
                f"for {gender}s ({min_bf:.0f}%). Clamped to {min_bf:.0f}%."
            )
            mode = classify_mode(current_bf, clamped_target, mg_total, gender)
        else:
            warnings.append(
                f"Target body fat {target_bf:.1f}% is outside the supported range."
            )

    if abs(current_bf - clamped_target) < 0.5 and mg_total < 0.5:
        warnings.append(
            "Current and target body fat are nearly identical. "
            "Consider adjusting your goal for a visible difference."
        )

    timeline = estimate_timeline_weeks(mode, current_bf, clamped_target, mg_total)

    stages = _build_stages(
        mode, current_bf, clamped_target,
        weight_kg, mg_total, gender, timeline,
    )

    # Render prompts for generated stages (1-4)
    for stage in stages:
        if stage.stage_number > 0:
            stage.prompt = render_stage_prompt(
                stage=stage,
                mode=mode,
                gender=gender,
                current_bf=current_bf,
                muscle_gains=muscle_gains,
            )

    nutrition = build_nutrition_plan(
        mode=mode,
        current_bf=current_bf,
        target_bf=clamped_target,
        weight_kg=weight_kg or 75.0,
        height_cm=height_cm or 170.0,
        age=age or 30,
        gender=gender,
        activity_level=activity_level or "moderate",
        total_weeks=timeline,
    )

    workout = build_workout_plan(
        mode=mode,
        muscle_gains=muscle_gains,
        gender=gender,
        activity_level=activity_level or "moderate",
        total_weeks=timeline,
    )

    return TransformationPlan(
        mode=mode,
        current_bf=current_bf,
        target_bf=clamped_target,
        target_bf_clamped=target_bf_clamped,
        total_weeks=timeline,
        stages=stages,
        nutrition=nutrition,
        workout=workout,
        warnings=warnings,
        disclaimer=_DISCLAIMER,
    )
