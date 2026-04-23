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
   `https://devenira.com/blog/losing-weight-is-not-the-same-as-getting-leaner` — exact
   slug is `losing-weight-is-not-the-same-as-getting-leaner` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Losing Weight Is Not the Same as Getting Leaner

## SEO Title
What's the Difference Between Weight Loss and Fat Loss?

## Subtitle / Description
You can lose weight and not get leaner. You can get leaner and not lose weight. The scale is telling you one thing, the mirror is telling you another.

## Meta Description
What's the difference between weight loss and fat loss? You can drop 5 kg without getting leaner. Here's the composition test the scale can't run.

## Primary Keyword
what's the difference between weight loss and fat loss

## Secondary Keywords
- weight loss vs fat loss difference
- losing weight but not leaner
- getting lean not just skinny
- fat loss vs body recomposition
- leaner body same weight

## Medium Tags
- Weight Loss
- Fat Loss
- Body Composition
- Body Recomposition
- Fitness

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/body-composition-proof-20251221.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# Losing Weight Is Not the Same as Getting Leaner

What's the difference between weight loss and fat loss? One moves the scale; the other actually changes how you look.

At one point in the middle of my transformation, I weighed the same for eight weeks.

My clothes stopped fitting anyway.

Looser around the waist. Tighter around the shoulders. The same number. A different body.

I spent those eight weeks mostly frustrated because I did not yet understand what was happening.

> **What is the difference between weight loss and fat loss?**
>
> Weight is total mass: water, bone, organ, muscle, fat, food in transit. Fat loss is just the fat portion. You can lose weight and get less lean if you lose mostly muscle, or stay the same weight and get leaner through recomposition. The scale weighs everything. It cannot tell those stories apart.

## The Two Lines Do Not Always Move Together

Weight loss and getting leaner are two different processes. They usually overlap. They do not have to.

Weight is total mass. Water, bone, organ, muscle, fat, food in transit. It is one number.

Leanness is the ratio of fat to non-fat tissue. Specifically, it is usually about body fat percentage and how the fat distributes visually.

You can lose weight and get less lean (if you lose mostly muscle). You can stay the same weight and get more lean (if you lose fat and gain muscle). You can even gain weight and look visibly leaner, if the gain is muscle and the loss is fat.

The scale cannot tell these apart. It weighs everything.

## Why The Scale Misses This

The scale is measuring total mass. It does not care what the mass is made of.

If you lose 2 kg of fat and gain 1 kg of muscle, the scale moves 1 kg. You are a different body. The scale is telling you that one week barely happened.

This is why some people stop losing weight and notice their clothes still changing. Their composition is still shifting. The scale is just the wrong instrument for that week.

## What I Did Not Notice For A While

During the eight-week plateau, I kept weighing daily and treating the flat number as the story.

I was also training consistently. Four days a week. Lifting. Eating roughly at maintenance.

What was actually happening was body recomposition. Slow fat loss. Slow muscle gain. The two canceling out on the scale.

By week nine, I did a body composition test and realized the fat mass had dropped by about 2.5 kg and the lean mass had risen. At the same scale number.

None of my daily weigh-ins had told me this. All my clothing had.

## What Matters For Most People

Unless you are an athlete, body composition matters more than weight. For most people, the actual goal is not weigh less. The actual goal is look and feel leaner. Those goals are related but not identical.

A 70 kg person at 25 percent body fat looks softer than a 72 kg person at 18 percent body fat. The heavier one is the leaner one.

People who only track scale weight for years sometimes end up at their target number and still feel soft, because they lost more muscle than fat on the way down. This is most common with severe cardio-only dieting.

People who track the combined picture, slowly, over months, tend to arrive at a body they actually wanted.

## How To Actually Track It

You do not need a lab.

- Photos every two weeks, same spot, same lighting, same clothing. Looking at groups of four.
- Tape measurements every two weeks. Waist, chest, hip, thigh, arm. This picks up composition changes the scale misses.
- Clothing as evidence. Same jeans, same shirt, every two weeks. Fit tells the truth.
- The scale once a week as a reference point, not the whole story.

If you only use one of these, use photos. If you use two, use photos and measurements. The scale alone is the least useful of the four.

## The Line I Wish I Had Heard Earlier

Getting leaner is a composition story told over months.

Losing weight is a mass story told over weeks.

They are not the same number and they are not the same clock.

---

I write about weight loss, appetite, body image, and the slow work of learning how to read the body without panic.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### How can I tell which one I'm doing?

Track three things together: weekly scale average, tape measurements at waist and hip, and photos every two weeks under matched conditions. If the scale moves but measurements do not, you are losing the wrong tissue. If measurements move but the scale does not, you are recomposing.

### Can you gain weight and look leaner?

Yes. If the gain is muscle and the loss is fat, the scale moves up while the body looks visibly leaner. A 70 kg person at 25 percent body fat looks softer than a 72 kg person at 18 percent. The heavier one is the leaner one.

### Why do people lose muscle on a diet?

Two reasons: protein intake is too low, or the deficit is so aggressive the body sheds tissue indiscriminately. Adequate protein (1.6 to 2.2 g/kg) plus resistance training tilts the loss toward fat and away from muscle. Cardio-only severe diets do the opposite.

### Is body recomposition possible at any age?

Yes, though the rate slows with age. Trained adults in their thirties, forties, and beyond still build muscle and lose fat at the same time, just more slowly than beginners. The direction is the same. The clock runs differently.

### Should I care about body fat percentage instead of weight?

For most people, yes. Unless you are an athlete with a weight class, the actual goal is composition, not mass. Track a waist measurement, a clothing size, and photos. Use the scale as one of four signals, not the sentence.

```
