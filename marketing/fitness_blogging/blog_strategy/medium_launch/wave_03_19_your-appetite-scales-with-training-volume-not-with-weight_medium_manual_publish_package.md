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
   `https://devenira.com/blog/your-appetite-scales-with-training-volume-not-with-weight` — exact
   slug is `your-appetite-scales-with-training-volume-not-with-weight` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Your Appetite Scales With Training Volume, Not With Weight

## SEO Title
Why Am I So Hungry After Lifting Weights?

## Subtitle / Description
Why am I so hungry after lifting weights, even on weeks the scale didn't move? Hunger reads training volume, not body weight. Appetite is not a function of how much you weigh. It is a function of how much you trained, how you slept, and what your body is rebuilding. The scale is not what your hunger is reading.

## Meta Description
Why am I so hungry after lifting weights? Appetite tracks training volume and recovery, not body weight. Most diet hunger is a repair signal, not failure.

## Primary Keyword
why am I so hungry after lifting weights

## Secondary Keywords
- appetite after workout
- hungry on training days
- strength training increases appetite
- training volume hunger
- post workout hunger weight loss

## Medium Tags
- Weight Loss
- Appetite
- Hunger
- Strength Training
- Recovery

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/sleep-reflective-20260106.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# Your Appetite Scales With Training Volume, Not With Weight

Why am I so hungry after lifting weights, even on weeks the scale didn't move? Hunger reads training volume, not body weight. Appetite is not a function of how much you weigh. It is a function of how much you trained, how you slept, and what your body is rebuilding. The scale is not what your hunger is reading.

People assume their appetite scales with their weight.

The intuition is that as you get smaller, you should need less food, so you should be less hungry. As you get bigger, the opposite. The relationship feels straightforward.

The intuition is mostly wrong. Appetite, day to day and week to week, scales much more closely with training volume, sleep quality, and the body's recent repair workload than with what the scale says you weigh.

This is not a small distinction. It changes what to do when hunger is loud, and it explains why two people at the same weight can have wildly different appetite signals on the same day.

> **Why am I so hungry after lifting weights?**
>
> Because appetite tracks training volume and recovery, not body weight. The body's energy demand spikes 6 to 36 hours after a real session and stays elevated through the recovery window. Add a poor night of sleep and the signal climbs further. Most diet hunger is not failure. It is a repair signal asking for fuel.

## What your appetite is actually responding to

Three input variables matter much more than weight on a day-to-day basis.

Training volume in the past 24 to 72 hours. The body's energy demand spikes after meaningful training and stays elevated through the recovery window. A heavy lifting day or a long cardio session sends a hunger signal 6 to 36 hours later that has very little to do with what you weigh and a great deal to do with what you just asked the body to do.

Sleep quality across the past three to five nights. Sleep-deprived bodies are hungrier the next day. The relationship is direct and dose-dependent — fewer hours of sleep produces more hunger, especially in the afternoon and evening. A 3-night stretch of 6-hour nights versus 7.5-hour nights routinely produces 200 to 400 calories of additional hunger demand, with no other variable changing.

Recent repair load. The body in active rebuild — recovering from a hard week, healing tissue, fighting a low-grade inflammation, integrating a training stimulus — runs hungrier than the same body at rest. The signal does not always announce itself as "I am rebuilding"; it just shows up as elevated appetite for several days.

The appetite read the workload. It did not read the bathroom scale.

A 70 kg lifter who trained heavy yesterday and slept 6 hours the night before will be hungrier today than a 95 kg sedentary person who slept 8 hours. Same Tuesday, different appetite signals, different bodies. Weight is the smaller variable.

## Why people misread their own appetite

Three reasons.

The cultural framing is wrong. Diet narratives treat appetite as a function of body size. "You are bigger, so you need more" or "you are smaller, so you should need less." The math is true at maintenance over weeks and months. The math is false at the daily and weekly level, where most appetite reading happens.

The scale is the most visible variable. People weigh daily, see the number, and look for an appetite explanation that involves the number. The actual drivers — training, sleep, repair — are invisible on a scale.

The fast variables get attributed to the slow ones. The body's weight changes slowly. Appetite changes daily. When daily appetite spikes, the brain looks for a slow-variable explanation ("I'm holding extra weight, so my body is asking for more food") rather than the obvious fast-variable one ("I lifted heavy yesterday and slept poorly").

The result is people interpreting normal training-volume hunger as a sign that their body wants to gain weight. It does not. It wants to repair what they trained.

## Why this matters during a cut

A cut layered on a hard training week produces louder hunger than a cut on a deload week. Same calorie deficit. Same body. Different appetite.

Most cuts run into trouble in week 4 to 8 because two things are stacking that the user is not separating:

- The cumulative energy debt from the deficit (real, slow, expected)
- A spike in training volume that is adding repair demand on top (real, fast, often unnoticed)

The user reads both as "the cut is getting harder" and adds emotional weight to that reading. The actual fix is not "more discipline." The fix is recognizing that the training volume drove most of this week's spike, and either temporarily ease the training load or temporarily add 100 to 200 calories of protein-forward food to absorb the repair demand without breaking the deficit framework.

People keep diagnosing appetite spikes as "I want to give up." Most of them are "I trained hard and slept badly. The body is asking for fuel."

## Why this matters during maintenance

Maintenance shows the same pattern at a different baseline.

A maintenance week with normal training and normal sleep runs a quiet appetite signal that is easy to satisfy. A maintenance week that adds a fourth training session, drops sleep by 45 minutes per night, and increases life stress will produce a louder appetite signal that often gets misread as "the body is trying to gain weight."

It is not. The body is asking for the energy that the training volume consumed and the sleep failed to fully restore.

The right response in maintenance is to feed the signal — add 150 to 250 calories of clean food, give it 7 to 10 days, and watch where the body settles. The wrong response is to fight the signal with cut-era discipline. The wrong response produces the binge-then-rebound pattern.

## What the timeline actually looks like

For most people, training-driven appetite arrives 6 to 36 hours after the session.

A heavy lower-body session on Monday morning often shows up as elevated hunger Tuesday afternoon and evening, sometimes Wednesday morning. Not Monday itself.

A long cardio session on Sunday tends to peak Monday afternoon.

Sleep deprivation is faster — the appetite signal is usually loud the same day and the day after a poor night.

If you are tracking your appetite alongside your training and sleep logs (not just calorie totals), the pattern usually shows up cleanly within 3 to 4 weeks of looking. If you are only tracking weight and calories, the pattern stays invisible.

## Why athletes and lifters know this and most dieters do not

Athletes are trained to read body signals through the lens of training and recovery. A coach explains that the soreness, the appetite, the sleep need are downstream of the training program. The body is interpreted in terms of what was demanded of it.

Most dieters are trained to read body signals through the lens of weight and discipline. A diet program explains that hunger is friction to push through. The body is interpreted in terms of how much it weighs and how much willpower the person has.

Both framings are doing the same job — interpreting hunger — but only the athlete framing maps onto the actual physiology of the signal. The dieter framing routinely produces "the diet is failing" diagnoses for what are really "you trained hard and slept badly" days.

If you can borrow the athlete's framing inside the diet, the appetite signal stops being scary. It just becomes data about what you did to the body.

## What I started doing once I saw the pattern

I added two columns to my weekly tracking.

The first was a 1-to-5 rating of training intensity that week.

The second was an average sleep number across the prior 7 nights.

I noticed within four weeks that my "hard" appetite weeks lined up almost perfectly with high training intensity + low sleep, and my "easy" appetite weeks lined up with normal training intensity + good sleep. Body weight changed in the background but had almost no week-to-week relationship with how hungry I felt.

After that, my response to a hungry week shifted. Instead of asking "is the diet broken," I asked "did I train harder than usual" and "did I sleep worse." The answer was almost always yes to one or both.

The fix moved upstream — to the sleep, mostly — rather than downstream into restriction. The appetite signal calmed within a week of fixing the upstream variable. The diet kept running.

## What to do practically

Track training volume and sleep alongside calories and weight. Without those two columns, the appetite story is invisible.

When appetite is loud, ask: training? sleep? before asking: diet?

Allow training-driven hunger to be fed. The repair demand is real. Adding 100 to 200 calories of protein-forward food on a hard training day is not breaking the diet. It is feeding the work the diet is supposed to support.

Treat the scale as the slow variable. Treat appetite as the fast variable. Do not confuse them.

## The line worth keeping

Appetite is the body asking for fuel for the work it just did.

Weight is what the body looks like over months.

The appetite is reading the workload. It is not reading the scale.

If you keep diagnosing daily hunger as a weight problem, you will keep applying restriction to a signal that was asking for repair.

---

If this piece felt familiar, the rest of this writing lives inside the Devenira world.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).



## Frequently Asked Questions

### What variables actually drive day-to-day appetite?

Three matter more than weight. Training volume in the past 24 to 72 hours. Sleep across the past three to five nights. The body's recent repair load. A lifter who trained heavy yesterday and slept six hours will be hungrier than a sedentary person who slept eight.

### When does training-driven hunger actually show up?

Six to 36 hours after the session. A heavy lower-body Monday morning often shows up as elevated hunger Tuesday afternoon and evening. A long Sunday cardio session tends to peak Monday afternoon. Sleep deprivation is faster — usually the same day and the day after a poor night.

### Should I feed training-driven hunger or push through?

Feed it, especially on hard training days. The repair demand is real. Adding 100 to 200 calories of protein-forward food on a heavy session day is not breaking the diet. It is feeding the work the diet is supposed to support. Pushing through usually backfires by week's end.

### How can I tell if my hunger is training, sleep, or actual food shortage?

Track training intensity and a rolling sleep average alongside calories. Within three to four weeks the pattern usually shows. Loud-appetite weeks line up with high training and low sleep. Quiet weeks line up with the opposite. Body weight has almost no week-to-week relationship with how hungry the body feels.

### Why don't more dieters know this?

Because diet narratives frame appetite as a function of body size and willpower. Athletes are taught to read appetite through training and recovery. The first framing maps onto the actual physiology. The second produces 'the diet is failing' diagnoses for what are really hard-training nights.

```
