# Medium Manual Publish Package

## How to publish on Medium (READ FIRST)

**DO NOT copy-paste the ```md block below into Medium's editor.**
Medium's editor does not parse markdown — `##`, `#`, `-`, and other
prefixes will appear as literal characters and destroy the heading
hierarchy. Observed 2026-04-23: wave_01_01 and wave_01_02 were
published this way and got 0 views because Medium's feed algorithm
throttles stories with no heading structure.

### Recommended workflow: Import from URL

1. In Medium: click your avatar → **Stories** → the "…" next to
   "Write a story" → **Import a story**. (Or visit
   https://medium.com/p/import directly.)
2. Paste the owned-site URL:
   `https://devenira.com/blog/the-unglamorous-middle-of-transformation` — exact
   slug is `the-unglamorous-middle-of-transformation` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
3. Click **Import**. Medium converts the rendered HTML into its
   native format; H1/H2/lists/answerBox all transfer cleanly.
4. Before publishing:
   - Verify **Title** and **Subtitle** (they come from the page meta
     but may need the Medium-friendly versions — see **Title** and
     **Subtitle / Description** sections in this file).
   - Add the 5 **Medium Tags** from this file exactly.
   - Verify the **Cover image** is correct (it auto-pulls the hero
     webp from devenira.com).
   - **Canonical URL**: clear it per the canonical-flip policy
     below. Medium may auto-set it during import; clear the field
     in Story settings → SEO before publishing.
5. Publish.
6. Copy the new Medium URL → paste into `posts.ts` for the matching
   slug (the `mediumUrl:` field) → commit & push.

### Fallback: manual paste (only if import fails)

If Medium's importer rejects the URL (rare — only happens for posts
that haven't propagated to Vercel yet), use the markdown block below
but **manually convert each heading**:

- Every line starting with `# X` → delete the `# ` and apply Medium's
  **Large Heading** (T1) style
- Every line starting with `## X` → delete the `## ` and apply Medium's
  **Medium Heading** (T2) style
- Every line starting with `- X` → delete the `- ` and apply Medium's
  bulleted-list style
- `> X` blockquotes → delete `> ` and apply quote style

This is slow and error-prone. Prefer import whenever possible.

---

## Title
The Unglamorous Middle of a Transformation

## SEO Title
Why Is the Middle of Weight Loss the Hardest?

## Subtitle / Description
Before-and-after photos make transformations look linear. The middle is where most people quit. This is what it actually looked like.

## Meta Description
Why is the middle of weight loss the hardest? Months 3 to 9 don't photograph well. Here's what the unglamorous middle looks like — and why most quit.

## Primary Keyword
why is the middle of weight loss the hardest

## Secondary Keywords
- middle of weight loss journey
- messy middle transformation
- hardest phase of weight loss
- plateau stage motivation
- weight loss motivation middle

## Medium Tags
- Weight Loss
- Weight Loss Journey
- Transformation
- Mindset
- Habits

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/patience-middle-checkin-20250731.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# The Unglamorous Middle of a Transformation

Why is the middle of weight loss the hardest stretch? The dramatic feedback is gone and the work hasn't ended.

The before photo is easy. The after photo is easy.

The six months between them is where everybody quits.

> **Why is the middle of weight loss the hardest stretch?**
>
> Because the dramatic feedback is gone and the work has not ended. The first 5 kg often come from water, better sleep, and accidental protein increases. The middle is when the body starts negotiating, the novelty fades, and the diet becomes boring. Most transformation content skips it because the middle is not a story.

## The Photograph Problem

Transformation content is lying to you structurally.

Not intentionally. Just by format. Two images side by side. One blurry. One composed. The middle gets cropped out because the middle does not photograph well.

In the middle you look mostly the same. Slightly less bloated. Slightly more tired. Your face has started to change before your body does, which makes photos of yourself feel dishonest in both directions.

The photo I never posted was the one from July. I was down about 8 kg from my highest. My face looked thinner. My clothes fit worse than before because the fat had shifted but not left. I looked somehow worse than the beginning.

That is the middle.

## What The Middle Actually Is

The middle is not a plateau.

It is the phase where the easy wins are over, the novelty is gone, and the real work has become boring. The first 5 kg often come off from water, better sleep, and accidental protein increases. The middle is when the body starts negotiating.

You stop losing visibly. You start noticing the diet. You start noticing your friends eating again. You start wondering whether this is actually going to work.

Everyone who transforms goes through it.

Most transformation content skips it, because it is not a story.

## What I Did With It

I kept showing up in the boring way. I did not chase a new plan. I did not add a supplement. I did not cut further.

I logged weight. Some days up. Some days down. I let the graph tell me nothing for three weeks at a time.

I took photos I did not post. I wrote down the exact meals I could eat without thinking.

I let the middle be the middle.

## What The Middle Taught Me

The middle is where the habit becomes structure. The body is not changing much, because the body is learning what the new normal is.

If you quit in the middle, you do not quit the diet. You quit the thing that was about to start working.

The after photo is produced by a boring middle. There is no shortcut past it. There are only people who got through it and people who restarted.

---

I write about weight loss, appetite, body image, and the slow work of learning how to read the body without panic.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### Is the middle the same as a plateau?

No. A plateau is the body holding under the same conditions for three or more weeks. The middle is broader: the easy wins are gone, motivation has thinned, and the work has become unphotogenic. The graph still moves; it just moves quietly.

### Why do most people quit during this phase?

Because the dopamine drops at the same time the work continues. Visible feedback stops. Compliments slow. The plan still demands the same things and gives back less. People assume something is wrong with the program. Usually the program is fine. The middle is the cost of being in one.

### Should I change the plan if the middle drags?

Usually not. Chasing a new plan in the middle is almost always a way to feel busy without making progress. The middle keeps asking for novelty because novelty feels like motion. It is not. The skill in the middle is staying boring while the body adapts.

### How long does the middle usually last?

Months three through nine for most longer cuts. Some people get out earlier; many take longer. The exact length matters less than recognizing what phase you are in. Treating month four like month one is the fastest way to make month five worse than it had to be.

### What is actually happening to the body in the middle?

Habits are becoming structure. The body is learning what the new normal is. Composition shifts are quietly continuing. Maintenance calories are dropping as the body gets smaller. None of that photographs well. All of it is the program doing the thing it is supposed to do.

```
