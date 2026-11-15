# SESSION_PLAN — Blog SEO Rollout (2026-04-22)

This is the source-of-truth for this working session. We stick to it. If
something comes up that isn't here, we either defer it to a new session
or we consciously amend this file.

---

## Context

- **State at session start**: 74 blog posts live on `devenira.com/blog`. 1 post
  (founder story) published on Medium. RSS feed (`/blog/feed.xml`) already
  wired and working.
- **User constraint**: Email outreach is PAUSED. Focus is blog-only.
- **Blocker**: SEO visibility is zero until GSC + Bing are set up. Several
  field gaps in `posts.ts`. Deployment state unconfirmed.

---

## Guardrails (do NOT violate without explicit user approval)

1. **No email outreach**. Don't touch `outreach_emails_ready_to_send.md`.
2. **No Medium publishing actions** unless user explicitly asks. Medium
   wave_01_02 and beyond are deferred.
3. **No schema redesign** — work within existing `BlogPost` interface.
4. **No slug renames**. Slugs were just renamed; further changes would
   break the 301 redirect chain.
5. **No `mediumUrl` edits** — those are only set when something is
   actually published on Medium.
6. **Everything goes into `posts.ts`** as the single content source of
   truth. No separate files, no new frameworks.
7. **Every batch edit that touches more than 5 posts** gets a dry-run
   audit first (list affected slugs) before writing.

---

## Plan (ordered, executed in sequence)

### TIER 1 — Audit (do these first; no side effects)

- [ ] **A. Deployment audit** — confirm Vercel vs other host, confirm
  last deploy, check `next.config.js`, `vercel.json`, git remote. Output:
  "deploy host = X, last deploy = Y, image optimization = auto/manual."
- [ ] **B. Gap inventory** — for each of 74 posts, flag which are missing
  `keywords`, `cluster`, `schemaType`, `lastModified`. Output:
  `SESSION_AUDIT.md` table with slug × missing-fields.
- [ ] **C. Prior subagent work check** — look for:
  - `scripts/seo_retrofit/featured_snippets_spec_round2.py`
  - `scripts/seo_retrofit/howto_schema_spec.py`
  - `scripts/seo_retrofit/apply_featured_snippets_round2.py`
  - Decide: apply / re-kick / skip.

### TIER 2 — Fix (safe, mechanical changes)

- [ ] **D. `lastModified` bulk add** — set `lastModified = date` on all
  74 posts via script (authoritative batch). This gives Google a
  freshness signal and matches `Article.dateModified` to publish date.
- [ ] **E. `cluster` fill** — for the ~10 posts missing cluster, assign
  from the existing 10-cluster set based on content.
- [ ] **F. `keywords` fill** — for the ~11 posts missing keywords, add
  3–5 keywords each (primary + secondary) derived from title / cluster.
- [ ] **G. `schemaType` fill** — for the ~20 posts missing schemaType,
  default to `'article'` (or `'faq'` if the post has faq section).
- [ ] **H. Image strategy verify** — if Vercel → confirmed auto-optimized,
  done. If not Vercel → bulk WebP conversion.

### TIER 3 — Enhance (lower leverage, still worthwhile)

- [ ] **I. Featured snippet round 2** — if spec exists, apply. Else skip.
- [ ] **J. HowTo schema** — if spec exists, apply. Else skip.
- [ ] **K. Sitemap / robots / canonical integrity** — verify
  `/sitemap.xml`, `/robots.txt`, and canonical URLs are consistent.

### FINAL

- [ ] **Lint + typecheck** on `posts.ts` and related files. Fix any
  errors introduced.
- [ ] **Audit report** — write a short `SESSION_REPORT.md` summarizing
  what was changed, what was skipped, what the user still needs to do
  manually.

---

## User actions (NOT automatable — user does in browser / other apps)

These are listed here so we don't lose track. They block some SEO
results but not the in-repo work.

1. **Set up Google Search Console** — verify domain, submit
   `https://devenira.com/sitemap.xml`.
2. **Set up Bing Webmaster Tools** — import from GSC after GSC is live.
3. **Medium wave_01_01 canonical fix** — clear canonical URL on the
   already-published Medium story (60 seconds in Medium's SEO settings).
4. **Deploy** — if auto-deploy isn't set up, user pushes to trigger.

---

## Out of scope for this session (explicitly)

- Medium publishing cadence (wave_01_02+)
- Email outreach to SBS / Authority / BarBend / etc
- Image replacement beyond optimization format
- Blog post rewriting / voice review
- New blog post creation
- Author bio variants
- Backlink outreach templates
- Progress-update post re-framing

If the user asks for any of the above mid-session, we either add it to
this plan with a time-estimate, or we explicitly defer.

---

## Progress log (append-only)

- 2026-04-22 — Session start. Plan created. Starting Tier 1 A.
- 2026-04-22 — **PAUSED at Tier 1 A.** Git/deploy audit uncovered
  critical state issue: workspace is a manual merge-in-progress (see
  `MERGE_NOTES_20260420.txt`), HEAD is detached at 1f6ba52 with 935
  staged deletions. The 74-post blog in working tree is **NOT committed
  to any branch or remote.** Nearest committed state (`v2/main` /
  `prodrepo/main` @ fae4295) has 69 posts. `v2/v2-main` is a separate
  feature branch with 0 blog posts. See `SESSION_STATUS_20260422.md`
  for full findings. Session paused pending user verification of Vercel
  deploy source and decision on commit strategy.
