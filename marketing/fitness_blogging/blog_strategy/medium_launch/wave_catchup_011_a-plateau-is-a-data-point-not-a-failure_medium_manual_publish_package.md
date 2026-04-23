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
   `https://devenira.com/blog/a-plateau-is-a-data-point-not-a-failure` — exact
   slug is `a-plateau-is-a-data-point-not-a-failure` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
A Plateau Is a Data Point, Not a Failure

## SEO Title
How to Break a Weight Loss Plateau (Without Panicking)

## Subtitle / Description
A plateau is the body telling you something specific. Most people read it as rejection and quit. That is not what it is saying.

## Meta Description
How to break a weight loss plateau without panicking and cutting harder. The body is sending feedback — here's how to read it before you escalate.

## Primary Keyword
how to break a weight loss plateau

## Secondary Keywords
- weight loss plateau strategies
- plateau not moving on scale
- how to push through plateau
- weight loss stalled what to do
- plateau recovery weight loss

## Medium Tags
- Weight Loss
- Weight Loss Plateau
- Dieting
- Plateau
- Habits

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
# A Plateau Is a Data Point, Not a Failure

Here's how to break a weight loss plateau without escalating to punishment-mode. The fix is rarely more discipline.

Most people read a plateau as their body firing them.

It is not.

A plateau is the cleanest feedback your body ever gives you. Most people are too frustrated to read it.

> **How do I break a weight loss plateau?**
>
> First, confirm it is a real plateau: three weeks of stable weight under same conditions, not three days. Then check actual eating, sleep, stress, and NEAT before cutting calories. Most plateaus break by fixing the thing that drifted, not by adding more deficit. A plateau is a report, not a verdict.

## What A Plateau Actually Is

Three weeks of the same weight, under the same conditions, is a plateau. Less than that is noise.

Real plateaus happen for specific reasons and each one points to something. They are not random. They are not the body quitting on you.

A plateau is your body telling you that the current inputs and the current outputs have matched.

Whatever you are doing is now maintenance for this weight.

## What The Plateau Is Saying

It depends on where you are.

Early plateau, first 3 kg in. The easy water and glycogen are gone. Your body is now asking you to actually be in a deficit to continue. Usually means you were not quite as in-deficit as you thought, and now it shows.

Middle plateau, 6 to 12 kg in. Your maintenance calories have dropped because you weigh less. A deficit that worked at the start is not a deficit anymore. The same plan has quietly become a maintenance plan.

Late plateau, near goal. Your body is close to the weight it will most naturally defend. Appetite may increase. NEAT can drop. Metabolism tends to compress. This plateau is loud and takes longer to break.

Each one is a different message. Each one has a different response.

## How To Respond

First, confirm it is actually a plateau. Three weeks of stable weight. Not three days. Then, not panic. Not cut more. Not add cardio. Instead:

- Check your actual eating, not your perceived eating. Weigh a few meals. Count for three days.
- Check your sleep. Poor sleep can stall weight loss cleanly.
- Check your stress. Cortisol may retain water and mask fat loss for weeks.
- Check your NEAT. Many people unconsciously move less as the diet continues.

Most plateaus break without cutting calories. Most plateaus break by fixing the thing that drifted.

## What A Plateau Is Not

It is not punishment.

It is not a sign you should eat more drastically.

It is not a sign the plan does not work.

It is not permanent. A plateau is a report, not a verdict.

## The Longer Frame

Plateaus are part of the architecture of fat loss. Bodies do not lose weight linearly. They lose in steps and long plateaus. The plateau you are in right now is the ledge between the last step and the next step.

The people who break plateaus are almost always the ones who stopped trying to break them and just kept going.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### How long does it take to break a real plateau?

Two to four weeks once the right intervention is applied. Honest re-tracking, a one-week diet break, fixing sleep, or adding daily walks all tend to resolve stalls within that window. Cutting more calories often extends the plateau by raising stress and dropping NEAT further.

### Should I add cardio to break a plateau?

Usually as a later move, not the first. Cardio added to an already-aggressive deficit tends to be compensated for behaviorally — lower NEAT and higher appetite later in the day. A 30-minute walk on rest days often works better than adding a structured cardio session.

### Is a diet break necessary or just helpful?

On a long cut, diet breaks tend to be necessary. People who take planned 7-to-14-day breaks at maintenance every 4 to 8 weeks retain more muscle, report lower hunger, and have better outcomes at six and twelve months than people who diet straight through.

### Why does my weight stall right at month three?

Maintenance calories drop as you lose weight, NEAT decreases unconsciously, and appetite rises. All four things stack around month three for most diets. The fix is a 7 to 14 day maintenance break, not deeper cuts. Cutting harder usually backfires here.

### What's the difference between slow progress and a real plateau?

Slow progress is still movement — even 0.2 kg per week is direction. A plateau is no scale movement and no shape change for three weeks under your usual conditions. Most 'plateaus' people complain about are actually slow weeks called the wrong name.

```
