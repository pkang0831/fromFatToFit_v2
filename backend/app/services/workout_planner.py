"""Generate a workout plan tied to the transformation mode."""

from __future__ import annotations

from .transformation_types import TransformationMode, MuscleGainSpec, WorkoutPlan


def _emphasis_areas(gains: MuscleGainSpec) -> list[str]:
    """Body parts with > 0.5 kg muscle goal, sorted by size priority."""
    parts: list[str] = []
    if gains.legs_kg > 0.5:
        parts.append("legs")
    if gains.back_kg > 0.5:
        parts.append("back")
    if gains.chest_kg > 0.5:
        parts.append("chest")
    if gains.shoulders_kg > 0.5:
        parts.append("shoulders")
    if gains.arms_kg > 0.5:
        parts.append("arms")
    if gains.core_kg > 0.5:
        parts.append("core")
    return parts


def build_workout_plan(
    mode: TransformationMode,
    muscle_gains: MuscleGainSpec,
    gender: str,
    activity_level: str,
    total_weeks: int,
) -> WorkoutPlan:
    emphasis = _emphasis_areas(muscle_gains)
    if mode == TransformationMode.CUT:
        return _cut_plan(total_weeks)
    if mode == TransformationMode.LEAN_BULK:
        return _lean_bulk_plan(emphasis, total_weeks)
    if mode == TransformationMode.MASS_GAIN:
        return _mass_gain_plan(total_weeks)
    return _recomp_plan(emphasis, total_weeks)


# ── Cut ─────────────────────────────────────────────────────────────────────

def _cut_plan(total_weeks: int) -> WorkoutPlan:
    return WorkoutPlan(
        split_type="Upper / Lower or Full Body",
        sessions_per_week=3,
        exercises=[
            {"name": "Barbell Squat", "muscle_group": "legs", "type": "compound"},
            {"name": "Romanian Deadlift", "muscle_group": "legs / back", "type": "compound"},
            {"name": "Bench Press", "muscle_group": "chest", "type": "compound"},
            {"name": "Overhead Press", "muscle_group": "shoulders", "type": "compound"},
            {"name": "Barbell Row", "muscle_group": "back", "type": "compound"},
            {"name": "Pull-ups or Lat Pulldown", "muscle_group": "back", "type": "compound"},
            {"name": "Dumbbell Curl", "muscle_group": "arms", "type": "isolation"},
            {"name": "Tricep Pushdown", "muscle_group": "arms", "type": "isolation"},
        ],
        sets_reps_guidance=(
            "3-4 sets of 6-10 reps for compound lifts. "
            "2-3 sets of 10-15 reps for isolation. "
            "Maintain intensity (weight on bar). Reduce volume if recovery suffers."
        ),
        progression_scheme=(
            "Maintain current strength. Do not expect PRs during a deficit. "
            "If strength drops significantly, the cut may be too aggressive."
        ),
        cardio_guidance=(
            "8,000-10,000 steps daily. 2-3 sessions of 20-30 min low-intensity "
            "cardio (walking, cycling). Limit HIIT to preserve recovery."
        ),
        recovery_notes=(
            "Sleep 7-9 hours. Manage stress. Energy will decrease as the cut "
            "progresses — listen to your body."
        ),
        deload_protocol=(
            f"Every {min(6, max(3, total_weeks // 4))} weeks, reduce volume "
            f"by 40-50 % for one week. Keep intensity, cut sets in half."
        ),
        stage_adjustments={
            1: "Full training volume. Establish baseline strength.",
            2: "Drop 1 set per exercise if recovery declines.",
            3: "Reduce accessories. Prioritise compound lifts and recovery.",
            4: "Minimum effective volume. Focus on retaining, not building.",
        },
    )


# ── Lean Bulk ───────────────────────────────────────────────────────────────

def _lean_bulk_plan(emphasis: list[str], total_weeks: int) -> WorkoutPlan:
    emp = f" Prioritise volume for: {', '.join(emphasis)}." if emphasis else ""
    return WorkoutPlan(
        split_type="Push / Pull / Legs or Upper / Lower",
        sessions_per_week=4,
        exercises=[
            {"name": "Barbell Squat", "muscle_group": "legs", "type": "compound"},
            {"name": "Leg Press", "muscle_group": "legs", "type": "compound"},
            {"name": "Romanian Deadlift", "muscle_group": "legs / back", "type": "compound"},
            {"name": "Bench Press", "muscle_group": "chest", "type": "compound"},
            {"name": "Incline Dumbbell Press", "muscle_group": "chest", "type": "compound"},
            {"name": "Overhead Press", "muscle_group": "shoulders", "type": "compound"},
            {"name": "Lateral Raises", "muscle_group": "shoulders", "type": "isolation"},
            {"name": "Barbell Row", "muscle_group": "back", "type": "compound"},
            {"name": "Pull-ups", "muscle_group": "back", "type": "compound"},
            {"name": "Barbell Curl", "muscle_group": "arms", "type": "isolation"},
            {"name": "Skull Crushers", "muscle_group": "arms", "type": "isolation"},
        ],
        sets_reps_guidance=(
            f"3-4 sets of 6-12 reps for compounds. "
            f"3-4 sets of 10-15 reps for isolation.{emp}"
        ),
        progression_scheme=(
            "Progressive overload: increase weight or reps each session. "
            "When you hit the top of the rep range for all sets, add 2.5-5 kg."
        ),
        cardio_guidance=(
            "6,000-8,000 steps daily for general health. "
            "Minimise extra cardio to avoid interfering with recovery and surplus."
        ),
        recovery_notes=(
            "Sleep 7-9 hours. Eat enough. Recovery is when muscle is built. "
            "If not recovering between sessions, reduce frequency."
        ),
        deload_protocol=(
            f"Every {min(8, max(4, total_weeks // 3))} weeks, deload: "
            f"reduce volume by 40 % and intensity by 10 % for one week."
        ),
        stage_adjustments={
            1: "Establish progressive overload baseline. Focus on form.",
            2: "Add 1-2 sets per muscle group if recovering well.",
            3: "Peak training volume. Push for strength PRs.",
            4: "Transition to maintenance volume if fatigued.",
        },
    )


# ── Mass Gain ───────────────────────────────────────────────────────────────

def _mass_gain_plan(total_weeks: int) -> WorkoutPlan:
    return WorkoutPlan(
        split_type="Full Body or Upper / Lower",
        sessions_per_week=3,
        exercises=[
            {"name": "Squat or Leg Press", "muscle_group": "legs", "type": "compound"},
            {"name": "Bench or Machine Press", "muscle_group": "chest", "type": "compound"},
            {"name": "Cable or Machine Row", "muscle_group": "back", "type": "compound"},
            {"name": "Shoulder Press (machine or DB)", "muscle_group": "shoulders", "type": "compound"},
            {"name": "Lat Pulldown", "muscle_group": "back", "type": "compound"},
            {"name": "Leg Curl", "muscle_group": "legs", "type": "isolation"},
        ],
        sets_reps_guidance=(
            "2-3 sets of 8-12 reps. Focus on form and consistency rather "
            "than intensity. Resistance training helps partition nutrients."
        ),
        progression_scheme=(
            "Gradual progression. Add weight when comfortable. "
            "Primary goal is consistency, not maximal strength."
        ),
        cardio_guidance=(
            "5,000-7,000 steps daily for health. Light walking preferred."
        ),
        recovery_notes=(
            "Sleep well. Eat consistently. Training is moderate so recovery "
            "demands are lower."
        ),
        deload_protocol="Rest week if feeling run down. No strict schedule needed.",
        stage_adjustments={
            1: "Build a training routine with full-body sessions.",
            2: "Maintain consistency.",
            3: "Add variety if motivation drops. Try new exercises.",
            4: "Assess whether to continue or transition goals.",
        },
    )


# ── Recomp ──────────────────────────────────────────────────────────────────

def _recomp_plan(emphasis: list[str], total_weeks: int) -> WorkoutPlan:
    emp = f" Emphasis on: {', '.join(emphasis)}." if emphasis else ""
    return WorkoutPlan(
        split_type="Upper / Lower or Full Body",
        sessions_per_week=4,
        exercises=[
            {"name": "Barbell Squat", "muscle_group": "legs", "type": "compound"},
            {"name": "Deadlift", "muscle_group": "back / legs", "type": "compound"},
            {"name": "Bench Press", "muscle_group": "chest", "type": "compound"},
            {"name": "Overhead Press", "muscle_group": "shoulders", "type": "compound"},
            {"name": "Barbell Row", "muscle_group": "back", "type": "compound"},
            {"name": "Pull-ups", "muscle_group": "back", "type": "compound"},
            {"name": "Dumbbell Curl", "muscle_group": "arms", "type": "isolation"},
            {"name": "Lateral Raises", "muscle_group": "shoulders", "type": "isolation"},
        ],
        sets_reps_guidance=(
            f"3-4 sets of 6-10 reps for compounds. "
            f"2-3 sets of 10-15 reps for isolation. High intensity, moderate volume.{emp}"
        ),
        progression_scheme=(
            "Slow progressive overload. Focus on getting stronger at the same "
            "body weight. Recomposition demands patience."
        ),
        cardio_guidance=(
            "7,000-9,000 steps daily. 1-2 moderate cardio sessions per week. "
            "Don't overdo it — recomp relies on training stimulus, not cardio."
        ),
        recovery_notes=(
            "Sleep 7-9 hours. High protein intake is critical for recomp."
        ),
        deload_protocol=(
            f"Every {min(6, max(3, total_weeks // 4))} weeks, reduce volume "
            f"by 40 % for one week."
        ),
        stage_adjustments={
            1: "Establish strength baselines. Progressive overload focus.",
            2: "Push intensity. Strength gains drive recomposition.",
            3: "Subtle visual changes. Trust measurements and strength gains.",
            4: "Evaluate: continue recomp, or switch to a dedicated cut or bulk.",
        },
    )
