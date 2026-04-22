#!/usr/bin/env python3
"""
Apply P1 SEO retrofit (wave_02 + wave_03, 33 posts) to:

- Medium publish packages (marketing/fitness_blogging/blog_strategy/medium_launch/*.md)
- Site blog posts (frontend/src/content/blog/posts.ts)

Driven by the spec dictionary below. Idempotent: re-running against an already-retrofit
file is a no-op because the replacement targets look for the legacy format only.

Usage: python3 scripts/seo_retrofit/apply_p1.py
"""

from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"


# One row per post. `package_basename` is the filename inside MEDIUM_DIR.
# `posts_ts_slug` is the slug used in posts.ts (None if not ported).
SPEC: list[dict] = [
    # ---------- Wave 02 ----------
    {
        "package_basename": "wave_02_01_appetite_louder_medium_manual_publish_package.md",
        "posts_ts_slug": "why-appetite-feels-stronger-the-longer-you-diet",
        "seo_title": "Why Appetite Gets Stronger the Longer You Diet",
        "meta_description": "Dieting doesn't always make hunger go away. Here's why appetite actually gets louder the longer you diet — and how restriction makes it worse.",
        "primary_keyword": "why is my appetite stronger on a diet",
        "secondary_keywords": [
            "hunger gets worse on diet",
            "appetite increases while dieting",
            "deprivation cravings",
            "diet fatigue hunger",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Appetite", "Cravings", "Mindset"],
    },
    {
        "package_basename": "wave_02_02_how-to-track-body-transformation-without-obsessing-over-the-scale_medium_manual_publish_package.md",
        "posts_ts_slug": "how-to-track-body-transformation-without-obsessing-over-the-scale",
        "seo_title": "How to Track Body Transformation Without the Scale",
        "meta_description": "The scale alone can't tell you if your body is changing. Here's a weekly evidence loop using photos, fit, and measurements that actually shows progress.",
        "primary_keyword": "how to track body transformation",
        "secondary_keywords": [
            "track fat loss without scale",
            "weekly progress check-in",
            "body transformation tracking",
            "fat loss visual proof",
        ],
        "medium_tags": ["Weight Loss", "Body Recomposition", "Progress Photos", "Fitness", "Transformation"],
    },
    {
        "package_basename": "wave_02_03_why-it-feels-like-you-gain-weight-even-when-you-barely-eat_medium_manual_publish_package.md",
        "posts_ts_slug": "why-it-feels-like-you-gain-weight-even-when-you-barely-eat",
        "seo_title": "Why the Scale Goes Up When You're Barely Eating",
        "meta_description": "A rude scale reading isn't always fat gain. Here's what water, sodium, and timing actually do to the morning weigh-in on a diet.",
        "primary_keyword": "why does the scale go up when I barely eat",
        "secondary_keywords": [
            "scale went up eating less",
            "water weight fluctuation",
            "daily weight spike diet",
            "weight up but eating clean",
        ],
        "medium_tags": ["Weight Loss", "Weight Fluctuation", "Dieting", "Scale Anxiety", "Nutrition"],
    },
    {
        "package_basename": "wave_02_04_what-actually-counts-as-a-weight-loss-plateau_medium_manual_publish_package.md",
        "posts_ts_slug": "what-actually-counts-as-a-weight-loss-plateau",
        "seo_title": "What Is a Weight Loss Plateau (and What Isn't)?",
        "meta_description": "Not every slow scale week is a plateau. Here's the honest test for whether your weight loss has actually stalled — or just stopped flattering you.",
        "primary_keyword": "what counts as a weight loss plateau",
        "secondary_keywords": [
            "weight loss plateau definition",
            "am i in a plateau",
            "scale not moving diet",
            "plateau vs slow progress",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Plateau", "Dieting", "Plateau", "Fitness"],
    },
    {
        "package_basename": "wave_02_05_why-losing-5kg-in-a-week-usually-means-water-not-fat_medium_manual_publish_package.md",
        "posts_ts_slug": "why-losing-5kg-in-a-week-usually-means-water-not-fat",
        "seo_title": "Why Losing 5 kg in a Week Is Usually Water Weight",
        "meta_description": "Rapid scale drops look like fat loss but rarely are. Here's what a 5 kg drop in one week actually measures — and why the timescale matters.",
        "primary_keyword": "losing 5kg in a week water weight",
        "secondary_keywords": [
            "rapid weight loss water",
            "lost 5kg in a week",
            "fast weight loss not fat",
            "scale drop first week diet",
        ],
        "medium_tags": ["Weight Loss", "Water Weight", "Rapid Weight Loss", "Dieting", "Nutrition"],
    },
    {
        "package_basename": "wave_02_06_the-most-important-reason-you-think-youre-not-losing-weight_medium_manual_publish_package.md",
        "posts_ts_slug": "the-most-important-reason-you-think-youre-not-losing-weight",
        "seo_title": "Why You're Not Losing Weight Anymore (It's Not You)",
        "meta_description": "The dramatic first week of a diet teaches the wrong lesson. Here's why later progress feels like failure even when the body is still changing.",
        "primary_keyword": "why am I not losing weight anymore",
        "secondary_keywords": [
            "weight loss slowed down",
            "first week diet too fast",
            "stopped losing weight dieting",
            "patience weight loss",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Weight Loss Plateau", "Mindset", "Patience"],
    },
    {
        "package_basename": "wave_02_07_the-scale-can-say-normal-and-still-tell-you-nothing-useful_medium_manual_publish_package.md",
        "posts_ts_slug": "the-scale-can-say-normal-and-still-tell-you-nothing-useful",
        "seo_title": "Normal Weight but Unhappy With Body: What's Happening",
        "meta_description": "You can be at a normal weight and still not feel lean or strong. The scale is too crude for what most people are actually struggling with.",
        "primary_keyword": "normal weight but unhappy with body",
        "secondary_keywords": [
            "skinny fat",
            "body composition vs weight",
            "scale says normal still fat",
            "body recomposition",
        ],
        "medium_tags": ["Weight Loss", "Body Composition", "Body Image", "Dieting", "Health"],
    },
    {
        "package_basename": "wave_02_08_progress-update-2-the-body-changed-slower-than-my-head-did_medium_manual_publish_package.md",
        "posts_ts_slug": "progress-update-2-the-body-changed-slower-than-my-head-did",
        "seo_title": "Weight Loss Progress Update: When the Body Leads the Mind",
        "meta_description": "A real weight loss update: the body changed fast, but the panic took longer to quiet down. Here's what the middle of a transformation actually looks like.",
        "primary_keyword": "weight loss progress update",
        "secondary_keywords": [
            "weight loss journey update",
            "middle of transformation",
            "body vs mind weight loss",
            "trusting weight loss progress",
        ],
        "medium_tags": ["Weight Loss", "Transformation", "Weight Loss Journey", "Founder Story", "Mindset"],
    },
    {
        "package_basename": "wave_02_09_dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight_medium_manual_publish_package.md",
        "posts_ts_slug": "dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight",
        "seo_title": "How to Know You're Losing Weight Without the Scale",
        "meta_description": "The scale is one witness, not the whole case. Here's what actually proves fat loss — from how clothes fit to repeated visual change.",
        "primary_keyword": "how to know if you're losing weight without the scale",
        "secondary_keywords": [
            "fat loss without scale",
            "visual proof weight loss",
            "signs you are losing fat",
            "how to measure fat loss",
        ],
        "medium_tags": ["Weight Loss", "Fat Loss", "Progress Photos", "Body Composition", "Dieting"],
    },
    {
        "package_basename": "wave_02_10_you-do-not-need-to-love-hunger-you-need-to-understand-it_medium_manual_publish_package.md",
        "posts_ts_slug": "you-do-not-need-to-love-hunger-you-need-to-understand-it",
        "seo_title": "How to Deal With Hunger on a Diet (Without Hating It)",
        "meta_description": "You don't need to love hunger to diet well. You need to tell normal hunger apart from chaotic craving — and stop making it worse with restriction.",
        "primary_keyword": "how to deal with hunger on a diet",
        "secondary_keywords": [
            "managing hunger while dieting",
            "hunger vs craving",
            "hunger signals dieting",
            "intuitive eating weight loss",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Hunger", "Appetite", "Intuitive Eating"],
    },
    {
        "package_basename": "wave_02_11_if-your-diet-broke-your-sleep-it-is-not-discipline-anymore_medium_manual_publish_package.md",
        "posts_ts_slug": "if-your-diet-broke-your-sleep-it-is-not-discipline-anymore",
        "seo_title": "Why You Can't Sleep on a Diet (and What to Do)",
        "meta_description": "If dieting wrecked your sleep, the answer isn't more discipline. Here's why under-fueling a hard-trained body breaks rest — and how to fix it.",
        "primary_keyword": "can't sleep on a diet",
        "secondary_keywords": [
            "diet ruined my sleep",
            "insomnia while dieting",
            "under-fueling training",
            "sleep and weight loss",
        ],
        "medium_tags": ["Weight Loss", "Sleep", "Dieting", "Overtraining", "Recovery"],
    },
    {
        "package_basename": "wave_02_12_youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth_medium_manual_publish_package.md",
        "posts_ts_slug": "youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth",
        "seo_title": "Does One Bad Day Ruin a Diet? The Honest Answer",
        "meta_description": "One bad day rarely ruins a diet. The problem is how that fact turns into cheat-day strategy — and what actually happens after several bad days in a row.",
        "primary_keyword": "does one bad day ruin a diet",
        "secondary_keywords": [
            "one cheat day diet",
            "did i ruin my diet",
            "cheat day damage",
            "several bad days diet",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Cheat Day", "Binge Eating", "Habits"],
    },
    {
        "package_basename": "wave_02_13_do-people-who-have-been-obese-for-years-lose-weight-more-slowly_medium_manual_publish_package.md",
        "posts_ts_slug": "do-people-who-have-been-obese-for-years-lose-weight-more-slowly",
        "seo_title": "Do Long-Term Obese People Lose Weight More Slowly?",
        "meta_description": "If weight came on slowly over years, more of it is true fat rather than water. Here's why long-term obesity feels heavier — but isn't uniquely cursed.",
        "primary_keyword": "long-term obesity weight loss speed",
        "secondary_keywords": [
            "long-term obesity weight loss",
            "harder to lose weight after obese",
            "true fat vs water weight",
            "years of being overweight",
        ],
        "medium_tags": ["Weight Loss", "Dieting", "Health", "Mindset", "Fitness"],
    },
    # ---------- Wave 03 ----------
    {
        "package_basename": "wave_03_01_the-quiet-erosion-of-not-believing-your-progress_medium_manual_publish_package.md",
        "posts_ts_slug": "the-quiet-erosion-of-not-believing-your-progress",
        "seo_title": "Why You Stop Believing Your Weight Loss Progress",
        "meta_description": "The biggest weight-loss setbacks happen on quiet days, not bad ones. Here's how doubt erodes belief — and what to do when the process stops feeling real.",
        "primary_keyword": "not believing weight loss progress",
        "secondary_keywords": [
            "can't trust weight loss progress",
            "weight loss self doubt",
            "losing belief diet",
            "quiet erosion diet",
        ],
        "medium_tags": ["Weight Loss", "Mindset", "Weight Loss Journey", "Dieting", "Habits"],
    },
    {
        "package_basename": "wave_03_02_progress-photos-can-lie-as-much-as-the-mirror-does_medium_manual_publish_package.md",
        "posts_ts_slug": "progress-photos-can-lie-as-much-as-the-mirror-does",
        "seo_title": "Why Progress Photos Lie (and How to Use Them Right)",
        "meta_description": "A single progress photo can fake an entire month of gains or losses. Here's how lighting, posture, and timing distort — and how to photograph honestly.",
        "primary_keyword": "progress photos lie weight loss",
        "secondary_keywords": [
            "progress photo accuracy",
            "how to take progress photos",
            "progress photo lighting",
            "body transformation photo",
        ],
        "medium_tags": ["Weight Loss", "Body Image", "Progress Photos", "Self Image", "Fitness"],
    },
    {
        "package_basename": "wave_03_03_is-this-craving-the-food-or-the-deprivation-talking_medium_manual_publish_package.md",
        "posts_ts_slug": "is-this-craving-the-food-or-the-deprivation-talking",
        "seo_title": "Cravings During Dieting: Food or Deprivation?",
        "meta_description": "Not every craving is a craving for food. Some are cravings for permission. Here's how to tell them apart — and why restriction makes them louder.",
        "primary_keyword": "craving from deprivation diet",
        "secondary_keywords": [
            "deprivation cravings",
            "food cravings dieting",
            "restriction makes cravings worse",
            "diet cravings psychology",
        ],
        "medium_tags": ["Weight Loss", "Cravings", "Dieting", "Food Psychology", "Intuitive Eating"],
    },
    {
        "package_basename": "wave_03_04_the-same-number-on-the-scale-feels-different-at-30-than-at-20_medium_manual_publish_package.md",
        "posts_ts_slug": "the-same-number-on-the-scale-feels-different-at-30-than-at-20",
        "seo_title": "Same Weight, Different Body: Why It Changes by 30",
        "meta_description": "Weighing 75 kg at 22 looks different from 75 kg at 30. Here's what changes underneath the scale number — and why composition matters more than weight.",
        "primary_keyword": "same weight different decade body",
        "secondary_keywords": [
            "same weight different body composition",
            "aging weight loss",
            "weight loss after 30",
            "body composition changes with age",
        ],
        "medium_tags": ["Weight Loss", "Body Composition", "Aging", "Health", "Fitness"],
    },
    {
        "package_basename": "wave_03_05_the-small-wins-between-progress-updates-are-the-real-program_medium_manual_publish_package.md",
        "posts_ts_slug": "the-small-wins-between-progress-updates-are-the-real-program",
        "seo_title": "The Small Weight Loss Wins Between Milestones",
        "meta_description": "The headline number isn't the program. Real weight loss happens in the quiet weeks nobody photographs. Here's what those small wins actually look like.",
        "primary_keyword": "small wins between weight loss milestones",
        "secondary_keywords": [
            "small weight loss wins",
            "boring weight loss weeks",
            "consistent progress dieting",
            "weight loss discipline",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Journey", "Habits", "Mindset", "Consistency"],
    },
    {
        "package_basename": "wave_03_06_the-first-month-of-maintenance-feels-nothing-like-the-diet_medium_manual_publish_package.md",
        "posts_ts_slug": "the-first-month-of-maintenance-feels-nothing-like-the-diet",
        "seo_title": "The First Month of Maintenance After a Diet: Real Talk",
        "meta_description": "Maintenance has no finish line, and the first month feels nothing like the cut. Here's what actually happens when the diet ends but the work doesn't.",
        "primary_keyword": "first month of maintenance after diet",
        "secondary_keywords": [
            "maintenance after weight loss",
            "after the diet is over",
            "transitioning to maintenance",
            "keeping weight off first month",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Dieting", "Long Game", "Mindset"],
    },
    {
        "package_basename": "wave_03_07_why-does-my-hunger-spike-at-night-when-i-was-fine-all-day_medium_manual_publish_package.md",
        "posts_ts_slug": "why-does-my-hunger-spike-at-night-when-i-was-fine-all-day",
        "seo_title": "Why Does Hunger Spike at Night When Dieting?",
        "meta_description": "A clean day can end at 9 p.m. with you at the fridge. Here's why night hunger hits harder during a diet — and what your day was actually missing.",
        "primary_keyword": "hunger spike at night dieting",
        "secondary_keywords": [
            "night hunger diet",
            "why am I hungry at night",
            "evening hunger dieting",
            "late night food cravings",
        ],
        "medium_tags": ["Weight Loss", "Hunger", "Appetite", "Dieting", "Cravings"],
    },
    {
        "package_basename": "wave_03_08_the-plateau-that-was-actually-an-honesty-problem_medium_manual_publish_package.md",
        "posts_ts_slug": "the-plateau-that-was-actually-an-honesty-problem",
        "seo_title": "The Plateau That's Really a Tracking Problem",
        "meta_description": "A meaningful share of weight loss plateaus aren't plateaus at all. Here's the honest audit of what your day actually contained — and why tracking lies.",
        "primary_keyword": "weight loss plateau tracking honesty",
        "secondary_keywords": [
            "weight loss plateau tracking",
            "not a real plateau",
            "honest calorie tracking",
            "plateau or tracking error",
        ],
        "medium_tags": ["Weight Loss", "Weight Loss Plateau", "Calorie Counting", "Dieting", "Habits"],
    },
    {
        "package_basename": "wave_03_09_progress-update-4-the-body-finally-stopped-being-the-loud-thing_medium_manual_publish_package.md",
        "posts_ts_slug": "progress-update-4-the-body-finally-stopped-being-the-loud-thing",
        "seo_title": "Weight Loss Progress Update: The Quiet Maintenance Phase",
        "meta_description": "Four months past the last update. The numbers moved less. The relationship with the body moved more. A founder check-in from the quiet phase.",
        "primary_keyword": "weight loss progress update maintenance",
        "secondary_keywords": [
            "maintenance progress update",
            "after 50kg weight loss",
            "body at maintenance",
            "long term weight loss check-in",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Weight Loss Journey", "Founder Story", "Long Game"],
    },
    {
        "package_basename": "wave_03_10_clothes-tell-you-the-truth-the-mirror-cannot_medium_manual_publish_package.md",
        "posts_ts_slug": "clothes-tell-you-the-truth-the-mirror-cannot",
        "seo_title": "Why Clothes Are Better Than the Scale for Weight Loss",
        "meta_description": "The mirror lies fast. The scale is noisy. Clothes don't negotiate. Here's why fit is the honest metric during a diet — and how to use it properly.",
        "primary_keyword": "clothes better than scale weight loss",
        "secondary_keywords": [
            "clothes fit weight loss",
            "pants getting looser",
            "non scale victory",
            "how clothes fit during diet",
        ],
        "medium_tags": ["Weight Loss", "Body Composition", "Body Image", "Progress Photos", "Dieting"],
    },
    {
        "package_basename": "wave_03_11_the-bad-weekend-that-finally-taught-me-something_medium_manual_publish_package.md",
        "posts_ts_slug": "the-bad-weekend-that-finally-taught-me-something",
        "seo_title": "What a Bad Diet Weekend Actually Teaches You",
        "meta_description": "A Friday dinner became a Saturday lunch became a Saturday night. The damage was small. The lesson was huge. Here's what a bad diet weekend really reveals.",
        "primary_keyword": "bad diet weekend lessons",
        "secondary_keywords": [
            "bad diet weekend",
            "blew diet on weekend",
            "weekend overeating diet",
            "how to recover from bad weekend",
        ],
        "medium_tags": ["Weight Loss", "Cheat Day", "Binge Eating", "Dieting", "Habits"],
    },
    {
        "package_basename": "wave_03_12_how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud_medium_manual_publish_package.md",
        "posts_ts_slug": "how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud",
        "seo_title": "How to Stop Checking the Mirror Every Day on a Diet",
        "meta_description": "In most cuts, the diet is working and the mirror is getting louder. Here's how to look less, look better, and stop letting the mirror run the program.",
        "primary_keyword": "mirror diet weight loss anxiety",
        "secondary_keywords": [
            "stop checking mirror diet",
            "mirror anxiety weight loss",
            "body dysmorphia dieting",
            "how to look in the mirror less",
        ],
        "medium_tags": ["Weight Loss", "Body Image", "Self Image", "Mindset", "Body Dysmorphia"],
    },
    {
        "package_basename": "wave_03_13_do-i-actually-have-to-meal-prep-to-lose-weight_medium_manual_publish_package.md",
        "posts_ts_slug": "do-i-actually-have-to-meal-prep-to-lose-weight",
        "seo_title": "Do You Have to Meal Prep to Lose Weight? The Real Answer",
        "meta_description": "The honest answer is no. But you have to solve what meal prep solves — decision fatigue, macro reliability, friction. Here are the working alternatives.",
        "primary_keyword": "do i have to meal prep to lose weight",
        "secondary_keywords": [
            "meal prep for weight loss",
            "lose weight without meal prep",
            "alternatives to meal prepping",
            "decision fatigue diet",
        ],
        "medium_tags": ["Weight Loss", "Meal Prep", "Dieting", "Meal Planning", "Habits"],
    },
    {
        "package_basename": "wave_03_14_why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think_medium_manual_publish_package.md",
        "posts_ts_slug": "why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think",
        "seo_title": "Why Adding Cardio to a Cut Often Backfires",
        "meta_description": "Cardio looks like the obvious fix when fat loss slows. It often makes things worse. Here's why — physiologically and behaviorally — and what to do instead.",
        "primary_keyword": "cardio backfires on diet",
        "secondary_keywords": [
            "too much cardio on cut",
            "cardio slowed weight loss",
            "when to add cardio diet",
            "cardio vs diet",
        ],
        "medium_tags": ["Weight Loss", "Cardio", "Exercise Science", "Dieting", "Overtraining"],
    },
    {
        "package_basename": "wave_03_15_weighing-yourself-every-day-can-be-a-trap-not-a-discipline_medium_manual_publish_package.md",
        "posts_ts_slug": "weighing-yourself-every-day-can-be-a-trap-not-a-discipline",
        "seo_title": "Is Daily Weighing a Trap? The Honest Answer",
        "meta_description": "The advice to weigh yourself daily sounds like discipline. For many people, it's the trap that wrecks the program. Here's how to tell which one you are.",
        "primary_keyword": "daily weigh in trap weight loss",
        "secondary_keywords": [
            "weigh yourself every day",
            "daily weighing disorder",
            "scale anxiety daily",
            "should i stop daily weighing",
        ],
        "medium_tags": ["Weight Loss", "Scale Anxiety", "Mental Health", "Dieting", "Weight Fluctuation"],
    },
    {
        "package_basename": "wave_03_16_why-cutting-sodium-too-hard-can-backfire_medium_manual_publish_package.md",
        "posts_ts_slug": "why-cutting-sodium-too-hard-can-backfire",
        "seo_title": "Why Cutting Sodium Too Low Backfires on a Diet",
        "meta_description": "Cutting sodium hard makes the scale drop. It feels like discipline. It's mostly water — and it teaches you to chase the wrong signal. Here's the honest version.",
        "primary_keyword": "cutting sodium too low backfire",
        "secondary_keywords": [
            "low sodium weight loss",
            "cutting salt for weight loss",
            "sodium water weight",
            "is low sodium bad for dieting",
        ],
        "medium_tags": ["Weight Loss", "Water Weight", "Nutrition", "Dieting", "Scale Anxiety"],
    },
    {
        "package_basename": "wave_03_17_the-week-my-appetite-came-back-during-maintenance_medium_manual_publish_package.md",
        "posts_ts_slug": "the-week-my-appetite-came-back-during-maintenance",
        "seo_title": "Why Appetite Returns During Maintenance (Normal Not Failure)",
        "meta_description": "Five months into maintenance, my appetite came back. Not as failure — as normal. Here's what that week looked like and what I almost did wrong.",
        "primary_keyword": "appetite returns during maintenance",
        "secondary_keywords": [
            "hungry during maintenance",
            "appetite after weight loss",
            "maintenance hunger",
            "why is appetite back after cut",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Appetite", "Founder Story", "Hunger"],
    },
    {
        "package_basename": "wave_03_18_when-does-one-bad-meal-actually-become-a-slip_medium_manual_publish_package.md",
        "posts_ts_slug": "when-does-one-bad-meal-actually-become-a-slip",
        "seo_title": "When Does One Bad Meal Become a Diet Slip?",
        "meta_description": "People treat one bad meal and a slip as the same thing. They aren't. The meal is the trigger. The slip is everything you do in the 48 hours after.",
        "primary_keyword": "when one bad meal becomes diet slip",
        "secondary_keywords": [
            "one bad meal diet",
            "diet slip recovery",
            "morning after a binge",
            "how to recover from one bad meal",
        ],
        "medium_tags": ["Weight Loss", "Cheat Day", "Binge Eating", "Dieting", "Food Psychology"],
    },
    {
        "package_basename": "wave_03_19_your-appetite-scales-with-training-volume-not-with-weight_medium_manual_publish_package.md",
        "posts_ts_slug": "your-appetite-scales-with-training-volume-not-with-weight",
        "seo_title": "Why Hunger Follows Training Volume, Not the Scale",
        "meta_description": "Appetite isn't a function of how much you weigh. It tracks training, sleep, and the body's repair workload. Here's what your hunger is actually reading.",
        "primary_keyword": "appetite scales with training volume",
        "secondary_keywords": [
            "hungry on training days",
            "training volume appetite",
            "workout hunger dieting",
            "why am I hungry after workout",
        ],
        "medium_tags": ["Weight Loss", "Appetite", "Hunger", "Strength Training", "Recovery"],
    },
    {
        "package_basename": "wave_03_20_the-day-i-realized-the-program-was-just-my-life-now_medium_manual_publish_package.md",
        "posts_ts_slug": "the-day-i-realized-the-program-was-just-my-life-now",
        "seo_title": "When Dieting Becomes Lifestyle: The Quiet Transition",
        "meta_description": "There's a quiet moment when the program stops being a project and starts being your life. The shift isn't announced. You notice it weeks later, by accident.",
        "primary_keyword": "when diet becomes lifestyle",
        "secondary_keywords": [
            "diet to lifestyle transition",
            "weight loss becomes habit",
            "when diet is lifestyle",
            "sustainable weight loss mindset",
        ],
        "medium_tags": ["Weight Loss", "Maintenance Phase", "Lifestyle Change", "Long Game", "Habits"],
    },
]


# --- Medium package retrofit ---------------------------------------------------

# Matches the legacy section block: "## SEO Title\n<line>\n\n## Subtitle / Description\n<line>\n\n## Medium Tags\n- tag\n- tag\n- tag\n- tag\n- tag"
# Captures <seo_title>, <subtitle>, <existing_tags_block>
MEDIUM_BLOCK_RE = re.compile(
    r"## SEO Title\n(?P<seo_title>.+?)\n\n## Subtitle / Description\n(?P<subtitle>.+?)\n\n## Medium Tags\n(?P<tags>(?:- .+\n)+)",
    re.MULTILINE,
)

# Presence of "## Meta Description" indicates already-retrofit (idempotency guard).
MEDIUM_RETROFIT_MARKER_RE = re.compile(r"^## Meta Description\n", re.MULTILINE)


def apply_medium_package(path: Path, spec: dict) -> str:
    """Return status string: 'updated' / 'already-retrofit' / 'no-match'."""
    text = path.read_text(encoding="utf-8")
    if MEDIUM_RETROFIT_MARKER_RE.search(text):
        return "already-retrofit"

    m = MEDIUM_BLOCK_RE.search(text)
    if not m:
        return "no-match"

    subtitle = m.group("subtitle")
    new_tags_block = "\n".join(f"- {t}" for t in spec["medium_tags"]) + "\n"
    secondary_block = "\n".join(f"- {k}" for k in spec["secondary_keywords"])

    replacement = (
        f"## SEO Title\n{spec['seo_title']}\n"
        f"\n## Subtitle / Description\n{subtitle}\n"
        f"\n## Meta Description\n{spec['meta_description']}\n"
        f"\n## Primary Keyword\n{spec['primary_keyword']}\n"
        f"\n## Secondary Keywords\n{secondary_block}\n"
        f"\n## Medium Tags\n{new_tags_block}"
    )

    new_text = text[:m.start()] + replacement + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    return "updated"


# --- posts.ts retrofit ---------------------------------------------------------


def posts_ts_insert_seo_fields(text: str, slug: str, spec: dict) -> tuple[str, str]:
    """Insert seoTitle / metaDescription / keywords before heroImage. Returns (new_text, status)."""
    # Find the entry for this slug.
    slug_escaped = re.escape(slug)
    # Match the slug line and capture until next heroImage line (within the same entry).
    entry_re = re.compile(
        rf"(    slug: '{slug_escaped}',\n(?:.*\n)*?    tags: \[[^\]]+\],\n)(    heroImage:)",
        re.MULTILINE,
    )
    m = entry_re.search(text)
    if not m:
        return text, "slug-not-found"

    head, hero_line = m.group(1), m.group(2)

    # Idempotency: already has seoTitle key between slug and heroImage?
    if "    seoTitle:" in head:
        return text, "already-retrofit"

    # Escape single quotes in strings for JS single-quote literals.
    def js_string(s: str) -> str:
        # Prefer double quotes when the string contains single quotes (apostrophes).
        if "'" in s and '"' not in s:
            return f'"{s}"'
        if "'" in s:
            return "'" + s.replace("'", "\\'") + "'"
        return f"'{s}'"

    seo_title_js = js_string(spec["seo_title"])
    meta_js = js_string(spec["meta_description"])
    primary_js = js_string(spec["primary_keyword"])
    secondary_js_list = ",\n".join(f"      {js_string(k)}" for k in spec["secondary_keywords"])

    insertion = (
        f"    seoTitle: {seo_title_js},\n"
        f"    metaDescription:\n      {meta_js},\n"
        f"    keywords: [\n"
        f"      {primary_js},\n"
        f"{secondary_js_list},\n"
        f"    ],\n"
    )

    new_entry_head = head + insertion
    new_text = text[:m.start()] + new_entry_head + hero_line + text[m.end():]
    return new_text, "updated"


# --- main ----------------------------------------------------------------------


def main() -> int:
    medium_stats: dict[str, int] = {"updated": 0, "already-retrofit": 0, "no-match": 0}
    posts_stats: dict[str, int] = {"updated": 0, "already-retrofit": 0, "slug-not-found": 0, "skipped-no-slug": 0}

    # 1) Medium packages.
    for row in SPEC:
        path = MEDIUM_DIR / row["package_basename"]
        if not path.exists():
            print(f"[MEDIUM] MISSING: {path}")
            medium_stats["no-match"] += 1
            continue
        status = apply_medium_package(path, row)
        medium_stats[status] += 1
        print(f"[MEDIUM] {status}: {row['package_basename']}")

    # 2) posts.ts — accumulate all edits then write once.
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

    # Nonzero exit if any unexpected failures.
    if medium_stats["no-match"] > 0 or posts_stats["slug-not-found"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
