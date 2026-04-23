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
   `https://devenira.com/blog/why-you-stop-losing-weight-around-month-three` — exact
   slug is `why-you-stop-losing-weight-around-month-three` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Why You Stop Losing Weight Around Month Three

## SEO Title
Why Did I Stop Losing Weight at 3 Months?

## Subtitle / Description
Around month three, most diets slow down for reasons that are not about effort. Here is what is actually happening and why the fix is not cutting more.

## Meta Description
Why did I stop losing weight at 3 months? Adaptation, fatigue, and slow calorie creep — not a broken plan. Here's what to change without escalating.

## Primary Keyword
why did I stop losing weight at 3 months

## Secondary Keywords
- weight loss plateau month 3
- stopped losing weight after 3 months
- diet slows down after three months
- plateau 3 months into diet
- month 3 weight loss wall

## Medium Tags
- Weight Loss
- Weight Loss Plateau
- Dieting
- Metabolism
- Long Game

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
# Why You Stop Losing Weight Around Month Three

Why did I stop losing weight at 3 months on a plan that worked in week one? Mostly because the body adapted to it.

Most diets slow down around month three.

Not because effort dropped. Not because the plan got worse. Not because willpower collapsed.

The body has simply become better at operating on less.

> **Why did I stop losing weight at 3 months?**
>
> Because four things stack quietly around month three. Maintenance calories drop as the body weighs less. Unconscious daily movement drops. Digestive efficiency shifts slightly. Appetite climbs. The diet did not break. The body adapted to it. Cutting harder usually backfires here. The fix is almost always a 7 to 14 day diet break.

## What The First Two Months Did

The first two months of a reasonable diet usually produce the cleanest numbers you will see.

Water and glycogen cleared in week one. Novelty held behavior steady through weeks two and three. Maintenance calories were still close to where they were before, so the deficit was meaningful.

The graph looks linear. Most of it is honest fat loss. A bit is residual water. You feel like you cracked something.

Then month three arrives and the graph bends.

## What Is Actually Happening

Four things, stacking quietly.

- Maintenance calories have dropped. A body that weighs 8 kg less requires roughly 150 to 250 fewer calories per day to maintain itself. A deficit that was 500 calories at the start is now closer to 300. The math changed while you were not looking.
- NEAT has dropped. The unconscious daily movement — fidgeting, standing, walking on phone calls — starts to decrease during sustained dieting. This is largely automatic. Your body is running a smaller version of itself.
- Digestive efficiency has shifted slightly. The body gets slightly better at absorbing calories when food is scarce. Not dramatic, but real.
- Appetite has started to rise. The gap between calories you need and calories you want is widening. Not enough to wreck the day, but enough to make adherence feel harder.

These four are not a mystery. They are the body adapting. Every serious diet produces some version of this around month three.

## Why Cutting More Usually Backfires

The intuitive response is to cut more calories. Month three is slowing, so drop another 200 calories.

This often works for a week or two. Then the body adapts again. The deficit shrinks again. You cut again. A few cycles in, you are eating 1,200 calories a day and losing nothing.

You have also trained your appetite louder, your NEAT quieter, and your muscle protein down. You are smaller, weaker, and hungrier, and the scale has not moved.

This is the most common pattern that produces a stalled, miserable, vulnerable-to-rebound dieter around month four.

## What Usually Works Better

A diet break. Not a binge. Not a cheat day. A structured increase to maintenance calories for 7 to 14 days.

During that window, NEAT tends to rise back up, appetite tends to settle slightly, and the body stops aggressively defending its current weight. When you return to deficit after the break, the deficit starts working again.

This is sometimes called a refeed or diet break, and it has been studied in several formal trials. The people who take planned breaks every 4 to 8 weeks on long diets tend to retain more muscle, report lower hunger, and have better outcomes at the 6 and 12 month marks than people who diet continuously.

The break is not quitting. The break is part of the program.

## What To Do At Month Three Specifically

- Confirm the slowdown is real (3 consecutive weeks of no scale movement, same conditions).
- Do not cut calories yet. Do not add cardio. Do not restrict further.
- Consider a 7 to 14 day maintenance phase. Eat at the calories that would produce zero weight change at your current weight. This is usually 10 to 20 percent more than your current deficit intake.
- Expect water weight to bump up 1 to 2 kg in the first days of the break. This is normal. It will come off when you return to deficit.
- After the break, return to your previous deficit. Do not deepen it. The deficit will start working again for 4 to 6 weeks. Then you may need another break.

## The Longer Frame

People who go from 100 kg to 75 kg rarely do it in a single smooth line. Almost none do. The ones who finish usually took two to four planned breaks along the way.

The month-three slowdown is not a failure point. It is the first of several scheduled rest points in a serious loss phase.

If you are here, the diet is working. It is asking you to rest before it can keep working.

---

If this piece felt familiar, the rest of this writing lives inside the Devenira world.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### Why does cutting more calories backfire here?

Because it works for a week or two, then the body adapts again. A few cycles in, you are eating 1,200 calories a day, losing nothing, and have trained your appetite louder, NEAT quieter, and muscle protein down. Smaller, weaker, hungrier — and the scale still has not moved.

### What is a diet break and how long should it be?

Seven to fourteen days at maintenance calories. Not a binge, not a cheat day. NEAT rises back up, appetite settles slightly, and the body stops aggressively defending its current weight. When you return to deficit, the deficit starts working again for another four to six weeks.

### Will I gain weight during a diet break?

Yes, in the form of water and glycogen. Expect 1 to 2 kg in the first few days. That is normal and not fat. It comes off when you return to deficit. The discomfort of seeing the scale rise is the price of breaking the plateau cleanly.

### How do I know the slowdown is a real plateau and not a slow week?

Three consecutive weeks of no scale movement under your usual conditions, with no shape change either. Less than that is noise. Most month-three slowdowns turn into resumed loss within a couple of weeks if the response is patient instead of aggressive.

### Are diet breaks studied or just a coaching trick?

Studied, in several formal trials. People who take planned 7 to 14 day breaks every 4 to 8 weeks on long diets tend to retain more muscle, report lower hunger, and have better outcomes at six and twelve months than people who diet straight through.

```
