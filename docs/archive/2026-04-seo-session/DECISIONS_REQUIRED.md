# Decisions Required (after gym session)

You said you'd run for ~3 hours; this file lists everything that needs
your input before further work proceeds. Read top-to-bottom — items are
ordered by urgency.

---

## 1. wave_01_01 Medium canonical (urgent — 1 minute fix)

The first post you published on Medium (`The Most Reliable Way to Succeed
at Dieting...`) was published BEFORE the canonical flip. It still has
`https://devenira.com/blog/the-most-reliable-way-to-succeed-at-dieting...`
set as its canonical URL on Medium.

**Why this matters**: Every visitor who lands on that Medium URL is
telling Google "this isn't the primary version — devenira.com is." But
devenira.com has no authority, so the post can't rank from there either.
Both lose. This needs a 60-second fix.

**Action**: 
1. Open the Medium story in edit mode
2. Three-dot menu → "More settings" → "SEO"
3. Clear the "Canonical URL" field (currently `https://devenira.com/...`)
4. Save

After this, Medium's DR ~95 authority stays with the Medium URL where
it can actually rank.

---

## 2. wave_01_02 publish — ready to go (30 min total)

The founder story (`How I Lost 50 kg: Why the Middle of the Diet Is the
Hardest`) is the next-up post. Everything is prepped:

- SEO Title: `How I Lost 50 kg: Why the Middle of the Diet Is the Hardest`
- Subtitle: (in package file)
- Tags: `Weight Loss / Transformation / Weight Loss Journey / Founder Story / Mindset`
- Cover: `frontend/public/founder/founder-story-hanok-20260119.jpg`
- Meta description, primary keyword, secondary keywords: in package
- First-paragraph SEO opener: applied
- Featured-snippet answerBox + 5 FAQ items: applied
- Canonical URL: leave blank (per the 2026-04-21 flip)

Open the package and publish:
`marketing/fitness_blogging/blog_strategy/medium_launch/wave_01_02_founder_story_medium_manual_publish_package.md`

After publishing, paste the Medium URL into:
- `posts.ts` → set `mediumUrl: '...'` on the matching entry
- `wave_01_tracker.md` → row #2 → Status + URL

---

## 3. Image performance — needs founder action (~2 hours; one-time)

Audit at `marketing/fitness_blogging/blog_strategy/seo_performance_audit.md`
flagged **60 of 64 hero images** as exceeding the 200 KB LCP budget. Largest
are 800 KB+, which means LCP is probably > 4 seconds on mobile.

**This is the single biggest Core Web Vitals problem you have.**

### Recommended action

Convert all hero images to WebP at 1920px max width, ~80% quality. Tools:
- macOS: `cwebp` (homebrew: `brew install webp`)
- Bulk script: `find frontend/public/founder -iname '*.jpg' -exec cwebp -q 80 -resize 1920 0 {} -o {}.webp \;`

Then update `posts.ts` heroImage paths from `.jpg` → `.webp`.

If you'd rather defer: Vercel's built-in image optimization (with `<Image>`)
already serves WebP automatically when the source is JPEG. So this is
optional IF you deploy on Vercel. Confirm your hosting before acting.

---

## 4. Search Console + Bing Webmaster setup (~30 min one-time)

Walked through in `marketing/fitness_blogging/blog_strategy/founder_publishing_toolkit.md` §3-4.

Without GSC/Bing setup, you have ZERO visibility into:
- Which keywords actually drive impressions/clicks
- Whether FAQPage schema is being recognized
- Whether the new sitemap is crawled
- Indexing errors

**Action**: Set up both. The toolkit doc has the step-by-step.

---

## 5. Slug rename = old URLs are dead unless deployed (~when ready to deploy)

We renamed all 64 posts.ts slugs to short keyword-rich versions. The
301 redirects are registered in `frontend/src/content/blog/redirects.js`
and wired into `next.config.js`.

**These redirects only fire after the next deploy.** Until you deploy:
- Direct visits to the old URLs will 404 (the static page no longer exists at the old slug)
- Direct visits to the new URLs will work

**No external links to the old URLs exist yet** (only wave_01_01 was
public, and it points to the Medium URL not the site URL), so this is
safe. But after the deploy, run `curl -I https://devenira.com/blog/<old-slug>`
to confirm 301 chain works.

---

## 6. Optional: backlink outreach (manual, ongoing)

`marketing/fitness_blogging/blog_strategy/outreach_templates.md` has
copy-paste templates for:
- Reddit replies (NEVER cold link drops)
- Hacker News submissions (best Tue–Thu 7am PT)
- Indie Hackers founder posts
- Guest post pitches to fitness/founder publications
- Newsletter swap pitches

Realistic: 5% response rate, so target 20+ pitches/month for traction.

**Decision needed**: Do you want me to draft personalized first emails
to 5 specific publications (Mind Body Green, Examine, Stronger by
Science, etc.) using your real bio? Or would you rather draft those
yourself for voice authenticity?

---

## 7. Featured-snippet round 2 (writing in progress as of session end)

Subagent was writing 25 more Featured Snippet (answerBox + FAQ) entries
when the session ended. It may or may not have finished.

**Check**: does `scripts/seo_retrofit/featured_snippets_spec_round2.py`
exist?

- If YES: run `python3 scripts/seo_retrofit/apply_featured_snippets_round2.py`
  (which I'll either have created or you can copy from `apply_featured_snippets.py`
   and change the spec import)
- If NO: re-kick the subagent in a future session, or skip — round 1
  already covered the top 10 + 20 highest-leverage Q&A posts; round 2
  is "nice to have."

---

## 8. HowTo schema (writing in progress as of session end)

Same as above — subagent was writing HowTo schema content for ~10 how-to
posts. Check `scripts/seo_retrofit/howto_schema_spec.py`.

If it exists, an apply script is needed (similar to apply_featured_snippets.py
but for `howToSteps`). I'll either have built it or it's an easy add.

---

## 9. Author bio variants for guest pitches (manual edit pending)

`outreach_templates.md` includes ONE bio variant for pitches:

> "I'm pkang. I lost 50 kg over five years and write about appetite,
>  body image, and the slow work of reading the body without panic."

For high-stakes pitches (Mind Body Green, Healthline), you may want to
craft 2-3 variants per audience: founder-led, science-leaning,
personal-essay leaning. **Decision: do this when you actually have a
specific publication to pitch — premature optimization otherwise.**

---

## 10. Blog post that's "always been weird" — `progress-update-3` etc.

The 3 progress-update posts are tagged NOT RANKABLE in the keyword
research (they're journal-style; Google won't rank them on info queries).

**Decision**: That's fine for now — they target Medium recommendation
engine. If you want to make them rankable later, would need to re-frame
each one around a specific question/intent. Not urgent.

---

## What's NOT decided here (because I made a call)

I made these choices without asking. If any are wrong, course-correct
in next session:

1. **Slug structure**: chose short keyword-rich slugs (e.g. `does-one-bad-day-ruin-a-diet`).
   Alternative was keeping editorial slugs. Slug change = link equity reset
   IF anything was linked. Since only wave_01_01 was public AND linked from
   Medium with its own URL, the cost was zero.

2. **Canonical → Medium for ALL posts**: Including pillar pages and the
   author page. Pillar pages are SELF-canonical (because they don't have
   a Medium counterpart). All blog posts canonical → Medium when mediumUrl
   set; self-canonical otherwise.

3. **Cluster count**: 10 clusters instead of the 8 originally planned.
   Split `food-structure` (meal prep, protein, social events) and
   `body-composition` (recomposition, bloat-vs-fat) out from the others
   because they had enough posts to deserve their own pillar.

4. **Featured snippet limit**: Did 30 in round 1 (top 10 + 20 highest-quality
   Q&A). Round 2 (in progress) may add 25 more. Posts NOT included =
   journal-style or non-Q&A; they don't need answerBox.

5. **No Twitter handle confirmed**: I assumed `@pkang` for Twitter card
   creator field. If you have a different handle, search & replace in
   `frontend/src/app/(blog)/blog/[slug]/page.tsx` and `BlogStructuredData.tsx`.

6. **No GA4 measurement ID confirmed**: The `<GoogleAnalytics />`
   component already exists; assuming you've set it up. If not,
   tracking is broken.

---

## Summary of "go publish wave_01_02 now" checklist

If you only have 30 min and want to publish #2 today:

1. Fix wave_01_01 canonical (60 sec — see §1)
2. Open wave_01_02 package, publish per founder_publishing_toolkit.md §1
3. Paste Medium URL into posts.ts mediumUrl + wave_01_tracker.md
4. Share to X / LinkedIn / Facebook with UTM tags

The rest can wait.
