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
   `https://devenira.com/blog/what-actually-counts-as-a-weight-loss-plateau` — exact
   slug is `what-actually-counts-as-a-weight-loss-plateau` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
What Actually Counts as a Weight Loss Plateau?

## SEO Title
What Counts as a Weight Loss Plateau (and What Doesn't)?

## Subtitle / Description
What counts as a weight loss plateau is narrower than people think. Most slow weeks are not plateaus — just real life. A slower scale is not automatically a plateau. Sometimes progress just stopped flattering you and started looking like real life.

## Meta Description
What counts as a weight loss plateau? Most people call it after 7 days. The honest threshold is 3 weeks of zero trend — and most never get there.

## Primary Keyword
what counts as a weight loss plateau

## Secondary Keywords
- weight loss plateau definition
- how long until it's a plateau
- am I in a plateau or slow progress
- how many weeks to call it a plateau
- weight stall vs plateau

## Medium Tags
- Weight Loss
- Weight Loss Plateau
- Dieting
- Plateau
- Fitness

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/plateau-middle-checkin-20250711.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# What Actually Counts as a Weight Loss Plateau?

What counts as a weight loss plateau is narrower than people think. Most slow weeks are not plateaus — just real life. A slower scale is not automatically a plateau. Sometimes progress just stopped flattering you and started looking like real life.

I used to call anything slower than week one a plateau.

That is how impatient people talk when the scale stops flattering them.

Week three arrives, the number barely moves, and suddenly you are acting like the whole plan entered hospice care.

People use the word plateau way too early.

> **What actually counts as a weight loss plateau?**
>
> A real plateau is three weeks of stable weight under the same conditions, with no shape change either. Less than that is noise. Slower progress than week one is not a plateau. One or two flat weigh-ins is not a plateau. Most people use the word way too early and start punishing a plan that is still working.

## Slower Is Not the Same as Stuck

If your weight is still going down, just not at the absurdly flattering rate it did at the beginning, that is not automatically a plateau.

That is often just the end of the loud phase.

Early dieting is noisy. Water moves fast. Motivation is still fresh. The scale is weirdly generous and makes people think this is what doing well is supposed to look like forever.

Then real life resumes. The drop gets slower. The excitement fades. That is not a plateau. That is adulthood.

## A Flat Scale Is Not Always a Bad Sign Either

Sometimes weight stays the same while the body is still changing.

That can happen when body fat is going down while muscle mass is increasing. The scale sees equal amounts of loss and gain and gives you a boring answer.

Your body does not necessarily agree with that answer. This is why some people say, “My weight has not changed,” while their waist, shape, or photos tell a more interesting story.

That is exactly why one number should not be treated like a final verdict.

## Look Longer and Look Wider

A lot of people ask the wrong question. They ask, “Did my body change today?”

That is a terrible question. Bodies are not customer service desks. They do not issue neat daily updates just because you had a disciplined Tuesday.

A better question is: what has happened over the last week?

That is where photos matter. That is where weekly comparisons matter. That is where a calmer check-in matters.

## So What Is a Real Plateau?

A real plateau is not:

- slower progress than the first week
- one or two flat weigh-ins
- a moody Thursday
- a number that did not validate your effort quickly enough

A real plateau is closer to this: weight is not changing, body shape is not changing, and that pattern continues long enough to matter.

## Why This Misunderstanding Ruins Diets

The moment people use the word plateau, they start behaving like something has gone wrong.

Now the response becomes: eat less, cut more carbs, add more cardio, maybe I need to get serious now.

That is how decent plans get punished for not being dramatic enough.

Most people do not need a harsher reaction to a flat scale. They need another lens before panic starts freelancing.

## What to Do Instead

- Ask whether progress actually stopped or just slowed.
- Check whether the body is changing even if the number is flat.
- Stop letting week one define success forever.
- Only troubleshoot what is actually happening.

Do not use a real-plateau response on a fake plateau. That is like bringing bolt cutters to a door that was never locked.

## Closing

If one number keeps deciding your mood, your meals, and your training plan, you are not just tracking progress. You are letting the scale run management.

That is a bad workplace.

A better check-in helps you see whether you are actually stuck or just annoyed.

Before you call it a plateau, get one calmer read on what your body is actually doing.

If this piece felt familiar, the rest of my writing lives on [Devenira](https://devenira.com/blog).

I'm pkang, a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.



## Frequently Asked Questions

### How long until I can call it a plateau?

Three weeks of stable weight under similar conditions, with no shape change either. Anything shorter is noise. The early water-loss phase fooled people about what real progress looks like, so the second month often gets read as a plateau when it is just adulthood.

### Can the scale stay flat while I'm still losing fat?

Yes. If body fat is going down while a small amount of muscle is going up, the scale shows nothing while the body is still changing. That is why one number should not be treated as a final verdict, especially during training.

### Why does cutting more usually backfire?

Because most plateaus are not actually plateaus, so the harsher response is solving a problem that does not exist. Even on real plateaus, cutting harder tends to drop NEAT, raise appetite, and trigger a binge later in the week. Bolt cutters on an unlocked door.

### Why does week one feel so dramatic compared to week three?

Week one is mostly water, glycogen, and a noisier scale. Motivation is fresh. The body is not yet in any real fat-loss rhythm. By week three, the noise has cleared and the actual rate of loss is what shows. Week one was the bad teacher.

### How should I respond if it is a real plateau?

Run an honest tracking week before changing anything. Check sleep, stress, and unconscious activity drift. Most plateaus break by fixing the variable that drifted, not by cutting calories or adding cardio. A plateau is a report, not a verdict. Read it before reacting.

```
