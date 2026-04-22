# Founder Publishing Toolkit

A single document that walks through everything you do AROUND the writing — Medium publish, Search Console, Bing Webmaster, social distribution, link building, and analytics.

Use this every time you publish. The first six sections are once-per-post. The rest are once-per-platform setup.

---

## 1. Medium publish workflow (~10 min per post)

### Before paste

- Open the package file: `marketing/fitness_blogging/blog_strategy/medium_launch/wave_<XX>_<NN>_<topic>_medium_manual_publish_package.md`
- Open Medium → "Write a story" (NOT "Import from URL" — see canonical note below)

### Step-by-step

1. **Title** → paste from `## Title`
2. **Subtitle** → paste from `## Subtitle / Description`
3. **Body** → paste from inside `## Markdown` block (only what's between ` ```md ` and ` ``` `)
4. **Cover image** → upload from the path under `## Cover Direction`
5. **Story settings** (three-dot menu → "More settings" → "SEO"):
   - **SEO Title** → paste from `## SEO Title` (NOT the same as the visible title)
   - **Canonical URL** → **LEAVE BLANK** (per the 2026-04-21 canonical flip — Medium is canonical primary)
6. **Tags** → add the 5 tags from `## Medium Tags` in order (the first tag gets slightly more recommendation weight on Medium)
7. **Publish**

### After publish

1. Copy the live Medium URL (you'll need it twice).
2. **In `frontend/src/content/blog/posts.ts`**, find the entry with the matching `slug` and add:
   ```ts
   mediumUrl: 'https://medium.com/@pkang/<slug>-<id>',
   ```
   This makes the owned-site canonical re-point to Medium for that post (link equity flows correctly).
3. **In `marketing/fitness_blogging/blog_strategy/medium_launch/wave_01_tracker.md`** (or its successor), update the row:
   - Status → `published`
   - Planned Publish Date → today
   - Medium URL → paste the URL
4. **Submit the new URL to Google Search Console** (see §3) — usually crawled within 24h anyway, but a manual submit speeds it.
5. **Share to X / LinkedIn / Facebook** with the canonical Medium URL (NOT the devenira.com mirror — Medium is primary).

### One-time fix for `wave_01_01_consistency`

That post was published BEFORE the canonical flip. Edit it on Medium right now:

- Open the story → three-dot menu → "More settings" → "SEO"
- **Clear** the Canonical URL field (currently `https://devenira.com/blog/...`)
- Save

This stops the post from re-routing all of Medium's DR 95 authority to the empty owned site.

---

## 2. Distribution checklist (per post, ~15 min)

After Medium publish:

### a. Internal cross-promotion

- **Tweet/post on X** with the post's primary share-card line + Medium URL
- **LinkedIn**: share with the meta description as caption
- **Facebook**: share with the social description as caption (NOT the meta description — Facebook crowd different)
- **Threads** (if you use): same as X

### b. External seeding (only do these for posts you're proud of)

- **Reddit** — see "Reddit subreddit map" below; pick 1 high-fit subreddit; share NOT as a self-promo but as "I wrote about X — happy to discuss" comment in a relevant thread
- **Hacker News** — only the strongest 1–2 posts of every batch (founder story, 50kg transformation, the Medium-platform-itself essays). Submit at 7am US Pacific for best visibility window
- **Indie Hackers** — founder story posts only
- **Newsletter swaps** — see "Newsletter swap targets" below

### c. Tracking

Use UTM parameters on EVERY shared link so you can see traffic origin in Search Console / Plausible / GA:

```
?utm_source=<source>&utm_medium=<medium>&utm_campaign=<post-slug>
```

Examples:
- X share: `?utm_source=x&utm_medium=social&utm_campaign=cheat-day-post`
- Reddit comment: `?utm_source=reddit&utm_medium=community&utm_campaign=cheat-day-post`
- Newsletter swap: `?utm_source=morning-brew&utm_medium=newsletter&utm_campaign=cheat-day-post`

The Medium URL accepts UTM parameters — they show up in Medium stats AND your owned-site analytics if the click eventually flows there.

---

## 3. Google Search Console setup (one-time, ~30 min)

You need GSC to:
- Submit your sitemap so Google indexes the owned site
- Get search query data (which keywords actually drive clicks)
- Be alerted to indexing issues (most common: canonical conflicts)

### Setup steps

1. Go to https://search.google.com/search-console
2. Add property → choose "Domain" (NOT "URL prefix") if you can verify via DNS — easier
3. **DNS verification**: GSC gives you a TXT record. Add it to your domain DNS (Cloudflare/Vercel/whoever hosts your domain). Wait ~10 min for propagation.
4. Once verified, submit sitemap: `https://devenira.com/sitemap.xml`
5. Submit RSS feed too: `https://devenira.com/blog/feed.xml`
6. **For each Medium post you publish**, also submit the Medium URL via GSC (use a SEPARATE property for `medium.com/@pkang` — also verifiable)

### What to watch in GSC after the first month

- **Performance → Search results** → which queries are getting impressions but zero clicks (= title/description needs work)
- **Coverage → Errors** → any indexing failures (common: redirect loops if 301 chain breaks)
- **Enhancements → FAQ** → confirms FAQPage schema is being picked up
- **Enhancements → Article** → confirms Article schema is being picked up
- **Sitelinks Search Box** appears under brand search after ~1 month if WebSite SearchAction schema is being recognized

---

## 4. Bing Webmaster setup (one-time, ~15 min)

Bing is ~7% of US search but underweighted by most marketers. Easy win:

1. Go to https://www.bing.com/webmasters
2. Sign in with Microsoft account
3. **Import from Google Search Console** — Bing offers a one-click GSC import. This auto-verifies and submits sitemap.
4. Confirm `https://devenira.com/sitemap.xml` is submitted
5. Add `https://devenira.com/blog/feed.xml` as separate sitemap

That's it. Bing crawls more aggressively than Google for new domains, so you may get traction here first.

---

## 5. Social platforms — one-time profile setup

### X (Twitter)
- Username: `@pkang_devenira` (or @pkang if available)
- Bio: "Lost 50 kg over 5 years. Now writing about appetite, body image, and the slow work of reading the body without panic. Building Devenira."
- Pinned tweet: link to `wave_01_02` (founder story) once published
- **Profile link**: `https://devenira.com/authors/pkang` (NOT a generic homepage — drives organic discovery)

### LinkedIn
- Headline: "Fitness and diet writer. Lost 50 kg over 5 years. Founder, Devenira."
- About: paraphrase of the author page text
- Featured: pin the founder story Medium URL once published

### Threads / Bluesky
- Same bio as X
- Use as "shorter takes" feed; cross-promote Medium posts as digestible pull-quotes

---

## 6. Reddit subreddit map

For each cluster, here are subreddits that fit. **Rule**: don't drop links cold. Read 5+ threads first, then participate genuinely; share your post URL only when it actually answers someone's question.

| Cluster | Subreddits | Notes |
|---------|-----------|-------|
| Scale | r/loseit, r/1200isplenty, r/intuitiveeating | r/loseit is the biggest; participate weekly |
| Mirror | r/loseit, r/fatlogic, r/progresspics | r/progresspics for visual proof discussions |
| Appetite | r/loseit, r/intuitiveeating, r/EDAnonymous (sensitive) | EDAnonymous is for ED-adjacent content — rare |
| Binge / cheat | r/loseit, r/intuitiveeating, r/BingeEatingDisorder | Be careful in BED — community is sensitive |
| Maintenance | r/loseit, r/maintenance, r/xxfitness | Maintenance has a smaller, more loyal audience |
| Plateau | r/loseit, r/fitness30plus, r/IntermittentFasting | Many plateau threads daily |
| Exercise | r/Fitness, r/xxfitness, r/weightroom | Weightroom is more advanced; tone-match |
| Founder story | r/loseit, r/Entrepreneur, r/IndieHackers (for Devenira) | Cross-purpose with founder story |
| Body composition | r/Fitness, r/leangains, r/xxfitness | Composition niche is well-served |

### Posting cadence
- Read 1 hour, comment 4–5 places before sharing 1 link
- Max 1 post-link per week per subreddit (most have rules; check sidebar)
- ALWAYS use the canonical Medium URL with UTM tag

---

## 7. Newsletter swap targets

These newsletters are aligned with Devenira's audience and may be open to a swap (one tile in their newsletter for one tile in yours, OR a free guest post):

- **Mind Body Green** (large, tough to land — long shot)
- **The Pump** (Gary Brecka adjacent — fitness)
- **Examine.com daily** (research-heavy fitness)
- **Stronger by Science** newsletter (training-leaning audience)
- **The Whoop blog** (recovery / tracker audience)
- **Eight Sleep blog** (sleep-fitness adjacent)

Pitch template (~3 sentences):

> "Hi, I'm pkang. I lost 50 kg over five years and write about the parts of weight loss that don't get covered — appetite returning during maintenance, the unglamorous middle, the math of one bad day vs three. Latest piece on [topic] is at [URL]. Would your audience be a fit for a swap or guest spot?"

Send to listed editor email; one shot per newsletter.

---

## 8. UTM parameter strategy

Use a CONSISTENT UTM scheme so analytics aggregate cleanly. Recommended:

| Source | utm_source | utm_medium | utm_campaign |
|--------|-----------|------------|--------------|
| X organic | x | social | <slug> |
| LinkedIn organic | linkedin | social | <slug> |
| Facebook organic | facebook | social | <slug> |
| Reddit comment | reddit | community | <slug>-<subreddit> |
| Hacker News submit | hn | community | <slug> |
| Newsletter swap (yours) | newsletter | newsletter-swap | <slug> |
| Newsletter swap (theirs) | <their-name> | newsletter | <slug> |
| Email signature | sig | email | always-on |
| Devenira homepage card | homepage | direct | <slug> |
| Devenira /blog index | bloglist | direct | <slug> |

Save these as a snippet so you don't think every time.

---

## 9. Analytics — what to actually watch

Setup-wise, GA4 is already wired (`<GoogleAnalytics />` component in `app/layout.tsx`).

Weekly metrics to watch (set as a saved view):

1. **Acquisition → Users by source** — confirms which channels drive traffic
2. **Engagement → Pages and screens** — top blog post by views, average engagement time per post
3. **Engagement → Events → scroll** — % readers reaching 90% scroll depth (= read-through)
4. **GSC → Performance → Pages** — which posts are getting impressions but zero clicks (re-write CTAs / metas for those)
5. **Medium Stats** — for posts on Medium, watch read time, claps, follow rate

After 30 days of data, identify:
- The 3 posts driving 80% of traffic (your "money pages") — promote these harder
- The posts with high impressions but zero clicks (re-write SEO title + meta description)
- The posts with traffic but zero engagement (probably the wrong audience — content-fit problem)

---

## 10. Quick action sequence after a publish (15 min)

Copy-paste this checklist into a sticky note:

```
□ Medium publish complete (per §1)
□ Medium SEO settings: SEO Title set, Canonical BLANK
□ posts.ts → mediumUrl set
□ wave_01_tracker.md row updated
□ GSC → URL inspect → request indexing
□ Bing Webmaster → submit URL
□ X share with UTM
□ LinkedIn share with UTM
□ Facebook share with UTM
□ One Reddit thread reply (NOT a link drop)
□ Reading time check: open Medium URL on a real phone, time to first contentful paint
```

---

## 11. Once-per-month maintenance (1 hour)

Every 30 days:

1. **Re-rerun the SEO audits**:
   ```
   python3 scripts/seo_retrofit/audit_title_pixels.py
   python3 scripts/seo_retrofit/audit_first_paragraph.py
   python3 scripts/seo_retrofit/audit_blog_performance.py
   ```
2. **Pull GSC top-10 queries** and check if any post is showing well for unintended keywords (= add that keyword to its `keywords` array)
3. **Pull GSC zero-click queries** (high impressions, zero clicks) — re-write their SEO title or meta
4. **Check FAQ rich-result coverage** in GSC Enhancements → FAQ → confirms FAQPage schema is firing
5. **Update `lastModified`** on any post that got a content edit in the last 30 days (Google rewards freshness)
6. **Run Lighthouse on 3 random posts** — flag any LCP > 2.5s; trace back to image weight (see `seo_performance_audit.md`)

---

## 12. Three-month review

Every quarter:
- Re-run the keyword research subagent (`marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md` is the template — generate a new dated file)
- Decide if the canonical strategy needs to flip BACK to owned-site (only if site DR is now 30+; otherwise keep Medium primary)
- Re-evaluate the cluster taxonomy — are any underperforming? Should two be merged?
- Consider opening a Substack mirror for newsletter capture (tied to RSS feed)
