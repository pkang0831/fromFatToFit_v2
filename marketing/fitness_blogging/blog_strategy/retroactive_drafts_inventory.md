# Retroactive Drafts Inventory

Generated 2026-04-19 during the post-batch-12 backlog cleanup. This file documents the 21 old-format publish-ready drafts in `marketing/devenira_prelaunch/` that were authored before the current blueprint and have **not** been ported to `frontend/src/content/blog/posts.ts`.

## Why these are not auto-ported

These drafts pre-date the current blueprint (`blog_post_blueprint.md`). They use a different front-matter structure (SEO Title / SEO Slug / Meta Description as H2 sections instead of `**Field**:` lines), reference hero images at archive paths that no longer exist in the worktree (`marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/...`), and were written before the voice anchor was locked at post 10. Auto-porting them would risk:

- voice drift (reviewer subagent could flag multiple as `rewrite`)
- broken hero references (would 404 or need replacement from current 22-image pool, which is already at saturation per post-60 image checkpoint)
- claim-class undercalibration in physiology-adjacent topics (sodium, refined carbs)
- topic collision with already-ported posts of similar lanes

**Decision: hold for editorial review by founder. Do not bulk-port.**

## The 21 Unported Retroactive Drafts

| # | Filename Stem | Working Title | Topic Lane | Notes |
|---|---------------|---------------|------------|-------|
| 1 | `already_thin_still_want_to_diet` | "I'm Already Thin, But I Still Want to Diet." Here Is Why That Is Common. | body image / disorder-adjacent | Class 4 candidate (ED-adjacent — needs sign-off) |
| 2 | `cant_stick_to_diet` | If You Can't Stick to a Diet, This May Matter More Than Willpower | consistency | overlaps with `the-most-reliable-way-to-succeed-at-dieting` (worldview) |
| 3 | `eating_too_little` | Eating Too Little Can Make Food Feel Even Louder | appetite | overlaps with `you-do-not-need-to-love-hunger` (appetite) |
| 4 | `food_freedom` | Do You Really Have to Avoid Bread and Chocolate Forever to Stay Slim | restriction | overlaps with batch 11's `is-this-craving-the-food-or-the-deprivation-talking` |
| 5 | `highly_processed_food_voltage` | Why Highly Processed Food Starts Feeling Emotionally Loud | appetite / hyper-palatables | distinct topic, low collision |
| 6 | `junk_food_tastes_better_when_dieting` | Why Junk Food Starts Tasting Better When You Diet | appetite / restriction | overlaps with `you-do-not-need-to-love-hunger` |
| 7 | `low_sodium_backfire` | Why Cutting Sodium Too Hard Can Backfire | scale / water-weight | distinct topic; Class 3+ (electrolytes physiology) |
| 8 | `lower_body_stubborn` | Why Lower Body Fat Feels So Stubborn | body composition | distinct topic; Class 3+ (regional fat distribution) |
| 9 | `maintenance_feels_scarier_than_dieting` | Why Maintenance Can Feel Scarier Than Dieting | maintenance | overlaps with batch 12's `the-first-month-of-maintenance-feels-nothing-like-the-diet` |
| 10 | `normal_eating_after_restriction` | Why Normal Eating Can Feel Impossible After Hard Restriction | restriction | overlaps with `is-this-craving...` (deprivation framing) |
| 11 | `real_fat_loss_vs_fake_progress` | How to Tell Real Fat Loss From Fake Progress | body composition / scale | overlaps with `losing-weight-is-not-the-same-as-getting-leaner` |
| 12 | `refined_carbs` | Can You Lose Weight While Eating Refined Carbs | food structure | distinct topic; Class 3 |
| 13 | `satisfying_food_matters` | If You Can't Stick to a Diet, Satisfying Food Matters More Than You Think | food structure | overlaps thematically with `cant_stick_to_diet` |
| 14 | `scale_reward_addiction` | If the Scale Still Decides Your Mood, It Still Has Too Much Power | scale | overlaps with `one-emotional-weigh-in-can-wreck-a-good-week` |
| 15 | `set_point_feeling_stuck` | Why Your Body Starts Feeling "Stuck" at the Same Weight | plateau / set point | overlaps with `how-do-you-know-when-youve-reached-your-set-point` |
| 16 | `softer_body_at_lower_weight` | Why Your Body Can Look Softer Even at a Lower Weight | body composition | overlaps with `losing-weight-is-not-the-same-as-getting-leaner` |
| 17 | `stability_food` | If You Can't Stick to a Diet, This Kind of Food May Matter More Than Willpower | food structure | overlaps with `the-quiet-role-vegetables-play-in-staying-full` |
| 18 | `thin_people_can_gain_weight` | Thin People Can Gain Weight Too. Here Is Why That Matters. | body composition | distinct topic, low collision |
| 19 | `weaker_at_lower_weight` | Why You Can Feel Weaker Even at a Lower Weight | exercise / body composition | overlaps with `why-your-workouts-feel-harder-when-youre-dieting` |
| 20 | `weekends_keep_restarting_the_diet` | Why Weekends Keep Restarting Your Diet | consistency | overlaps with `the-plateau-that-was-actually-an-honesty-problem` (weekend amnesia section) |
| 21 | `working_out_harder` | Working Out Harder Is Not Always the Answer. Here Is Why. | exercise | overlaps with `why-your-workouts-feel-harder-when-youre-dieting` |

## Triage Recommendation

**Tier A — Distinct topics, low collision, would add real value if rewritten to current blueprint** (4 drafts):
- `low_sodium_backfire` (scale lane, water-weight mechanism)
- `lower_body_stubborn` (body comp lane, regional fat)
- `refined_carbs` (food structure, refined-grain mechanism)
- `thin_people_can_gain_weight` (body comp lane, weight-set-point inversion)
- `highly_processed_food_voltage` (appetite, hyper-palatables — distinct from existing)

**Tier B — Overlapping with already-ported posts, likely need rewrite or merge** (12 drafts):
- `cant_stick_to_diet`, `eating_too_little`, `food_freedom`, `junk_food_tastes_better_when_dieting`, `maintenance_feels_scarier_than_dieting`, `normal_eating_after_restriction`, `real_fat_loss_vs_fake_progress`, `satisfying_food_matters`, `scale_reward_addiction`, `set_point_feeling_stuck`, `softer_body_at_lower_weight`, `stability_food`, `weaker_at_lower_weight`, `weekends_keep_restarting_the_diet`, `working_out_harder`

**Tier C — Class 4 / ED-adjacent, needs human (founder) sign-off before any port** (1 draft):
- `already_thin_still_want_to_diet` — body image / disorder-adjacent territory

## Recommended Action

1. **Tier A (5 drafts)**: Slot into batches 14–18 (1 per batch) as fresh rewrites under current blueprint, using these old drafts as research material, not as direct source.
2. **Tier B (15 drafts)**: Archive in `marketing/devenira_prelaunch/_archive_pre_blueprint/` directory after founder review; do not port.
3. **Tier C (1 draft)**: Hold; surface to founder during the next 50-post checkpoint or as a Class 4 sign-off ticket.

This plan keeps the 100-post target on track (need 39 more new approved posts; Tier A contributes 5 of those) while not contaminating current voice with pre-anchor drafts.

## Status (updated 2026-04-19, post-batch-13 cleanup)

- Inventory date: 2026-04-19
- Tier B (15 drafts): **MOVED to `marketing/devenira_prelaunch/_archive_pre_blueprint/`** (no port action; held for record)
- Tier A (5 drafts): old drafts **MOVED to archive with `_OLD.md` suffix**; **research notes extracted** to `_archive_pre_blueprint/_research_notes_for_tier_a/`. Modern rewrites scheduled into batches 14–18 per `tier_a_slotting_plan.md`.
- Tier C (1 draft, `already_thin_still_want_to_diet`): **MOVED to archive with `_TIER_C_HOLD.md` suffix**. Held for founder Class 4 sign-off (no action without explicit founder review).
- Batch 14+ pipeline: 4 fresh drafts per batch + 1 Tier A rewrite (using extracted research notes as source material)

## Resulting State of `marketing/devenira_prelaunch/`

After this cleanup:
- 35 modern publish-ready drafts (fully ported through batch 13)
- 0 retroactive drafts at the top level
- 21 drafts archived under `_archive_pre_blueprint/`
- 5 Tier A research notes ready for batch 14–18 use

## Resulting State of Drafts Directory

```
marketing/devenira_prelaunch/
├── (35 modern publish_ready drafts — all ported through batch 13)
└── _archive_pre_blueprint/
    ├── README.md
    ├── (15 Tier B old drafts)
    ├── (5 Tier A old drafts, _OLD.md suffix)
    ├── already_thin_still_want_to_diet_publish_ready_TIER_C_HOLD.md
    └── _research_notes_for_tier_a/
        ├── low_sodium_backfire_research_notes.md
        ├── lower_body_stubborn_research_notes.md
        ├── refined_carbs_research_notes.md
        ├── thin_people_can_gain_weight_research_notes.md
        └── highly_processed_food_voltage_research_notes.md
```
