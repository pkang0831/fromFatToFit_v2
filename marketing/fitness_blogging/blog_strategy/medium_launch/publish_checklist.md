# Medium Publish Checklist

Use this every time before hitting publish.

## SEO Fields (fill first, before anything else)

All Medium packages carry these fields (added 2026-04-21 per `seo_optimization_rules.md`). Apply them when publishing:

1. **Display Title** — use the value under `## Title` (voice / brand headline; what readers see on the feed and on the article page).
2. **SEO Title** — use the value under `## SEO Title`. On Medium this lives under story settings → "SEO settings" → "SEO title" field (≤ 60 chars; keyword-front-loaded; NOT the same as the display title).
3. **Subtitle / Deck** — use the value under `## Subtitle / Description`.
4. **Tags** — copy the 5 tags under `## Medium Tags` (brand broad + niche mix; first tag is highest-traffic; do not add or remove).
5. **Meta Description** — Medium does NOT expose a separate meta description field; it auto-extracts from the first line or subtitle. The `## Meta Description` value in the package is for:
   - the owned-site `<meta name="description">` (auto-populated from posts.ts)
   - LinkedIn / X share-preview (paste when you share the link)
6. **Primary Keyword / Secondary Keywords** — reference only; used in owned-site `<meta name="keywords">` and for writing the opening paragraph so Medium's auto-extract grabs a keyword-rich preview.
7. **Canonical URL** — **DO NOT set a canonical URL in Medium's story settings.** Leave it blank. See `## Canonical URL` section of each package for the 2026-04-21 canonical-flip rationale. For any post imported from a URL, manually clear Medium's auto-populated canonical field before publishing.

After publishing, copy the live Medium URL and:
  - record it in `wave_01_tracker.md` (or its successor) under the Medium URL column
  - set `mediumUrl` on the matching `posts.ts` entry so the owned-site canonical re-points to Medium

If any field is missing from the package, STOP and retrofit per `seo_optimization_rules.md` before publishing.

## Before Paste

- remove the `# Draft Package` block
- remove the full `## SEO Package`
- keep only the article title and body
- convert the `Meta description` into the Medium subtitle / deck if useful
- make sure no internal metadata remains in the article body

## Body Cleanup

- remove any leftover internal notes
- remove photo placeholders if you are not using them
- keep headers readable and not too numerous
- keep sentence spacing natural
- keep lists flat and readable

## Brand Cleanup

- no product pitch at the end
- no app download ask
- no “book a call”
- no startup-sounding CTA
- if there is a closing line, it should feel like a writer’s close, not a funnel step

## Bio Line

Use one consistent bio line at the bottom:

*I’m pkang — a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.*

## Cover Rules

- use real photos only when they add trust or proof
- do not use modelling shots for every post
- do not use AI body images that look uncanny
- for conceptual covers, prefer objects, rooms, food, calendars, scales, wrappers, clocks, notes, mirrors

## Medium-Specific Positioning

- write like a person, not like a content team
- subtitles should clarify, not oversell
- do not stuff tags with every adjacent fitness word
- choose only the tags that actually fit the article

## Final Read

Before publishing, ask:

1. Would someone highlight at least one line in this piece?
2. Does the opening make a stranger feel immediately seen?
3. Does the ending feel like a human close instead of a system close?
4. Would the cover image make sense even if the reader never knew your app existed?
5. Does the article still work if someone reads only this one piece?

If the answer to any of those is no, fix it before publishing.
