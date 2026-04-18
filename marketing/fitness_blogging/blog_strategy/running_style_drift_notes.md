# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology, demographic, or named-hormone claims | physiology/demographic → Class 3 min; any of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4} named → Class 4; writer must noun-scan every draft for these tokens before submit | _open; batch_7 miscalled hunger, batch_8 miscalled sleep, batch_9 miscalled rebound (insulin). Physiology-numbers catching is now reliable; hormone-name scanning is the remaining gap._
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch | pick unique inline frames per post; check not just inline-vs-inline but hero-vs-inline | _open; violated batch_7, batch_8 (cross-role), batch_9 (inline-inline between drafts 3 and 5)_
- 2026-04-17 | batch_6 | draft front-matter image names referenced photos that did not exist | always ls frontend/public/founder/ first; only reference files that exist | _clean in batch_9 (pre-flight validation worked), needs one more clean batch to resolve_
- 2026-04-17 | batch_7 | hero image reuse across hunger cluster | for next hunger-category post, select different hero | _clean in batch_8 (no hunger post), clean in batch_9 (no hunger post) → pending one more clean batch_
- 2026-04-17 | batch_8 | hero/inline cross-role reuse within batch | check both hero and inline slots across all 5 drafts at pre-flight | _clean in batch_9_
- 2026-04-17 | batch_8 | hero/topic semantic mismatch via cover taxonomy | verify hero matches the cover_mapping lane for the post's category, not just "fits generically" | _open; batch_9 regressed on same asset (water-weight-proof on food-structure post), same as batch_8. Writer must explicitly look up category → lane → asset before hero selection._

## Resolved (3 consecutive clean batches)

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames | internal link target MUST be a slug already present in posts.ts | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | banned-phrase family ("journey") in primary keyword | primary-keyword check against banned-phrases list | **RESOLVED in batch_9**
- 2026-04-17 | batch_6 | head-term keyword collision with posts.ts | grep primary keyword against posts.ts titles/slugs | **RESOLVED in batch_9**

## Batch Log

| Batch | Drafts | Verdicts | Ported | Closed |
|-------|--------|----------|--------|--------|
| 1–5   | posts 1–26 / 19 in posts.ts | retroactive | partial (19/26) | partial |
| 6     | posts 27–31 | 2 pass, 3 revise, 0 rewrite | yes | yes |
| 7     | posts 32–36 | 3 pass, 2 revise, 0 rewrite + 1 Class 4 signed off | yes | yes |
| 8     | posts 37–41 | 1 pass, 4 revise, 0 rewrite + 1 Class 4 stripped | yes | yes |
| 9     | posts 42–46 | 2 pass, 3 revise, 0 rewrite + 1 Class 4 stripped | yes | yes |

## Drift Compliance Trend

| Batch | Rules Tracked | Rules Clean | Ratio | New Resolutions |
|-------|---------------|-------------|-------|-----------------|
| 6 | 6 | 0 (pre-revise) | 0/6 | — |
| 7 | 6 | 4 | 4/6 | — |
| 8 | 7 | 4 | 4/7 | — |
| 9 | 9 | 6 | 6/9 | rules 1, 3, 4 RESOLVED |

## Archive

_(populated at post 50 and post 100 compressions)_
