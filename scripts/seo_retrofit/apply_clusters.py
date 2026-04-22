#!/usr/bin/env python3
"""
Add topical `cluster` field to each posts.ts entry. Clusters organize
64 posts into 8 pillar groups for topical authority / internal linking.

Cluster slugs (snake-case; match the pillar page routes):
- scale
- mirror
- appetite
- binge
- maintenance
- plateau
- exercise
- founder-story     (progress updates + founder-angle + transformations)
- food-structure    (meal prep, protein, vegetables, social events)
- body-composition  (body recomp / composition angle)
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"


CLUSTER_ASSIGNMENTS: dict[str, str] = {
    # ---------- Scale / weighing ----------
    "one-emotional-weigh-in-can-wreck-a-good-week": "scale",
    "why-it-feels-like-you-gain-weight-even-when-you-barely-eat": "scale",
    "why-losing-5kg-in-a-week-usually-means-water-not-fat": "scale",
    "the-scale-can-say-normal-and-still-tell-you-nothing-useful": "scale",
    "dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight": "scale",
    "the-same-number-on-the-scale-feels-different-at-30-than-at-20": "scale",
    "weighing-yourself-every-day-can-be-a-trap-not-a-discipline": "scale",
    "why-cutting-sodium-too-hard-can-backfire": "scale",
    "the-scale-lies-differently-in-the-morning-than-in-the-evening": "scale",
    # ---------- Mirror / body image ----------
    "why-the-mirror-can-make-real-progress-feel-fake": "mirror",
    "progress-photos-can-lie-as-much-as-the-mirror-does": "mirror",
    "clothes-tell-you-the-truth-the-mirror-cannot": "mirror",
    "how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud": "mirror",
    "you-look-different-to-other-people-before-yourself": "mirror",
    "the-body-looks-different-from-behind": "mirror",
    # ---------- Appetite / hunger ----------
    "why-appetite-feels-stronger-the-longer-you-diet": "appetite",
    "you-do-not-need-to-love-hunger-you-need-to-understand-it": "appetite",
    "is-this-craving-the-food-or-the-deprivation-talking": "appetite",
    "why-does-my-hunger-spike-at-night-when-i-was-fine-all-day": "appetite",
    "the-week-my-appetite-came-back-during-maintenance": "appetite",
    "your-appetite-scales-with-training-volume-not-with-weight": "appetite",
    "hunger-in-maintenance-is-different-from-hunger-on-a-diet": "appetite",
    "am-i-actually-hungry-or-am-i-bored": "appetite",
    "the-quiet-role-vegetables-play-in-staying-full": "appetite",
    # ---------- Binge / cheat day ----------
    "read-this-before-you-try-to-fix-your-diet-slip": "binge",
    "cheat-days-do-not-expose-your-character-they-expose-your-system": "binge",
    "youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth": "binge",
    "the-bad-weekend-that-finally-taught-me-something": "binge",
    "when-does-one-bad-meal-actually-become-a-slip": "binge",
    "how-do-i-stop-a-binge-from-becoming-a-binge-week": "binge",
    # ---------- Maintenance / long game ----------
    "the-first-month-of-maintenance-feels-nothing-like-the-diet": "maintenance",
    "the-day-i-realized-the-program-was-just-my-life-now": "maintenance",
    "how-do-you-know-when-youve-reached-your-set-point": "maintenance",
    "why-people-gain-more-back-than-they-lost": "maintenance",
    "the-kind-of-person-who-stays-at-their-goal-weight": "maintenance",
    # ---------- Plateau / consistency ----------
    "the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one": "plateau",
    "what-actually-counts-as-a-weight-loss-plateau": "plateau",
    "the-most-important-reason-you-think-youre-not-losing-weight": "plateau",
    "the-quiet-erosion-of-not-believing-your-progress": "plateau",
    "the-small-wins-between-progress-updates-are-the-real-program": "plateau",
    "the-plateau-that-was-actually-an-honesty-problem": "plateau",
    "a-plateau-is-a-data-point-not-a-failure": "plateau",
    "why-you-stop-losing-weight-around-month-three": "plateau",
    # ---------- Exercise / training ----------
    "if-your-diet-broke-your-sleep-it-is-not-discipline-anymore": "exercise",
    "why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think": "exercise",
    "exercise-isnt-shrinking-you-the-way-you-expected": "exercise",
    "when-the-workout-becomes-therapy-not-punishment": "exercise",
    "why-your-workouts-feel-harder-when-youre-dieting": "exercise",
    "why-your-strength-increases-before-your-shape-changes": "exercise",
    "sleep-debt-ruins-a-week-of-dieting-in-three-nights": "exercise",
    # ---------- Founder story / progress ----------
    "why-i-built-devenira-for-the-weeks-where-you-want-to-quit": "founder-story",
    "progress-update-2-the-body-changed-slower-than-my-head-did": "founder-story",
    "progress-update-4-the-body-finally-stopped-being-the-loud-thing": "founder-story",
    "progress-update-3-past-the-messy-middle": "founder-story",
    "the-unglamorous-middle-of-transformation": "founder-story",
    # ---------- Food structure ----------
    "do-i-actually-have-to-meal-prep-to-lose-weight": "food-structure",
    "how-do-i-eat-normally-at-social-events": "food-structure",
    "how-much-protein-do-i-actually-need-to-lose-fat": "food-structure",
    "how-to-track-body-transformation-without-obsessing-over-the-scale": "food-structure",
    "the-first-week-of-any-diet-is-the-most-misleading-one": "food-structure",
    # ---------- Body composition ----------
    "losing-weight-is-not-the-same-as-getting-leaner": "body-composition",
    "is-it-bloat-or-is-it-fat": "body-composition",
    "the-friend-who-never-diets-and-never-gains": "body-composition",
    "do-people-who-have-been-obese-for-years-lose-weight-more-slowly": "body-composition",
}


def insert_cluster_field(text: str, slug: str, cluster: str) -> tuple[str, str]:
    """Insert `cluster: '...',` after the `keywords: [...]` array in posts.ts entry."""
    slug_escaped = re.escape(slug)
    # Find the entry: from `slug:` up to `heroImage:`; replace within.
    entry_re = re.compile(
        rf"(    slug: '{slug_escaped}',\n(?:.*\n)*?)"  # head up to (exclusive of) heroImage
        r"(    heroImage:)",
        re.MULTILINE,
    )
    m = entry_re.search(text)
    if not m:
        return text, "slug-not-found"

    head, hero_line = m.group(1), m.group(2)

    # Idempotency.
    if "    cluster:" in head:
        return text, "already-set"

    # Ensure there's a keywords: [...] block; if yes, insert after that closing `],`.
    if "    keywords: [" not in head:
        # No keywords block — just insert before heroImage.
        insertion = f"    cluster: '{cluster}',\n"
        new_head = head + insertion
        return text[: m.start()] + new_head + hero_line + text[m.end() :], "updated-no-keywords"

    # Insert AFTER the closing `],` of the keywords array.
    keywords_end_re = re.compile(r"    keywords: \[(?:[^\]]*)\],\n", re.DOTALL)
    km = keywords_end_re.search(head)
    if not km:
        return text, "keywords-malformed"

    insertion = f"    cluster: '{cluster}',\n"
    new_head = head[: km.end()] + insertion + head[km.end() :]
    return text[: m.start()] + new_head + hero_line + text[m.end() :], "updated"


def main() -> int:
    text = POSTS_TS.read_text(encoding="utf-8")
    stats = {"updated": 0, "updated-no-keywords": 0, "already-set": 0, "slug-not-found": 0, "keywords-malformed": 0}
    unassigned_slugs: list[str] = []

    # Collect all slugs from posts.ts to catch any that we missed in CLUSTER_ASSIGNMENTS.
    all_slugs = re.findall(r"    slug: '([^']+)',", text)

    for slug in all_slugs:
        cluster = CLUSTER_ASSIGNMENTS.get(slug)
        if cluster is None:
            unassigned_slugs.append(slug)
            continue
        text, status = insert_cluster_field(text, slug, cluster)
        stats[status] += 1
        print(f"[{status}] {slug} -> {cluster}")

    POSTS_TS.write_text(text, encoding="utf-8")

    print("\n=== Summary ===")
    print(stats)
    if unassigned_slugs:
        print(f"\nUnassigned slugs ({len(unassigned_slugs)}):")
        for s in unassigned_slugs:
            print(f"  - {s}")
    return 0 if not unassigned_slugs else 1


if __name__ == "__main__":
    sys.exit(main())
