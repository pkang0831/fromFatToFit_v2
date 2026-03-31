"""
Prompt templates for the two-pass CPU inpainting refinement.

PASS 1 — Seam repair:
  Artifact-only repair.  Preserve current silhouette exactly.

PASS 2 — Torso texture refinement:
  Geometry is fully owned by warp.  Pass 2 only refines skin texture
  in the upper-ab / oblique zone.  It must NOT undo the slimmer
  silhouette created by warp.
"""

# ── Pass 1: seam repair ──────────────────────────────────────────────────────

SEAM_PROMPT = (
    "Same person, same photo. "
    "Repair seam lines and interpolation artifacts on torso skin. "
    "Preserve current silhouette, skin tone, lighting exactly."
)

SEAM_NEGATIVE = (
    "wider waist, protruding belly, rounded abdomen, larger chest, "
    "broader shoulders, larger arms, changed navel, fake abs, "
    "harsh shadows, darker skin, blurry, cartoon, painting"
)


# ── Pass 2: torso texture refinement ─────────────────────────────────────────

def get_torso_prompt(delta_bf_pct: float = 5.0, preset: str = "medium") -> str:
    base = (
        "Same person, same photo. "
        "Preserve current torso silhouette exactly. "
        "Preserve lower-abdomen shape below navel exactly. "
        "Refine only upper-ab and oblique skin texture. "
    )

    if preset == "mild":
        detail = (
            "Very faint linea alba hint and subtle oblique texture. "
            "No visible abs."
        )
    elif preset == "strong":
        detail = (
            "Clear upper-ab structure and oblique texture. "
            "No six-pack or deep cuts."
        )
    else:  # medium
        detail = (
            "Subtle upper-ab definition and mild oblique texture. "
            "Natural skin only."
        )

    return base + detail


def get_torso_negative(delta_bf_pct: float = 5.0, preset: str = "medium") -> str:
    return (
        "protruding belly, bloated stomach, rounded abdomen, soft belly, "
        "wider waist, thicker torso, larger chest, broader shoulders, "
        "larger arms, fake six-pack, deep abdominal grooves, "
        "harsh shadows, darker skin, bodybuilder, changed navel, "
        "blurry, cartoon, painting, distorted"
    )
