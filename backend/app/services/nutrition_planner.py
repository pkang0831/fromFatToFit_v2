"""Generate a conservative nutrition plan tied to the transformation mode."""

from __future__ import annotations

from .transformation_types import TransformationMode, NutritionPlan

_DISCLAIMER = (
    "This nutrition plan is an AI-generated estimate for educational purposes. "
    "It is not medical or clinical dietary advice. Consult a registered "
    "dietitian or physician before making significant dietary changes, "
    "especially if you have any health conditions."
)


def _estimate_tdee(
    weight_kg: float, height_cm: float, age: int,
    gender: str, activity_level: str,
) -> int:
    """Mifflin-St Jeor TDEE estimate."""
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    multipliers = {
        "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
        "active": 1.725, "very_active": 1.9, "heavy": 1.725, "athlete": 1.9,
    }
    return int(bmr * multipliers.get(activity_level.lower(), 1.55))


def _macros_from_calories(
    calories: int, protein_g: int, fat_g_min: int, fat_g_max: int,
) -> tuple[int, int]:
    """Return (carbs_g_min, carbs_g_max) after subtracting protein and fat."""
    protein_cals = protein_g * 4
    fat_cals_avg = ((fat_g_min + fat_g_max) / 2) * 9
    remaining = max(0, calories - protein_cals - fat_cals_avg)
    return int(remaining * 0.85 / 4), int(remaining * 1.15 / 4)


def build_nutrition_plan(
    mode: TransformationMode,
    current_bf: float,
    target_bf: float,
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    total_weeks: int,
) -> NutritionPlan:
    tdee = _estimate_tdee(weight_kg, height_cm, age, gender, activity_level)

    if mode == TransformationMode.CUT:
        deficit = 400 if current_bf > 20 else 300
        cals = tdee - deficit
        protein = int(weight_kg * 2.2)
        fat_min, fat_max = int(weight_kg * 0.8), int(weight_kg * 1.1)
        meals = [
            "3-4 meals per day, evenly spaced",
            "30-50 g protein per meal",
            "Largest meal post-workout when possible",
            "Prioritise whole foods, vegetables, lean protein",
        ]
        adj = (
            "Weigh daily, use weekly average. If no loss for 2 consecutive "
            "weeks, reduce by 100 kcal/day. Never go below BMR."
        )
        checkin = "Weekly weigh-in (same day, fasted). Bi-weekly progress photos."
        notes = {
            1: "Initial adaptation. Hunger may increase — stay consistent.",
            2: "Fat loss visible. Maintain protein. Consider a diet break if fatigued.",
            3: "Lower body fat slows progress. Patience required. Don't slash calories.",
            4: "Final push. Monitor energy and mood. Plan a maintenance phase afterwards.",
        }

    elif mode == TransformationMode.LEAN_BULK:
        cals = tdee + 250
        protein = int(weight_kg * 2.0)
        fat_min, fat_max = int(weight_kg * 0.8), int(weight_kg * 1.0)
        meals = [
            "4-5 meals per day including pre- and post-workout nutrition",
            "35-50 g protein per meal",
            "Higher carbs around training sessions",
            "Calorie-dense whole foods if appetite is low",
        ]
        adj = (
            "Weigh weekly. Aim for 0.25-0.5 kg gain per month. "
            "If gaining faster, reduce surplus by 100 kcal."
        )
        checkin = "Weekly weigh-in. Monthly progress photos and strength benchmarks."
        notes = {
            1: "Establish surplus. Focus on training intensity.",
            2: "Strength should be increasing. Monitor weight-gain rate.",
            3: "Some fat gain is expected. Don't panic-cut if gaining muscle.",
            4: "Evaluate body composition. Transition to maintenance or mini-cut if needed.",
        }

    elif mode == TransformationMode.MASS_GAIN:
        cals = tdee + 500
        protein = int(weight_kg * 1.8)
        fat_min, fat_max = int(weight_kg * 0.9), int(weight_kg * 1.3)
        meals = [
            "3-5 meals per day, consistent schedule",
            "25-40 g protein per meal",
            "Calorie-dense foods if appetite is limited",
            "Do not skip meals",
        ]
        adj = (
            "Weigh weekly. Aim for 0.5-1.0 kg total gain per month. "
            "Adjust if gaining too quickly or too slowly."
        )
        checkin = "Weekly weigh-in. Monthly check-ins."
        notes = {
            1: "Establish eating routine. Expect water-weight fluctuation initially.",
            2: "Weight gain should be steady.",
            3: "Monitor how clothes fit. Adjust if uncomfortable.",
            4: "Evaluate whether to continue gaining or transition to maintenance.",
        }

    else:  # RECOMP
        cals = tdee
        protein = int(weight_kg * 2.4)
        fat_min, fat_max = int(weight_kg * 0.8), int(weight_kg * 1.0)
        meals = [
            "3-4 meals per day, protein-focused",
            "40-50 g protein per meal",
            "Slight surplus on training days, slight deficit on rest days",
            "High-quality whole foods",
        ]
        adj = (
            "Weight should stay roughly stable. Focus on strength progression "
            "and visual changes rather than scale weight."
        )
        checkin = "Weekly weigh-in. Bi-weekly progress photos. Monthly strength tests."
        notes = {
            1: "Body recomposition is slow. Trust the process.",
            2: "Strength gains appear before visual changes.",
            3: "Visual changes becoming apparent. Continue consistency.",
            4: "Evaluate: continue recomp, or switch to a dedicated cut or bulk.",
        }

    carbs_min, carbs_max = _macros_from_calories(cals, protein, fat_min, fat_max)

    return NutritionPlan(
        daily_calories=cals,
        protein_g=protein,
        carbs_g_min=carbs_min,
        carbs_g_max=carbs_max,
        fat_g_min=fat_min,
        fat_g_max=fat_max,
        meal_structure=meals,
        weekly_adjustment=adj,
        checkin_cadence=checkin,
        stage_notes=notes,
        assumptions=[
            f"Estimated TDEE: {tdee} kcal/day",
            f"Activity level: {activity_level}",
            f"Starting weight: {weight_kg} kg",
            "Macros are starting points — adjust based on actual progress",
        ],
        disclaimer=_DISCLAIMER,
    )
