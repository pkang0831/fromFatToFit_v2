"""Goal Planner calculation engine.

Tier comparison, macro splits, whole-food suggestions, dish composition,
and automatic meal-plan recommendations.
"""

from __future__ import annotations

import math
import random
import logging
from typing import Optional

from .food_database_service import get_food_database

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────────────────────

KCAL_PER_KG_FAT = 7700

MACRO_PRESETS: dict[str, tuple[float, float, float]] = {
    "balanced":     (40, 30, 30),
    "high_protein": (30, 40, 30),
    "keto":         (10, 30, 60),
    "low_fat":      (55, 25, 20),
}

TIER_LEVELS = [300, 500, 700, 1000]

MEAL_LABELS = [
    "Breakfast", "Lunch", "Dinner",
    "Snack 1", "Snack 2", "Snack 3", "Snack 4", "Snack 5",
]


# ── BMR / TDEE (shared with nutrition_planner) ──────────────────────────────

def _bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


_ACTIVITY_MULT = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def _tdee(weight_kg: float, height_cm: float, age: int,
          gender: str, activity_level: str) -> float:
    return _bmr(weight_kg, height_cm, age, gender) * _ACTIVITY_MULT.get(
        activity_level, 1.55
    )


# ── Tier comparison ──────────────────────────────────────────────────────────

def calculate_tier_comparison(
    current_weight_kg: float,
    current_bf_pct: float,
    target_bf_pct: float,
    gender: str,
    age: int,
    height_cm: float,
    activity_level: str,
    target_weight_kg: Optional[float] = None,
) -> dict:
    """Produce 4 calorie tiers with weekly change rates and timelines."""
    bmr_val = round(_bmr(current_weight_kg, height_cm, age, gender))
    tdee_val = round(_tdee(current_weight_kg, height_cm, age, gender, activity_level))

    current_fat_kg = current_weight_kg * current_bf_pct / 100
    current_lean_kg = current_weight_kg - current_fat_kg

    if target_weight_kg is None:
        target_fat_kg = current_lean_kg * target_bf_pct / (100 - target_bf_pct)
        target_weight_kg = current_lean_kg + target_fat_kg
    else:
        target_fat_kg = target_weight_kg * target_bf_pct / 100

    fat_to_change_kg = current_fat_kg - target_fat_kg
    direction = "deficit" if fat_to_change_kg > 0 else "surplus"

    tiers = []
    for level in TIER_LEVELS:
        cal_change = -level if direction == "deficit" else level
        daily_cals = max(int(bmr_val * 0.8), tdee_val + cal_change)

        weekly_change_kg = round(cal_change * 7 / KCAL_PER_KG_FAT, 3)
        if abs(weekly_change_kg) < 0.001:
            weeks_needed = 999
        else:
            weeks_needed = max(1, int(math.ceil(abs(fat_to_change_kg / weekly_change_kg))))

        milestones = []
        for m in range(1, min(13, (weeks_needed // 4) + 2)):
            weeks_elapsed = m * 4
            fat_changed = weekly_change_kg * weeks_elapsed
            proj_fat = current_fat_kg - fat_changed if direction == "deficit" else current_fat_kg + fat_changed
            proj_fat = max(0.5, proj_fat)
            proj_weight = current_lean_kg + proj_fat
            proj_bf = round(proj_fat / proj_weight * 100, 1) if proj_weight > 0 else current_bf_pct

            milestones.append({
                "month": m,
                "projected_weight_kg": round(proj_weight, 1),
                "projected_bf_pct": proj_bf,
                "fat_lost_kg": round(abs(fat_changed), 1),
                "lean_mass_kg": round(current_lean_kg, 1),
            })

        safety = ""
        if daily_cals < bmr_val:
            safety = f"Warning: {daily_cals} kcal is below BMR ({bmr_val}). Not recommended long-term."
        elif level >= 1000:
            safety = "Aggressive tier — monitor energy, sleep, and mood closely."
        else:
            safety = "Sustainable pace for most individuals."

        tiers.append({
            "deficit_or_surplus": cal_change,
            "daily_calories": daily_cals,
            "weekly_change_kg": weekly_change_kg,
            "weeks_to_goal": weeks_needed,
            "monthly_milestones": milestones,
            "safety_note": safety,
        })

    return {
        "tdee": tdee_val,
        "bmr": bmr_val,
        "direction": direction,
        "tiers": tiers,
    }


# ── Macro split ──────────────────────────────────────────────────────────────

def calculate_macro_split(
    daily_calories: int,
    weight_kg: float,
    preset: Optional[str] = None,
    carb_pct: Optional[float] = None,
    protein_pct: Optional[float] = None,
    fat_pct: Optional[float] = None,
) -> dict:
    """Calculate macro grams from percentage split or preset."""
    if preset and preset in MACRO_PRESETS:
        c, p, f = MACRO_PRESETS[preset]
    elif carb_pct is not None and protein_pct is not None and fat_pct is not None:
        total = carb_pct + protein_pct + fat_pct
        c = carb_pct / total * 100
        p = protein_pct / total * 100
        f = fat_pct / total * 100
    else:
        c, p, f = MACRO_PRESETS["balanced"]
        preset = "balanced"

    carb_g = int(daily_calories * c / 100 / 4)
    protein_g = int(daily_calories * p / 100 / 4)
    fat_g = int(daily_calories * f / 100 / 9)
    cal_check = carb_g * 4 + protein_g * 4 + fat_g * 9

    return {
        "preset_used": preset,
        "breakdown": {
            "carb_pct": round(c, 1),
            "protein_pct": round(p, 1),
            "fat_pct": round(f, 1),
            "carb_g": carb_g,
            "protein_g": protein_g,
            "fat_g": fat_g,
            "calories_check": cal_check,
        },
    }


# ── Food suggestions ────────────────────────────────────────────────────────

def _density_score(food: dict, priority: str) -> float:
    """Score a food by how much of the priority macro it delivers per calorie."""
    n = food.get("nutrition_per_100g", {})
    cals = n.get("calories", 1) or 1
    if priority == "protein":
        return n.get("protein", 0) / cals * 100
    if priority == "carb":
        return n.get("carbs", 0) / cals * 100
    if priority == "fat":
        return n.get("fat", 0) / cals * 100
    return (n.get("protein", 0) + n.get("carbs", 0) + n.get("fat", 0)) / cals * 100


def suggest_whole_foods(
    protein_g: int,
    carb_g: int,
    fat_g: int,
    priority: str = "balanced",
    categories: Optional[list[str]] = None,
    limit: int = 20,
) -> dict:
    """Return whole foods ranked by macro density for the given priority."""
    db = get_food_database()
    foods = db.foods

    if categories:
        cat_set = set(c.lower() for c in categories)
        foods = [f for f in foods if f.get("category", "").lower() in cat_set]

    scored = []
    for f in foods:
        n = f.get("nutrition_per_100g", {})
        servings = f.get("common_serving_sizes", [])
        serving_name = servings[0]["name"] if servings else None
        serving_g = servings[0]["grams"] if servings else None

        scored.append({
            "id": f["id"],
            "name": f["name"],
            "category": f.get("category", ""),
            "calories_per_100g": n.get("calories", 0),
            "protein_per_100g": n.get("protein", 0),
            "carb_per_100g": n.get("carbs", 0),
            "fat_per_100g": n.get("fat", 0),
            "density_score": round(_density_score(f, priority), 2),
            "common_serving": serving_name,
            "common_serving_g": serving_g,
        })

    scored.sort(key=lambda x: x["density_score"], reverse=True)

    return {
        "priority": priority,
        "foods": scored[:limit],
        "total_available": len(scored),
    }


# ── Dish composition ────────────────────────────────────────────────────────

def compose_dishes(
    ingredients: list[dict],
    meals_per_day: int = 3,
    target_calories: Optional[int] = None,
    target_protein_g: Optional[int] = None,
    target_carb_g: Optional[int] = None,
    target_fat_g: Optional[int] = None,
) -> dict:
    """Build per-meal breakdown from selected ingredients, distributing evenly."""
    db = get_food_database()

    resolved = []
    for ing in ingredients:
        food = db.get_food_by_id(ing["food_id"])
        if not food:
            logger.warning(f"Food ID not found: {ing['food_id']}")
            continue
        n = food["nutrition_per_100g"]
        mult = ing["amount_g"] / 100
        resolved.append({
            "food_id": food["id"],
            "food_name": food["name"],
            "amount_g": ing["amount_g"],
            "calories": round(n["calories"] * mult, 1),
            "protein_g": round(n["protein"] * mult, 1),
            "carb_g": round(n.get("carbs", 0) * mult, 1),
            "fat_g": round(n["fat"] * mult, 1),
        })

    day_cal = sum(r["calories"] for r in resolved)
    day_p = sum(r["protein_g"] for r in resolved)
    day_c = sum(r["carb_g"] for r in resolved)
    day_f = sum(r["fat_g"] for r in resolved)

    meals = []
    per_meal = max(1, len(resolved) // meals_per_day)
    for i in range(meals_per_day):
        start = i * per_meal
        end = start + per_meal if i < meals_per_day - 1 else len(resolved)
        meal_items = resolved[start:end]
        if not meal_items:
            continue
        meals.append({
            "meal_label": MEAL_LABELS[i] if i < len(MEAL_LABELS) else f"Meal {i + 1}",
            "ingredients": meal_items,
            "total_calories": round(sum(m["calories"] for m in meal_items), 1),
            "total_protein_g": round(sum(m["protein_g"] for m in meal_items), 1),
            "total_carb_g": round(sum(m["carb_g"] for m in meal_items), 1),
            "total_fat_g": round(sum(m["fat_g"] for m in meal_items), 1),
        })

    target_diff = None
    if target_calories is not None:
        target_diff = {
            "calories": round(day_cal - target_calories, 1),
            "protein_g": round(day_p - (target_protein_g or 0), 1) if target_protein_g else None,
            "carb_g": round(day_c - (target_carb_g or 0), 1) if target_carb_g else None,
            "fat_g": round(day_f - (target_fat_g or 0), 1) if target_fat_g else None,
        }

    return {
        "meals": meals,
        "day_total_calories": round(day_cal, 1),
        "day_total_protein_g": round(day_p, 1),
        "day_total_carb_g": round(day_c, 1),
        "day_total_fat_g": round(day_f, 1),
        "target_diff": target_diff,
    }


# ── Auto meal-plan recommendation ───────────────────────────────────────────

_MEAL_TEMPLATES = {
    "breakfast": {
        "protein_sources": ["meat_poultry", "dairy"],
        "carb_sources": ["grains"],
        "extras": ["fruits", "dairy"],
        "protein_pct": 0.25, "carb_pct": 0.25, "fat_pct": 0.25,
    },
    "lunch": {
        "protein_sources": ["meat_poultry", "seafood"],
        "carb_sources": ["grains"],
        "extras": ["vegetables"],
        "protein_pct": 0.35, "carb_pct": 0.35, "fat_pct": 0.35,
    },
    "dinner": {
        "protein_sources": ["meat_poultry", "seafood"],
        "carb_sources": ["grains"],
        "extras": ["vegetables"],
        "protein_pct": 0.30, "carb_pct": 0.30, "fat_pct": 0.30,
    },
    "snack": {
        "protein_sources": ["dairy", "nuts_seeds"],
        "carb_sources": ["fruits"],
        "extras": ["nuts_seeds"],
        "protein_pct": 0.10, "carb_pct": 0.10, "fat_pct": 0.10,
    },
}

_EXCLUDE_CATEGORIES = {
    "fast_food", "desserts", "beverages", "brand_foods",
    "condiments", "snacks", "oils_fats",
}

_NOT_STANDALONE_FOODS = {
    "lemon", "lime", "garlic", "ginger", "cilantro", "parsley",
    "basil", "mint", "chili", "jalapeno", "vinegar", "mustard",
    "soy_sauce", "hot_sauce", "fish_sauce", "sesame_oil",
    "cooking_spray", "baking", "yeast", "vanilla", "cinnamon",
}


def _is_standalone_food(food: dict) -> bool:
    """Filter out garnish/seasoning/condiment items nobody eats as a meal."""
    fid = food.get("id", "").lower()
    name = food.get("name", "").lower()
    for kw in _NOT_STANDALONE_FOODS:
        if kw in fid or kw in name:
            return False
    n = food.get("nutrition_per_100g", {})
    if n.get("calories", 0) < 15:
        return False
    return True


def _max_serving_g(food: dict) -> float:
    """Reasonable max single-serving amount based on common_serving_sizes."""
    servings = food.get("common_serving_sizes", [])
    if servings:
        max_common = max(s.get("grams", 100) for s in servings)
        return min(350, max_common * 2.5)
    cat = food.get("category", "")
    if cat in ("nuts_seeds",):
        return 60
    if cat in ("fruits",):
        return 250
    if cat in ("dairy",):
        return 300
    return 300


def _best_food_for_macro(
    foods: list[dict], macro: str, exclude_ids: set[str],
) -> Optional[dict]:
    """Pick a good standalone food for a given macro, avoiding already-used foods."""
    key_map = {"protein": "protein", "carb": "carbs", "fat": "fat"}
    mk = key_map.get(macro, macro)

    candidates = [
        f for f in foods
        if f["id"] not in exclude_ids
        and f.get("category", "") not in _EXCLUDE_CATEGORIES
        and _is_standalone_food(f)
        and f.get("nutrition_per_100g", {}).get(mk, 0) >= 3
    ]
    if not candidates:
        return None

    candidates.sort(
        key=lambda f: f.get("nutrition_per_100g", {}).get(mk, 0),
        reverse=True,
    )
    top = candidates[:8]
    return random.choice(top) if top else None


def _amount_for_calories(food: dict, target_cal: float) -> float:
    """Calculate grams of food to hit a calorie target, capped to a sane serving."""
    cal_per_100 = food.get("nutrition_per_100g", {}).get("calories", 100) or 100
    raw = target_cal / cal_per_100 * 100
    cap = _max_serving_g(food)
    return round(max(25, min(cap, raw)) / 5) * 5


def _make_ingredient(food: dict, amount_g: float) -> dict:
    n = food["nutrition_per_100g"]
    mult = amount_g / 100
    return {
        "food_id": food["id"],
        "food_name": food["name"],
        "amount_g": amount_g,
        "calories": round(n["calories"] * mult, 1),
        "protein_g": round(n["protein"] * mult, 1),
        "carb_g": round(n.get("carbs", 0) * mult, 1),
        "fat_g": round(n["fat"] * mult, 1),
    }


def auto_recommend_meal_plan(
    daily_calories: int,
    protein_g: int,
    carb_g: int,
    fat_g: int,
    meals_per_day: int = 3,
) -> dict:
    """Auto-pick whole foods from the DB, calorie-budgeted per meal."""
    db = get_food_database()
    all_foods = [
        f for f in db.foods
        if f.get("category", "") not in _EXCLUDE_CATEGORIES
        and _is_standalone_food(f)
    ]

    if meals_per_day <= 2:
        meal_keys = ["breakfast", "dinner"]
    elif meals_per_day == 3:
        meal_keys = ["breakfast", "lunch", "dinner"]
    elif meals_per_day == 4:
        meal_keys = ["breakfast", "lunch", "dinner", "snack"]
    else:
        meal_keys = ["breakfast", "lunch", "snack", "dinner", "snack"]

    cal_pcts = {
        "breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10,
    }
    total_pct = sum(cal_pcts.get(k, 0.25) for k in meal_keys)

    used_ids: set[str] = set()
    meals = []

    for i, mk in enumerate(meal_keys):
        template = _MEAL_TEMPLATES.get(mk, _MEAL_TEMPLATES["lunch"])
        meal_cal_budget = daily_calories * cal_pcts.get(mk, 0.25) / total_pct

        # Allocate ~50% of meal calories to protein, ~35% to carb, ~15% to side
        protein_cal = meal_cal_budget * 0.50
        carb_cal = meal_cal_budget * 0.35
        side_cal = meal_cal_budget * 0.15

        ingredients = []

        # 1) Protein source
        cat_foods = [f for f in all_foods if f.get("category") in template["protein_sources"]]
        pf = _best_food_for_macro(cat_foods or all_foods, "protein", used_ids)
        if pf:
            amt = _amount_for_calories(pf, protein_cal)
            ingredients.append(_make_ingredient(pf, amt))
            used_ids.add(pf["id"])

        # 2) Carb source
        cat_foods = [f for f in all_foods if f.get("category") in template["carb_sources"]]
        cf = _best_food_for_macro(cat_foods or all_foods, "carb", used_ids)
        if cf:
            amt = _amount_for_calories(cf, carb_cal)
            ingredients.append(_make_ingredient(cf, amt))
            used_ids.add(cf["id"])

        # 3) Veggie/fruit side
        extra_cats = template.get("extras", ["vegetables"])
        extras = [
            f for f in all_foods
            if f.get("category") in extra_cats
            and f["id"] not in used_ids
            and _is_standalone_food(f)
        ]
        if extras:
            ex = random.choice(extras[:15])
            amt = _amount_for_calories(ex, side_cal)
            ingredients.append(_make_ingredient(ex, amt))
            used_ids.add(ex["id"])

        meal_total_cal = sum(ing["calories"] for ing in ingredients)
        meal_total_p = sum(ing["protein_g"] for ing in ingredients)
        meal_total_c = sum(ing["carb_g"] for ing in ingredients)
        meal_total_f = sum(ing["fat_g"] for ing in ingredients)

        label = mk.capitalize()
        if meal_keys.count(mk) > 1:
            label = f"Snack {meal_keys[:i+1].count(mk)}" if mk == "snack" else label

        meals.append({
            "meal_label": label,
            "ingredients": ingredients,
            "total_calories": round(meal_total_cal, 1),
            "total_protein_g": round(meal_total_p, 1),
            "total_carb_g": round(meal_total_c, 1),
            "total_fat_g": round(meal_total_f, 1),
        })

    # Post-hoc scale: if total calories drifted, proportionally adjust all amounts
    raw_total_cal = sum(m["total_calories"] for m in meals)
    if raw_total_cal > 0 and abs(raw_total_cal - daily_calories) > daily_calories * 0.05:
        scale = daily_calories / raw_total_cal
        for meal in meals:
            for ing in meal["ingredients"]:
                ing["amount_g"] = round(ing["amount_g"] * scale / 5) * 5
                ing["amount_g"] = max(25, ing["amount_g"])
                mult = ing["amount_g"] / 100
                food = db.get_food_by_id(ing["food_id"])
                if food:
                    n = food["nutrition_per_100g"]
                    ing["calories"] = round(n["calories"] * mult, 1)
                    ing["protein_g"] = round(n["protein"] * mult, 1)
                    ing["carb_g"] = round(n.get("carbs", 0) * mult, 1)
                    ing["fat_g"] = round(n["fat"] * mult, 1)
            meal["total_calories"] = round(sum(ig["calories"] for ig in meal["ingredients"]), 1)
            meal["total_protein_g"] = round(sum(ig["protein_g"] for ig in meal["ingredients"]), 1)
            meal["total_carb_g"] = round(sum(ig["carb_g"] for ig in meal["ingredients"]), 1)
            meal["total_fat_g"] = round(sum(ig["fat_g"] for ig in meal["ingredients"]), 1)

    day_cal = sum(m["total_calories"] for m in meals)
    day_p = sum(m["total_protein_g"] for m in meals)
    day_c = sum(m["total_carb_g"] for m in meals)
    day_f = sum(m["total_fat_g"] for m in meals)

    return {
        "meals": meals,
        "day_total_calories": round(day_cal, 1),
        "day_total_protein_g": round(day_p, 1),
        "day_total_carb_g": round(day_c, 1),
        "day_total_fat_g": round(day_f, 1),
        "target_diff": {
            "calories": round(day_cal - daily_calories, 1),
            "protein_g": round(day_p - protein_g, 1),
            "carb_g": round(day_c - carb_g, 1),
            "fat_g": round(day_f - fat_g, 1),
        },
    }
