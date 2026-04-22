# Publishing Schedule: Posts 30–56

Generated 2026-04-19 to consolidate the overdue reminder expansions per Plan §18 (regenerations were due at approved-post 40 and again at 60; this catches up the 30→40, 40→56 gap in one document).

Existing Calendar/Reminders cover posts 1–29 (prior setup). This schedule adds the 27 newly ported posts spanning batches 8–11.

## Rule
- Publish to owned-site: date from `frontend/src/content/blog/posts.ts` (auto via Git push)
- Publish to Medium manually: same date, 09:00 KST
- Share to SNS: same date, 11:00 KST
- Reminder fires: 08:00 KST on publish date

## Schedule

| # | Date | Slug | Wave / Batch |
|---|------|------|--------------|
| 30 | 2026-05-14 | why-do-i-weigh-more-at-night | batch 8 |
| 31 | 2026-05-15 | does-bad-sleep-ruin-weight-loss | batch 8 |
| 32 | 2026-05-16 | do-vegetables-help-you-feel-full-on-a-diet | batch 8 |
| 33 | 2026-05-17 | how-to-stop-a-binge-from-becoming-a-binge-week | batch 8 |
| 34 | 2026-05-18 | why-do-others-notice-my-weight-loss-before-me | batch 8 |
| 35 | 2026-05-19 | why-do-you-lose-so-much-weight-first-week | batch 9 |
| 36 | 2026-05-20 | difference-between-weight-loss-and-fat-loss | batch 9 |
| 37 | 2026-05-21 | why-do-i-gain-back-more-weight-than-i-lost | batch 9 |
| 38 | 2026-05-22 | how-to-eat-at-social-events-on-a-diet | batch 9 |
| 39 | 2026-05-23 | how-to-stay-at-your-goal-weight-long-term | batch 9 |
| 40 | 2026-05-24 | why-did-i-stop-losing-weight-at-3-months | batch 10 |
| 41 | 2026-05-25 | how-to-tell-if-youre-hungry-or-bored | batch 10 |
| 42 | 2026-05-26 | how-much-protein-do-i-need-to-lose-fat | batch 10 |
| 43 | 2026-05-27 | why-are-my-workouts-harder-on-a-cut | batch 10 |
| 44 | 2026-05-28 | why-does-strength-increase-before-muscle-size | batch 10 |
| 45 | 2026-05-29 | how-to-trust-slow-weight-loss-progress | batch 11 |
| 46 | 2026-05-30 | why-progress-photos-dont-show-progress | batch 11 |
| 47 | 2026-05-31 | why-does-restriction-make-cravings-worse | batch 11 |
| 48 | 2026-06-01 | why-does-the-same-weight-feel-different-as-you-age | batch 11 |
| 49 | 2026-06-02 | non-scale-victories-weight-loss | batch 11 |
| 50 | 2026-06-03 | first-month-of-maintenance-after-weight-loss | batch 12 |
| 51 | 2026-06-04 | why-am-i-hungry-at-night-but-not-during-the-day | batch 12 |
| 52 | 2026-06-05 | am-i-really-in-a-plateau-or-tracking-wrong | batch 12 |
| 53 | 2026-06-06 | life-after-50kg-weight-loss | batch 12 (Progress Update #4 milestone) |
| 54 | 2026-06-07 | clothes-fit-better-but-scale-is-the-same | batch 12 |
| 55 | 2026-06-08 | how-to-get-back-on-track-after-a-bad-weekend | batch 13 |
| 56 | 2026-06-09 | how-to-stop-mirror-checking-on-a-diet | batch 13 |
| 57 | 2026-06-10 | do-i-have-to-meal-prep-to-lose-weight | batch 13 |
| 58 | 2026-06-11 | why-adding-cardio-to-a-cut-backfires | batch 13 |
| 59 | 2026-06-12 | daily-weighing-eating-disorder-risk | batch 13 |
| 60 | 2026-06-13 | does-cutting-sodium-cause-water-retention | batch 14 (Tier A slot 1) |
| 61 | 2026-06-14 | appetite-returns-during-maintenance | batch 14 |
| 62 | 2026-06-15 | does-one-bad-meal-ruin-a-diet | batch 14 |
| 63 | 2026-06-16 | why-am-i-so-hungry-after-lifting-weights | batch 14 |
| 64 | 2026-06-17 | when-does-a-diet-become-a-lifestyle | batch 14 |

(The "#" column is sequential publish order. The earlier `posts_20_to_29_schedule.md` numbered posts 20–29; numbering above starts at 30 to continue cleanly. The discrepancy with the 49 entries currently in posts.ts vs the 51 approved-post counter is because posts 1–26 includes 7 retroactive drafts that were never ported into posts.ts.)

## Calendar
- Calendar: `Devenira Blog`
- Events: each at 09:00–09:15 on publish date

## Reminders
- List: `Devenira Blog`
- Due: each at 08:00 on publish date
- Title: `Publish: <slug> → Medium + SNS`

## AppleScript Setup

A new AppleScript to create Calendar events and Reminders for posts 30–49 should be generated and run on a Mac with permissions enabled. The shape mirrors `setup_reminders_20260417.applescript` and `setup_reminders_posts_30_44.applescript` already in this directory — extend posts_30_44 to cover up through 49 (5 additional entries from batch 11).

## Next Checkpoint

At approved-post 80, regenerate for posts 60–79.
