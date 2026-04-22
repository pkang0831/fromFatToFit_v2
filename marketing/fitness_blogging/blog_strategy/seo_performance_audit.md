# Blog Performance Audit

Generated: 2026-04-21
Read-only audit of static-asset weight + per-post content size.

## Why this matters for SEO

- LCP (Largest Contentful Paint) is dominated by hero-image weight on blog posts.
- Google rewards LCP < 2.5s; > 4s is a ranking penalty.
- Hero image budget: warn at 100 KB, fail at 200 KB.
- Content-heavy posts (3500+ words) need careful image lazy-loading and font-display: swap.

## Hero image budget

- Total posts audited: 74
- OK     (< 100 KB):       0
- WARN   (100–199 KB):     4
- FAIL   (>= 200 KB):    60
- MISSING (image not on disk):  10
- WebP-conversion candidates (jpg/png > 100 KB): 64

### Top 20 heaviest hero images (action: convert to WebP / resize)

| Slug | Hero image | Size (KB) | Bucket |
|------|-----------|-----------|--------|
| how-to-track-body-transformation-without-the-scale | /founder/transformation-proof-20251119.jpg | 3482 | FAIL |
| why-does-my-body-look-different-from-different-angles | /founder/transformation-proof-20251119.jpg | 3482 | FAIL |
| why-adding-cardio-to-a-cut-backfires | /founder/transformation-proof-20251119.jpg | 3482 | FAIL |
| progress-update-body-changes-slower-than-mind | /founder/progress-update-hanok-20260119.jpg | 3121 | FAIL |
| past-the-messy-middle-of-weight-loss | /founder/progress-update-hanok-20260119.jpg | 3121 | FAIL |
| how-to-trust-slow-weight-loss-progress | /founder/progress-update-hanok-20260119.jpg | 3121 | FAIL |
| does-one-bad-day-ruin-a-diet | /founder/cheat-day-founder-20251221.jpg | 3086 | FAIL |
| do-obese-people-lose-weight-slower | /founder/long-game-founder-20251221.jpg | 3086 | FAIL |
| why-some-people-never-gain-weight-no-matter-what | /founder/long-game-founder-20251221.jpg | 3086 | FAIL |
| why-do-i-gain-back-more-weight-than-i-lost | /founder/long-game-founder-20251221.jpg | 3086 | FAIL |
| why-does-restriction-make-cravings-worse | /founder/cheat-day-founder-20251221.jpg | 3086 | FAIL |
| first-month-of-maintenance-after-weight-loss | /founder/long-game-founder-20251221.jpg | 3086 | FAIL |
| does-one-bad-meal-ruin-a-diet | /founder/cheat-day-founder-20251221.jpg | 3086 | FAIL |
| why-cant-i-see-weight-loss-in-the-mirror | /founder/mirror-middle-checkin-20250716.jpg | 3070 | FAIL |
| why-do-others-notice-my-weight-loss-before-me | /founder/mirror-middle-checkin-20250716.jpg | 3070 | FAIL |
| why-progress-photos-dont-show-progress | /founder/mirror-middle-checkin-20250716.jpg | 3070 | FAIL |
| how-to-stick-to-a-diet-when-progress-slows | /founder/consistency-editorial-20251229.jpg | 2992 | FAIL |
| how-to-stop-using-exercise-as-punishment | /founder/consistency-editorial-20251229.jpg | 2992 | FAIL |
| why-are-my-workouts-harder-on-a-cut | /founder/consistency-editorial-20251229.jpg | 2992 | FAIL |
| does-bad-sleep-ruin-weight-loss | /founder/sleep-reflective-20260106.jpg | 2884 | FAIL |

## Long posts (estimated word count)

Posts above 3,500 words deserve special care — explicit image lazy-loading,
font-display: swap, and possibly content splitting via `<details>` accordions
to keep first-paint fast.

| Slug | Words (estimate) | Sections |
|------|------------------|----------|
| do-i-have-to-meal-prep-to-lose-weight | 1895 | 12 |
| when-does-a-diet-become-a-lifestyle | 1648 | 10 |
| why-am-i-hungry-at-night-but-not-during-the-day | 1636 | 12 |
| why-am-i-so-hungry-after-lifting-weights | 1563 | 10 |
| daily-weighing-eating-disorder-risk | 1557 | 10 |
| appetite-returns-during-maintenance | 1437 | 8 |
| first-month-of-maintenance-after-weight-loss | 1431 | 9 |
| why-does-the-same-weight-feel-different-as-you-age | 1390 | 11 |
| does-one-bad-meal-ruin-a-diet | 1313 | 12 |
| does-cutting-sodium-cause-water-retention | 1262 | 9 |

## Recommended actions

1. **Convert WARN/FAIL hero images to WebP** (use `cwebp` or an image pipeline). WebP
   typically saves 30–50% vs JPEG at equivalent quality. Next.js `<Image>` already
   serves WebP automatically when the source is jpg, but the source weight still
   bounds the WebP weight. Resize source to 1920px max-width before converting.
2. **Set `priority` on every blog hero `<Image>`** (already done in [slug]/page.tsx). Confirm.
3. **Lazy-load all inline images** (default for non-priority Next.js Image). Confirm.
4. **Long posts (above): consider splitting** into a `<details>` 'Read on' block midway
   — keeps initial DOM small without losing content.
5. **Audit fonts**: Plus_Jakarta_Sans and Space_Grotesk are loaded with `display: swap`
   per `app/layout.tsx`. ✓
6. **Consider self-hosting hero images on a CDN with WebP/AVIF auto-conversion**
   (Cloudflare Images, Bunny CDN, or Vercel built-in image optimization). The latter
   is automatic on Vercel deploys.

## Out of scope (need real measurement)

This audit can't measure:
- Real LCP / INP / CLS (need Chrome Lighthouse / WebPageTest)
- TTFB (depends on hosting tier)
- JS bundle size (run `ANALYZE=true npm run build` for that)

Run Lighthouse on `/blog/<slug>` for a real score after the next deploy.