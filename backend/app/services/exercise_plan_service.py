"""Exercise plan engine.

Structured workout routines (equipment / sets / reps per exercise)
and cardio duration calculator (inverse MET).
"""

from __future__ import annotations

import math
import logging
from typing import Optional

from .calorie_calculator import MET_VALUES, CalorieCalculator

logger = logging.getLogger(__name__)

# ── Exercise database ────────────────────────────────────────────────────────
# Each exercise: name, muscle_group, equipment, type, default sets/reps/rest

_EXERCISES = [
    # Compound — legs
    {"name": "Barbell Back Squat",      "muscle_group": "legs",      "equipment": "barbell",   "type": "compound", "sets": 4, "reps": (6, 10), "rest": 120, "tempo": "3-1-1-0"},
    {"name": "Leg Press",               "muscle_group": "legs",      "equipment": "machine",   "type": "compound", "sets": 3, "reps": (8, 12), "rest": 90,  "tempo": "3-0-1-0"},
    {"name": "Romanian Deadlift",       "muscle_group": "legs",      "equipment": "barbell",   "type": "compound", "sets": 3, "reps": (8, 12), "rest": 90,  "tempo": "3-1-1-0"},
    {"name": "Bulgarian Split Squat",   "muscle_group": "legs",      "equipment": "dumbbell",  "type": "compound", "sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "2-1-1-0"},
    {"name": "Goblet Squat",            "muscle_group": "legs",      "equipment": "dumbbell",  "type": "compound", "sets": 3, "reps": (10, 15),"rest": 60,  "tempo": "2-1-1-0"},
    # Isolation — legs
    {"name": "Leg Extension",           "muscle_group": "legs",      "equipment": "machine",   "type": "isolation","sets": 3, "reps": (10, 15),"rest": 60,  "tempo": "2-1-2-0"},
    {"name": "Leg Curl",                "muscle_group": "legs",      "equipment": "machine",   "type": "isolation","sets": 3, "reps": (10, 15),"rest": 60,  "tempo": "2-1-2-0"},
    {"name": "Calf Raise",             "muscle_group": "legs",      "equipment": "machine",   "type": "isolation","sets": 3, "reps": (12, 20),"rest": 45,  "tempo": "2-2-1-0"},
    # Compound — chest
    {"name": "Barbell Bench Press",     "muscle_group": "chest",     "equipment": "barbell",   "type": "compound", "sets": 4, "reps": (6, 10), "rest": 120, "tempo": "3-1-1-0"},
    {"name": "Incline Dumbbell Press",  "muscle_group": "chest",     "equipment": "dumbbell",  "type": "compound", "sets": 3, "reps": (8, 12), "rest": 90,  "tempo": "2-1-1-0"},
    {"name": "Dumbbell Bench Press",    "muscle_group": "chest",     "equipment": "dumbbell",  "type": "compound", "sets": 3, "reps": (8, 12), "rest": 90,  "tempo": "2-1-1-0"},
    # Isolation — chest
    {"name": "Cable Fly",               "muscle_group": "chest",     "equipment": "cable",     "type": "isolation","sets": 3, "reps": (10, 15),"rest": 60,  "tempo": "2-1-2-0"},
    {"name": "Pec Deck",                "muscle_group": "chest",     "equipment": "machine",   "type": "isolation","sets": 3, "reps": (10, 15),"rest": 60,  "tempo": "2-1-2-0"},
    # Compound — back
    {"name": "Barbell Row",             "muscle_group": "back",      "equipment": "barbell",   "type": "compound", "sets": 4, "reps": (6, 10), "rest": 90,  "tempo": "2-1-1-0"},
    {"name": "Pull-up",                 "muscle_group": "back",      "equipment": "bodyweight","type": "compound", "sets": 3, "reps": (5, 12), "rest": 90,  "tempo": "2-1-1-0"},
    {"name": "Lat Pulldown",            "muscle_group": "back",      "equipment": "cable",     "type": "compound", "sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "2-1-2-0"},
    {"name": "Seated Cable Row",        "muscle_group": "back",      "equipment": "cable",     "type": "compound", "sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "2-1-1-0"},
    {"name": "Deadlift",                "muscle_group": "back",      "equipment": "barbell",   "type": "compound", "sets": 3, "reps": (5, 8),  "rest": 150, "tempo": "2-1-1-0"},
    # Compound — shoulders
    {"name": "Overhead Press",          "muscle_group": "shoulders", "equipment": "barbell",   "type": "compound", "sets": 4, "reps": (6, 10), "rest": 90,  "tempo": "2-1-1-0"},
    {"name": "Dumbbell Shoulder Press", "muscle_group": "shoulders", "equipment": "dumbbell",  "type": "compound", "sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "2-1-1-0"},
    # Isolation — shoulders
    {"name": "Lateral Raise",           "muscle_group": "shoulders", "equipment": "dumbbell",  "type": "isolation","sets": 3, "reps": (12, 20),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Face Pull",               "muscle_group": "shoulders", "equipment": "cable",     "type": "isolation","sets": 3, "reps": (12, 20),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Rear Delt Fly",           "muscle_group": "shoulders", "equipment": "dumbbell",  "type": "isolation","sets": 3, "reps": (12, 15),"rest": 45,  "tempo": "2-1-2-0"},
    # Arms
    {"name": "Barbell Curl",            "muscle_group": "arms",      "equipment": "barbell",   "type": "isolation","sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "2-1-2-0"},
    {"name": "Dumbbell Curl",           "muscle_group": "arms",      "equipment": "dumbbell",  "type": "isolation","sets": 3, "reps": (10, 15),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Hammer Curl",             "muscle_group": "arms",      "equipment": "dumbbell",  "type": "isolation","sets": 3, "reps": (10, 15),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Tricep Pushdown",         "muscle_group": "arms",      "equipment": "cable",     "type": "isolation","sets": 3, "reps": (10, 15),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Skull Crusher",           "muscle_group": "arms",      "equipment": "barbell",   "type": "isolation","sets": 3, "reps": (8, 12), "rest": 60,  "tempo": "3-1-1-0"},
    {"name": "Overhead Tricep Extension","muscle_group": "arms",     "equipment": "dumbbell",  "type": "isolation","sets": 3, "reps": (10, 15),"rest": 45,  "tempo": "2-1-2-0"},
    # Core
    {"name": "Hanging Leg Raise",       "muscle_group": "core",      "equipment": "bodyweight","type": "isolation","sets": 3, "reps": (10, 15),"rest": 45,  "tempo": None},
    {"name": "Cable Crunch",            "muscle_group": "core",      "equipment": "cable",     "type": "isolation","sets": 3, "reps": (12, 20),"rest": 45,  "tempo": "2-1-2-0"},
    {"name": "Plank",                   "muscle_group": "core",      "equipment": "bodyweight","type": "isolation","sets": 3, "reps": (30, 60),"rest": 45,  "tempo": None, "notes": "Hold for seconds, not reps"},
]

# ── Split templates ──────────────────────────────────────────────────────────

_SPLITS = {
    "push_pull_legs": {
        "label": "Push / Pull / Legs",
        "days": [
            {"day_label": "Day A — Push", "focus": "chest, shoulders, triceps",
             "groups": [("chest", 2), ("shoulders", 2), ("arms", 1)]},
            {"day_label": "Day B — Pull", "focus": "back, biceps, rear delts",
             "groups": [("back", 3), ("arms", 1), ("shoulders", 1)]},
            {"day_label": "Day C — Legs", "focus": "quads, hamstrings, calves, core",
             "groups": [("legs", 4), ("core", 1)]},
        ],
    },
    "upper_lower": {
        "label": "Upper / Lower",
        "days": [
            {"day_label": "Day A — Upper", "focus": "chest, back, shoulders, arms",
             "groups": [("chest", 2), ("back", 2), ("shoulders", 1), ("arms", 1)]},
            {"day_label": "Day B — Lower", "focus": "legs, core",
             "groups": [("legs", 4), ("core", 1)]},
        ],
    },
    "full_body": {
        "label": "Full Body",
        "days": [
            {"day_label": "Day A — Full Body", "focus": "all major muscle groups",
             "groups": [("legs", 2), ("chest", 1), ("back", 2), ("shoulders", 1), ("arms", 1)]},
        ],
    },
}

_MODE_DEFAULTS = {
    "cut":       {"split": "upper_lower", "sessions": 3, "volume_mult": 0.8},
    "lean_bulk": {"split": "push_pull_legs", "sessions": 4, "volume_mult": 1.0},
    "mass_gain": {"split": "full_body", "sessions": 3, "volume_mult": 0.7},
    "recomp":    {"split": "upper_lower", "sessions": 4, "volume_mult": 1.0},
}

_EXP_ADJ = {
    "beginner":     {"sets_mult": 0.7, "rest_add": 30},
    "intermediate": {"sets_mult": 1.0, "rest_add": 0},
    "advanced":     {"sets_mult": 1.2, "rest_add": -15},
}


def _pick_exercises(
    muscle_group: str,
    count: int,
    equipment_filter: Optional[set[str]],
    used: set[str],
) -> list[dict]:
    """Select `count` exercises for a muscle group, respecting equipment filter."""
    candidates = [
        e for e in _EXERCISES
        if e["muscle_group"] == muscle_group
        and e["name"] not in used
        and (equipment_filter is None or e["equipment"] in equipment_filter)
    ]
    candidates.sort(key=lambda e: (0 if e["type"] == "compound" else 1))
    picked = candidates[:count]
    for p in picked:
        used.add(p["name"])
    return picked


def build_structured_routine(
    mode: str,
    gender: str,
    experience: str = "intermediate",
    available_equipment: Optional[list[str]] = None,
    sessions_per_week: Optional[int] = None,
) -> dict:
    """Build a structured workout routine with specific exercises, sets, reps."""
    defaults = _MODE_DEFAULTS.get(mode, _MODE_DEFAULTS["cut"])
    split_key = defaults["split"]
    split = _SPLITS[split_key]
    vol_mult = defaults["volume_mult"]
    exp = _EXP_ADJ.get(experience, _EXP_ADJ["intermediate"])
    sessions = sessions_per_week or defaults["sessions"]

    equip_set = set(available_equipment) if available_equipment else None
    if equip_set:
        equip_set.add("bodyweight")

    used: set[str] = set()
    days = []
    for day_template in split["days"]:
        exercises = []
        for group, count in day_template["groups"]:
            for ex in _pick_exercises(group, count, equip_set, used):
                adj_sets = max(2, round(ex["sets"] * vol_mult * exp["sets_mult"]))
                adj_rest = max(30, ex["rest"] + exp["rest_add"])
                exercises.append({
                    "name": ex["name"],
                    "muscle_group": ex["muscle_group"],
                    "equipment": ex["equipment"],
                    "exercise_type": ex["type"],
                    "sets": adj_sets,
                    "reps_min": ex["reps"][0],
                    "reps_max": ex["reps"][1],
                    "rest_seconds": adj_rest,
                    "tempo": ex.get("tempo"),
                    "notes": ex.get("notes"),
                })

        est_minutes = sum(
            e["sets"] * (e["rest_seconds"] / 60 + 0.5) for e in exercises
        )
        days.append({
            "day_label": day_template["day_label"],
            "focus": day_template["focus"],
            "exercises": exercises,
            "estimated_duration_min": round(est_minutes),
        })

    progression = {
        "cut": "Maintain current strength. If weight on bar drops >10%, the cut is too aggressive.",
        "lean_bulk": "Add weight or reps each session. When you hit top of rep range for all sets, increase load by 2.5-5 kg.",
        "mass_gain": "Focus on consistency over intensity. Gradual load increases when comfortable.",
        "recomp": "Slow progressive overload. Aim to get stronger at the same body weight.",
    }.get(mode, "Progressive overload when possible.")

    deload = {
        "cut": "Every 4-6 weeks: reduce volume 40-50%, keep intensity.",
        "lean_bulk": "Every 6-8 weeks: reduce volume 40%, intensity 10% for one week.",
        "mass_gain": "Rest week when fatigued. No strict schedule needed.",
        "recomp": "Every 4-6 weeks: reduce volume 40% for one week.",
    }.get(mode, "Every 4-6 weeks: reduce volume by 40%.")

    return {
        "split_type": split["label"],
        "sessions_per_week": sessions,
        "days": days,
        "progression_scheme": progression,
        "deload_note": deload,
    }


# ── Cardio duration calculator ───────────────────────────────────────────────

_CARDIO_ACTIVITIES = {
    "walking":                {"met": MET_VALUES.get("walking_brisk", 4.5),    "intensity": "low"},
    "jogging":                {"met": MET_VALUES.get("jogging", 7.0),          "intensity": "moderate"},
    "running":                {"met": MET_VALUES.get("running_moderate", 9.0), "intensity": "high"},
    "cycling":                {"met": MET_VALUES.get("cycling_moderate", 8.0), "intensity": "moderate"},
    "stationary_bike":        {"met": MET_VALUES.get("stationary_bike_moderate", 6.8), "intensity": "moderate"},
    "swimming":               {"met": MET_VALUES.get("swimming_laps_moderate", 8.0),   "intensity": "moderate"},
    "elliptical":             {"met": MET_VALUES.get("elliptical_moderate", 5.0),      "intensity": "low-moderate"},
    "rowing":                 {"met": MET_VALUES.get("rowing_moderate", 7.0),          "intensity": "moderate"},
    "stair_climber":          {"met": MET_VALUES.get("stair_climber", 9.0),            "intensity": "high"},
    "jump_rope":              {"met": MET_VALUES.get("jump_rope", 12.0),               "intensity": "very high"},
    "hiking":                 {"met": 6.0, "intensity": "moderate"},
}


def calculate_cardio_duration(
    weight_kg: float,
    gender: str,
    height_cm: float,
    age: int,
    target_calories: int,
    preferred_activities: Optional[list[str]] = None,
) -> dict:
    """For each cardio activity, compute how many minutes to burn target_calories.

    Formula (inverse of MET):  minutes = target_calories / (MET * weight_kg / 60)
    Adjusted for gender/age via CalorieCalculator.
    """
    activities = _CARDIO_ACTIVITIES
    if preferred_activities:
        pref_set = set(a.lower() for a in preferred_activities)
        activities = {k: v for k, v in activities.items() if k in pref_set}
    if not activities:
        activities = _CARDIO_ACTIVITIES

    gender_factor = 0.9 if gender == "female" else 1.0
    age_factor = 1.0
    if age > 30:
        age_factor = 1 - ((age - 30) / 10) * 0.02

    options = []
    for name, info in activities.items():
        met = info["met"]
        cal_per_min = met * weight_kg / 60 * gender_factor * age_factor
        if cal_per_min <= 0:
            continue
        minutes = math.ceil(target_calories / cal_per_min)
        actual_burn = round(cal_per_min * minutes)
        options.append({
            "activity": name,
            "met_value": met,
            "duration_minutes": minutes,
            "calories_burned": actual_burn,
            "intensity": info["intensity"],
        })

    options.sort(key=lambda o: o["duration_minutes"])

    return {
        "target_calories": target_calories,
        "options": options,
    }
