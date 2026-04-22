# SEO Optimization Rules

Governs SEO title, meta description, and tag selection for all blog posts across:

- Medium publish packages (`marketing/fitness_blogging/blog_strategy/medium_launch/*.md`)
- Owned-site posts (`frontend/src/content/blog/posts.ts`)

Introduced: 2026-04-21. Retrofit trigger: first SEO audit found all 67 Medium packages had `SEO Title == Title` (verbatim copy) and `posts.ts` `BlogPost` interface was missing `seoTitle` / `metaDescription` / `keywords` fields entirely. Batch-verdict `primary_keyword` intelligence was not propagated into any shipped surface.

This file is to SEO what `writer_pre_flight_class_checklist.md` is to claim class. It defines the corrective mechanism.

---

## Core Principle — Two Titles, Two Jobs

Every post has **two distinct titles that must not be the same string**.

### Display Title (the editorial headline)
- **Role**: voice, brand, emotional hook, scroll-stopping
- **Length**: unlimited (current average is 60–80 chars; the program's signature)
- **Surface**: H1 on owned site, headline on Medium, link text in share cards
- **Optimizer for**: click-through on feed / social
- **Current state**: healthy (anchor-set consistent, voice recognizable)

### SEO Title (the search snippet)
- **Role**: keyword front-loading, search intent match, snippet-safe length
- **Length**: **≤ 60 characters** (hard ceiling — Google truncates around 60)
- **Surface**: HTML `<title>` tag, Medium SEO title field, Google SERP
- **Optimizer for**: first-page search ranking + click-through on SERP
- **Current state**: **broken** (verbatim copies of display title across all 67 posts as of 2026-04-21)

**Rule**: `seoTitle` MUST differ from `title`. If they are identical the post is not considered SEO-complete.

---

## SEO Title Formula

### Priority stack (apply first matching)

| Priority | Pattern | Example (from wave_01_01) |
|----------|---------|---------------------------|
| 1 | `How to [verb] [target] (without [pain])` | `How to Stick With a Diet Long-Term (Without Starting Over)` |
| 2 | `Why [observation] [during/when X]` | `Why the Mirror Stops Showing Diet Progress (Even When You're Losing)` |
| 3 | `What [to do/happens] [context]` | `What to Do After a Diet Slip (Before It Becomes a Bad Week)` |
| 4 | `[Noun phrase with primary keyword] + colon + value prop` | `Weigh-In Anxiety: Why One Bad Scale Day Is Not a Verdict` |

Informational voice (question / how-to / what-happens) is preferred. Google's helpful-content and People-Also-Ask boxes both reward this pattern.

### Hard rules

1. **Length ≤ 60 chars** (test before ship)
2. **Primary keyword in the first 40 chars** (front-loading — SERPs truncate tails)
3. **No brand in SEO title for Medium** (Medium adds the publication tag automatically; brand burns chars)
4. **For owned site**: brand appended by Next.js metadata — so SEO title should NOT include "Devenira" or "| Devenira"
5. **No clickbait violation of voice**: the program is anti-hype. No "SHOCKING", "ONE WEIRD TRICK", "You Won't Believe". Informational curiosity is fine; tabloid language is not.
6. **Exactly one primary keyword per post** (from batch verdict `primary_keyword` field)

### Voice-safe lexicon

Allowed curiosity words: `how`, `why`, `what`, `when`, `before`, `after`, `actually`, `really`, `the truth about`, `stops`, `keeps`, `hidden`, `quiet`, `slow`, `normal`.

Banned (violates voice per `running_style_drift_notes.md`): `ultimate`, `best`, `top [N]`, `secret`, `shocking`, `crazy`, `insane`, `you won't believe`, `guaranteed`, `fast results`, `transform your body`, `life-changing`.

---

## Meta Description Formula

### Role separation (three description fields)

| Field | Where it lives | Length | Role |
|-------|---------------|--------|------|
| `metaDescription` | `<meta name="description">`, Google SERP snippet | ≤ 155 chars | Search CTR |
| `description` | On-page deck, feed card copy | 150–250 chars | On-site UX |
| `socialDescription` | OG / Twitter card | 100–200 chars | Social CTR |

Currently only the last two exist in `posts.ts`. Adding `metaDescription`.

### Formula

**Sentence 1** (≤ 80 chars) — Value claim with primary keyword
Example: `Most people quit dieting not because they're lazy, but because slow middle progress feels like failure.`

**Sentence 2** (≤ 75 chars, optional if sentence 1 is complete) — Pay-off promise
Example: `Here's why the quietest diet strategy is the one that actually holds.`

### Hard rules

1. **Length ≤ 155 chars** (Google typical snippet cut-off; 155 is the safe ceiling)
2. **Primary keyword in first 100 chars**
3. **No ellipses mid-sentence** (SERPs add their own ellipsis on truncation — adding one mid-text creates double)
4. **First letter capitalized; ends with period** (cleaner SERP rendering)
5. **No emoji** (Google strips from most SERPs; wastes chars even when kept)
6. **Not identical to subtitle / deck** (search and on-site have different jobs)

---

## Tag Formula (Medium, 5-tag ceiling)

Medium allows 5 tags. Use **3 broad + 2 niche** mix.

### Broad tag pool (use 3 of these per post)

The brand-relevant broad pool:
- `Weight Loss` (program's spine — use on nearly every post)
- `Dieting`
- `Nutrition`
- `Fitness`
- `Health`
- `Mental Health`
- `Mindset`
- `Habits`
- `Psychology`
- `Lifestyle`

### Niche tag pool (use 2 of these per post — MATCHED to primary keyword)

Program-specific lanes (maps to `§11` category lanes + primary keyword subtopic):

| Category lane | Niche tag candidates (pick 1–2 that fit) |
|---------------|------------------------------------------|
| Scale | `Weight Fluctuation`, `Scale Anxiety`, `Weight Loss Plateau`, `Body Composition` |
| Mirror / body image | `Body Image`, `Self Image`, `Body Dysmorphia`, `Progress Photos` |
| Food structure | `Meal Planning`, `Meal Prep`, `Macros`, `Calorie Counting`, `Protein` |
| Cheat / binge | `Binge Eating`, `Cheat Day`, `Emotional Eating`, `Food Psychology` |
| Exercise / recovery | `Strength Training`, `Cardio`, `Recovery`, `Exercise Science`, `Overtraining` |
| Appetite / hunger | `Appetite`, `Hunger`, `Intuitive Eating`, `Cravings`, `Satiety` |
| Maintenance / long game | `Maintenance Phase`, `Long Game`, `Lifestyle Change`, `Sustainable Weight Loss` |
| Founder / progress | `Founder Story`, `Transformation`, `Personal Growth`, `Weight Loss Journey` |
| Body composition | `Body Recomposition`, `Muscle Gain`, `Fat Loss`, `Body Fat` |
| Plateau / consistency | `Plateau`, `Consistency`, `Motivation`, `Discipline` |

### Hard rules

1. **5 tags maximum** (Medium enforces)
2. **3 broad + 2 niche** — break this only if primary keyword is so specific that 2 niche tags are a stretch (then 2 broad + 3 niche)
3. **First tag is the highest-traffic match for primary keyword** (Medium weights left-most tag slightly heavier in its recommendation engine)
4. **No tag appears in > 80% of all posts** (prevents program from becoming monotonal in Medium recommendation; if `Weight Loss` already on 60 of 67, consider swapping to `Dieting` or `Health` for new posts)
5. **Niche tags rotate by topic lane** — do not reuse `Body Image` on every post; use `Self Image` / `Body Dysmorphia` / `Progress Photos` as the lane alternates

---

## Primary Keyword Pipeline

### Where it comes from

1. **Reviewer's batch verdict** — each draft has `primary_keyword: ...` field
2. **If missing or reviewer deferred** — run targeted web search (see Research Procedure below)
3. **For retroactive posts** (wave_catchup_*, wave_01/02 pre-blueprint) — extract from draft's subject matter using Research Procedure

### Where it must propagate

| Surface | Field |
|---------|-------|
| Medium package | SEO Title + Meta Description both use primary keyword |
| `posts.ts` | `seoTitle` + `metaDescription` both use primary keyword; first element of `keywords` array is primary |
| Batch verdict (already exists) | `primary_keyword: ...` front-matter-style field |

### Research procedure (for missing keywords)

For each candidate keyword:

1. Web search the exact phrase + "people also ask" + "search intent"
2. Verify at least one of:
   - Organic results are Healthline / WebMD / Psychology Today / MyFitnessPal / Reddit — indicates established query
   - "People also ask" box contains the phrase or a close variant
   - At least 3 blog / forum / community posts rank for it
3. Check head-term collision: primary keyword must NOT already be the primary_keyword of another approved post (reviewer tracks this per batch). Collision = downgrade to secondary keyword + pick fresh primary.
4. Prefer long-tail (3+ words) over head term (1–2 words) — lower competition, higher intent-match

### Pre-flight SEO keyword gate (mirror of claim_class gate)

Before marking a Medium package / `posts.ts` entry as "seo-ready":

- [ ] `seoTitle` exists, differs from `title`, ≤ 60 chars, contains primary keyword in first 40 chars
- [ ] `metaDescription` exists, differs from `description`, ≤ 155 chars, contains primary keyword in first 100 chars
- [ ] 5 tags chosen with 3 broad + 2 niche split, no banned-phrase tag
- [ ] `keywords` array has primary + 2–4 secondary (secondary pulled from PAA / related queries)
- [ ] No head-term collision with any other approved post
- [ ] Voice check: no banned phrases from `running_style_drift_notes.md`

---

## Schema Extensions

### `BlogPost` interface additions (`frontend/src/content/blog/posts.ts`)

```ts
export interface BlogPost {
  // ... existing fields ...

  // SEO per-post metadata (2026-04-21).
  seoTitle?: string;          // ≤ 60 chars; if omitted, falls back to title
  metaDescription?: string;   // ≤ 155 chars; if omitted, falls back to description
  keywords?: string[];        // primary + 2-4 secondary; used in <meta name="keywords">

  // Canonical flip (2026-04-21). When mediumUrl is set, the site's
  // canonical points to Medium so Medium (DR ~95) gets the ranking signal.
  mediumUrl?: string;

  // Topical cluster slug (matches CLUSTERS[slug]). Powers
  // cluster-aware related-posts, pillar pages, breadcrumbs.
  cluster?: string;

  // JSON-LD schema selection. Article is always emitted; this unlocks
  // secondary schema (FAQPage, HowTo) per post type.
  schemaType?: 'article' | 'faq' | 'howto';
  faqItems?: Array<{ question: string; answer: string }>;
  howToSteps?: Array<{ name: string; text: string }>;
}
```

All SEO/optional fields are optional to allow progressive migration.
Production `generateMetadata` applies fallback patterns so partially-
filled entries still render safely.

### New `BlogSection` types

- `answerBox` — featured-snippet-friendly direct-answer block for Q&A
  posts. Rendered as a highlighted `<h3>` + `<p>` pair under the
  relevant H2 so Google can pluck it into position 0.
- `faq` — FAQ accordion rendered as semantic `<details>/<summary>`
  elements; auto-harvested into FAQPage JSON-LD by `BlogStructuredData`.

---

## Site Architecture Surfaces (2026-04-21)

The following owned-site surfaces exist to build topical authority
independent of individual post rankings:

1. **Author page** (`/authors/pkang`) — E-E-A-T signal, Person JSON-LD
   anchor for every Article schema's author @id reference.
2. **Pillar pages** (`/blog/topic/[cluster]`) — 10 hub pages, one per
   cluster, aggregating all spokes in that cluster with a pillar-
   keyword-targeted title/description and a CollectionPage+ItemList
   JSON-LD payload. Sitemap priority 0.9 (higher than individual posts).
3. **Breadcrumb trails** — every blog post page now renders a
   cluster-aware breadcrumb: Blog › [Cluster Title] › [Post], backed
   by BreadcrumbList JSON-LD.
4. **Cluster-aware related posts** — `getRelatedBlogPosts()` prefers
   same-cluster posts, falling back to other posts only when the
   cluster pool is too small. Concentrates internal link equity within
   the topical cluster.
5. **301 redirect registry** (`src/content/blog/redirects.js`) — every
   slug change adds an entry, Next.js issues a 301 at
   `/blog/<old-slug>`. Link equity transfers cleanly.
6. **Sitemap** includes site pages + pillar pages + all blog posts.
   Pillar pages marked as `changeFrequency: 'weekly'` to encourage
   re-crawl.

### Medium package format additions

Every Medium package adds one line under existing `## SEO Title` field:

```markdown
## SEO Title
[≤ 60 chars, primary keyword front-loaded]

## Meta Description
[≤ 155 chars, primary keyword in first 100]

## Primary Keyword
[exact phrase for this post's ranking target]

## Secondary Keywords
- [2-4 PAA / related query phrases]
```

---

## Retrofit Priority

The audit on 2026-04-21 found 0 of 67 posts SEO-complete. Priority order:

| Priority | Group | Count | Rationale |
|----------|-------|-------|-----------|
| P0 | Medium wave_01 (first 6 being published now) | 6 | Immediate publish queue; biggest CTR upside |
| P1 | Medium wave_02 + wave_03 (30 posts) | 30 | Next 3 months' publish queue; fixable before publish |
| P2 | Medium wave_catchup + batch 14 packages (31 posts) | 31 | Later in queue + freshly closed batch |
| P3 | `posts.ts` retrofit (all 67 entries, in parallel with Medium retrofits) | 67 | Owned-site organic traffic; ongoing crawl benefit |

Each priority ships as a batch with founder sign-off (`진행해` pattern) before the next batch begins.

---

## Batch 15 Onwards (Forward-Going Rule)

Starting with batch 15 drafting:

1. Writer fills `seoTitle` + `metaDescription` + `keywords` at draft time (not after reviewer's pass)
2. Reviewer grades against pre-flight SEO keyword gate as a new rule 11 in the drift scorecard
3. Batch verdict front-matter per draft gains two fields:
   - `seo_title: ...`
   - `seo_complete: yes|no`
4. If `seo_complete: no`, draft enters revise cycle with SEO-only fix (no voice changes)

The reviewer agent spec (`reviewer_agent_spec.md`) gets a new Rule 11 section appended on first use. Drift scorecard gains row 11.

---

## Owned-Site Rendering Rules

`frontend/src/app/(blog)/blog/[slug]/page.tsx`'s `generateMetadata` emits:

```ts
const canonicalUrl = post.mediumUrl ?? `https://devenira.com/blog/${post.slug}`;
return {
  title: post.seoTitle ?? post.title,
  description: post.metaDescription ?? post.description,
  keywords: post.keywords,
  authors: [{ name: 'pkang', url: 'https://devenira.com/authors/pkang' }],
  alternates: { canonical: canonicalUrl },
  openGraph: {
    title: post.title,                      // share cards use display title (voice)
    description: post.socialDescription,    // social CTR, not search
    authors: ['pkang'],
    // ... rest unchanged
  },
  twitter: {
    title: post.title,
    description: post.socialDescription,
    creator: '@pkang',
    // ... rest unchanged
  },
};
```

Plus JSON-LD structured data is emitted via `<BlogStructuredData post={post} />`
(Article + BreadcrumbList always; FAQPage when `schemaType === 'faq'`;
HowTo when `schemaType === 'howto'`).

Rationale: **SEO title is for Google; social title is for humans scrolling a feed.** The two have different CTR drivers. Keep them separate.

---

## Canonical URL Strategy (2026-04-21 flip)

### Problem discovered in the first audit

All 64 Medium publish packages instructed the author to paste
`https://devenira.com/blog/[slug]` into Medium's canonical URL field. This
redirects all ranking signals from Medium (DR ~95) to devenira.com (DR ~0,
new domain, zero backlinks). Result: both pages fail to rank. Medium
won't rank because its canonical points elsewhere; the owned site can't
rank because the domain has no authority.

### New canonical strategy (binding from 2026-04-21)

**Medium is the canonical primary for every post.** Medium gets the Google
traffic; the owned site keeps the brand surface and internal-link hub.

Operationally:

1. **Medium packages** — `## Canonical URL` field now says "DO NOT set a
   canonical URL in Medium's story settings." This leaves the post
   self-canonical on Medium. Any import-from-URL workflow must have its
   auto-populated canonical cleared before publishing.

2. **Owned-site rendering** — `BlogPost.mediumUrl` holds the Medium
   article URL. When set, `generateMetadata` points `<link rel="canonical">`
   at that URL so search engines treat Medium as primary. When missing
   (drafts, pillars, never-published), canonical falls back to self.

3. **Writer workflow** — after publishing on Medium and getting a URL,
   populate `mediumUrl` in `posts.ts` for that slug. Update
   `wave_01_tracker.md` (and successor tracker files) with the Medium URL
   column filled in.

### Already-published posts that need manual correction

Any post already live on Medium with canonical pointing to devenira.com
must have its Medium story settings edited:

- Open the story on Medium
- Go to story settings (three dots) → "SEO settings"
- Clear the "Canonical URL" field
- Save

As of the flip:
- `wave_01_01_consistency_medium_manual_publish_package.md` (published) — requires this manual fix

Going-forward: the corrected `## Canonical URL` field in the package
tells the author not to set one.

### When the site's DR grows

Once the owned site accumulates real authority (DR 30+, hundreds of
indexed backlinks, consistent organic traffic), re-audit. At that point
a hybrid or site-primary canonical strategy may out-perform. Until then
Medium is primary, no exceptions.

---

## Maintenance

This file co-lives with `writer_pre_flight_class_checklist.md` and `image_pool_tightened_policy.md` as a corrective rule file. Update triggers:

- Tag pool expansion (add niche tags when new topic lane opens in §11)
- Banned lexicon additions (cross-reference `running_style_drift_notes.md`)
- Schema changes to `BlogPost` interface (update the schema section)
- New surface introduced (e.g. if we launch a separate Substack — add surface rules)

Last audit: 2026-04-21 (founding).
Next required audit: at approved-post 100 (program close-out) or on any new surface launch, whichever comes first.
