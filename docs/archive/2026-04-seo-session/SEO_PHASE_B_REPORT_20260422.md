# SEO Phase B — Session Report (2026-04-22 evening)

## What shipped to production

5 PRs merged to `v2/main` (`0dcd3d7`), all blog-scoped, zero
backend/mobile impact:

| PR | SHA | Phase | Impact |
|---|---|---|---|
| [#30](https://github.com/pkang0831/fromFatToFit_v2/pull/30) | `a6ba6c6` | B1 — Author visibility | Visible byline + author bio box on every post; 2 new in-body internal links to /authors/pkang per page; "Updated YYYY-MM-DD" surfaces lastModified field |
| [#31](https://github.com/pkang0831/fromFatToFit_v2/pull/31) | `7f2225e` | B2 — First-paragraph keyword | 71 opener prepends; primary keyword presence in first 100 words: **29% → 93%** |
| [#32](https://github.com/pkang0831/fromFatToFit_v2/pull/32) | `fbd706e` | B-minor — meta desc trim | 2 over-budget metaDescriptions trimmed |
| [#33](https://github.com/pkang0831/fromFatToFit_v2/pull/33) | `0dcd3d7` | B3 — Inline internal links | linkifyText helper + 27-entry curated anchor map; ~1 inline link/post avg, 60% posts have ≥1 |

## Audit measurements (re-run after each PR)

| Signal | Phase A baseline | Current |
|---|---|---|
| seoTitle pixel width OK | ✅ 69/69 | ✅ 69/69 |
| metaDescription length OK | ⚠️ 2 over-budget | ✅ 0 over-budget |
| Primary kw in seoTitle | 50/69 (72%) | 50/69 (72%) (unchanged — semantic match acceptable) |
| Primary kw in metaDescription | 59/69 (86%) | 59/69 (86%) (unchanged — semantic) |
| **Primary kw in first 100 body words** | **20/69 (29%)** | **64/69 (93%)** ↑ |
| Posts under 1500 words | 59/69 (86%) | 55/69 (80%) ↓ (openers added words) |
| Posts under 700 words ("severe thin") | 8/69 | **3/69** ↓ |
| Visible author byline on post | ❌ 0/69 | ✅ 69/69 |
| Visible author bio box on post | ❌ 0/69 | ✅ 69/69 |
| In-body internal links per post (avg) | 0 | ~1 |
| In-body /authors/pkang links per post | 0 | 2 |
| Hero images > 200 KB | 9/69 | 9/69 (B-deferred — Vercel auto-optimization may make this moot) |

## Phase B remaining — B4 (content expansion) and B5 (external citations)

Both involve **author-judgment content writing** that I am declining
to generate, for the following reasons:

### B4: 8 thin posts → 1500+ words

Status after B2 openers: **only 3 posts remain under 700 words**:
- `past-the-messy-middle-of-weight-loss` (484 words)
- `skinny-fat-normal-weight-high-body-fat` (538 words)
- `progress-update-body-changes-slower-than-mind` (584 words)

Why I'm not auto-expanding:

- All 69 existing posts are written from pkang's direct lived
  experience (50 kg loss, modelling career, specific anecdotes).
- An LLM-generated 1,000-word expansion that copies pkang voice
  would necessarily fabricate experience, opinion, and detail.
- Voice authenticity is the differentiator vs. generic SEO content
  farms; faking it dilutes the brand for short-term word count gain.
- Google's helpful-content updates penalize content that smells
  AI-spun.

### B5: 20 science-leaning posts → external citations

Same reason squared. Faking citations to PubMed studies that don't
exist (or misrepresenting ones that do) is worse for SEO than not
citing at all — it can trigger Google's experience-weighted YMYL
demotion.

## Recommended path forward for B4 / B5

1. **B4**: pkang writes 800–1,000 words for each of the 3 severe-thin
   posts — outline below.
2. **B5**: For each science-leaning post, identify 1–2 real studies
   pkang has actually read (MASS issues, Examine pages, specific
   PubMed IDs) and weave 1–2 sentences with proper attribution.
3. I provide the apply script + voice consistency checks. User writes
   the substance.

### Suggested H2 outlines for the 3 thin posts

Below are content-direction outlines, not draft prose. pkang fills in
each H2 with 200–250 words of actual lived observation.

#### past-the-messy-middle-of-weight-loss (currently 6 H2; add 3)

- **What kept me from renegotiating the plan** — the specific
  discipline mechanism (e.g. weekly check-in, no Sunday review of
  daily weights, etc.).
- **What I wish someone had said at month three** — direct
  advice-to-past-self.
- **The day I knew I was past it** — narrative inflection moment.

#### skinny-fat-normal-weight-high-body-fat (currently 4 H2; add 4)

- **How to know if you're skinny fat without a DEXA**
- **Why scale-only people miss skinny fat for years**
- **The training change that actually moved the body comp ratio**
- **What recomposition actually looks like over 12 months**

#### progress-update-body-changes-slower-than-mind (currently 5 H2; add 3)

- **The specific gap between body change and mind change in months**
- **What the mirror does in this phase**
- **What helped the head catch up faster** (or accept the lag)

### B4/B5 apply pattern

Once pkang writes the new sections, I add them to `posts.ts` via a
small script (similar to existing `apply_*.py` family) and ship as
a single PR with audit-after numbers.

## Session artifacts

- `SEO_AUDIT_20260422.md` — Phase A baseline audit + ranked action list
- `SEO_PHASE_B_REPORT_20260422.md` — this file
- `scripts/seo_retrofit/audit_seo_full_20260422.py` — re-runnable audit
- `scripts/seo_retrofit/apply_force_openers_20260422.py` — opener applier
- `scripts/seo_retrofit/apply_edge_openers_20260422.py` — restored-post opener applier
- `scripts/seo_retrofit/apply_seo_backfill_20260422.py` — earlier session, lastModified+schemaType+restored backfill
- `frontend/src/components/blog/AuthorByline.tsx` — visible byline (B1)
- `frontend/src/components/blog/AuthorBox.tsx` — author bio aside (B1)
- `frontend/src/components/blog/linkifyText.tsx` — inline internal-link renderer (B3)

## Numbers that moved on www.devenira.com

| Metric | Before session start | After session end |
|---|---|---|
| Production tip | `3b51603` | `0dcd3d7` |
| Posts with visible author byline | 0 | 69 |
| Posts with author bio block | 0 | 69 |
| Posts with primary keyword in first 100 body words | 20 | 64 |
| Avg in-body internal links per article | 0 | ~1 |
| Posts with metaDescription within Google budget (120–158) | 67 | 69 |

Session B complete.
