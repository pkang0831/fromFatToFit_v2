# SEO Session Handoff — 2026-04-21

This is the resume-point for SEO optimization work. Read this first in
the next session before starting anything.

## Session context

Founder directive: "도구 접근 다 줄꺼고, 모든 작업을 다해. seo 무조건
잘해야돼. 나 이거 홍보 제대로 해야한단 말야."

Founder decisions:

- **Canonical**: flip to Medium (Medium DR ~95, site DR ~0)
- **Keyword research tools**: none (web search only)
- **Slug changes**: all 64 posts in scope (max SEO, max work)

Total scope estimate: 40–50 hours. Built the technical foundation this
session; content work remains.

---

## What is DONE

### Infrastructure (frontend/src)

| File | Purpose |
|------|---------|
| `src/content/blog/posts.ts` | Added `seoTitle`, `metaDescription`, `keywords`, `mediumUrl`, `cluster`, `schemaType`, `faqItems`, `howToSteps` fields. Added `CLUSTERS` metadata (10 clusters). Added `getBlogPostsByCluster`, `getAllClusters`. Extended `BlogSection` with `answerBox` + `faq` types. Updated `getRelatedBlogPosts` to be cluster-aware. |
| `src/app/(blog)/blog/[slug]/page.tsx` | `generateMetadata` now canonical → mediumUrl ?? self. Added JSON-LD emit. Added cluster breadcrumb + "More in topic" link. |
| `src/app/(blog)/blog/topic/[cluster]/page.tsx` | **NEW** — pillar pages at `/blog/topic/[cluster]`. CollectionPage + ItemList + BreadcrumbList JSON-LD. |
| `src/app/authors/pkang/page.tsx` | **NEW** — E-E-A-T author page with Person JSON-LD and full post index. |
| `src/app/sitemap.ts` | Added author page + 10 pillar pages. |
| `src/components/blog/BlogStructuredData.tsx` | **NEW** — Article + BreadcrumbList always; FAQPage auto-harvested from sections; HowTo when schemaType===`howto`. |
| `src/components/blog/BlogArticleContent.tsx` | Added `answerBox` + `faq` rendering. |
| `src/content/blog/redirects.js` | **NEW** — 301 redirect registry (empty, awaiting slug renames). |
| `next.config.js` | Wired `buildBlogRedirects()` into `redirects()`. |

### Medium publish packages (64)

- Canonical URL field flipped from "set to devenira.com" to "DO NOT set
  canonical on Medium" (per `scripts/seo_retrofit/canonical_flip.py`)
- All packages have SEO Title, Meta Description, Primary Keyword,
  Secondary Keywords, optimized Medium Tags (from P0/P1/P2 retrofits)

### Strategy documents

- `seo_optimization_rules.md` — canonical binding rules, including the
  canonical-flip section (new) and site-architecture surfaces section (new)
- `publish_checklist.md` — includes canonical-flip instruction
- `reviewer_agent_spec.md` — Rule 11 SEO gate (active from batch 15)
- `seo_retrofit_P0_wave01.md`, `seo_retrofit_P1_wave02_wave03.md` — Retrofit logs
- `seo_title_pixel_audit.json` — pixel-width audit of all 138 titles
  (136 OK, 2 WARN, 0 FAIL) — informational snapshot

### Already-live posts requiring manual Medium edit

- `wave_01_01_consistency` (The Most Reliable Way to Succeed at
  Dieting...) — on Medium. Founder must edit story settings → SEO
  settings → clear the Canonical URL field.

---

## What is IN-PROGRESS (was running at session end)

### Subagent: keyword research for 64 posts

- Agent ID logged in parent session's todo trail
- Output target: `marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md`
- At end of session this file did not yet exist. The subagent is doing
  web SERP analysis for every post's current primary keyword and
  harvesting PAA queries.

**Next session: first action is to check if this file exists.** If yes,
read it and start applying. If no, check subagent status (resume with
agent ID) or re-kick a fresh research run.

---

## What remains (content work)

Ordered by founder ROI:

### 1. Apply keyword research (blocks everything else)

- Script: extend `scripts/seo_retrofit/apply_*.py` pattern to take
  research file as input, replace `primary_keyword` + `secondary_keywords`
  in Medium packages + `keywords[]` in posts.ts
- Estimate: 1 hour (scripted apply + review)

### 2. Slug redesign (64 posts)

- Input: keyword research file's "new primary keyword" per post
- Design new slugs: short (≤ 50 chars), keyword-rich, hyphenated
- Update `posts.ts` slug field for each entry
- Update Medium package canonical URL text (though we cleared those, the
  URL appears in the block for future reference)
- Register old→new redirects in `src/content/blog/redirects.js`
- Update `posts_30_to_71_schedule.md` + any other schedule refs
- Estimate: 2–3 hours

### 3. Meta description real rewrites

- Current state: most are light rewrites of subtitles; many miss
  numbers / specific promises / primary keyword in first 80 chars
- Rewrite to: sentence 1 = value claim + primary keyword, sentence 2 =
  payoff promise with number or specific
- Estimate: 1 hour

### 4. Medium first paragraph rewrites (64 posts, HIGHEST LEVERAGE)

- Google auto-extracts first ~155 chars as SERP snippet on Medium
- Current first paragraphs are editorial voice hooks — no keywords
- Rewrite opening 1-2 sentences to include primary keyword NATURALLY
  while preserving voice (hard — requires voice discipline)
- Estimate: 3–4 hours (most demanding content work)

### 5. Featured snippet direct answers (20+ Q&A posts)

- For posts like `am-i-actually-hungry-or-am-i-bored`,
  `do-i-actually-have-to-meal-prep-to-lose-weight`,
  `when-does-one-bad-meal-actually-become-a-slip`, etc.
- Add `answerBox` section near the top: H3 = primary query verbatim,
  P = 40–60 word direct answer
- Then 4–6 item `faq` section somewhere in the body
- Also set `schemaType: 'faq'` on those posts
- Estimate: 2 hours

### 6. Internal link anchor text rewrites

- Current posts.ts sections already contain links to other posts via
  slug references in paragraph text
- Audit each section's paragraphs; where a post-slug is referenced,
  rewrite the sentence so the anchor text is keyword-rich
- Estimate: 2 hours

### 7. H2 keyword optimization (selective)

- Current H2s are editorial ("The Middle Looked Ordinary")
- Only rewrite H2s where voice allows a keyword-richer alt
- Target only posts with realistic keyword targets (from research file)
- Estimate: 1–2 hours

### 8. OG image automation (low priority)

- Next.js `opengraph-image.tsx` convention for dynamic 1200x630 per
  post with title + author
- Current: uses heroImage — acceptable
- Estimate: 1 hour

---

## Known issues / watch items

1. **wave_catchup_014 title pixel width = 592px** (WARN, under 600px
   cap). "When the Workout Stops Being Punishment and Starts Being Care"
   may truncate on some SERPs. Rewrite candidate: "When the Workout
   Becomes Therapy, Not Punishment" (~49 chars / ~500px).

2. **10 cluster CLUSTERS vs 8 originally planned**: Split `food-structure`
   and `body-composition` out of founder-story/misc. Now:
   scale, mirror, appetite, binge, maintenance, plateau, exercise,
   founder-story, food-structure, body-composition.

3. **Medium wave_01_01 is live with OLD canonical → devenira.com**.
   Founder must manually edit on Medium.

4. **Schema.org FAQPage will only trigger when faqItems are added per
   post.** Component is ready; content isn't. See step 5 above.

5. **HowTo schema is ready** but no post currently uses it. Candidates:
   `do-i-actually-have-to-meal-prep-to-lose-weight` (has how-to steps
   implicitly), `how-do-i-eat-normally-at-social-events`,
   `how-do-i-stop-a-binge-from-becoming-a-binge-week`. If we add
   `howToSteps` to these, the HowTo schema auto-emits.

---

## Session-to-session checklist

Next session opens with:

- [ ] Read this file first
- [ ] Check `marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md`
- [ ] If keyword research exists: review + start applying (step 1 above)
- [ ] If not: decide to re-kick subagent or do manual research in smaller batches
- [ ] Confirm founder still wants full slug redesign (big commitment)
- [ ] Proceed through pending content work in ROI order
