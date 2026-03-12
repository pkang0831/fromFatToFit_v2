"""Prompt renderer for FLUX Kontext Pro body-composition editing.

Pipeline rules (enforced in every prompt):
  1. Every stage is edited from the ORIGINAL photo — never chain outputs.
  2. Big BF% jumps must be split into ≤3 pp steps (15.5→13→11→9→7→6).
  3. Prompts describe RELATIVE changes from the original, not absolute targets.
     Never tell the model "show this person at X% body fat" — it will
     regenerate the person instead of editing them.
  4. Banned identity-swap terms are validated and rejected.
  5. Small edits (≤3 pp) use torso-only focus to keep identity stable.
"""

from __future__ import annotations

from .transformation_types import (
    TransformationMode,
    TransformationStage,
    MuscleGainSpec,
)

BANNED_TERMS: tuple[str, ...] = (
    "fitness model",
    "8% body fat",
    "shredded",
    "very narrow waist",
    "deep muscle separation",
    "bodybuilder physique",
    "competition ready",
    "stage ready",
    "ripped",
    "extremely muscular",
)

MAX_BF_STEP = 3.0


def _validate_prompt(prompt: str) -> str:
    lower = prompt.lower()
    for term in BANNED_TERMS:
        if term.lower() in lower:
            raise ValueError(
                f"Prompt contains banned term '{term}' — causes identity swap."
            )
    return prompt


def compute_gradual_steps(current_bf: float, target_bf: float) -> list[float]:
    """Return BF% targets in ≤MAX_BF_STEP increments, always from original.

    Example: compute_gradual_steps(15.5, 6.0) → [13.0, 11.0, 9.0, 7.0, 6.0]
    """
    if abs(current_bf - target_bf) <= MAX_BF_STEP:
        return [round(target_bf, 1)]

    going_down = target_bf < current_bf
    steps: list[float] = []
    cursor = current_bf

    while True:
        if going_down:
            nxt = cursor - MAX_BF_STEP
            if nxt <= target_bf:
                steps.append(round(target_bf, 1))
                break
            steps.append(round(nxt, 1))
            cursor = nxt
        else:
            nxt = cursor + MAX_BF_STEP
            if nxt >= target_bf:
                steps.append(round(target_bf, 1))
                break
            steps.append(round(nxt, 1))
            cursor = nxt

    return steps


# ── Identity & guardrails ────────────────────────────────────────────────────

_IDENTITY_LOCK = (
    "Same person, same face, same skin tone, same hair, same pose, "
    "same clothing, same background, same lighting, same camera angle. "
    "Realistic photograph."
)

_CUT_GUARDRAILS = (
    "No added muscle. No skin tone, contrast, or lighting changes."
)

_MASS_GAIN_GUARDRAILS = (
    "No added muscle or definition — weight gain only. "
    "No skin tone, contrast, or lighting changes."
)

_LEAN_BULK_GUARDRAILS = (
    "Keep realistic proportions. "
    "No skin tone, contrast, or lighting changes."
)

_RECOMP_GUARDRAILS = (
    "Keep subtle and realistic. "
    "No skin tone, contrast, or lighting changes."
)


def _compose(parts: list[str]) -> str:
    prompt = " ".join(p for p in parts if p)
    return _validate_prompt(prompt)


# ── CUT ──────────────────────────────────────────────────────────────────────

def _cut_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    delta = current_bf - stage.bf_pct
    is_male = gender == "male"
    torso_only = delta <= 3.0

    # Positive framing only — describe desired state, never name problem areas.
    # Saying "reduce belly" makes Kontext emphasise the belly instead.

    if torso_only:
        parts = [
            "Edit this photo. Make the torso slightly leaner.",
            "Only edit the torso area. "
            "Do not change the face, arms, legs, or any other body part.",
        ]
    else:
        parts = [
            "Edit this photo. Make the body slightly leaner.",
        ]

    # ── Midsection — positive target description only ──
    if delta <= 2.0:
        parts.append(
            "The midsection should be just a little flatter and tighter than the original."
        )
    elif delta <= 3.5:
        parts.append(
            "The midsection should be noticeably flatter and tighter. "
            "The waist should be slightly narrower."
        )
    elif delta <= 5.5:
        parts.append(
            "The midsection should be clearly flatter and the waist narrower. "
            "A faint midline may be visible on the abdomen."
        )
    elif delta <= 7.5:
        if is_male:
            parts.append(
                "The midsection should be flat with the waist visibly narrower. "
                "Upper-ab outlines may be faintly visible. "
                "The sides of the torso should be tighter."
            )
        else:
            parts.append(
                "The midsection should be flat and toned with the waist visibly narrower. "
                "The sides of the torso should be tighter."
            )
    else:
        if is_male:
            parts.append(
                "The midsection should be flat with visible ab outlines. "
                "The waist should be tight. "
                "Keep the physique natural and believable."
            )
        else:
            parts.append(
                "The midsection should be flat and toned. "
                "The waist should be tight and defined. "
                "Keep the physique natural and believable."
            )

    # ── Face — only for larger deltas, never torso-only ──
    if not torso_only and delta > 4.0:
        parts.append("The jawline may appear very slightly leaner.")

    # ── Arms/legs — only for big deltas ──
    if not torso_only and delta > 6.0:
        parts.append(
            "Arms and legs stay the same size but may show "
            "slightly more definition."
        )

    parts.append(_CUT_GUARDRAILS)
    parts.append(_IDENTITY_LOCK)
    return _compose(parts)


# ── MASS GAIN ────────────────────────────────────────────────────────────────

def _mass_gain_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    delta = stage.bf_pct - current_bf

    parts = [
        "Edit this photo to show the same person with slightly more body fat.",
    ]

    if delta <= 2.0:
        parts.append(
            "Very slightly add soft tissue to the lower abdomen and flanks. "
            "The belly should look just a little softer and fuller."
        )
    elif delta <= 4.0:
        parts.append(
            "Add softness and fullness to the midsection. "
            "The belly should be noticeably rounder. "
            "Reduce any visible ab definition."
        )
    else:
        parts.append(
            "Add significant softness to the midsection, flanks, and waist. "
            "The belly should be clearly fuller and rounder. "
            "Hide any ab definition under a soft layer."
        )

    if delta > 1.5:
        if delta <= 3.5:
            parts.append("The waist should appear slightly wider.")
        else:
            parts.append("The waist should appear noticeably wider.")

    if delta > 3.0:
        parts.append("The face may appear slightly fuller.")

    if delta > 4.0:
        parts.append(
            "Arms and legs should appear slightly thicker with a smoother, "
            "softer look."
        )

    parts.append(_MASS_GAIN_GUARDRAILS)
    parts.append(_IDENTITY_LOCK)
    return _compose(parts)


# ── LEAN BULK ────────────────────────────────────────────────────────────────

def _lean_bulk_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    delta = abs(stage.bf_pct - current_bf)

    parts = [
        "Edit this photo to show the same person slightly bigger with a bit more muscle.",
        "The shoulders should appear marginally broader and rounder.",
        "The chest should appear very slightly thicker.",
        "The arms should appear very slightly bigger.",
    ]

    if delta > 1:
        parts.append(
            "The midsection may be slightly less defined as a thin layer "
            "of additional soft tissue covers the abs."
        )

    parts.append(
        "The overall change should be very subtle — slightly bigger "
        "but not dramatically different."
    )
    parts.append(_LEAN_BULK_GUARDRAILS)
    parts.append(_IDENTITY_LOCK)
    return _compose(parts)


# ── RECOMP ───────────────────────────────────────────────────────────────────

def _recomp_prompt(
    stage: TransformationStage, current_bf: float, gender: str,
) -> str:
    is_losing = stage.bf_pct < current_bf
    delta = abs(stage.bf_pct - current_bf)

    parts = [
        "Edit this photo to show the same person with very subtly improved "
        "muscle definition and very slightly less body fat.",
    ]

    if is_losing and delta > 1:
        parts.append(
            "The midsection should be very slightly tighter "
            "and muscle outlines marginally clearer."
        )
    else:
        parts.append(
            "Muscle outlines should be very marginally more visible "
            "without any change in body size."
        )

    parts.append(
        "Do not change muscle size — only very subtly improve definition."
    )
    parts.append(_RECOMP_GUARDRAILS)
    parts.append(_IDENTITY_LOCK)
    return _compose(parts)


# ── Public API ───────────────────────────────────────────────────────────────

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
    Every prompt is designed to be applied to the ORIGINAL image,
    not a previously generated output.
    """
    if stage.stage_number == 0:
        return ""
    renderer = _RENDERERS.get(mode, _cut_prompt)
    return renderer(stage, current_bf, gender)
