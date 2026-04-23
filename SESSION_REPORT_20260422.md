# Blog SEO Rollout — Session Report (2026-04-22)

## TL;DR

What started as "push blog overlay to production" became a full SEO
rollout across **5 PRs merged to `v2/main`**, all blog-scoped with
zero backend/mobile impact. Production (`www.devenira.com`) now has:

- **69 blog posts** live (was 69 with old slugs; now on SEO-optimized
  slugs with full metadata)
- **100% SEO field coverage** across all 69 posts
- **64 old URLs** 308-redirect to new keyword-rich slugs
- **All hero images webp** (LCP win over mixed jpg/webp)
- **87 sitemap URLs** including 10 topic pillar pages + /authors/pkang
- **Full JSON-LD** (Article + BreadcrumbList + Organization + Person +
  WebPage; FAQ on 54 posts; HowTo on 13 posts)

## PRs shipped

| PR | Commit | Scope |
|---|---|---|
| [#25](https://github.com/pkang0831/fromFatToFit_v2/pull/25) | `2c8cc8d` | Consolidate blog overlay: +5 posts, hero webp migration, 26 SEO retrofit scripts, 97 strategy docs, new blog routes & components (165 files) |
| [#26](https://github.com/pkang0831/fromFatToFit_v2/pull/26) | `61ecb57` | Wire blog slug redirects into next.config.js (1 file, fixes 64 OLD URL 404s) |
| [#27](https://github.com/pkang0831/fromFatToFit_v2/pull/27) | `3bc0a56` | SEO backfill: `lastModified` on all 69, `schemaType` on 15, full metadata for 5 restored posts |
| [#28](https://github.com/pkang0831/fromFatToFit_v2/pull/28) | `ced7177` | Swap 5 remaining jpg hero images to webp (1 file) |
| [#29](https://github.com/pkang0831/fromFatToFit_v2/pull/29) | `3b51603` | Add /authors/pkang page + include author & topic pages in sitemap |

## Discovered-and-fixed mid-session

- **Detached HEAD / 935 staged deletions** — working tree was a manual
  merge-in-progress. Resolved by resetting to `v2/main@8090afb` and
  selectively staging blog paths only.
- **User belief "74 posts live"** was off — my earlier grep counted
  `posts + cluster slugs`. Real post count: 64 (after overlay) vs 69
  (on v2/main). This gap led to the discovery that 5 posts were
  accidentally dropped in the overlay.
- **5 restored posts missing full SEO metadata** — came from v2/main
  with old schema. Backfilled with content-inferred `seoTitle`,
  `metaDescription`, `keywords`, `cluster`, `schemaType`.
- **64 OLD URLs returned 404 post-PR #25** — `redirects.js` existed
  but wasn't wired into `next.config.js`. Fixed in PR #26.
- **Topic pages and /authors/pkang missing from sitemap** — fixed in
  PR #29 along with author page.

## Final state on production

### SEO field coverage (69 posts)

| Field | Coverage |
|---|---|
| seoTitle | 69/69 |
| metaDescription | 69/69 |
| keywords | 69/69 |
| cluster | 69/69 |
| schemaType | 69/69 (15 article, 41 faq, 13 howto) |
| lastModified | 69/69 |
| answerBox (featured snippet) | 54/69 |
| faqItems / faq sections | 54/69 |
| howToSteps | 13/13 how-to posts |

### URL routes (production, www.devenira.com)

| Route | Status |
|---|---|
| `/blog` | HTTP 200, 69 posts rendered |
| `/blog/[new-slug]` | HTTP 200 for all 69 |
| `/blog/[old-slug]` | HTTP 308 → new slug (64 redirects) |
| `/blog/feed.xml` | HTTP 200, 50 latest items (cap intentional) |
| `/blog/topic/[cluster]` | HTTP 200 for all 10 clusters |
| `/authors/pkang` | HTTP 200 |
| `/sitemap.xml` | HTTP 200, 87 URLs |
| `/robots.txt` | HTTP 200, allows `/blog/`, disallows app routes |

### Backend/mobile impact

**Zero.** Verified via `git diff-tree` on each merge commit — no path
under `backend/`, `mobile/`, `tests/`, `qa/`, `.github/`,
`playwright-report/`, `frontend/src/app/(dashboard)/`,
`frontend/src/components/landing/`, or `marketing/devenira_prelaunch/`
was touched.

## What the user still needs to do (browser / external)

These are NOT automatable from the repo and remain open:

### High priority

1. **Set up Google Search Console**
   - Verify domain `devenira.com`
   - Submit sitemap: `https://devenira.com/sitemap.xml`
   - Enables keyword impression/click tracking, indexing diagnostics,
     FAQPage/HowTo rich-result validation.

2. **Set up Bing Webmaster Tools**
   - Import site from GSC after GSC verified (saves re-verification)
   - Bing drives ~5-10% of English search traffic (Duckduckgo too).

### Medium priority

3. **Medium wave_01_01 canonical fix** (60 seconds, see
   `DECISIONS_REQUIRED.md §1`)
   - The first Medium post's canonical still points at `devenira.com`
     which has DR 0. Medium's DR ~95. Clearing canonical on Medium
     keeps link equity where it can rank.

### Low priority

4. **Publish Medium wave_01_02 (founder story)** — fully prepped in
   `marketing/.../wave_01_02_founder_story_medium_manual_publish_package.md`
   but deferred per user instruction this session.

5. **HARO / reddit reputation building** — per
   `DECISIONS_REQUIRED.md §6`, deferred per user focus on blog this
   session.

## Artifacts (this session)

- `SESSION_PLAN.md` — source-of-truth plan with full progress log
- `SESSION_STATUS_20260422.md` — mid-session discovery + pause summary
- `SESSION_REPORT_20260422.md` — this file
- `~/ff_merge_backup_20260422.tar.gz` — 20GB working-tree backup (can
  be deleted once confident the merge is durable)
- `scripts/seo_retrofit/apply_seo_backfill_20260422.py` — one-shot
  script that added lastModified + schemaType + 5-restored metadata;
  idempotent, safe to re-run.

## Branches on `v2` remote

All 5 feature branches merged. They can be deleted via GitHub UI or
`git push v2 --delete <branch>`:

- `blog/seo-rollout-20260422`
- `blog/wire-redirects-20260422`
- `blog/seo-backfill-20260422`
- `blog/swap-jpg-heroes-20260422`
- `blog/authors-sitemap-20260422`

## Numbers that changed

| Metric | Before | After |
|---|---|---|
| Production branch tip | `8090afb` | `3b51603` |
| Blog posts live | 69 | 69 |
| Hero images .webp ratio | ? (mixed) | 69/69 |
| Old-slug URLs that 404 | 64 | 0 (all 308 redirect) |
| Sitemap URL count | 76 | 87 |
| Post `lastModified` coverage | 0/69 | 69/69 |
| Post `schemaType` coverage | 54/69 | 69/69 |
| Posts with complete SEO metadata | 64/69 | 69/69 |

Session complete.
