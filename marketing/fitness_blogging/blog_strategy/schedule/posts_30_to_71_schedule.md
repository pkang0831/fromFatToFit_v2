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
| 30 | 2026-05-14 | the-scale-lies-differently-in-the-morning-than-in-the-evening | batch 8 |
| 31 | 2026-05-15 | sleep-debt-ruins-a-week-of-dieting-in-three-nights | batch 8 |
| 32 | 2026-05-16 | the-quiet-role-vegetables-play-in-staying-full | batch 8 |
| 33 | 2026-05-17 | how-do-i-stop-a-binge-from-becoming-a-binge-week | batch 8 |
| 34 | 2026-05-18 | you-look-different-to-other-people-before-yourself | batch 8 |
| 35 | 2026-05-19 | the-first-week-of-any-diet-is-the-most-misleading-one | batch 9 |
| 36 | 2026-05-20 | losing-weight-is-not-the-same-as-getting-leaner | batch 9 |
| 37 | 2026-05-21 | why-people-gain-more-back-than-they-lost | batch 9 |
| 38 | 2026-05-22 | how-do-i-eat-normally-at-social-events | batch 9 |
| 39 | 2026-05-23 | the-kind-of-person-who-stays-at-their-goal-weight | batch 9 |
| 40 | 2026-05-24 | why-you-stop-losing-weight-around-month-three | batch 10 |
| 41 | 2026-05-25 | am-i-actually-hungry-or-am-i-bored | batch 10 |
| 42 | 2026-05-26 | how-much-protein-do-i-actually-need-to-lose-fat | batch 10 |
| 43 | 2026-05-27 | why-your-workouts-feel-harder-when-youre-dieting | batch 10 |
| 44 | 2026-05-28 | why-your-strength-increases-before-your-shape-changes | batch 10 |
| 45 | 2026-05-29 | the-quiet-erosion-of-not-believing-your-progress | batch 11 |
| 46 | 2026-05-30 | progress-photos-can-lie-as-much-as-the-mirror-does | batch 11 |
| 47 | 2026-05-31 | is-this-craving-the-food-or-the-deprivation-talking | batch 11 |
| 48 | 2026-06-01 | the-same-number-on-the-scale-feels-different-at-30-than-at-20 | batch 11 |
| 49 | 2026-06-02 | the-small-wins-between-progress-updates-are-the-real-program | batch 11 |
| 50 | 2026-06-03 | the-first-month-of-maintenance-feels-nothing-like-the-diet | batch 12 |
| 51 | 2026-06-04 | why-does-my-hunger-spike-at-night-when-i-was-fine-all-day | batch 12 |
| 52 | 2026-06-05 | the-plateau-that-was-actually-an-honesty-problem | batch 12 |
| 53 | 2026-06-06 | progress-update-4-the-body-finally-stopped-being-the-loud-thing | batch 12 (Progress Update #4 milestone) |
| 54 | 2026-06-07 | clothes-tell-you-the-truth-the-mirror-cannot | batch 12 |
| 55 | 2026-06-08 | the-bad-weekend-that-finally-taught-me-something | batch 13 |
| 56 | 2026-06-09 | how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud | batch 13 |
| 57 | 2026-06-10 | do-i-actually-have-to-meal-prep-to-lose-weight | batch 13 |
| 58 | 2026-06-11 | why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think | batch 13 |
| 59 | 2026-06-12 | weighing-yourself-every-day-can-be-a-trap-not-a-discipline | batch 13 |
| 60 | 2026-06-13 | why-cutting-sodium-too-hard-can-backfire | batch 14 (Tier A slot 1) |
| 61 | 2026-06-14 | the-week-my-appetite-came-back-during-maintenance | batch 14 |
| 62 | 2026-06-15 | when-does-one-bad-meal-actually-become-a-slip | batch 14 |
| 63 | 2026-06-16 | your-appetite-scales-with-training-volume-not-with-weight | batch 14 |
| 64 | 2026-06-17 | the-day-i-realized-the-program-was-just-my-life-now | batch 14 |

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
