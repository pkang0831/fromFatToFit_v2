# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology claims or named hormones | physiology/demographic → Class 3 min; any of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4} named → Class 4 | _open; batch_15 narrowed to **0/5 (5 of 5 correct self-bumps, 100%)** — drafts 73, 74, 75 self-bumped to Class 3 with trigger annotations D, A, A respectively; drafts 72 and 76 correctly held Class 2 under Step 4 generosity. Trend: 60% (batch 13 retro) → 80% (batch 14) → **100% (batch 15)**. **First measurable 100% batch on Rule 2.** Pre-flight checklist (added 2026-04-19) is now demonstrably effective. Batch 16 target: **hold 5/5 (100%)** for second consecutive batch — full re-resolution per "0/5 holds for 2 consecutive batches" criterion. Hormone noun-scan stays clean (one generic "hormonal fluctuation" reference in draft 75 inside a list with no specific hormone named did not trigger Class 4)._

## Watch-only observations (not Active rules, monitored only)

- 2026-04-20 | post_75_audit | Tier A deep_dive rewrites (physiology-adjacent topics with explicit numbers) trend ~1.5 points below anchor on Imagery Density as physics/arithmetic density displaces concrete sensory anchors | no action yet — observe across batches 15–18 (lower_body_stubborn, refined_carbs, thin_people_can_gain_weight, highly_processed_food_voltage). If 2 of 4 Tier A rewrites score Imagery ≤ 7.5, promote to Active drift rule 11. If 3 of 4 score ≥ 8.0, close the watch. | _observation only; no corrective action required from writer. **Sample after batch 15: 1 of 2 above threshold** — sodium (post 67) 7.5; lower-body (post 73) **8.5**. Watch narrows: from "2 of 2 below" → "1 of 2 above," with 2 more Tier A samples to come. The lower-body post deliberately seeded sensory anchors around the physiology numbers per writer's pre-flight, validating the workflow described in `tier_a_slotting_plan.md`. If both refined_carbs (batch 16) and thin_people (batch 17) also score ≥ 8.0, the watch closes at batch 17 close (3 of 4 ≥ 8.0)._

## Resolved (3 consecutive clean batches)

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames | internal link target MUST be a slug already present in posts.ts | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | banned-phrase family in primary keyword | primary-keyword check against banned-phrases list | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | head-term keyword collision with posts.ts | grep primary keyword against posts.ts titles/slugs | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | draft image names referenced photos that did not exist | ls frontend/public/founder/ before finalizing | **RESOLVED in batch_10**
- 2026-04-17 | batch_7 | hero image reuse across hunger cluster | for next hunger-category post, select different hero | **RESOLVED in batch_10**
- 2026-04-17 | batch_8 | hero/inline cross-role reuse within batch | check both hero and inline slots at pre-flight | **RESOLVED in batch_10** (3 clean batches: 10, 11, 12). REGRESSION in batch_13. Re-confirmation: batch_14 = 1st clean, batch_15 = 2nd clean — **2-clean-consecutive-batch threshold MET**. **RE-RESOLVED at batch_15 close.** All 10 hero+inline paths in batch 15 are distinct files (start, body-composition-proof, sleep-reflective-window-20241217, patience-middle-checkin, mirror-middle-checkin / consistency-editorial, scale-proof, progress-update-hanok, weighin-middle-progress, cheat-day-founder).
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch | pick unique inline frames per post | **RESOLVED in batch_12** (3 consecutive clean batches: 10, 11, 12; cross-batch soft flag on water-weight-proof cleared in batch 12 — no inline reuse)
- 2026-04-17 | batch_8 | hero/topic semantic mismatch via cover taxonomy | verify hero matches cover_mapping lane for post's category | **RESOLVED in batch_13** (3 consecutive clean batches: 11, 12, 13; soft lane-bridges on batch 11 draft 4 and batch 13 draft 2 acknowledged via hero alt framing under reuse pressure — defensible under 3-clean rubric)
- 2026-04-19 | post_50_audit | Q&A-format posts drop founder-I and substitute mechanism numbers for sensory imagery, dragging Reader Address and Imagery Density ~2 points below anchor (drift delta -1.08, just past §10 -1.0 threshold) | every Q&A post must include at least one founder-anchored Q (first-person observation, not prescription) and at least one concrete sensory/metaphorical line replacing a bullet-list mechanism; if the Q&A would otherwise contain zero "I", reframe one Q as "Q: What did this look like for me?" | **RESOLVED at batch_15 close** — 5th consecutive clean cycle (drafts 54, 58, 64, 69, 75) honored both halves of the corrective. Batch 15 draft 75 (`my-scale-wont-move-but-my-jeans-fit-looser`) included a founder-anchored "Q: What did this look like for me?" with the five-month-cut / 2 cm waist / belt-new-hole / scale-moved-0.3 kg anecdote, plus multiple concrete sensory lines including "The scale is a summary paragraph. Your clothes are sentences." and "Waist tape is the earliest honest instrument most bodies have." Independent corroboration: post-75 voice_audit_75 sampled `do-i-actually-have-to-meal-prep-to-lose-weight` (post 64) and scored Reader Address 8.5 + Imagery Density 8.5 — both ~2 points above the audit_50 Q&A floor. Resolution criterion ("eligible for RESOLVED at batch 15 close if batch 15 Q&A stays clean (5th consecutive cycle)") is met.

## Batch Log

| Batch | Drafts | Verdicts | Ported | Closed |
|-------|--------|----------|--------|--------|
| 1–5   | posts 1–26 / 19 in posts.ts | retroactive | partial | partial |
| 6     | posts 27–31 | 2 pass, 3 revise | yes | yes |
| 7     | posts 32–36 | 3 pass, 2 revise + 1 Class 4 signed off | yes | yes |
| 8     | posts 37–41 | 1 pass, 4 revise + 1 Class 4 stripped | yes | yes |
| 9     | posts 42–46 | 2 pass, 3 revise + 1 Class 4 stripped | yes | yes |
| 10    | posts 47–51 | 2 pass, 3 revise | yes | yes |
| 11    | posts 52–56 | 4 pass, 1 revise | yes | yes |
| 12    | posts 57–61 | 4 pass, 1 revise (incl. Progress Update #4 milestone) | yes | yes |
| 13    | posts 62–66 | 3 pass, 2 revise (claim_class + 1 inline swap) | yes | yes |
| 14    | posts 67–71 | 4 pass, 1 revise (incl. Tier A slot 1: sodium); pre-flight checklist 80% effective | yes | yes |
| 15    | posts 72–76 | **5 pass, 0 revise** (first all-pass batch since batch 11; incl. Tier A slot 2: lower-body); pre-flight checklist **100% (5/5)**; Tier A slot 73 executed clean with **Imagery Density 8.5** (above voice_audit_75 watch threshold of 8.0) | yes | yes |

## Drift Compliance Trend

| Batch | Rules Tracked | Rules Clean | New Resolutions |
|-------|---------------|-------------|-----------------|
| 6 | 6 | 0 | — |
| 7 | 6 | 4 | — |
| 8 | 7 | 4 | — |
| 9 | 9 | 6 | rules 1, 3, 4 RESOLVED |
| 10 | 9 | 7 | rules 6, 7, 8 RESOLVED |
| 11 | 10 | 8 | rule 10 (post-50 Q&A correction) ADDED + honored on first batch; rule 9 had 1st clean batch (2 more needed to resolve) |
| 12 | 10 | 9 | rule 5 RESOLVED (3 consecutive clean); rule 9 = 2nd clean batch (1 more to resolve); rule 10 = 2 consecutive clean cycles |
| 13 | 10 | 8 | rule 9 RESOLVED (3rd consecutive clean); rule 10 = 3 cycles (continues to post-75 audit); rule 8 REGRESSED 1 occurrence (caught at revise, fixed); rule 2 widened to 2/5 |
| 14 | 10 | 9 | rule 2 narrowed 2/5 → 1/5 (pre-flight checklist effective at 80%); rule 8 re-confirming (1st clean batch); rule 10 = 4 cycles; first Tier A slot executed clean |
| 15 | 10 | **10** | **first batch where all 10 tracked rules are clean simultaneously**; rule 2 hits 0/5 (100% self-bump rate, 1st clean batch toward full re-resolution); rule 8 = 2nd clean batch → **RE-RESOLVED**; rule 10 = 5th consecutive clean cycle → **RESOLVED**; pre-flight checklist 100% effective; Tier A slot 73 imagery-density 8.5 narrows the voice_audit_75 watch (1 of 2 above threshold) |

1 rule in active observation:
- Rule 2 (claim_class) — narrowed to 0/5 in batch 15 (100% self-bump rate). Batch 16 target: hold 5/5 for full re-resolution per "0/5 holds for 2 consecutive batches" criterion.

## Archive

_(populated at post 50 and post 100 compressions)_
