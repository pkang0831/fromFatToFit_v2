# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology claims or named hormones | physiology/demographic → Class 3 min; any of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4} named → Class 4 | _open; batch_14 narrowed to 1/5 (only draft 69 missed; drafts 67 and 70 self-bumped via new pre-flight checklist with trigger annotations E and F). **Corrective action effective** — pre-flight checklist (added 2026-04-19) catching 80% of triggers. Batch 15 target: 0/5 self-bump misses for first time. Hormone noun-scan stays clean. Expected resolution by batch 16 if 0/5 holds for 2 consecutive batches._
- 2026-04-19 | post_50_audit | Q&A-format posts drop founder-I and substitute mechanism numbers for sensory imagery, dragging Reader Address and Imagery Density ~2 points below anchor (drift delta -1.08, just past §10 -1.0 threshold) | every Q&A post must include at least one founder-anchored Q (first-person observation, not prescription) and at least one concrete sensory/metaphorical line replacing a bullet-list mechanism; if the Q&A would otherwise contain zero "I", reframe one Q as "Q: What did this look like for me?" | _open; honored across batch 11 (draft 54), batch 12 (draft 58), batch 13 (draft 64), batch 14 (draft 69). 4 consecutive clean cycles. Continues in observation through post-75 audit (after batch 15 closes).

## Resolved (3 consecutive clean batches)

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames | internal link target MUST be a slug already present in posts.ts | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | banned-phrase family in primary keyword | primary-keyword check against banned-phrases list | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | head-term keyword collision with posts.ts | grep primary keyword against posts.ts titles/slugs | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | draft image names referenced photos that did not exist | ls frontend/public/founder/ before finalizing | **RESOLVED in batch_10**
- 2026-04-17 | batch_7 | hero image reuse across hunger cluster | for next hunger-category post, select different hero | **RESOLVED in batch_10**
- 2026-04-17 | batch_8 | hero/inline cross-role reuse within batch | check both hero and inline slots at pre-flight | **RESOLVED in batch_10** (3 clean batches: 10, 11, 12). REGRESSION in batch_13. Re-confirmation in progress: batch_14 clean (1st of 2 consecutive needed). Batch_15 must also be clean to re-resolve.
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch | pick unique inline frames per post | **RESOLVED in batch_12** (3 consecutive clean batches: 10, 11, 12; cross-batch soft flag on water-weight-proof cleared in batch 12 — no inline reuse)
- 2026-04-17 | batch_8 | hero/topic semantic mismatch via cover taxonomy | verify hero matches cover_mapping lane for post's category | **RESOLVED in batch_13** (3 consecutive clean batches: 11, 12, 13; soft lane-bridges on batch 11 draft 4 and batch 13 draft 2 acknowledged via hero alt framing under reuse pressure — defensible under 3-clean rubric)

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

2 rules in active observation + 1 in re-confirmation:
- Rule 2 (claim_class) — narrowed via pre-flight checklist, target 0/5 in batch 15 to start trending toward resolution.
- Rule 8 (hero/inline cross-role within batch) — RE-OPENED, 1 of 2 clean batches achieved; batch 15 must also be clean.
- Rule 10 (Q&A correction) — 4 cycles clean; held in observation through post-75 audit (after batch 15 closes).

## Archive

_(populated at post 50 and post 100 compressions)_
