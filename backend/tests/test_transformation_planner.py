"""Tests for the transformation journey planner, prompts, and plan generation."""

import pytest

from app.services.transformation_types import TransformationMode, MuscleGainSpec
from app.services.transformation_planner import (
    classify_mode,
    estimate_timeline_weeks,
    build_plan,
    MIN_BF_MALE,
    MIN_BF_FEMALE,
    MAX_BF,
)
from app.services.transformation_prompts import render_stage_prompt


# ── Mode classification ────────────────────────────────────────────────────


class TestClassifyMode:
    def test_cut(self):
        assert classify_mode(25, 12, 0, "male") == TransformationMode.CUT

    def test_recomp_with_muscle_gain(self):
        assert classify_mode(20, 20, 3, "male") == TransformationMode.RECOMP

    def test_recomp_cut_with_large_muscle(self):
        assert classify_mode(25, 18, 3, "male") == TransformationMode.RECOMP

    def test_lean_bulk(self):
        assert classify_mode(12, 15, 3, "male") == TransformationMode.LEAN_BULK

    def test_mass_gain(self):
        assert classify_mode(15, 25, 0, "male") == TransformationMode.MASS_GAIN

    def test_unsupported_below_floor_male(self):
        assert classify_mode(20, 3, 0, "male") == TransformationMode.UNSUPPORTED

    def test_unsupported_below_floor_female(self):
        assert classify_mode(25, 10, 0, "female") == TransformationMode.UNSUPPORTED

    def test_unsupported_above_ceiling(self):
        assert classify_mode(20, 50, 0, "male") == TransformationMode.UNSUPPORTED

    def test_small_cut_no_muscle(self):
        assert classify_mode(18, 17, 0, "male") == TransformationMode.CUT

    def test_small_gain_no_muscle(self):
        assert classify_mode(17, 18, 0, "male") == TransformationMode.LEAN_BULK

    def test_female_cut(self):
        assert classify_mode(30, 22, 0, "female") == TransformationMode.CUT


# ── Timeline bounds ─────────────────────────────────────────────────────────


class TestTimeline:
    def test_minimum_weeks(self):
        weeks = estimate_timeline_weeks(TransformationMode.CUT, 20, 18, 0)
        assert weeks >= 8

    def test_maximum_weeks(self):
        weeks = estimate_timeline_weeks(TransformationMode.RECOMP, 30, 10, 5)
        assert weeks <= 104

    def test_cut_conservative(self):
        weeks = estimate_timeline_weeks(TransformationMode.CUT, 25, 12, 0)
        assert weeks >= 20, "13% BF cut should take at least 20 weeks"

    def test_mass_gain_reasonable(self):
        weeks = estimate_timeline_weeks(TransformationMode.MASS_GAIN, 15, 25, 0)
        assert weeks >= 8


# ── Guardrails (build_plan) ─────────────────────────────────────────────────


class TestGuardrails:
    def test_extreme_low_bf_male_is_clamped(self):
        plan = build_plan(current_bf=20, target_bf=3, gender="male")
        assert plan.target_bf == MIN_BF_MALE
        assert plan.target_bf_clamped == MIN_BF_MALE
        assert any("clamped" in w.lower() or "below" in w.lower() for w in plan.warnings)

    def test_extreme_low_bf_female_is_clamped(self):
        plan = build_plan(current_bf=25, target_bf=10, gender="female")
        assert plan.target_bf == MIN_BF_FEMALE
        assert any("clamped" in w.lower() or "below" in w.lower() for w in plan.warnings)

    def test_above_ceiling_warns(self):
        plan = build_plan(current_bf=20, target_bf=50, gender="male")
        assert any("outside" in w.lower() or "supported" in w.lower() for w in plan.warnings)

    def test_nearly_identical_bf_warns(self):
        plan = build_plan(current_bf=20, target_bf=20.2, gender="male")
        assert any("nearly identical" in w.lower() for w in plan.warnings)

    def test_higher_bf_never_implies_leaner(self):
        """Mass-gain descriptors must not positively assert athletic/lean traits."""
        plan = build_plan(current_bf=15, target_bf=25, gender="male")
        assert plan.mode == TransformationMode.MASS_GAIN
        positive_banned = [
            "more defined", "more vascular", "more muscular",
            "ab visible", "six-pack", "striation", "leaner",
            "visible abs", "muscle definition",
        ]
        for stage in plan.stages:
            if stage.stage_number == 0:
                continue
            desc_text = " ".join([
                stage.body_state.chest,
                stage.body_state.arms,
                stage.body_state.shoulders,
                stage.body_state.overall,
            ]).lower()
            for phrase in positive_banned:
                assert phrase not in desc_text, (
                    f"Stage {stage.stage_number} mass_gain descriptor "
                    f"contains banned phrase '{phrase}': {desc_text}"
                )

    def test_cut_never_adds_muscle_size(self):
        """Cut descriptors must not imply added muscle size."""
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        assert plan.mode == TransformationMode.CUT
        banned = ["bigger", "broader", "thicker"]
        for stage in plan.stages:
            if stage.stage_number == 0:
                continue
            for field in ["chest", "arms", "shoulders"]:
                val = getattr(stage.body_state, field).lower()
                for word in banned:
                    assert word not in val, (
                        f"Stage {stage.stage_number} cut descriptor '{field}' "
                        f"contains banned word '{word}': {val}"
                    )


# ── Stage progression ───────────────────────────────────────────────────────


class TestStageProgression:
    def test_five_stages(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        assert len(plan.stages) == 5

    def test_stage_0_is_original(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        s0 = plan.stages[0]
        assert s0.stage_number == 0
        assert s0.week == 0
        assert s0.label == "Original"
        assert s0.bf_pct == 25.0

    def test_final_stage_hits_target(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        assert plan.stages[-1].bf_pct == 12.0

    def test_bf_monotonic_decreasing_for_cut(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        bfs = [s.bf_pct for s in plan.stages]
        for i in range(1, len(bfs)):
            assert bfs[i] <= bfs[i - 1], f"BF not monotonic decreasing: {bfs}"

    def test_bf_monotonic_increasing_for_mass_gain(self):
        plan = build_plan(current_bf=15, target_bf=25, gender="male")
        bfs = [s.bf_pct for s in plan.stages]
        for i in range(1, len(bfs)):
            assert bfs[i] >= bfs[i - 1], f"BF not monotonic increasing: {bfs}"

    def test_weeks_monotonic_nondecreasing(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        weeks = [s.week for s in plan.stages]
        for i in range(1, len(weeks)):
            assert weeks[i] >= weeks[i - 1], f"Weeks not monotonic: {weeks}"

    def test_labels_are_ordered(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        labels = [s.label for s in plan.stages]
        assert labels == ["Original", "Early", "Mid", "Late", "Final"]

    def test_weight_progression_for_cut(self):
        plan = build_plan(
            current_bf=25, target_bf=12, gender="male", weight_kg=80.0,
        )
        weights = [s.weight_kg for s in plan.stages]
        assert all(w is not None for w in weights)
        for i in range(1, len(weights)):
            assert weights[i] <= weights[i - 1], f"Weight not decreasing in cut: {weights}"


# ── Prompt rendering ────────────────────────────────────────────────────────


class TestPromptRendering:
    def test_stage_0_returns_empty(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        assert plan.stages[0].prompt == ""

    def test_cut_prompts_contain_no_muscle_growth(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        for s in plan.stages[1:]:
            assert "Do not add any muscle mass" in s.prompt

    def test_mass_gain_prompts_contain_no_added_definition(self):
        plan = build_plan(current_bf=15, target_bf=25, gender="male")
        for s in plan.stages[1:]:
            assert "Do not make the person look more muscular" in s.prompt

    def test_all_prompts_contain_identity_anchor(self):
        plan = build_plan(current_bf=25, target_bf=12, gender="male")
        for s in plan.stages[1:]:
            assert "same face" in s.prompt
            assert "same pose" in s.prompt
            assert "same clothing" in s.prompt
            assert "same background" in s.prompt

    def test_lean_bulk_prompts_mention_muscle(self):
        plan = build_plan(
            current_bf=12, target_bf=15, gender="male",
            muscle_gains=MuscleGainSpec(chest_kg=2, shoulders_kg=2),
        )
        for s in plan.stages[1:]:
            assert "muscle" in s.prompt.lower()

    def test_recomp_prompts_constrain_size(self):
        plan = build_plan(
            current_bf=20, target_bf=18, gender="male",
            muscle_gains=MuscleGainSpec(chest_kg=2, back_kg=2),
        )
        for s in plan.stages[1:]:
            assert "Do not change muscle size" in s.prompt


# ── Plan completeness ──────────────────────────────────────────────────────


class TestPlanCompleteness:
    @pytest.fixture(params=[
        {"current_bf": 25, "target_bf": 12, "gender": "male"},
        {"current_bf": 15, "target_bf": 25, "gender": "male"},
        {"current_bf": 12, "target_bf": 15, "gender": "male",
         "muscle_gains": MuscleGainSpec(chest_kg=2)},
        {"current_bf": 30, "target_bf": 22, "gender": "female"},
    ])
    def plan(self, request):
        return build_plan(**request.param)

    def test_nutrition_plan_present(self, plan):
        assert plan.nutrition.daily_calories > 0
        assert plan.nutrition.protein_g > 0
        assert len(plan.nutrition.meal_structure) > 0
        assert plan.nutrition.disclaimer

    def test_workout_plan_present(self, plan):
        assert plan.workout.sessions_per_week > 0
        assert len(plan.workout.exercises) > 0
        assert plan.workout.split_type

    def test_disclaimer_present(self, plan):
        assert plan.disclaimer
        assert "not" in plan.disclaimer.lower()
        assert "medical" in plan.disclaimer.lower() or "advice" in plan.disclaimer.lower()

    def test_timeline_in_bounds(self, plan):
        assert 8 <= plan.total_weeks <= 104

    def test_nutrition_has_stage_notes(self, plan):
        assert len(plan.nutrition.stage_notes) > 0

    def test_workout_has_stage_adjustments(self, plan):
        assert len(plan.workout.stage_adjustments) > 0

    def test_nutrition_has_assumptions(self, plan):
        assert len(plan.nutrition.assumptions) > 0
