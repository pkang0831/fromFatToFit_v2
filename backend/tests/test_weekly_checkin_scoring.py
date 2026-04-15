from app.schemas.weekly_checkin_schemas import (
    BodyObservation,
    EstimatedBodyFatRange,
    GoalWeighting,
    ImageQualityObservation,
    RegionNotes,
    VisualObservations,
)
from app.services.weekly_checkin_scoring import (
    build_hologram_visualization,
    build_regional_visualization,
    classify_weekly_status,
    compute_derived_scores,
    compute_weekly_delta,
)


def _observation(
    *,
    abdomen_softness: float,
    lower_abdomen_protrusion: float,
    ab_definition: float,
    chest_definition: float,
    arm_definition: float,
    shoulder_roundness: float,
    v_taper_visibility: float,
    overall_visual_leanness: float,
    comparison_confidence: float = 0.8,
) -> BodyObservation:
    return BodyObservation(
        image_quality=ImageQualityObservation(
            frontal_pose=0.92,
            body_visibility=0.94,
            lighting_consistency=0.8,
            pose_consistency=0.82,
            comparison_confidence=comparison_confidence,
            quality_flags=["none"],
        ),
        observations=VisualObservations(
            abdomen_softness=abdomen_softness,
            lower_abdomen_protrusion=lower_abdomen_protrusion,
            ab_definition=ab_definition,
            chest_definition=chest_definition,
            arm_definition=arm_definition,
            shoulder_roundness=shoulder_roundness,
            v_taper_visibility=v_taper_visibility,
            overall_visual_leanness=overall_visual_leanness,
        ),
        estimated_ranges=EstimatedBodyFatRange(
            body_fat_percent_min=15,
            body_fat_percent_max=19,
            body_fat_confidence=0.62,
        ),
        qualitative_summary=[
            "Midsection looks slightly tighter.",
            "Arm definition is stable.",
        ],
        region_notes=RegionNotes(
            abdomen="Waistline appears tighter.",
            chest="Chest definition is slightly clearer.",
            arms="Arm outline is mostly stable.",
            shoulders="Shoulder line is unchanged.",
        ),
    )


def test_compute_derived_scores_favors_leanness_when_softness_drops():
    observation = _observation(
        abdomen_softness=4.2,
        lower_abdomen_protrusion=3.8,
        ab_definition=6.2,
        chest_definition=6.1,
        arm_definition=6.8,
        shoulder_roundness=6.2,
        v_taper_visibility=6.0,
        overall_visual_leanness=6.5,
    )

    scores = compute_derived_scores(
        observation,
        GoalWeighting(prioritize_leanness=0.6, prioritize_definition=0.25, target_body_fat=12),
    )

    assert scores.leanness_score > scores.definition_score - 5
    assert 0 <= scores.goal_proximity_score <= 100


def test_compute_weekly_delta_applies_confidence_multiplier():
    previous = _observation(
        abdomen_softness=6.5,
        lower_abdomen_protrusion=6.1,
        ab_definition=3.5,
        chest_definition=5.1,
        arm_definition=5.9,
        shoulder_roundness=5.6,
        v_taper_visibility=5.0,
        overall_visual_leanness=4.8,
        comparison_confidence=0.8,
    )
    current = _observation(
        abdomen_softness=5.7,
        lower_abdomen_protrusion=5.4,
        ab_definition=4.2,
        chest_definition=5.5,
        arm_definition=6.2,
        shoulder_roundness=5.8,
        v_taper_visibility=5.3,
        overall_visual_leanness=5.4,
        comparison_confidence=0.6,
    )

    previous_scores = compute_derived_scores(previous, GoalWeighting())
    current_scores = compute_derived_scores(current, GoalWeighting())
    delta, confidence = compute_weekly_delta(previous, current, previous_scores, current_scores)

    assert confidence == 0.6
    assert delta.abdomen_softness < 0
    assert delta.ab_definition > 0
    assert delta.goal_proximity_score > 0


def test_classify_weekly_status_prefers_low_confidence_over_false_change():
    assert classify_weekly_status(3.2, 0.4) == "low_confidence"
    assert classify_weekly_status(1.8, 0.7) == "improved"
    assert classify_weekly_status(-1.2, 0.8) == "regressed"
    assert classify_weekly_status(0.2, 0.9) == "stable"


def test_regional_and_hologram_visualization_produce_meaningful_outputs():
    previous = _observation(
        abdomen_softness=6.1,
        lower_abdomen_protrusion=5.9,
        ab_definition=3.4,
        chest_definition=5.0,
        arm_definition=5.8,
        shoulder_roundness=5.8,
        v_taper_visibility=4.9,
        overall_visual_leanness=4.7,
        comparison_confidence=0.76,
    )
    current = _observation(
        abdomen_softness=5.5,
        lower_abdomen_protrusion=5.2,
        ab_definition=4.0,
        chest_definition=5.4,
        arm_definition=6.3,
        shoulder_roundness=5.9,
        v_taper_visibility=5.2,
        overall_visual_leanness=5.3,
        comparison_confidence=0.76,
    )

    previous_scores = compute_derived_scores(previous, GoalWeighting())
    current_scores = compute_derived_scores(current, GoalWeighting())
    delta, confidence = compute_weekly_delta(previous, current, previous_scores, current_scores)
    regions = build_regional_visualization(current, delta)
    hologram = build_hologram_visualization(current_scores, confidence)

    assert [region.region for region in regions] == ["abdomen", "chest", "arms"]
    assert any(region.status == "improved" for region in regions)
    assert 0 <= hologram.body_clarity <= 1
    assert 0 <= hologram.pedestal_progress <= 1
