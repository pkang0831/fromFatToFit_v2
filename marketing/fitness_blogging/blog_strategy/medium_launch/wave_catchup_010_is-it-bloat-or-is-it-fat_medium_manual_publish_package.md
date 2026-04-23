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
   `https://devenira.com/blog/is-it-bloat-or-is-it-fat` — exact
   slug is `is-it-bloat-or-is-it-fat` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Is It Bloat or Is It Fat

## SEO Title
Is My Stomach Bloat or Fat? How to Tell

## Subtitle / Description
A practical guide to distinguishing temporary bloat from real fat gain, so you stop reacting to noise as if it is signal.

## Meta Description
How to tell if my stomach is bloat or fat: the body can't make 1.5 kg of fat overnight. Here's the 3-question test that ends most morning panic.

## Primary Keyword
how to tell if my stomach is bloat or fat

## Secondary Keywords
- is my belly bloat or fat
- bloating vs belly fat difference
- how to tell bloat from fat gain
- stomach swelling vs fat
- bloat feels hard belly fat soft

## Medium Tags
- Weight Loss
- Bloating
- Water Weight
- Nutrition
- Body Image

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/water-weight-proof-20251031.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# Is It Bloat or Is It Fat

Here's how to tell if your stomach is bloat or fat: time it across days, not minutes. Bloat moves; fat doesn't.

This is one of the most useful questions anyone can ask.

It is also one of the most mis-answered.

> **How do I tell if my stomach is bloat or fat?**
>
> Time it across days, not minutes. Bloat moves; fat does not. The body cannot synthesize 1.5 kg of fat overnight — that would take roughly 11,000 calories above maintenance in a day. Real fat gain is slow, gradual, and survives a normal week. If the spike clears in three days, it was never fat.

## Q: I Gained 1.5 kg Overnight. Is That Fat?

No.

The body generally cannot synthesize 1.5 kg of fat in one day. To store that much fat you would need to eat roughly 11,000 calories above maintenance in 24 hours. You would remember doing it.

What you are seeing is almost always water, glycogen, salt balance, bowel contents, or some combination of the four.

## Q: Then What Does Real Fat Gain Look Like On The Scale?

Slow. Quiet. Unglamorous.

Real fat gain usually looks like a gradual, unexplained drift of 0.5 to 1 kg over 2 to 4 weeks that does not reverse after a normal day. The daily noise is still there, but the trendline is moving in one direction.

If the scale is up today and back to baseline in three days, it was not fat.

## Q: How Can I Tell Which Is Which In The Moment?

You usually cannot, in the moment. That is the point.

Waiting is the answer.

Fat does not appear overnight. Water does. Salt does. Carbs do. Periods do. Poor sleep does. Travel does. Stress does. Almost everything that makes the scale move quickly is not fat.

If the scale spikes, wait four days and weigh again under your usual conditions. If it is still up, and up for three consecutive measurements under usual conditions, then it is worth looking at.

## Q: What About The Mirror?

The mirror is worse than the scale for this.

Bloat changes how you look dramatically in the mirror within hours. Fat changes how you look slowly over weeks. If you thought you looked smaller yesterday and larger today, you are looking at bloat.

A week of mirror-same is more meaningful than a week of mirror-changes.

## Q: Is It Ever Worth Panicking About One Day?

No.

There is no decision you make on a one-day spike that a patient decision three days later would not also catch. The cost of over-reacting is emotional, behavioral, and usually leads to a binge or a skipped meal that does more damage than the original blip.

The honest answer is: it is almost always bloat, and even when it is not, waiting does not cost you anything.

---

If this piece felt familiar, the rest of this writing lives inside the Devenira world.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### Can I really gain 1.5 kg of fat overnight?

No. That would require roughly 11,000 calories above maintenance in 24 hours, and you would remember doing it. Overnight scale jumps of 1 to 2 kg are almost entirely water, sodium, glycogen, and food still moving through digestion. Fat does not arrive that fast.

### What does real fat gain look like on the scale?

Slow, quiet, and unglamorous. Usually a gradual drift of 0.5 to 1 kg over two to four weeks that does not reverse after a normal day. The daily noise is still there, but the trendline is moving in one direction across multiple weeks.

### How can I tell which is which in the moment?

Usually you cannot, in the moment. That is the point. Wait four days, weigh again under your usual conditions. If the spike has cleared, it was bloat. If it has held across three consecutive measurements under usual conditions, then it is worth looking at.

### What about how the mirror looks?

The mirror is worse than the scale for this. Bloat changes how you look dramatically within hours. Fat changes how you look slowly over weeks. If you thought you looked smaller yesterday and larger today, you are looking at bloat, not at a body change.

### Is it ever worth panicking about a one-day spike?

No. There is no decision you can make on a one-day spike that a calmer decision three days later would not also catch. Over-reacting almost always leads to a binge or skipped meal that does more damage than the original blip. Waiting costs nothing.

```
