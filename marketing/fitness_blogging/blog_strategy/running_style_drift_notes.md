# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames instead of slugs that actually exist in posts.ts | internal link target MUST be a slug already present in posts.ts; grep posts.ts for slug field before referencing; draft-folder filenames do NOT count as real internal-link targets | _clean in batch_7, needs one more clean batch to resolve_
- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology or demographic claims | when body copy mentions hormones, fat distribution, metabolism, demographic patterns → Class 3 at minimum; named-hormone / physiology-heavy content → Class 4 | _open; batch_7 draft 34 under-called 3 → 4 (human signed off at Class 4)_
- 2026-04-17 | batch_6 | banned-phrase family ("journey") drifted into a primary keyword | primary-keyword check against banned-phrases list in style_guide.md before finalizing front matter | _clean in batch_7, needs one more clean batch to resolve_
- 2026-04-17 | batch_6 | head-term keyword collision with an already-ported owned-site post | grep primary keyword against posts.ts titles and slugs before finalizing | _clean in batch_7, needs one more clean batch to resolve_
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch (minor flow issue) | pick unique inline frames per post where possible | _open; batch_7 had one violation (patience-middle-checkin on drafts 2 and 5, corrected at revise stage)_
- 2026-04-17 | batch_6 | draft front-matter image names referenced photos that did not actually exist in frontend/public/founder | always ls frontend/public/founder first; only reference files that exist | _clean in batch_7, needs one more clean batch to resolve_

## New in batch_7

- 2026-04-17 | batch_7 | hero image reuse across the hunger cluster now on its third post (`hunger-editorial-20260106.jpg`) | for the next hunger-category post, select a different hero and note it against cover_mapping; consider adding a new hunger-lane asset at post 30 photo checkpoint | _open_

## Format Migration Notes (not drift)
- Batch 6 was the first batch using the new blueprint front matter. Batch 7 continues cleanly.

## Batch Log

| Batch | Drafts | Verdicts | Ported | Closed |
|-------|--------|----------|--------|--------|
| 1–5   | posts 1–26 (drafts) / 19 in posts.ts | retroactive | partial (19/26) | partial |
| 6     | posts 27–31 | 2 pass, 3 revise, 0 rewrite | yes (5/5) | yes |
| 7     | posts 32–36 | 3 pass, 2 revise, 0 rewrite + 1 Class 4 signed off | yes (5/5) | yes |

## Archive

_(populated at post 50 and post 100 compressions)_
