"""Deterministic prompt renderer for FLUX Kontext Pro stage images.

Every prompt preserves identity (face, skin tone, pose, clothing,
background, lighting, camera angle, framing) and describes ONLY
the specific body-composition change for that stage.
"""

from __future__ import annotations

from .transformation_types import (
    TransformationMode,
    TransformationStage,
    MuscleGainSpec,
)

_IDENTITY_FOOTER = (
    "Keep the exact same person — same face, same facial hair, same skin tone, "
    "same hair, same pose, same clothing, same background, same lighting, "
    "same camera angle, same framing. "
    "Do not change skin color, tattoos, scars, jewelry, or any background elements. "
    "Realistic photograph, not illustration."
)

_NO_MUSCLE_GROWTH = (
    "Do not add any muscle mass, muscle size, or new muscle definition "
    "beyond what fat loss would naturally reveal."
)

_NO_ADDED_DEFINITION = (
    "Do not make the person look more muscular, more athletic, or more defined — "
    "this should look like weight gain, not muscle building."
)


def _scale_word(bf_change: float) -> str:
    if bf_change <= 1.5:
        return "very slightly"
    if bf_change <= 3.5:
        return "slightly"
    if bf_change <= 6:
        return "noticeably"
    return "significantly"


# ── Mode-specific prompt builders ──────────────────────────────────────────

def _cut_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    delta = current_bf - stage.bf_pct
    sw = _scale_word(delta)
    is_male = gender == "male"

    if is_male:
        if stage.bf_pct > 22:
            ab_desc = "The midsection should be slightly less soft but still without visible abs."
        elif stage.bf_pct > 18:
            ab_desc = "The midsection should be flatter with a faint upper-ab outline."
        elif stage.bf_pct > 14:
            ab_desc = "Upper abdominal muscles should be visible with moderate definition."
        elif stage.bf_pct > 10:
            ab_desc = "Abs should be clearly visible with moderate-to-deep separation."
        else:
            ab_desc = "Full six-pack should be visible with deep cuts and striations."
    else:
        if stage.bf_pct > 28:
            ab_desc = "The midsection should be slightly less soft, still naturally rounded."
        elif stage.bf_pct > 23:
            ab_desc = "The midsection should be flatter and smoother."
        elif stage.bf_pct > 18:
            ab_desc = "A flat, lightly toned midsection with subtle definition."
        else:
            ab_desc = "A toned, defined midsection with visible muscle outline."

    body_parts = [
        f"Reduce subcutaneous fat {sw}.",
        f"The waist should appear {sw} narrower." if delta > 1 else "",
        ab_desc,
    ]
    if delta > 2:
        body_parts.append(f"The face should appear {sw} leaner with a more defined jawline.")
    if delta > 3:
        body_parts.append(
            "Arms and legs remain the same size but with slightly more "
            "visible veins and definition."
        )

    body_desc = " ".join(p for p in body_parts if p)

    return (
        f"Edit this photo to show the same person at approximately "
        f"{stage.bf_pct:.0f}% body fat. "
        f"{body_desc} "
        f"{_NO_MUSCLE_GROWTH} "
        f"{_IDENTITY_FOOTER}"
    )


def _mass_gain_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    delta = stage.bf_pct - current_bf
    sw = _scale_word(delta)

    parts = [
        f"Edit this photo to show the same person at approximately "
        f"{stage.bf_pct:.0f}% body fat, having gained weight.",
    ]

    if delta > 1.5:
        parts.append(
            f"The face should appear {sw} fuller and rounder "
            f"with a less defined jawline."
        )

    parts.append(
        f"The midsection should have {sw} more subcutaneous fat — "
        f"reduce any visible ab definition and add soft belly roundness."
    )
    parts.append(f"The waist should appear {sw} wider.")

    if delta > 2:
        parts.append(
            f"Arms and legs should appear {sw} thicker with a smoother, "
            f"softer look and reduced vein visibility."
        )
        parts.append(
            f"The chest and torso should look {sw} thicker but without "
            f"increased muscular definition."
        )

    parts.append(_NO_ADDED_DEFINITION)
    parts.append(_IDENTITY_FOOTER)

    return " ".join(parts)


def _lean_bulk_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    bf_delta = abs(stage.bf_pct - current_bf)
    sw = _scale_word(bf_delta)

    parts = [
        f"Edit this photo to show the same person at approximately "
        f"{stage.bf_pct:.0f}% body fat with slightly more muscle mass.",
        "The shoulders should appear marginally broader and rounder.",
        "The chest should appear very slightly thicker.",
        "The arms should appear very slightly bigger.",
    ]

    if bf_delta > 1:
        parts.append(
            f"The midsection should be {sw} less defined as a thin layer "
            f"of additional subcutaneous fat covers the abs."
        )
        parts.append("The face may appear very slightly fuller.")

    parts.append(
        "The overall look should be of someone who has slowly gained "
        "a small amount of quality weight — slightly bigger but not "
        "dramatically different."
    )
    parts.append(_IDENTITY_FOOTER)

    return " ".join(parts)


def _recomp_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    is_losing = stage.bf_pct < current_bf
    delta = abs(stage.bf_pct - current_bf)
    sw = _scale_word(max(delta, 1.0))

    parts = [
        f"Edit this photo to show the same person at approximately "
        f"{stage.bf_pct:.0f}% body fat with very subtly improved "
        f"muscle definition.",
    ]

    if is_losing and delta > 1:
        parts.append(
            f"Reduce subcutaneous fat {sw} — the midsection should be "
            f"very slightly tighter and muscle outlines marginally clearer."
        )
    else:
        parts.append(
            "Muscle outlines should be very marginally more visible "
            "without any change in body size."
        )

    parts.append(
        "Do not change muscle size — only very subtly improve definition."
    )
    parts.append(_IDENTITY_FOOTER)

    return " ".join(parts)


# ── Public API ──────────────────────────────────────────────────────────────

_RENDERERS = {
    TransformationMode.CUT: _cut_prompt,
    TransformationMode.MASS_GAIN: _mass_gain_prompt,
    TransformationMode.LEAN_BULK: _lean_bulk_prompt,
    TransformationMode.RECOMP: _recomp_prompt,
}


def render_stage_prompt(
    stage: TransformationStage,
    mode: TransformationMode,
    gender: str,
    current_bf: float,
    muscle_gains: MuscleGainSpec,
) -> str:
    """Return a FLUX Kontext Pro edit prompt for *stage*.

    Stage 0 (the original photo) returns an empty string.
    """
    if stage.stage_number == 0:
        return ""
    renderer = _RENDERERS.get(mode, _cut_prompt)
    return renderer(stage, current_bf, gender)
