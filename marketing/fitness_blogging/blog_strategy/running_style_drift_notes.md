# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames | internal link target MUST be a slug already present in posts.ts; grep posts.ts for slug field before referencing | _clean in batch_7, clean in batch_8 → 2 consecutive clean batches → RESOLVED pending batch_9 confirmation_
- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology or demographic claims | physiology/demographic → Class 3 min; named-hormone → Class 4 | _open; batch_8 under-called 3 drafts (37, 38, 40); writer must self-audit every draft for any number, hormone, demographic claim before submitting to reviewer_
- 2026-04-17 | batch_6 | banned-phrase family ("journey") drifted into a primary keyword | primary-keyword check against banned-phrases list before finalizing | _clean in batch_7, clean in batch_8 → RESOLVED pending batch_9 confirmation_
- 2026-04-17 | batch_6 | head-term keyword collision with an already-ported owned-site post | grep primary keyword against posts.ts titles and slugs before finalizing | _clean in batch_7, clean in batch_8 → RESOLVED pending batch_9 confirmation_
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch | pick unique inline frames per post | _open; batch_7 had 1 violation, batch_8 had 1 cross-role violation (water-weight-proof used as hero AND inline in different drafts)_
- 2026-04-17 | batch_6 | draft front-matter image names referenced photos that did not exist | always ls frontend/public/founder/ first; only reference files that exist | _open; batch_8 regressed: draft 39 inline referenced nonexistent kitchen-prep-composed-20250816.jpg. Writer must block on non-existent asset reference, not merely prefer real ones._
- 2026-04-17 | batch_7 | hero image reuse across hunger cluster on third post (hunger-editorial-20260106.jpg) | for next hunger-category post, select different hero | _clean in batch_8 (no hunger-lane post in batch)_

## New in batch_8

- 2026-04-17 | batch_8 | batch-internal HERO/INLINE cross-role reuse (one image used as hero in one draft and inline in another) | check not just inline-vs-inline but also hero-vs-inline across the batch; unique image role per batch where possible | _open_
- 2026-04-17 | batch_8 | hero image semantically mismatched to cover taxonomy (water-weight-proof used on a food-structure post) | at hero selection, verify the image matches the cover_mapping lane for that post is category, not just "fits generically" | _open_

## Format Migration Notes (not drift)
- Batch 6–8 all using blueprint front matter. Consistent.

## Batch Log

| Batch | Drafts | Verdicts | Ported | Closed |
|-------|--------|----------|--------|--------|
| 1–5   | posts 1–26 / 19 in posts.ts | retroactive | partial (19/26) | partial |
| 6     | posts 27–31 | 2 pass, 3 revise, 0 rewrite | yes (5/5) | yes |
| 7     | posts 32–36 | 3 pass, 2 revise, 0 rewrite + 1 Class 4 signed off | yes (5/5) | yes |
| 8     | posts 37–41 | 1 pass, 4 revise, 0 rewrite + 1 Class 4 downgraded (hormone names stripped to stay Class 3) | yes (5/5) | yes |

## Drift Compliance Trend

| Batch | Rules Tracked | Rules Clean | Ratio |
|-------|---------------|-------------|-------|
| 6 | 6 | 0 (pre-revise baseline) | 0/6 |
| 7 | 6 | 4 | 4/6 |
| 8 | 7 (rule 7 added) | 4 | 4/7 |

Writer trend: improving topical discipline (slug, banned phrase, head-term collision, hunger-lane rotation all clean for 2 batches), regression on image-file existence. Writer must add pre-submit check: `ls frontend/public/founder/ | grep <filename>` for every image path in front matter.

## Archive

_(populated at post 50 and post 100 compressions)_
