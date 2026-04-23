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
   `https://devenira.com/blog/the-same-number-on-the-scale-feels-different-at-30-than-at-20` — exact
   slug is `the-same-number-on-the-scale-feels-different-at-30-than-at-20` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
The Same Number on the Scale Feels Different at 30 Than at 20

## SEO Title
Why Does the Same Weight Feel Different as You Age?

## Subtitle / Description
Why does the same weight feel different as you age? Same number on the scale, different body underneath it. The first time I weighed exactly 75 kg, I was 22. The second time I weighed exactly 75 kg, I was around 30. The number was identical. The body underneath it was not. Not even close.

## Meta Description
Why does the same weight feel different as you age? 75 kg at 22 isn't 75 kg at 32 — composition shifts under the number. Here's what the scale misses.

## Primary Keyword
why does the same weight feel different as you age

## Secondary Keywords
- body composition changes in your 30s
- same weight different body shape
- muscle loss with age sarcopenia
- body fat increase with age
- losing weight after 30 harder

## Medium Tags
- Weight Loss
- Body Composition
- Aging
- Health
- Fitness

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/scale-proof-20250919.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# The Same Number on the Scale Feels Different at 30 Than at 20

Why does the same weight feel different as you age? Same number on the scale, different body underneath it.

The first time I weighed exactly 75 kg, I was 22 years old.

The second time I weighed exactly 75 kg, I was around 30.

The number was identical.

The body underneath it was not. Not even close.

This is the part most people are not warned about. The scale is a long-running instrument that does not adjust for the slow work the rest of the body does between readings. The number stays the same. The body it describes does not.

> **Why does the same weight feel different as you age?**
>
> Because the same number describes a different body. Across decades, untrained adults usually lose a small amount of muscle and add a small amount of fat each year, even at constant weight. Glycogen storage drops. Recovery slows. The scale stays still while the body it describes quietly shifts underneath.

## What changes underneath the same number

Three things shift quietly across decades, even at constant weight.

Body composition shifts. The default trajectory for an adult who does not deliberately train is to lose a small amount of muscle and add a small amount of fat each year, even at constant weight. Over a decade, the difference can be visible without the scale moving.

Water and glycogen storage shifts. Younger bodies, especially trained ones, hold more glycogen and the water that comes with it. That makes the same scale weight look fuller, leaner, more athletic. Less glycogen storage shows up as a softer version of the same number.

Recovery shifts. The body's ability to bounce back from a bad week — bad sleep, high sodium, alcohol, low protein — slows in small steps. The same week of mild damage that disappeared in three days at 22 might take seven days at 32. Same body, same lifestyle, slower clearing.

The number stayed still. The body it described did not.

## Why the older 75 kg felt heavier

When I was 22 and at 75 kg, I had no idea how much of my body was muscle. I just knew I felt light, recovered fast, slept on demand, and could eat almost anything.

When I returned to 75 kg later in life, I had less muscle, slightly more fat at the waist, slower recovery, and a much louder appetite signal in the evenings.

The scale could not tell those bodies apart. The clothes could.

Pants that fit at 75 kg in my early twenties did not fit at 75 kg later. Specifically, the waist was different. The shoulders were narrower. The thighs were softer.

I had not gotten heavier. I had gotten different.

## What this means for goal-weight setting

If you are choosing a target weight today based on a number that worked for you a decade ago, you may be choosing the wrong number.

The body that produced that number then was made of different things than the body trying to produce that number now.

A more useful goal is composition. A waist measurement. A clothing size. A photo at a defined posture. A strength baseline. Those signals stay honest across decades. The scale alone does not.

The scale can still be a useful instrument. It is just no longer a complete one.

## What changes if you train

Training, especially resistance training, slows almost all of the underneath shifts.

Trained adults in their thirties hold more lean mass than untrained adults of the same age, often by several kilograms. They store more glycogen. They recover faster. The same scale number, on a trained body, looks and behaves much closer to the younger version of itself.

This is not "bodies of the past are unreachable." It is that the path to a given number now usually requires more training and less casual eating than the path to the same number then.

You can usually get back to the number. You will get there through slightly different work.

## What changes if you do not train

If you do not train and you arrive at the same number through diet alone, the body that meets you at that number will be lighter on muscle, lower on glycogen, and softer in places that used to be firm.

The scale is satisfied. The mirror is confused. The clothes do not fit the way they did.

This is the most common version of the "I am at my old weight and it does not look like my old weight" complaint. The number was met. The body that produced the number originally was not rebuilt.

Diet alone is enough to move the scale. It is not enough, by middle age, to rebuild the composition that the scale is silent about.

## What changes about the recovery curve

The bad-week recovery is the part that catches most people off guard.

In your early twenties, a heavy weekend, three nights of bad sleep, and four boozy dinners might leave a 1.5 kg bump on the scale that disappears by Wednesday.

In your thirties, the same weekend leaves a similar bump that takes until Sunday or longer to clear. The body has not changed its rules. It has changed its speed.

This matters because the noise window has widened. Daily and weekly fluctuations are larger, last longer, and look more like real change than they used to. If you read the scale daily and react quickly, you will overreact more often than you used to, even at the same actual rate of progress.

The fix is not weighing less often. The fix is reading the scale on a longer timescale than you read it on at 22.

## What changes about the food side

A 22-year-old body burns through a 1,000-calorie evening with relatively little metabolic fuss. The fluctuation is small, the sleep stays clean, the next day arrives mostly normal.

A 32-year-old body running the same 1,000-calorie evening will often see a louder next-day signal. More water held. Worse sleep. More appetite the following day.

Same input. Different downstream cost.

This is part of why programs that worked in your early twenties stop working at the same intensity later. The intake is the same. The body's response to it has gotten more honest.

## What does not change

Several things do not change with age, and they are the things worth investing in.

Energy balance still works. Eat slightly less than you burn, over time, and weight comes off. The clock is the same.

Strength training still builds muscle in your thirties, forties, and beyond. The rate is slower than at 22, but the direction is the same.

Protein still preserves lean mass during loss. Sleep still amplifies recovery. Walking still adds free energy expenditure with low cost.

The basics did not change. The tolerances around the basics narrowed.

## What I tell people who are frustrated about returning to a number

The number is not the wrong number. The reading of the number is.

The number used to mean: this body, this composition, this recovery, this firmness.

The same number now means: a different body, a different composition, a different recovery, a different firmness.

Neither body is wrong. They are just not the same body, and the scale was never going to tell you that.

If you want the older body back, the path runs through composition, not through chasing a single digit.

## The line worth keeping

The scale is a long-running instrument that does not adjust for the work the body does in the years between readings.

A number is a sample. A composition is the body. A decade is a different instrument entirely.

Read the number with the right age in mind. The scale will not do that for you.

---

If this piece felt familiar, the rest of this writing lives inside the Devenira world.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### What changes underneath the same number?

Three things, slowly. Body composition shifts toward less muscle and more fat unless training fights it. Water and glycogen storage drops, especially in untrained bodies. Recovery from a bad week slows. Same scale weight, very different body. The clothes know it before the scale does.

### Should I chase the weight I had a decade ago?

Probably not, at least not as a single number. The body that produced that number then was made of different things than the body trying to produce it now. Composition is the more useful target. A waist measurement, a clothing size, a strength baseline — those stay honest across decades.

### How much does training change this trajectory?

A lot. Trained adults in their thirties and beyond hold more lean mass, store more glycogen, and recover faster than untrained adults of the same age. The same scale number on a trained body looks and behaves much closer to the younger version of itself.

### Why does the bad-week recovery take longer with age?

Because the body has not changed its rules; it has changed its speed. A heavy weekend that cleared by Wednesday at 22 takes until Sunday at 32. Daily fluctuations are larger and last longer. The fix is not weighing less. It is reading the scale on a longer timescale.

### What hasn't changed across decades?

Energy balance still works. Strength training still builds muscle. Protein still preserves lean mass during a deficit. Sleep still amplifies recovery. Walking still adds free expenditure. The basics did not change. The tolerances around the basics narrowed. The same plan is just less forgiving than it used to be.

```
