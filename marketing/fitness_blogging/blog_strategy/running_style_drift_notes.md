# Running Style Drift Notes

Updated by writer after every reviewer cycle.

## Format
`date | batch# | recurring_issue | correction_direction | resolved_batch#`

## Active

- 2026-04-17 | batch_6 | internal-link slugs referenced non-ported draft filenames instead of slugs that actually exist in posts.ts | internal link target MUST be a slug already present in posts.ts; grep posts.ts for `slug: '` before referencing; draft-folder filenames do NOT count as real internal-link targets | _open_
- 2026-04-17 | batch_6 | claim_class under-calibrated when post contains physiology or demographic claims | when body copy mentions hormones, fat distribution, metabolism, demographic patterns → Class 3 at minimum; physiology-heavy or medical-adjacent → Class 4 | _open_
- 2026-04-17 | batch_6 | banned-phrase family ("journey") drifted into a primary keyword | primary-keyword check against banned-phrases list in style_guide.md before finalizing front matter | _open_
- 2026-04-17 | batch_6 | head-term keyword collision with an already-ported owned-site post | grep primary keyword against posts.ts titles and slugs before finalizing | _open_
- 2026-04-17 | batch_6 | inline image reused across multiple posts inside the same batch (minor flow issue) | pick unique inline frames per post where possible; acceptable for hero image dedup but inline should vary | _open_
- 2026-04-17 | batch_6 | draft front-matter image names referenced photos that did not actually exist in frontend/public/founder | always ls frontend/public/founder first; only reference files that exist; if new image needed, flag as port-time blocker or pick from existing pool | _open_

## Format Migration Notes (not drift)
- Batch 6 is the first batch using the new blueprint front matter (SEO Title, Meta Description, Primary Keyword, Secondary Keywords, Category, Format, Claim Class, Slug, Suggested Internal Links, Hero Image, Hero Alt, Inline Image Plan). Reviewer confirmed this is format progress, not voice drift. Earlier 26 drafts use older scaffold; can be retro-ported if needed at 50-post checkpoint.

## Batch Log

| Batch | Drafts | Verdicts | Ported | Closed |
|-------|--------|----------|--------|--------|
| 1–5   | posts 1–26 (drafts) / 19 in posts.ts | retroactive | partial (19/26) | partial |
| 6     | posts 27–31 | 2 pass, 3 revise, 0 rewrite → all approved | yes (5/5 in posts.ts) | yes |

## Archive

_(populated at post 50 and post 100 compressions)_
