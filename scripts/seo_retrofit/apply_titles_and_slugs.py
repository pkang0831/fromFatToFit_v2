#!/usr/bin/env python3
"""
Apply final SEO titles + new SEO-optimized slugs for all 64 posts based
on the 2026-04-21 keyword research.

Work performed per post:

1. If `new_seo_title` differs from the current `## SEO Title` in the
   Medium package AND the current `seoTitle` in posts.ts, update both.
2. If `new_slug` differs from the current posts.ts slug:
   - rename the posts.ts slug field to `new_slug`
   - register an old→new entry in `src/content/blog/redirects.js`
   - update any `## Canonical URL` reference text in the Medium package
3. All changes are idempotent.

Idempotency model: the script computes what the desired final state is
and replaces blocks only if the current state doesn't already match.
Re-running is safe.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
REDIRECTS_JS = ROOT / "frontend/src/content/blog/redirects.js"
SCHEDULE_FILE = ROOT / "marketing/fitness_blogging/blog_strategy/schedule/posts_30_to_71_schedule.md"

# Canonical URL of the owned site used in package files' comments.
SITE_ORIGIN = "https://devenira.com"


# Each entry:
#   package_basename        — Medium package filename (WITHOUT .md suffix)
#   current_slug            — existing slug in posts.ts (must match for mapping)
#   new_slug                — short, keyword-rich slug (≤ 55 chars ideally)
#   new_seo_title           — ≤ 60 chars, primary keyword front-loaded
#
# When new_slug == current_slug, no redirect is created (no rename happened).
#
# Slugs are designed to: front-load primary keyword, drop stopwords that
# waste chars, keep question starters (SEO value), target 30-45 chars.
#
# SEO titles are designed to: match the primary keyword in the first 40
# chars, stay ≤ 60 chars, use informational voice (Why / How / What).

SPEC: list[dict] = [
    # =========== wave_01 ===========
    {
        "package_basename": "wave_01_01_consistency",
        "current_slug": "the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one",
        "new_slug": "how-to-stick-to-a-diet-when-progress-slows",
        "new_seo_title": "How to Stick to a Diet When Progress Slows Down",
    },
    {
        "package_basename": "wave_01_02_founder_story",
        "current_slug": "why-i-built-devenira-for-the-weeks-where-you-want-to-quit",
        "new_slug": "how-i-lost-50-kg-middle-of-diet",
        "new_seo_title": "How I Lost 50 kg: Why the Middle of the Diet Is the Hardest",
    },
    {
        "package_basename": "wave_01_03_mirror",
        "current_slug": "why-the-mirror-can-make-real-progress-feel-fake",
        "new_slug": "why-cant-i-see-weight-loss-in-the-mirror",
        "new_seo_title": "Why Can't I See My Weight Loss in the Mirror?",
    },
    {
        "package_basename": "wave_01_04_weighin",
        "current_slug": "one-emotional-weigh-in-can-wreck-a-good-week",
        "new_slug": "should-i-weigh-myself-every-day-on-a-diet",
        "new_seo_title": "Should I Weigh Myself Every Day on a Diet?",
    },
    {
        "package_basename": "wave_01_05_binge_repair",
        "current_slug": "read-this-before-you-try-to-fix-your-diet-slip",
        "new_slug": "what-to-do-after-a-binge-on-a-diet",
        "new_seo_title": "What to Do After a Binge on a Diet (Before You Spiral)",
    },
    {
        "package_basename": "wave_01_06_cheat_day",
        "current_slug": "cheat-days-do-not-expose-your-character-they-expose-your-system",
        "new_slug": "are-cheat-days-bad-for-weight-loss",
        "new_seo_title": "Are Cheat Days Bad for Weight Loss? Why They Backfire",
    },
    # =========== wave_02 ===========
    {
        "package_basename": "wave_02_01_appetite_louder",
        "current_slug": "why-appetite-feels-stronger-the-longer-you-diet",
        "new_slug": "why-is-my-appetite-stronger-on-a-diet",
        "new_seo_title": "Why Is My Appetite Stronger the Longer I Diet?",
    },
    {
        "package_basename": "wave_02_02_how-to-track-body-transformation-without-obsessing-over-the-scale",
        "current_slug": "how-to-track-body-transformation-without-obsessing-over-the-scale",
        "new_slug": "how-to-track-body-transformation-without-the-scale",
        "new_seo_title": "How to Track Body Transformation Without the Scale",
    },
    {
        "package_basename": "wave_02_03_why-it-feels-like-you-gain-weight-even-when-you-barely-eat",
        "current_slug": "why-it-feels-like-you-gain-weight-even-when-you-barely-eat",
        "new_slug": "why-does-the-scale-go-up-when-i-barely-eat",
        "new_seo_title": "Why Does the Scale Go Up When You're Barely Eating?",
    },
    {
        "package_basename": "wave_02_04_what-actually-counts-as-a-weight-loss-plateau",
        "current_slug": "what-actually-counts-as-a-weight-loss-plateau",
        "new_slug": "what-counts-as-a-weight-loss-plateau",
        "new_seo_title": "What Counts as a Weight Loss Plateau (and What Doesn't)?",
    },
    {
        "package_basename": "wave_02_05_why-losing-5kg-in-a-week-usually-means-water-not-fat",
        "current_slug": "why-losing-5kg-in-a-week-usually-means-water-not-fat",
        "new_slug": "is-losing-5kg-in-a-week-water-weight",
        "new_seo_title": "Is Losing 5 kg in a Week Water Weight?",
    },
    {
        "package_basename": "wave_02_06_the-most-important-reason-you-think-youre-not-losing-weight",
        "current_slug": "the-most-important-reason-you-think-youre-not-losing-weight",
        "new_slug": "why-am-i-not-losing-weight-anymore",
        "new_seo_title": "Why Am I Not Losing Weight Anymore? (It's Not You)",
    },
    {
        "package_basename": "wave_02_07_the-scale-can-say-normal-and-still-tell-you-nothing-useful",
        "current_slug": "the-scale-can-say-normal-and-still-tell-you-nothing-useful",
        "new_slug": "skinny-fat-normal-weight-high-body-fat",
        "new_seo_title": "Skinny Fat: Normal Weight but High Body Fat",
    },
    {
        "package_basename": "wave_02_08_progress-update-2-the-body-changed-slower-than-my-head-did",
        "current_slug": "progress-update-2-the-body-changed-slower-than-my-head-did",
        "new_slug": "progress-update-body-changes-slower-than-mind",
        "new_seo_title": "Weight Loss Progress Update: Body vs Mind",
    },
    {
        "package_basename": "wave_02_09_dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight",
        "current_slug": "dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight",
        "new_slug": "how-to-know-youre-losing-weight-without-the-scale",
        "new_seo_title": "How to Know You're Losing Weight Without the Scale",
    },
    {
        "package_basename": "wave_02_10_you-do-not-need-to-love-hunger-you-need-to-understand-it",
        "current_slug": "you-do-not-need-to-love-hunger-you-need-to-understand-it",
        "new_slug": "how-to-handle-hunger-pangs-on-a-diet",
        "new_seo_title": "How to Handle Hunger Pangs on a Diet (Without Hating It)",
    },
    {
        "package_basename": "wave_02_11_if-your-diet-broke-your-sleep-it-is-not-discipline-anymore",
        "current_slug": "if-your-diet-broke-your-sleep-it-is-not-discipline-anymore",
        "new_slug": "why-cant-i-sleep-on-a-calorie-deficit",
        "new_seo_title": "Why Can't I Sleep on a Calorie Deficit?",
    },
    {
        "package_basename": "wave_02_12_youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth",
        "current_slug": "youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth",
        "new_slug": "does-one-bad-day-ruin-a-diet",
        "new_seo_title": "Does One Bad Day Ruin a Diet? The Honest Answer",
    },
    {
        "package_basename": "wave_02_13_do-people-who-have-been-obese-for-years-lose-weight-more-slowly",
        "current_slug": "do-people-who-have-been-obese-for-years-lose-weight-more-slowly",
        "new_slug": "do-obese-people-lose-weight-slower",
        "new_seo_title": "Do Obese People Lose Weight Slower Than Others?",
    },
    # =========== wave_03 ===========
    {
        "package_basename": "wave_03_01_the-quiet-erosion-of-not-believing-your-progress",
        "current_slug": "the-quiet-erosion-of-not-believing-your-progress",
        "new_slug": "how-to-trust-slow-weight-loss-progress",
        "new_seo_title": "How to Trust Slow Weight Loss Progress",
    },
    {
        "package_basename": "wave_03_02_progress-photos-can-lie-as-much-as-the-mirror-does",
        "current_slug": "progress-photos-can-lie-as-much-as-the-mirror-does",
        "new_slug": "why-progress-photos-dont-show-progress",
        "new_seo_title": "Why Progress Photos Don't Show Progress (and the Fix)",
    },
    {
        "package_basename": "wave_03_03_is-this-craving-the-food-or-the-deprivation-talking",
        "current_slug": "is-this-craving-the-food-or-the-deprivation-talking",
        "new_slug": "why-does-restriction-make-cravings-worse",
        "new_seo_title": "Why Does Restriction Make Cravings Worse?",
    },
    {
        "package_basename": "wave_03_04_the-same-number-on-the-scale-feels-different-at-30-than-at-20",
        "current_slug": "the-same-number-on-the-scale-feels-different-at-30-than-at-20",
        "new_slug": "why-does-the-same-weight-feel-different-as-you-age",
        "new_seo_title": "Why Does the Same Weight Feel Different as You Age?",
    },
    {
        "package_basename": "wave_03_05_the-small-wins-between-progress-updates-are-the-real-program",
        "current_slug": "the-small-wins-between-progress-updates-are-the-real-program",
        "new_slug": "non-scale-victories-weight-loss",
        "new_seo_title": "Non Scale Victories in Weight Loss: The Real Wins",
    },
    {
        "package_basename": "wave_03_06_the-first-month-of-maintenance-feels-nothing-like-the-diet",
        "current_slug": "the-first-month-of-maintenance-feels-nothing-like-the-diet",
        "new_slug": "first-month-of-maintenance-after-weight-loss",
        "new_seo_title": "The First Month of Maintenance After Weight Loss",
    },
    {
        "package_basename": "wave_03_07_why-does-my-hunger-spike-at-night-when-i-was-fine-all-day",
        "current_slug": "why-does-my-hunger-spike-at-night-when-i-was-fine-all-day",
        "new_slug": "why-am-i-hungry-at-night-but-not-during-the-day",
        "new_seo_title": "Why Am I Hungry at Night but Not During the Day?",
    },
    {
        "package_basename": "wave_03_08_the-plateau-that-was-actually-an-honesty-problem",
        "current_slug": "the-plateau-that-was-actually-an-honesty-problem",
        "new_slug": "am-i-really-in-a-plateau-or-tracking-wrong",
        "new_seo_title": "Am I Really in a Plateau, or Am I Tracking Wrong?",
    },
    {
        "package_basename": "wave_03_09_progress-update-4-the-body-finally-stopped-being-the-loud-thing",
        "current_slug": "progress-update-4-the-body-finally-stopped-being-the-loud-thing",
        "new_slug": "life-after-50kg-weight-loss",
        "new_seo_title": "Life After 50 kg Weight Loss: The Quiet Phase",
    },
    {
        "package_basename": "wave_03_10_clothes-tell-you-the-truth-the-mirror-cannot",
        "current_slug": "clothes-tell-you-the-truth-the-mirror-cannot",
        "new_slug": "clothes-fit-better-but-scale-is-the-same",
        "new_seo_title": "Clothes Fit Better but Scale Is the Same: What's Happening",
    },
    {
        "package_basename": "wave_03_11_the-bad-weekend-that-finally-taught-me-something",
        "current_slug": "the-bad-weekend-that-finally-taught-me-something",
        "new_slug": "how-to-get-back-on-track-after-a-bad-weekend",
        "new_seo_title": "How to Get Back on Track After a Bad Diet Weekend",
    },
    {
        "package_basename": "wave_03_12_how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud",
        "current_slug": "how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud",
        "new_slug": "how-to-stop-mirror-checking-on-a-diet",
        "new_seo_title": "How to Stop Mirror Checking on a Diet",
    },
    {
        "package_basename": "wave_03_13_do-i-actually-have-to-meal-prep-to-lose-weight",
        "current_slug": "do-i-actually-have-to-meal-prep-to-lose-weight",
        "new_slug": "do-i-have-to-meal-prep-to-lose-weight",
        "new_seo_title": "Do I Have to Meal Prep to Lose Weight? The Real Answer",
    },
    {
        "package_basename": "wave_03_14_why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think",
        "current_slug": "why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think",
        "new_slug": "why-adding-cardio-to-a-cut-backfires",
        "new_seo_title": "Why Adding Cardio to a Cut Can Backfire",
    },
    {
        "package_basename": "wave_03_15_weighing-yourself-every-day-can-be-a-trap-not-a-discipline",
        "current_slug": "weighing-yourself-every-day-can-be-a-trap-not-a-discipline",
        "new_slug": "daily-weighing-eating-disorder-risk",
        "new_seo_title": "Daily Weighing: When It Becomes an Eating-Disorder Risk",
    },
    {
        "package_basename": "wave_03_16_why-cutting-sodium-too-hard-can-backfire",
        "current_slug": "why-cutting-sodium-too-hard-can-backfire",
        "new_slug": "does-cutting-sodium-cause-water-retention",
        "new_seo_title": "Does Cutting Sodium Cause a Water-Retention Rebound?",
    },
    {
        "package_basename": "wave_03_17_the-week-my-appetite-came-back-during-maintenance",
        "current_slug": "the-week-my-appetite-came-back-during-maintenance",
        "new_slug": "appetite-returns-during-maintenance",
        "new_seo_title": "Why Appetite Returns During Maintenance After Weight Loss",
    },
    {
        "package_basename": "wave_03_18_when-does-one-bad-meal-actually-become-a-slip",
        "current_slug": "when-does-one-bad-meal-actually-become-a-slip",
        "new_slug": "does-one-bad-meal-ruin-a-diet",
        "new_seo_title": "Does One Bad Meal Ruin a Diet? The Honest Answer",
    },
    {
        "package_basename": "wave_03_19_your-appetite-scales-with-training-volume-not-with-weight",
        "current_slug": "your-appetite-scales-with-training-volume-not-with-weight",
        "new_slug": "why-am-i-so-hungry-after-lifting-weights",
        "new_seo_title": "Why Am I So Hungry After Lifting Weights?",
    },
    {
        "package_basename": "wave_03_20_the-day-i-realized-the-program-was-just-my-life-now",
        "current_slug": "the-day-i-realized-the-program-was-just-my-life-now",
        "new_slug": "when-does-a-diet-become-a-lifestyle",
        "new_seo_title": "When Does a Diet Become a Lifestyle?",
    },
    # =========== wave_catchup ===========
    {
        "package_basename": "wave_catchup_008_exercise-isnt-shrinking-you-the-way-you-expected",
        "current_slug": "exercise-isnt-shrinking-you-the-way-you-expected",
        "new_slug": "why-am-i-working-out-but-not-losing-weight",
        "new_seo_title": "Why Am I Working Out but Not Losing Weight?",
    },
    {
        "package_basename": "wave_catchup_009_the-unglamorous-middle-of-transformation",
        "current_slug": "the-unglamorous-middle-of-transformation",
        "new_slug": "why-is-the-middle-of-weight-loss-the-hardest",
        "new_seo_title": "Why Is the Middle of Weight Loss the Hardest?",
    },
    {
        "package_basename": "wave_catchup_010_is-it-bloat-or-is-it-fat",
        "current_slug": "is-it-bloat-or-is-it-fat",
        "new_slug": "is-my-stomach-bloat-or-fat",
        "new_seo_title": "Is My Stomach Bloat or Fat? How to Tell",
    },
    {
        "package_basename": "wave_catchup_011_a-plateau-is-a-data-point-not-a-failure",
        "current_slug": "a-plateau-is-a-data-point-not-a-failure",
        "new_slug": "how-to-break-a-weight-loss-plateau",
        "new_seo_title": "How to Break a Weight Loss Plateau (Without Panicking)",
    },
    {
        "package_basename": "wave_catchup_012_the-body-looks-different-from-behind",
        "current_slug": "the-body-looks-different-from-behind",
        "new_slug": "why-does-my-body-look-different-from-different-angles",
        "new_seo_title": "Why Does My Body Look Different From Different Angles?",
    },
    {
        "package_basename": "wave_catchup_013_progress-update-3-past-the-messy-middle",
        "current_slug": "progress-update-3-past-the-messy-middle",
        "new_slug": "past-the-messy-middle-of-weight-loss",
        "new_seo_title": "Past the Messy Middle of Weight Loss: A Check-In",
    },
    {
        "package_basename": "wave_catchup_014_when-the-workout-becomes-therapy-not-punishment",
        "current_slug": "when-the-workout-becomes-therapy-not-punishment",
        "new_slug": "how-to-stop-using-exercise-as-punishment",
        "new_seo_title": "How to Stop Using Exercise as Punishment",
    },
    {
        "package_basename": "wave_catchup_015_hunger-in-maintenance-is-different-from-hunger-on-a-diet",
        "current_slug": "hunger-in-maintenance-is-different-from-hunger-on-a-diet",
        "new_slug": "is-maintenance-hunger-different-from-diet-hunger",
        "new_seo_title": "Is Maintenance Hunger Different From Diet Hunger?",
    },
    {
        "package_basename": "wave_catchup_016_the-friend-who-never-diets-and-never-gains",
        "current_slug": "the-friend-who-never-diets-and-never-gains",
        "new_slug": "why-do-some-people-never-gain-weight",
        "new_seo_title": "Why Do Some People Never Gain Weight No Matter What They Eat?",
    },
    {
        "package_basename": "wave_catchup_017_how-do-you-know-when-youve-reached-your-set-point",
        "current_slug": "how-do-you-know-when-youve-reached-your-set-point",
        "new_slug": "how-do-you-know-youve-reached-set-point",
        "new_seo_title": "How Do You Know You've Reached Your Set Point Weight?",
    },
    {
        "package_basename": "wave_catchup_018_the-scale-lies-differently-in-the-morning-than-in-the-evening",
        "current_slug": "the-scale-lies-differently-in-the-morning-than-in-the-evening",
        "new_slug": "why-do-i-weigh-more-at-night",
        "new_seo_title": "Why Do I Weigh More at Night Than in the Morning?",
    },
    {
        "package_basename": "wave_catchup_019_sleep-debt-ruins-a-week-of-dieting-in-three-nights",
        "current_slug": "sleep-debt-ruins-a-week-of-dieting-in-three-nights",
        "new_slug": "does-bad-sleep-ruin-weight-loss",
        "new_seo_title": "Does Bad Sleep Ruin Weight Loss? Yes, and Fast",
    },
    {
        "package_basename": "wave_catchup_020_the-quiet-role-vegetables-play-in-staying-full",
        "current_slug": "the-quiet-role-vegetables-play-in-staying-full",
        "new_slug": "do-vegetables-help-you-feel-full-on-a-diet",
        "new_seo_title": "Do Vegetables Help You Feel Full on a Diet?",
    },
    {
        "package_basename": "wave_catchup_021_how-do-i-stop-a-binge-from-becoming-a-binge-week",
        "current_slug": "how-do-i-stop-a-binge-from-becoming-a-binge-week",
        "new_slug": "how-to-stop-a-binge-from-becoming-a-binge-week",
        "new_seo_title": "How to Stop a Binge From Becoming a Binge Week",
    },
    {
        "package_basename": "wave_catchup_022_you-look-different-to-other-people-before-yourself",
        "current_slug": "you-look-different-to-other-people-before-yourself",
        "new_slug": "why-do-others-notice-my-weight-loss-before-me",
        "new_seo_title": "Why Do Others Notice My Weight Loss Before I Do?",
    },
    {
        "package_basename": "wave_catchup_023_the-first-week-of-any-diet-is-the-most-misleading-one",
        "current_slug": "the-first-week-of-any-diet-is-the-most-misleading-one",
        "new_slug": "why-do-you-lose-so-much-weight-first-week",
        "new_seo_title": "Why Do You Lose So Much Weight the First Week of a Diet?",
    },
    {
        "package_basename": "wave_catchup_024_losing-weight-is-not-the-same-as-getting-leaner",
        "current_slug": "losing-weight-is-not-the-same-as-getting-leaner",
        "new_slug": "difference-between-weight-loss-and-fat-loss",
        "new_seo_title": "What's the Difference Between Weight Loss and Fat Loss?",
    },
    {
        "package_basename": "wave_catchup_025_why-people-gain-more-back-than-they-lost",
        "current_slug": "why-people-gain-more-back-than-they-lost",
        "new_slug": "why-do-i-gain-back-more-weight-than-i-lost",
        "new_seo_title": "Why Do I Gain Back More Weight Than I Lost?",
    },
    {
        "package_basename": "wave_catchup_026_how-do-i-eat-normally-at-social-events",
        "current_slug": "how-do-i-eat-normally-at-social-events",
        "new_slug": "how-to-eat-at-social-events-on-a-diet",
        "new_seo_title": "How to Eat at Social Events on a Diet",
    },
    {
        "package_basename": "wave_catchup_027_the-kind-of-person-who-stays-at-their-goal-weight",
        "current_slug": "the-kind-of-person-who-stays-at-their-goal-weight",
        "new_slug": "how-to-stay-at-your-goal-weight-long-term",
        "new_seo_title": "How to Stay at Your Goal Weight Long Term",
    },
    {
        "package_basename": "wave_catchup_028_why-you-stop-losing-weight-around-month-three",
        "current_slug": "why-you-stop-losing-weight-around-month-three",
        "new_slug": "why-did-i-stop-losing-weight-at-3-months",
        "new_seo_title": "Why Did I Stop Losing Weight at 3 Months?",
    },
    {
        "package_basename": "wave_catchup_029_am-i-actually-hungry-or-am-i-bored",
        "current_slug": "am-i-actually-hungry-or-am-i-bored",
        "new_slug": "how-to-tell-if-youre-hungry-or-bored",
        "new_seo_title": "How to Tell If You're Hungry or Bored",
    },
    {
        "package_basename": "wave_catchup_030_how-much-protein-do-i-actually-need-to-lose-fat",
        "current_slug": "how-much-protein-do-i-actually-need-to-lose-fat",
        "new_slug": "how-much-protein-do-i-need-to-lose-fat",
        "new_seo_title": "How Much Protein Do I Need to Lose Fat?",
    },
    {
        "package_basename": "wave_catchup_031_why-your-workouts-feel-harder-when-youre-dieting",
        "current_slug": "why-your-workouts-feel-harder-when-youre-dieting",
        "new_slug": "why-are-my-workouts-harder-on-a-cut",
        "new_seo_title": "Why Are My Workouts Harder on a Cut?",
    },
    {
        "package_basename": "wave_catchup_032_why-your-strength-increases-before-your-shape-changes",
        "current_slug": "why-your-strength-increases-before-your-shape-changes",
        "new_slug": "why-does-strength-increase-before-muscle-size",
        "new_seo_title": "Why Does Strength Increase Before Muscle Size?",
    },
]


def resolve_package_path(basename: str) -> Path | None:
    candidates = [
        MEDIUM_DIR / f"{basename}.md",
        MEDIUM_DIR / f"{basename}_medium_manual_publish_package.md",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def update_medium_seo_title(path: Path, new_title: str) -> str:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(^## SEO Title\n)(?P<val>[^\n]+)(\n)", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return "no-seo-block"
    if m.group("val").strip() == new_title:
        return "no-op"
    new_text = pattern.sub(lambda _: f"## SEO Title\n{new_title}\n", text, count=1)
    path.write_text(new_text, encoding="utf-8")
    return "updated"


def update_posts_ts(text: str, current_slug: str, new_slug: str, new_seo_title: str) -> tuple[str, dict]:
    """Update both slug (if changed) and seoTitle in the posts.ts entry for
    the current_slug. Returns (new_text, changes-log-dict)."""
    changes: dict[str, str] = {"slug": "unchanged", "seo_title": "unchanged"}

    slug_line = f"    slug: '{current_slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        changes["slug"] = "slug-not-found"
        changes["seo_title"] = "slug-not-found"
        return text, changes

    # Find end of this entry (next slug line or end).
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    entry_end = next_slug_idx if next_slug_idx != -1 else len(text)

    entry_text = text[slug_idx:entry_end]
    new_entry_text = entry_text

    # Update slug value (only if changed).
    if new_slug != current_slug:
        new_entry_text = new_entry_text.replace(
            f"    slug: '{current_slug}',",
            f"    slug: '{new_slug}',",
            1,
        )
        changes["slug"] = "updated"

    # Update seoTitle within this entry.
    seo_pattern = re.compile(
        r"    seoTitle: (?P<q>['\"])(?P<val>.+?)(?P=q),",
    )
    sm = seo_pattern.search(new_entry_text)
    if sm:
        current_title = sm.group("val")
        # Unescape any JS escape sequences for comparison.
        current_title_unescaped = current_title.replace("\\'", "'")
        if current_title_unescaped != new_seo_title:
            # Render new title as JS string literal preserving apostrophes.
            if "'" in new_seo_title and '"' not in new_seo_title:
                new_literal = f'"{new_seo_title}"'
            elif "'" in new_seo_title:
                new_literal = "'" + new_seo_title.replace("'", "\\'") + "'"
            else:
                new_literal = f"'{new_seo_title}'"
            new_entry_text = seo_pattern.sub(
                f"    seoTitle: {new_literal},", new_entry_text, count=1
            )
            changes["seo_title"] = "updated"

    new_text = text[:slug_idx] + new_entry_text + text[entry_end:]
    return new_text, changes


def append_redirect(current_slug: str, new_slug: str) -> str:
    if current_slug == new_slug:
        return "no-op"
    text = REDIRECTS_JS.read_text(encoding="utf-8")
    # Check for idempotency — redirect already present?
    existing = re.search(
        rf"{{\s*from:\s*'{re.escape(current_slug)}',\s*to:\s*'{re.escape(new_slug)}',?\s*}}",
        text,
    )
    if existing:
        return "already-present"

    insertion_marker = "const blogSlugRedirects = [\n"
    idx = text.find(insertion_marker)
    if idx == -1:
        return "marker-not-found"

    insertion = f"  {{ from: '{current_slug}', to: '{new_slug}' }},\n"
    insert_at = idx + len(insertion_marker)
    new_text = text[:insert_at] + insertion + text[insert_at:]
    REDIRECTS_JS.write_text(new_text, encoding="utf-8")
    return "added"


def update_schedule_slug_references(current_slug: str, new_slug: str) -> str:
    if current_slug == new_slug:
        return "no-op"
    if not SCHEDULE_FILE.exists():
        return "schedule-missing"
    text = SCHEDULE_FILE.read_text(encoding="utf-8")
    if current_slug not in text:
        return "no-reference"
    new_text = text.replace(f" {current_slug} ", f" {new_slug} ").replace(
        f" {current_slug}\n", f" {new_slug}\n"
    ).replace(f"| {current_slug} |", f"| {new_slug} |")
    if new_text == text:
        return "no-change"
    SCHEDULE_FILE.write_text(new_text, encoding="utf-8")
    return "updated"


def update_medium_canonical_ref(path: Path, current_slug: str, new_slug: str) -> str:
    """The package file has the old slug quoted in comments/backticks even
    after the canonical flip. Update those references for consistency."""
    if current_slug == new_slug:
        return "no-op"
    text = path.read_text(encoding="utf-8")
    old_url = f"{SITE_ORIGIN}/blog/{current_slug}"
    new_url = f"{SITE_ORIGIN}/blog/{new_slug}"
    if old_url not in text:
        return "no-reference"
    new_text = text.replace(old_url, new_url)
    path.write_text(new_text, encoding="utf-8")
    return "updated"


def main() -> int:
    posts_ts_text = POSTS_TS.read_text(encoding="utf-8")

    medium_title_stats = {"updated": 0, "no-op": 0, "no-seo-block": 0, "missing-file": 0}
    medium_canonical_stats = {"updated": 0, "no-op": 0, "no-reference": 0, "missing-file": 0}
    posts_ts_slug_stats = {"updated": 0, "unchanged": 0, "slug-not-found": 0}
    posts_ts_title_stats = {"updated": 0, "unchanged": 0, "slug-not-found": 0}
    redirect_stats = {"added": 0, "no-op": 0, "already-present": 0, "marker-not-found": 0}
    schedule_stats = {"updated": 0, "no-op": 0, "no-reference": 0, "no-change": 0, "schedule-missing": 0}

    # Build set of unique new_slugs to detect collisions.
    new_slugs: list[str] = [s["new_slug"] for s in SPEC]
    duplicates = {s for s in new_slugs if new_slugs.count(s) > 1}
    if duplicates:
        print("ERROR: new_slug collisions detected:", duplicates)
        return 2

    for spec in SPEC:
        pkg_path = resolve_package_path(spec["package_basename"])
        if pkg_path is None:
            print(f"[MISS] {spec['package_basename']} — package file not found")
            medium_title_stats["missing-file"] += 1
            medium_canonical_stats["missing-file"] += 1
            continue

        # 1) Medium SEO title
        mt = update_medium_seo_title(pkg_path, spec["new_seo_title"])
        medium_title_stats[mt] += 1

        # 2) Medium canonical ref (cosmetic but consistent)
        mc = update_medium_canonical_ref(pkg_path, spec["current_slug"], spec["new_slug"])
        medium_canonical_stats[mc] += 1

        # 3) posts.ts (slug + seoTitle)
        posts_ts_text, changes = update_posts_ts(
            posts_ts_text,
            spec["current_slug"],
            spec["new_slug"],
            spec["new_seo_title"],
        )
        if changes["slug"] == "slug-not-found":
            posts_ts_slug_stats["slug-not-found"] += 1
            posts_ts_title_stats["slug-not-found"] += 1
        else:
            posts_ts_slug_stats[changes["slug"]] += 1
            posts_ts_title_stats[changes["seo_title"]] += 1

        # 4) 301 redirect entry
        r = append_redirect(spec["current_slug"], spec["new_slug"])
        redirect_stats[r] = redirect_stats.get(r, 0) + 1

        # 5) schedule doc slug reference
        s = update_schedule_slug_references(spec["current_slug"], spec["new_slug"])
        schedule_stats[s] = schedule_stats.get(s, 0) + 1

        slug_note = "=" if spec["current_slug"] == spec["new_slug"] else "→ NEW"
        print(
            f"[OK] {spec['package_basename']}  "
            f"title:{mt:<8}  slug:{changes['slug']:<8} {slug_note}  "
            f"redirect:{r:<14}"
        )

    POSTS_TS.write_text(posts_ts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Medium SEO titles:       {medium_title_stats}")
    print(f"Medium canonical refs:   {medium_canonical_stats}")
    print(f"posts.ts slug renames:   {posts_ts_slug_stats}")
    print(f"posts.ts seoTitle:       {posts_ts_title_stats}")
    print(f"301 redirect entries:    {redirect_stats}")
    print(f"Schedule doc updates:    {schedule_stats}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
