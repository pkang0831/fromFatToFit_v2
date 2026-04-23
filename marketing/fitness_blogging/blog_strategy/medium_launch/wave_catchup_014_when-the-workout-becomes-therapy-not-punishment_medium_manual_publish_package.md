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
   `https://devenira.com/blog/when-the-workout-becomes-therapy-not-punishment` — exact
   slug is `when-the-workout-becomes-therapy-not-punishment` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
When the Workout Becomes Therapy, Not Punishment

## SEO Title
How to Stop Using Exercise as Punishment

## Subtitle / Description
Most people train to make up for something. The workouts that change you are the ones that stopped being repayment.

## Meta Description
How to stop using exercise as punishment, without quitting the gym. The same workout shifts when you change what you bring to it. Here's the line.

## Primary Keyword
how to stop using exercise as punishment

## Secondary Keywords
- exercise as self care not punishment
- working out as therapy mental health
- healthy relationship with exercise
- stop exercising to punish myself
- mindset shift fitness self love

## Medium Tags
- Weight Loss
- Mental Health
- Exercise
- Mindset
- Self Improvement

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/consistency-editorial-20251229.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# When the Workout Becomes Therapy, Not Punishment

Here's how to stop using exercise as punishment: change what the next training session is paying for.

For most of my life, the workout was a receipt.

I overate on Saturday. I earned the treadmill on Monday. I felt bloated after dinner. I did twenty more minutes than I planned. Every session was a small repayment for a small crime.

That kind of training can still produce results. It cannot produce peace.

> **How do I stop using exercise as punishment?**
>
> Change what the workout is paying for. Punishment-training closes the loop between effort and food, which makes rest days feel like unpaid debt. Stop weighing yourself right after sessions. Train on a fixed cadence, not a guilt cadence. The same workout shifts when it stops being a receipt for what you ate.

## What Punishment-Training Actually Costs You

When exercise is payment, three things happen that nobody talks about.

First, your rest days feel morally dangerous. You skip a session and your brain starts reading the skipped session as an unpaid debt. Then you overcompensate on the next session, or you undereat, or both.

Second, you start training more when you feel worse about yourself, not when your body is ready. So your hardest workouts end up happening on your worst sleep days, your most stressed weeks, your most underfed mornings. That is the arithmetic nobody fixes.

Third, you quietly start to dislike your body more, not less. Because every session is evidence of something you did wrong. Nothing in that loop teaches you to see yourself neutrally.

## The Switch

At some point in the middle of the diet, I stopped checking my weight right after training.

That sounds trivial. It was not.

Checking the scale post-workout is the most receipt-shaped thing you can do. It closes the loop between effort and reward. The body gives you water retention. The scale gives you a small increase. The mood tanks. The next session gets angrier.

I broke that loop by not weighing until the morning after. Some days the scale moved. Some days it did not. None of it was tied to how the session felt.

Within a few weeks, the training changed shape. I still did four days. I still did the same lifts. But the sessions stopped feeling like apology.

## What Therapy-Training Looks Like

It is boring. That is the honest answer.

The workouts became calmer. Not easier. Calmer.

I walked into sessions with no specific mood to regulate. I walked out of sessions without needing the scale to validate me. The sessions started working on the rest of the day, instead of the rest of the day working on the sessions.

Appetite calmed down. Sleep got better. Stress processed itself inside the gym instead of leaking into the evening.

Body changes came more steadily once I stopped using the body as collateral.

## What This Is Not

This is not a claim that exercise is free of effort. It is not. The lifts were heavy. The intervals were hard. The recovery was real.

It is a claim that the emotional function of the session changes how the session lands.

When the workout is repayment, you train more and change less.

When the workout is maintenance of your nervous system, you train consistently and your body changes while you are not watching.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### What does punishment training actually cost you?

Three things. Rest days start feeling morally dangerous, so you overcompensate later. Hard sessions land on bad sleep and underfed mornings, because mood drives them, not readiness. And you slowly start disliking your body more, because every session is evidence of something you did wrong.

### Why does weighing post-workout reinforce the loop?

Because it ties effort to a number that is mostly water retention from the session. The scale rises slightly. The mood drops. The next session starts angrier. Breaking the post-workout weigh-in habit is one of the smallest changes that produces the biggest shift in how training lands.

### What does therapy training look like instead?

Boring, mostly. Same lifts. Same cadence. Same days. The sessions stop carrying mood. You walk in without something to regulate. You walk out without needing the scale to validate the effort. The training starts working on the rest of the day instead of the other way around.

### Doesn't this mean training has to be soft?

No. The lifts can still be heavy. The intervals can still be hard. The recovery can still be real. What changes is the emotional function of the session. The body knows the difference between hard work and apology. So does the body's response to it.

### How long does the shift take?

Usually a few weeks of training without the scale right after. The change is not announced. You notice, weeks later, that you walked into a session without a mood to regulate. That noticing is the signal that the old loop has finished closing.

```
