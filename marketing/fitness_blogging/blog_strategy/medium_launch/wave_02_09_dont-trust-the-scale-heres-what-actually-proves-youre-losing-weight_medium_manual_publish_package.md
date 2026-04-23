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
   `https://devenira.com/blog/dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight` — exact
   slug is `dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Don’t Trust the Scale—Here’s What Actually Proves You’re Losing Weight

## SEO Title
How to Know You're Losing Weight Without the Scale

## Subtitle / Description
Here's how to know you're losing weight without the scale, with proof that holds up across a week. The receipt is rarely a number. A lot of people want fat loss to come with a receipt. But the scale is one witness, not the whole case. Real proof often shows up in shape, fit, firmness, and repeated visual change.

## Meta Description
How to know you're losing weight without the scale: 5 signals fat loss leaves before the number moves. Clothes, jaw, posture — and 2 most people miss.

## Primary Keyword
how to know you're losing weight without the scale

## Secondary Keywords
- signs you are losing fat not water
- non scale victories weight loss
- how to tell if losing fat
- ways to track fat loss
- visual signs weight loss

## Medium Tags
- Weight Loss
- Fat Loss
- Progress Photos
- Body Composition
- Dieting

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
# Don’t Trust the Scale—Here’s What Actually Proves You’re Losing Weight

Here's how to know you're losing weight without the scale, with proof that holds up across a week. The receipt is rarely a number.

A lot of people want fat loss to come with a receipt.

One clean number. One obvious answer. One cheerful little dashboard that says: yes, congratulations, your body is changing correctly.

Instead, they get this: the scale moves weirdly, the mirror feels moody, and the belly looks different on some days and rude on others.

So now they ask the question I hear constantly: how do I know this is real weight loss and not fake progress?

> **How can I tell I'm losing weight without the scale?**
>
> Look at shape, fit, firmness, and where the body is changing. The waistline on familiar clothes loosens before the scale fully cooperates. The upper abdomen feels less pushed out. The lower section softens and shifts. Real fat loss is often visible before it becomes official on a number.

## Not All Belly Change Looks the Same

Fat does not always sit or show up the same way.

Some people carry more around the organs and upper abdomen. Some carry more in softer, lower, more subcutaneous areas. Some have posture and muscle issues that change how the midsection projects.

So if you are waiting for weight loss to look identical on every body, you are going to stay confused for a long time.

## The Better Question Is Not “Am I Lighter?”

One of the best clues is not “am I lighter?” but “what is changing?”

That is the grown-up question.

What part of my body feels different? What looks less pushed out? What hangs differently? What fits differently?

People ignore these clues because they are messier than a scale reading. Too bad. Messier data is still data.

## Softness, Firmness, Shape, and Fit All Tell Stories

If the upper abdomen starts feeling less pushed out, that matters. If the lower section softens and shifts differently, that matters. If the waistline on your usual clothes changes before the scale fully cooperates, that matters too.

People often want proof while dismissing the exact body evidence that would calm them down, because it is not as neat as a number.

I understand that. I also think it keeps them trapped longer than necessary.

## The Scale Is One Witness. It Is Not the Whole Case

The scale can tell you something. It just cannot tell you everything.

And if you treat one witness like the full trial, you will keep missing what the body is actually showing you in shape, tension, softness, posture, and fit.

Then people say there are no signs of progress. There are. They just wanted the lazy kind.

## What to Do Instead

- Stop asking only whether your total weight changed.
- Use photos, fit, feel, and shape together.
- Be specific about where changes are showing up.
- Do not let a quiet scale erase obvious body evidence.

Track the body visually. Compare over time. Notice what your shape is doing, not just what gravity says on one morning.

## Closing

Real weight loss is often visible before it feels official.

And people who wait for the scale to approve it first waste a lot of peace.

If your only proof of progress is a number that keeps changing its personality, you are missing too much.

Use a better lens. One scan is a number. Weekly check-ins are proof.

If this piece felt familiar, the rest of my writing lives on [Devenira](https://devenira.com/blog).

I'm pkang, a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.

## Frequently Asked Questions

### What signals show up before the scale moves?

How clothes fit at the waist. Whether the upper abdomen feels less pushed out. How the lower section sits. Where shape is loosening or shifting. None of these are as neat as a number, but they often arrive earlier than the scale agrees to.

### Why doesn't fat loss look the same on every body?

Because fat does not sit or leave the same way for everyone. Some people carry more around the upper abdomen, some lower, some at the back or thighs. Posture and muscle change how the midsection projects. Waiting for one universal pattern keeps people confused for years.

### Are progress photos more reliable than the mirror?

Usually yes, if the conditions match. The mirror reads through the day's mood. A photo taken in the same light, same posture, same time of day every week strips most of that out. Looked at in groups of four, photos catch what the daily mirror misses.

### What if my clothes look different but the scale hasn't moved?

Your body composition probably shifted. The scale weighs everything at once: water, gut content, muscle, fat. A flat number can mean fat down and a little muscle up. Clothes catch what the scale is silent about. Trust the fit before the number.

### How long should I wait before deciding nothing changed?

Three weeks at minimum. Most weeks contain enough water and digestive noise to fake a stall in either direction. Comparing weekly photos, weekly waist measurements, and a rolling weekly weight average over three weeks tells you whether the body actually held or moved.

```
