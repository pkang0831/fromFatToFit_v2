#!/usr/bin/env python3
"""
Apply P2 SEO retrofit — wave_catchup (25 posts). Uses the same
retrofit logic as apply_p1.py so we can re-use the shared functions.

Batch coverage: verdicts 6-10 supply all 25 primary keywords verbatim.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Import shared logic from apply_p1.py.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from apply_p1 import (  # type: ignore
    MEDIUM_DIR,
    POSTS_TS,
    apply_medium_package,
    posts_ts_insert_seo_fields,
)


SPEC: list[dict] = [
    # --- batch 6 ---
    {
        "package_basename": "wave_catchup_008_exercise-isnt-shrinking-you-the-way-you-expected_medium_manual_publish_package.md",
        "posts_ts_slug": "exercise-isnt-shrinking-you-the-way-you-expected",
        "seo_title": "Why Exercise Alone Isn't Making You Lose Weight",
        "meta_description": "Training hard but the scale isn't moving? Here's why exercise alone doesn't shrink you the way you expected — and what actually drives fat loss.",
        "primary_keyword": "exercise not losing weight",
        "secondary_keywords": [
            "working out but not losing weight",
            "exercise alone weight loss",
            "gym not working scale",
            "why no weight loss despite exercise",
        ],
        "medium_tags": ["Weight Loss", "Exercise", "Fitness", "Dieting", "Nutrition"],
    },
    {
        "package_basename": "wave_catchup_009_the-unglamorous-middle-of-transformation_medium_manual_publish_package.md",
        "posts_ts_slug": "the-unglamorous-middle-of-transformation",
        "seo_title": "The Middle of a Weight Loss Journey Is the Hardest Part",
        "meta_description": "The middle of a weight loss journey isn't glamorous. Here's what the quiet, unphotogenic phase actually looks like — and why most people quit here.",
        "primary_keyword": "middle of weight loss journey",
        "secondary_keywords": [
            "weight loss slow middle",
            "messy middle transformation",
            "unglamorous weight loss",
            "ugly middle of diet",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Journey", "Transformation", "Mindset", "Habits"],
    },
    {
        "package_basename": "wave_catchup_010_is-it-bloat-or-is-it-fat_medium_manual_publish_package.md",
        "posts_ts_slug": "is-it-bloat-or-is-it-fat",
        "seo_title": "Is It Bloat or Is It Fat? How to Tell the Difference",
        "meta_description": "You woke up looking bigger. Is it bloat or fat? Here's the honest test — timing, texture, and what changes overnight vs what doesn't.",
        "primary_keyword": "bloat vs fat",
        "secondary_keywords": [
            "is it bloat or fat gain",
            "how to tell bloat from fat",
            "bloating vs weight gain",
            "stomach bloat or fat",
        ],
        "medium_tags": ["Weight Loss", "Bloating", "Water Weight", "Nutrition", "Body Image"],
    },
    {
        "package_basename": "wave_catchup_011_a-plateau-is-a-data-point-not-a-failure_medium_manual_publish_package.md",
        "posts_ts_slug": "a-plateau-is-a-data-point-not-a-failure",
        "seo_title": "How to Break a Weight Loss Plateau (Without Panicking)",
        "meta_description": "A plateau is a data point, not a verdict. Here's how to read a real weight loss plateau — and what most people do wrong when the scale stalls.",
        "primary_keyword": "weight loss plateau",
        "secondary_keywords": [
            "how to break a plateau",
            "weight loss stopped",
            "plateau not failure",
            "scale not moving anymore",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Plateau", "Dieting", "Plateau", "Habits"],
    },
    {
        "package_basename": "wave_catchup_012_the-body-looks-different-from-behind_medium_manual_publish_package.md",
        "posts_ts_slug": "the-body-looks-different-from-behind",
        "seo_title": "Why Your Body Looks Different From Behind Than the Mirror",
        "meta_description": "The back view is where weight-loss progress often shows first. Here's why your body looks different from behind and how to use that blind spot.",
        "primary_keyword": "body looks different from behind",
        "secondary_keywords": [
            "back view weight loss",
            "body from behind different",
            "progress from back",
            "how body looks to others",
        ],
        "medium_tags": ["Weight Loss", "Body Image", "Progress Photos", "Self Image", "Body Composition"],
    },
    # --- batch 7 ---
    {
        "package_basename": "wave_catchup_013_progress-update-3-past-the-messy-middle_medium_manual_publish_package.md",
        "posts_ts_slug": "progress-update-3-past-the-messy-middle",
        "seo_title": "Weight Loss Progress Update: Past the Messy Middle",
        "meta_description": "A progress update from past the messy middle. Here's what changed, what didn't, and why the quiet phase is where the program actually happens.",
        "primary_keyword": "progress update after weight loss middle",
        "secondary_keywords": [
            "weight loss progress update",
            "weight loss middle phase",
            "past the hardest part of diet",
            "weight loss journey checkpoint",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Journey", "Transformation", "Founder Story", "Long Game"],
    },
    {
        "package_basename": "wave_catchup_014_when-the-workout-becomes-therapy-not-punishment_medium_manual_publish_package.md",
        "posts_ts_slug": "when-the-workout-becomes-therapy-not-punishment",
        "seo_title": "When the Workout Stops Being Punishment and Starts Being Care",
        "meta_description": "The same exercise can be punishment or self-care depending on what you bring to it. Here's when the workout shifts — and why the shift is the point.",
        "primary_keyword": "exercise as self-care not punishment",
        "secondary_keywords": [
            "working out as therapy",
            "exercise for mental health",
            "stop punishing yourself with workouts",
            "workout mindset shift",
        ],
        "medium_tags": ["Weight Loss", "Mental Health", "Exercise", "Mindset", "Self Improvement"],
    },
    {
        "package_basename": "wave_catchup_015_hunger-in-maintenance-is-different-from-hunger-on-a-diet_medium_manual_publish_package.md",
        "posts_ts_slug": "hunger-in-maintenance-is-different-from-hunger-on-a-diet",
        "seo_title": "How Hunger Changes After You Stop Dieting",
        "meta_description": "Maintenance hunger isn't diet hunger. Here's how appetite signals change after weight loss — and why ignoring them the old way breaks the program.",
        "primary_keyword": "hunger after weight loss",
        "secondary_keywords": [
            "maintenance hunger",
            "appetite after dieting",
            "different hunger maintenance",
            "hunger signals after weight loss",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Hunger", "Appetite", "Intuitive Eating"],
    },
    {
        "package_basename": "wave_catchup_016_the-friend-who-never-diets-and-never-gains_medium_manual_publish_package.md",
        "posts_ts_slug": "the-friend-who-never-diets-and-never-gains",
        "seo_title": "Why Some People Never Diet and Never Gain Weight",
        "meta_description": "You know the friend who eats anything and stays lean. Here's what's actually going on — it isn't metabolism, and it isn't luck.",
        "primary_keyword": "friend who never gains weight",
        "secondary_keywords": [
            "people who never gain weight",
            "thin friend never diets",
            "how some stay slim without trying",
            "naturally thin people",
        ],
        "medium_tags": ["Weight Loss", "Body Composition", "Metabolism", "Habits", "Health"],
    },
    {
        "package_basename": "wave_catchup_017_how-do-you-know-when-youve-reached-your-set-point_medium_manual_publish_package.md",
        "posts_ts_slug": "how-do-you-know-when-youve-reached-your-set-point",
        "seo_title": "How to Know When You've Reached Your Body's Set Point",
        "meta_description": "Set point isn't a number — it's a pattern. Here's how to tell when your body has settled into its natural weight and what that actually feels like.",
        "primary_keyword": "reached set point weight",
        "secondary_keywords": [
            "body set point weight",
            "natural weight set point",
            "how to find your set point",
            "weight loss set point theory",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Body Composition", "Metabolism", "Long Game"],
    },
    # --- batch 8 ---
    {
        "package_basename": "wave_catchup_018_the-scale-lies-differently-in-the-morning-than-in-the-evening_medium_manual_publish_package.md",
        "posts_ts_slug": "the-scale-lies-differently-in-the-morning-than-in-the-evening",
        "seo_title": "Morning Weight vs Evening Weight: Why They Differ",
        "meta_description": "The scale can show 2 kg of difference between morning and evening. Here's what's actually changing — and which reading is closer to the truth.",
        "primary_keyword": "morning weight vs evening weight",
        "secondary_keywords": [
            "weigh yourself morning or night",
            "evening weight higher",
            "best time to weigh",
            "daily weight fluctuation time",
        ],
        "medium_tags": ["Weight Loss", "Weight Fluctuation", "Scale Anxiety", "Dieting", "Nutrition"],
    },
    {
        "package_basename": "wave_catchup_019_sleep-debt-ruins-a-week-of-dieting-in-three-nights_medium_manual_publish_package.md",
        "posts_ts_slug": "sleep-debt-ruins-a-week-of-dieting-in-three-nights",
        "seo_title": "How Sleep Debt Ruins a Week of Dieting Fast",
        "meta_description": "Three bad nights can undo a week of clean eating. Here's how sleep debt quietly wrecks a diet — appetite, cravings, energy, and recovery all shift.",
        "primary_keyword": "sleep and weight loss",
        "secondary_keywords": [
            "sleep deprivation weight loss",
            "bad sleep ruins diet",
            "sleep debt hunger",
            "not sleeping enough weight gain",
        ],
        "medium_tags": ["Weight Loss", "Sleep", "Recovery", "Dieting", "Health"],
    },
    {
        "package_basename": "wave_catchup_020_the-quiet-role-vegetables-play-in-staying-full_medium_manual_publish_package.md",
        "posts_ts_slug": "the-quiet-role-vegetables-play-in-staying-full",
        "seo_title": "Why Vegetables Keep You Full on a Weight Loss Diet",
        "meta_description": "Vegetables do a quiet, critical job in a diet — volume, fiber, water, and satiety. Here's how they keep hunger low without anyone making it a rule.",
        "primary_keyword": "vegetables for weight loss",
        "secondary_keywords": [
            "vegetables make you full",
            "high volume low calorie food",
            "fiber satiety weight loss",
            "eating more vegetables dieting",
        ],
        "medium_tags": ["Weight Loss", "Nutrition", "Dieting", "Intuitive Eating", "Hunger"],
    },
    {
        "package_basename": "wave_catchup_021_how-do-i-stop-a-binge-from-becoming-a-binge-week_medium_manual_publish_package.md",
        "posts_ts_slug": "how-do-i-stop-a-binge-from-becoming-a-binge-week",
        "seo_title": "How to Stop a Binge From Becoming a Binge Week",
        "meta_description": "One binge is a meal. A binge week is a pattern. Here's the 48-hour move that stops the spiral — and why punishment makes it worse.",
        "primary_keyword": "stop binge from becoming binge week",
        "secondary_keywords": [
            "how to recover from a binge",
            "binge to binge week",
            "stop binge cycle",
            "one binge doesn't ruin diet",
        ],
        "medium_tags": ["Weight Loss", "Binge Eating", "Emotional Eating", "Dieting", "Food Psychology"],
    },
    {
        "package_basename": "wave_catchup_022_you-look-different-to-other-people-before-yourself_medium_manual_publish_package.md",
        "posts_ts_slug": "you-look-different-to-other-people-before-yourself",
        "seo_title": "Why Other People Notice Your Weight Loss Before You Do",
        "meta_description": "Daily viewing hides change from you — but not from others. Here's why other people see your weight loss before you do, and how to catch up.",
        "primary_keyword": "other people notice weight loss before you",
        "secondary_keywords": [
            "people notice I lost weight",
            "can't see own weight loss",
            "others see weight loss first",
            "weight loss blind spot",
        ],
        "medium_tags": ["Weight Loss", "Body Image", "Self Image", "Progress Photos", "Transformation"],
    },
    # --- batch 9 ---
    {
        "package_basename": "wave_catchup_023_the-first-week-of-any-diet-is-the-most-misleading-one_medium_manual_publish_package.md",
        "posts_ts_slug": "the-first-week-of-any-diet-is-the-most-misleading-one",
        "seo_title": "Why the First Week of a Diet Is the Most Misleading",
        "meta_description": "Early scale drops feel like fat loss. They're mostly water. Here's what the first week of any diet actually teaches — and where the real work starts.",
        "primary_keyword": "first week of diet weight loss",
        "secondary_keywords": [
            "lost weight first week diet",
            "week one weight loss water",
            "first week diet misleading",
            "initial weight loss water",
        ],
        "medium_tags": ["Weight Loss", "Water Weight", "Dieting", "Rapid Weight Loss", "Mindset"],
    },
    {
        "package_basename": "wave_catchup_024_losing-weight-is-not-the-same-as-getting-leaner_medium_manual_publish_package.md",
        "posts_ts_slug": "losing-weight-is-not-the-same-as-getting-leaner",
        "seo_title": "Losing Weight vs Getting Leaner: The Real Difference",
        "meta_description": "You can lose weight without getting leaner. Here's why body composition matters more than the scale — and how to tell which one you're actually doing.",
        "primary_keyword": "weight loss vs getting leaner",
        "secondary_keywords": [
            "losing weight but not leaner",
            "fat loss vs weight loss",
            "body recomposition",
            "leaner but same weight",
        ],
        "medium_tags": ["Weight Loss", "Fat Loss", "Body Composition", "Body Recomposition", "Fitness"],
    },
    {
        "package_basename": "wave_catchup_025_why-people-gain-more-back-than-they-lost_medium_manual_publish_package.md",
        "posts_ts_slug": "why-people-gain-more-back-than-they-lost",
        "seo_title": "Why People Gain Back More Weight Than They Lost",
        "meta_description": "Most people who diet regain more than they lost. Here's what actually drives weight loss rebound — and the system move that prevents it.",
        "primary_keyword": "weight loss rebound gain back more",
        "secondary_keywords": [
            "weight loss rebound",
            "gained back more than I lost",
            "weight regain after diet",
            "yo-yo dieting cycle",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Dieting", "Long Game", "Health"],
    },
    {
        "package_basename": "wave_catchup_026_how-do-i-eat-normally-at-social-events_medium_manual_publish_package.md",
        "posts_ts_slug": "how-do-i-eat-normally-at-social-events",
        "seo_title": "How to Eat Normally at Social Events While Dieting",
        "meta_description": "Dinners, weddings, birthdays — here's how to eat normally at social events on a diet, without blowing the week or becoming the weird one at the table.",
        "primary_keyword": "eating at social events dieting",
        "secondary_keywords": [
            "how to eat at a party on diet",
            "social eating weight loss",
            "eating out while dieting",
            "diet-friendly social dinners",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Social Eating", "Habits", "Nutrition"],
    },
    {
        "package_basename": "wave_catchup_027_the-kind-of-person-who-stays-at-their-goal-weight_medium_manual_publish_package.md",
        "posts_ts_slug": "the-kind-of-person-who-stays-at-their-goal-weight",
        "seo_title": "How to Keep the Weight Off Long Term: What Actually Works",
        "meta_description": "Most people regain. Some don't. Here's the honest difference between people who hit a goal weight and stay, and people who only visit it once.",
        "primary_keyword": "keeping weight off long term",
        "secondary_keywords": [
            "how to maintain weight loss",
            "stay at goal weight",
            "long term weight maintenance",
            "keep weight off after diet",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Long Game", "Habits", "Lifestyle Change"],
    },
    # --- batch 10 ---
    {
        "package_basename": "wave_catchup_028_why-you-stop-losing-weight-around-month-three_medium_manual_publish_package.md",
        "posts_ts_slug": "why-you-stop-losing-weight-around-month-three",
        "seo_title": "Why Weight Loss Slows Down Around Month Three",
        "meta_description": "Around month three, most diets slow to a crawl. Here's why — adaptation, fatigue, creep — and how to push through without escalating to punishment mode.",
        "primary_keyword": "weight loss slows month three",
        "secondary_keywords": [
            "stopped losing weight month 3",
            "weight loss slowed down after 3 months",
            "diet fatigue month three",
            "three month weight loss plateau",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Plateau", "Dieting", "Metabolism", "Long Game"],
    },
    {
        "package_basename": "wave_catchup_029_am-i-actually-hungry-or-am-i-bored_medium_manual_publish_package.md",
        "posts_ts_slug": "am-i-actually-hungry-or-am-i-bored",
        "seo_title": "Am I Actually Hungry or Am I Bored? How to Tell",
        "meta_description": "Real hunger and boredom-hunger feel almost identical in the moment. Here's the honest test — timing, cravings, and what true hunger actually feels like.",
        "primary_keyword": "hungry or bored eating",
        "secondary_keywords": [
            "boredom eating",
            "am I really hungry",
            "emotional hunger vs physical",
            "stop boredom eating",
        ],
        "medium_tags": ["Weight Loss", "Hunger", "Emotional Eating", "Intuitive Eating", "Mindful Eating"],
    },
    {
        "package_basename": "wave_catchup_030_how-much-protein-do-i-actually-need-to-lose-fat_medium_manual_publish_package.md",
        "posts_ts_slug": "how-much-protein-do-i-actually-need-to-lose-fat",
        "seo_title": "How Much Protein Do You Need to Lose Fat?",
        "meta_description": "Protein targets for fat loss aren't the same as muscle-building targets. Here's the honest number — and the timing trick that makes it work.",
        "primary_keyword": "how much protein for fat loss",
        "secondary_keywords": [
            "protein for weight loss",
            "protein target fat loss",
            "grams of protein to lose fat",
            "high protein diet cutting",
        ],
        "medium_tags": ["Weight Loss", "Nutrition", "Protein", "Fat Loss", "Macros"],
    },
    {
        "package_basename": "wave_catchup_031_why-your-workouts-feel-harder-when-youre-dieting_medium_manual_publish_package.md",
        "posts_ts_slug": "why-your-workouts-feel-harder-when-youre-dieting",
        "seo_title": "Why Your Workouts Feel Harder When You're Dieting",
        "meta_description": "Training feels heavier on a cut. That's expected, not a signal to escalate. Here's what's actually happening under the hood — and how to adjust.",
        "primary_keyword": "workouts feel harder on diet",
        "secondary_keywords": [
            "harder to train on diet",
            "lifting weaker on cut",
            "energy low dieting workout",
            "training in a deficit",
        ],
        "medium_tags": ["Weight Loss", "Exercise Science", "Strength Training", "Dieting", "Recovery"],
    },
    {
        "package_basename": "wave_catchup_032_why-your-strength-increases-before-your-shape-changes_medium_manual_publish_package.md",
        "posts_ts_slug": "why-your-strength-increases-before-your-shape-changes",
        "seo_title": "Why Strength Improves Before Your Body Looks Different",
        "meta_description": "The first gains in strength training are neural, not visual. Here's why strength climbs before shape changes — and what that means for the mirror.",
        "primary_keyword": "strength increases before body changes",
        "secondary_keywords": [
            "strength gains without size",
            "neural adaptation strength",
            "lifting heavier same body",
            "strength vs size gains",
        ],
        "medium_tags": ["Weight Loss", "Strength Training", "Fitness", "Exercise Science", "Body Composition"],
    },
]


def main() -> int:
    medium_stats = {"updated": 0, "already-retrofit": 0, "no-match": 0}
    posts_stats = {"updated": 0, "already-retrofit": 0, "slug-not-found": 0, "skipped-no-slug": 0}

    for row in SPEC:
        path = MEDIUM_DIR / row["package_basename"]
        if not path.exists():
            print(f"[MEDIUM] MISSING: {path}")
            medium_stats["no-match"] += 1
            continue
        status = apply_medium_package(path, row)
        medium_stats[status] += 1
        print(f"[MEDIUM] {status}: {row['package_basename']}")

    posts_text = POSTS_TS.read_text(encoding="utf-8")
    for row in SPEC:
        slug = row.get("posts_ts_slug")
        if not slug:
            posts_stats["skipped-no-slug"] += 1
            continue
        posts_text, status = posts_ts_insert_seo_fields(posts_text, slug, row)
        posts_stats[status] += 1
        print(f"[POSTS] {status}: {slug}")
    POSTS_TS.write_text(posts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Medium packages: {medium_stats}")
    print(f"posts.ts entries: {posts_stats}")

    if medium_stats["no-match"] > 0 or posts_stats["slug-not-found"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
