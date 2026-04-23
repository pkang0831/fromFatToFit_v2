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
   `https://devenira.com/blog/how-do-you-know-when-youve-reached-your-set-point` — exact
   slug is `how-do-you-know-when-youve-reached-your-set-point` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
How Do You Know When You Have Reached Your Set Point

## SEO Title
How Do You Know You've Reached Your Set Point Weight?

## Subtitle / Description
Questions and honest answers about what a set point actually is, how to know you are at one, and what it means if you want to go lower.

## Meta Description
How do you know you've reached your set point weight? Set point is a 2 to 3 kg range, not a number. Here's the 6-week test that tells you you're at one.

## Primary Keyword
how do you know you've reached your set point weight

## Secondary Keywords
- signs you are at your set point
- what is set point weight
- body set point theory
- natural weight set point
- set point weight range

## Medium Tags
- Weight Loss
- Maintenance Phase
- Body Composition
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
- Current owned-site hero: `/founder/scale-proof-20250919.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# How Do You Know When You Have Reached Your Set Point

How do you know you've reached your set point weight, and not just a slow week? The set point is a slower signal than people use it as.

A set point is one of the more misused ideas in dieting conversations.

It is useful when understood correctly. It becomes an excuse when it is not.

> **How do you know you have reached your set point weight?**
>
> Five signals together: weight stable within a 2 to 3 kg range for 8 to 12 weeks, no active dieting, hunger normalized, energy and sleep reasonable, and small deviations like a heavier weekend do not push the weight permanently. If most of those are true, you are probably at a set point for your current life.

## Q: What Is A Set Point, Actually?

A set point is the weight range your body most naturally defends, given your current habits, sleep, stress, training, and eating pattern.

It is not a fixed number handed to you at birth.

It is not immune to change.

It is a rolling equilibrium that shifts as your inputs shift. The word "set" makes it sound more permanent than it is.

## Q: How Do I Know I Have Reached Mine?

A few signals, in combination.

- Your weight has been stable within roughly a 2 to 3 kg range for 8 to 12 weeks.
- You have stopped actively dieting. You are eating in a way that feels sustainable, not restrictive.
- Your hunger has normalized. It arrives on time, responds to normal meals, and does not dominate your day.
- Your energy, sleep, and mood are reasonable. You are not running on fumes.
- Small deviations (a heavier weekend, a lighter week of travel) do not send the weight permanently up or down.

If most of those are true, the weight you are at is probably a set point for your current life.

## Q: Why Does It Feel Like I Cannot Lose More?

Because your maintenance calories have adjusted downward as you lost weight, your body is defending the current state, and your signals for hunger and fullness are tuned to this range.

To go lower, you would need to either create a new deficit below your current maintenance (which will temporarily raise hunger again) or change the inputs by adding muscle, improving sleep, or shifting activity (which can lower the defended weight over time).

Neither of these is free. Both are possible. The question is whether the cost is worth the change.

## Q: Is The Set Point Really Immovable?

No. But it is sticky.

Research on weight regulation suggests the body defends recent weights more strongly than older weights. If you hold a new weight for 12 to 24 months, that weight often becomes the new defended range.

This is why maintenance is the real skill. Not because reaching a lower number is the hard part. Because holding it long enough for your body to accept it is the hard part.

## Q: If I Am At A Set Point, Should I Stop Trying To Lose More?

This is the question most people will not let themselves ask.

The honest answer is: sometimes yes.

If you are at a weight where your habits are sustainable, your health markers are reasonable, and your life functions well, the marginal benefit of another 3 to 5 kg down is often smaller than the cost of continuing to diet.

If you want to lose more for reasons that are yours, not reasons inherited from a magazine or a photo, that is a fine decision. But it is a decision, not an obligation.

The set point is not a verdict. It is information.

## Q: What Should I Do Once I Know I Am At One?

Hold it with boring discipline for at least six months. Let the body accept this weight as the new normal.

Then decide if you want to change the inputs.

That sequence, in that order, is what separates people who lose and hold from people who lose and yo-yo.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### What is a set point weight, exactly?

The weight range your body most naturally defends given your current habits, sleep, stress, training, and eating. It is not a fixed number from birth and it is not immune to change. It is a rolling equilibrium that shifts as the inputs shift.

### Can my set point change over time?

Yes. Research suggests the body defends recent weights more strongly than older ones. Holding a new weight for 12 to 24 months often makes it the new defended range. This is why maintenance is the real skill, not just the losing phase.

### Why does it feel like I cannot lose any more?

Because maintenance calories adjusted downward as you lost weight, your body is defending the current state, and your hunger and fullness signals are tuned to this range. To go lower you create a new deficit or change the inputs. Both are possible. Both have a cost.

### Should I stop trying to lose more if I'm at set point?

Sometimes yes. If your habits are sustainable and your health markers are reasonable, the cost of pushing another 3 to 5 kg lower is often higher than the benefit. Wanting to lose more for your own reasons is fine. It is a decision, not an obligation.

### How long should I hold a new weight before it sticks?

At least six months of boring maintenance, ideally 12 to 24. The body needs time to accept the new weight as normal before you change inputs again. People who lose and hold long-term almost always stay in maintenance longer than people who rebound.

```
