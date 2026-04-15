from __future__ import annotations

from dataclasses import dataclass

from ..schemas.weekly_checkin_schemas import (
    BodyObservation,
    DerivedScores,
    GoalWeighting,
    HologramVisualization,
    RegionStatus,
    RegionVisualization,
    WeeklyDelta,
    WeeklyStatus,
)


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _scale10_to_100(value: float) -> float:
    return clamp(value * 10.0)


def compute_derived_scores(observation: BodyObservation, goal: GoalWeighting) -> DerivedScores:
    o = observation.observations

    leanness = _scale10_to_100(
        (
            0.30 * (10 - o.abdomen_softness)
            + 0.25 * (10 - o.lower_abdomen_protrusion)
            + 0.25 * o.overall_visual_leanness
            + 0.20 * o.ab_definition
        )
    )

    definition = _scale10_to_100(
        (
            0.30 * o.ab_definition
            + 0.25 * o.chest_definition
            + 0.25 * o.arm_definition
            + 0.20 * o.shoulder_roundness
        )
    )

    proportion = _scale10_to_100(
        (
            0.55 * o.v_taper_visibility
            + 0.25 * o.shoulder_roundness
            + 0.20 * o.arm_definition
        )
    )

    goal_proximity = clamp(
        leanness * goal.prioritize_leanness
        + definition * goal.prioritize_definition
        + proportion * goal.prioritize_proportion
    )

    return DerivedScores(
        leanness_score=round(leanness, 1),
        definition_score=round(definition, 1),
        proportion_score=round(proportion, 1),
        goal_proximity_score=round(goal_proximity, 1),
    )


def compute_weekly_delta(
    previous: BodyObservation,
    current: BodyObservation,
    previous_scores: DerivedScores,
    current_scores: DerivedScores,
) -> tuple[WeeklyDelta, float]:
    confidence = min(
        previous.image_quality.comparison_confidence,
        current.image_quality.comparison_confidence,
    )

    delta = WeeklyDelta(
        abdomen_softness=round(
            (current.observations.abdomen_softness - previous.observations.abdomen_softness)
            * confidence,
            2,
        ),
        lower_abdomen_protrusion=round(
            (
                current.observations.lower_abdomen_protrusion
                - previous.observations.lower_abdomen_protrusion
            )
            * confidence,
            2,
        ),
        ab_definition=round(
            (current.observations.ab_definition - previous.observations.ab_definition) * confidence,
            2,
        ),
        chest_definition=round(
            (current.observations.chest_definition - previous.observations.chest_definition)
            * confidence,
            2,
        ),
        arm_definition=round(
            (current.observations.arm_definition - previous.observations.arm_definition)
            * confidence,
            2,
        ),
        overall_visual_leanness=round(
            (
                current.observations.overall_visual_leanness
                - previous.observations.overall_visual_leanness
            )
            * confidence,
            2,
        ),
        goal_proximity_score=round(
            (current_scores.goal_proximity_score - previous_scores.goal_proximity_score) * confidence,
            2,
        ),
    )
    return delta, confidence


def classify_weekly_status(delta_goal_proximity: float, comparison_confidence: float) -> WeeklyStatus:
    if comparison_confidence < 0.55:
        return "low_confidence"
    if delta_goal_proximity > 1.5:
        return "improved"
    if delta_goal_proximity < -1.0:
        return "regressed"
    return "stable"


def _region_status(value: float, positive_direction: bool = True) -> RegionStatus:
    normalized = value if positive_direction else -value
    if normalized > 0.4:
        return "improved"
    if normalized < -0.4:
        return "regressed"
    return "stable"


def _region_value_label(status: RegionStatus, improved_label: str, regressed_label: str) -> str:
    if status == "improved":
        return improved_label
    if status == "regressed":
        return regressed_label
    return "Stable"


def build_regional_visualization(
    observation: BodyObservation,
    delta: WeeklyDelta | None,
) -> list[RegionVisualization]:
    if not delta:
        return [
            RegionVisualization(
                region="abdomen",
                label="Abdomen",
                value="Baseline",
                note=observation.region_notes.abdomen,
                status="stable",
                intensity=round(clamp(observation.observations.ab_definition / 10.0, 0.18, 0.8), 2),
            ),
            RegionVisualization(
                region="chest",
                label="Chest",
                value="Baseline",
                note=observation.region_notes.chest,
                status="stable",
                intensity=round(clamp(observation.observations.chest_definition / 10.0, 0.18, 0.8), 2),
            ),
            RegionVisualization(
                region="arms",
                label="Arms",
                value="Baseline",
                note=observation.region_notes.arms,
                status="stable",
                intensity=round(clamp(observation.observations.arm_definition / 10.0, 0.18, 0.8), 2),
            ),
        ]

    abdomen_signal = (
        (-delta.abdomen_softness * 0.4)
        + (-delta.lower_abdomen_protrusion * 0.35)
        + (delta.ab_definition * 0.25)
    )
    chest_signal = delta.chest_definition
    arms_signal = delta.arm_definition

    abdomen_status = _region_status(abdomen_signal)
    chest_status = _region_status(chest_signal)
    arms_status = _region_status(arms_signal)

    return [
        RegionVisualization(
            region="abdomen",
            label="Abdomen",
            value=_region_value_label(abdomen_status, "Tighter", "Softer"),
            note=observation.region_notes.abdomen,
            status=abdomen_status,
            intensity=round(clamp(abs(abdomen_signal) / 2.2, 0.18, 0.92), 2),
        ),
        RegionVisualization(
            region="chest",
            label="Chest",
            value=_region_value_label(chest_status, "More defined", "Less defined"),
            note=observation.region_notes.chest,
            status=chest_status,
            intensity=round(clamp(abs(chest_signal) / 1.8, 0.16, 0.88), 2),
        ),
        RegionVisualization(
            region="arms",
            label="Arms",
            value=_region_value_label(arms_status, "Sharper", "Softer"),
            note=observation.region_notes.arms,
            status=arms_status,
            intensity=round(clamp(abs(arms_signal) / 1.8, 0.16, 0.88), 2),
        ),
    ]


def build_hologram_visualization(
    scores: DerivedScores,
    comparison_confidence: float,
) -> HologramVisualization:
    progress = clamp(scores.goal_proximity_score / 100.0, 0.08, 1.0)
    clarity = clamp((scores.leanness_score * 0.55 + comparison_confidence * 45.0) / 100.0, 0.18, 1.0)
    glow = clamp((scores.definition_score * 0.5 + scores.goal_proximity_score * 0.35) / 100.0, 0.22, 1.0)

    return HologramVisualization(
        glow_intensity=round(glow, 2),
        body_clarity=round(clarity, 2),
        pedestal_progress=round(progress, 2),
    )
