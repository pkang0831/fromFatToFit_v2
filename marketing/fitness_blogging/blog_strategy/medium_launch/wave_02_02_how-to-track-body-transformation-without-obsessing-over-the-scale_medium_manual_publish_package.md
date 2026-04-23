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
   `https://devenira.com/blog/how-to-track-body-transformation-without-obsessing-over-the-scale` — exact
   slug is `how-to-track-body-transformation-without-obsessing-over-the-scale` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
How to Track Body Transformation Without Obsessing Over the Scale

## SEO Title
How to Track Body Transformation Without the Scale

## Subtitle / Description
Here's how to track body transformation without the scale, with one weekly evidence loop instead of a daily morning verdict. If you want to know whether your body is actually changing, you need a better system than checking the scale and the mirror every day. A simple weekly evidence loop works better.

## Meta Description
How to track body transformation without the scale: 4 weekly signals more honest than the morning weigh-in. Photos, fit, and 2 you probably skip.

## Primary Keyword
how to track body transformation without the scale

## Secondary Keywords
- measuring body transformation
- track fat loss without scale
- weekly progress check-in method
- body transformation tracking tools
- measuring weight loss progress

## Medium Tags
- Weight Loss
- Body Recomposition
- Progress Photos
- Fitness
- Transformation

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/transformation-proof-20251119.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# How to Track Body Transformation Without Obsessing Over the Scale

Here's how to track body transformation without the scale, with one weekly evidence loop instead of a daily morning verdict. If you want to know whether your body is actually changing, you need a better system than checking the scale and the mirror every day. A simple weekly evidence loop works better.

Most people try to track transformation with the same two tools: the scale and the mirror.

The problem is not that those tools are useless. The problem is that people use them badly.

They look too often. They react too quickly. And they ask each tool to do more than it is good at.

That is how progress becomes confusing, even when the process is working.

> **How do I track body transformation without obsessing over the scale?**
>
> Build one weekly evidence loop instead of a daily judgment ritual. Take a baseline photo, add weekly progress photos under similar conditions, watch how clothes fit, and use the scale as a supporting metric rather than the main judge. The body usually changes slower than emotion. Weekly tracking gives the body room to tell a real story.

## What Most People Get Wrong

The most common mistake is turning a body transformation into a daily judgment ritual.

You weigh yourself. You look in the mirror. You decide how hopeful or hopeless to feel.

That is not tracking. That is emotional volatility with numbers attached to it.

The scale is too noisy for daily interpretation. The mirror is too familiar for subtle change.

If you rely on those two alone, you will keep bouncing between overconfidence and discouragement.

## What Better Tracking Actually Looks Like

A useful transformation-tracking system does three things.

- it creates a baseline
- it compares over meaningful gaps
- it reduces the room for panic-driven interpretation

That is why a weekly system works so well. It is frequent enough to stay relevant, but slow enough to let your body show direction.

## Start With A Real Baseline

You need one honest starting point.

Not a flattering photo. Not your best angle. Not the version of your body you wish were true.

Just a clear starting point.

That is what gives every future check-in meaning. Without a baseline, every new photo becomes a guess. With a baseline, each new check-in becomes comparison.

## Why Weekly Check-Ins Work Better

Weekly check-ins are better than daily obsession for one simple reason: the body usually changes slower than emotion.

Daily tracking gives emotion too many chances to interfere. Weekly tracking gives the body more room to tell a real story.

That does not mean every week looks dramatic. It means weekly data is more likely to mean something.

Because one of the biggest reasons people quit is not lack of discipline. It is lack of believable evidence.

## The Best Signals To Track

- weekly progress photos
- visual changes in waist, torso, face, and posture
- repeated check-ins under roughly similar conditions
- the scale as a supporting metric, not the main judge

This gives you a more stable read on reality. You stop trying to squeeze certainty out of one daily number.

## Progress Photos Matter More Than People Admit

A lot of people avoid progress photos because they feel awkward or discouraging. That is understandable.

But the uncomfortable truth is that progress photos often become useful before they become flattering.

That is exactly why they matter. They capture what memory edits. They preserve what the mirror normalizes. And over time, they become one of the clearest ways to see whether the work is paying off.

## You Do Not Need More Data. You Need Better Interpretation

Most people are not short on information. They are short on structure.

They do not need more dashboards. They do not need a more dramatic chart. They do not need to check five times a day.

They need a system that makes panic less persuasive. That is what a weekly proof loop does.

It gives you enough information to see direction. And it keeps that direction visible long enough for your confidence to catch up.

## Closing

If you want to track body transformation without obsessing over the scale, simplify the system.

Start with one baseline. Check in weekly. Store the record. Compare over time.

That is a much better way to judge whether your body is changing.

One scan is a number. Weekly check-ins are proof.

If this piece felt familiar, the rest of my writing lives on [Devenira](https://devenira.com/blog).

I'm pkang, a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.



## Frequently Asked Questions

### How often should I take progress photos?

Once a week, same spot, same lighting, same pose. Save them without analyzing them on the day. Compare in groups of four. Weekly is frequent enough to stay relevant; comparing every four weeks is slow enough to let your body actually show direction.

### Why is daily scale tracking misleading?

Daily readings are mostly water, sodium, and digestive contents — almost everything except fat. The number swings two kilos in a normal day. Reading those swings as fat loss or gain creates emotional volatility with numbers attached, not tracking.

### What should a baseline check-in include?

One honest starting photo, taken under conditions you can repeat. Not a flattering angle. Not your best lighting. Just a clear reference point. Without a baseline, every future photo becomes a guess. With one, every check-in becomes a real comparison.

### What signals are more honest than the scale?

Weekly progress photos under matched conditions. Visual changes in waist, torso, face, and posture. How familiar clothes are fitting. Tape measurements at waist and hip every two weeks. Together those four catch composition shifts the scale silently misses.

### Why do most people quit before they see real progress?

Because they track on a daily timescale and grade emotionally. Daily noise is louder than weekly signal, so the program feels like it is failing while the body is quietly moving. Most people quit not from lack of discipline, but from lack of believable evidence.

```
