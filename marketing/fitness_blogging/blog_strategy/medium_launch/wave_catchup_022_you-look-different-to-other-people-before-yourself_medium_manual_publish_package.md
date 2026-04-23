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
   `https://devenira.com/blog/you-look-different-to-other-people-before-yourself` — exact
   slug is `you-look-different-to-other-people-before-yourself` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
You Look Different to Other People Before You Look Different to Yourself

## SEO Title
Why Do Others Notice My Weight Loss Before I Do?

## Subtitle / Description
Other people see your body change before you do. The delay is not vanity. It is how self-perception actually works.

## Meta Description
Why do others notice my weight loss before me? They run the opposite experiment — months between visits. Here's the perception lag in plain terms.

## Primary Keyword
why do others notice my weight loss before me

## Secondary Keywords
- people notice weight loss before self
- how much weight loss before others notice
- weight loss face first noticed
- why can't I see my own weight loss
- weight loss blind spot perception

## Medium Tags
- Weight Loss
- Body Image
- Self Image
- Progress Photos
- Transformation

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/mirror-middle-checkin-20250716.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# You Look Different to Other People Before You Look Different to Yourself

Why do others notice my weight loss before me? Because your brain updates the body image last, not first.

People you have not seen in a few months will notice your body has changed.

You will not have noticed yet.

This is not modesty. It is not vanity. It is how your brain is built.

> **Why do others notice my weight loss before I do?**
>
> Self-perception updates slowly. You see your body every morning in the same mirror, so gradual change disappears into familiarity. Someone who has not seen you in three months gets a clean before-and-after read. The internal map usually runs three to six months behind the body. The compliment is data, not flattery.

## The Gap

Almost everyone who has lost meaningful weight has had the same disorienting moment.

An acquaintance says you look great, have you lost weight, and you feel simultaneously pleased and dishonest, because the mirror you saw that morning still looked like the old you. You received a compliment you cannot match to your own perception.

Then the same thing happens from a different person. Then a family member says it on a video call. Then a photo gets taken that looks like a stranger.

The outside world is seeing a body your head is still catching up to.

## Why They See It First

Self-perception of body size updates slowly. You are looking at yourself every morning, in the same mirror, at the same angle, in the same lighting, with the same hair. That continuous exposure is what makes change invisible to you. You are the least well-positioned observer of your own transformation.

Other people are running the opposite experiment. They saw you in July. They see you in November. The two readings are months apart with no in-between data. Their delta is the clearest signal in the room.

The people who see you less often get a clearer reading than you do.

## What This Means In Practice

Three practical things.

- First, the compliment is not flattery. If someone you have not seen in three months says you look different, you look different. Outside observers are usually directionally correct even when they are polite about the magnitude.
- Second, your mirror is the unreliable narrator in this story. Photos every two weeks, in the same spot, are more honest than daily mirror checks, because photos flatten the continuous exposure into comparable snapshots.
- Third, the delay in your own perception is normal and expected. Expect the head to run about three to six months behind the body. This is often cited by people who work with post-weight-loss body image professionally, though the exact timing varies.

## Why The Delay Exists At All

Self-image seems to be anchored by something slower than visual input. Some combination of memory of a body, emotional relationship with that body, and habitual self-description continues to run after the body has moved on.

A person who spent five years being a specific size does not update that internal map in a week of scale changes. The internal map updates gradually, usually pulled forward by external evidence: compliments, photos, clothes fitting differently, a stranger asking a new question.

That is why the outside world is part of the recalibration. Not in a shallow way. In a functional way.

## What To Do With This

Stop asking the mirror for validation it cannot yet give. The mirror is running on old data.

Start collecting external evidence without chasing it. Photos from a consistent setup. Comments people spontaneously offer, noted without fishing. Clothes that fit or do not fit. Your gait. Your stamina. Your resting heart rate.

When the internal map and the external evidence disagree, the evidence is more current than the map.

## The Uncomfortable Part

You will reach a point where other people treat you as a person with your new body, and you still feel like a person with your old body, and this gap will be strange. It may last months.

That is part of the work. It is not a sign you are not changing. It is a sign you have already changed and the self-image has not finished catching up.

Give it time.

---

If this piece felt familiar, the rest of this writing lives inside the Devenira world.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### How much weight loss does it take for others to notice?

Roughly 4 to 6 kg for face changes to register, 8 to 10 kg for the body shape. Frequent contacts notice later than people who see you only every few months. The face usually shifts first, which is why family members on video calls often comment before in-person friends.

### Why can't I see my own weight loss in photos?

Single photos are too noisy. Lighting, posture, and time of day can fake an entire month of change in either direction. The internal map also reads new photos through the old self-image, which lags the body. Compare groups of four photos across months, not single shots.

### How long until my own perception catches up?

Usually three to six months past the change, sometimes longer. There is no specific date. People who work with post-weight-loss body image professionally describe the lag as normal. The internal map updates gradually, pulled forward by external evidence and time.

### Should I trust compliments about my weight loss?

Yes, directionally. People may be polite about the magnitude, but if someone you have not seen in three months says you look different, you look different. Outside observers are usually closer to current reality than your own mirror is right now.

### Is body dysmorphia normal after weight loss?

A milder version of it is extremely common. Most people who lose meaningful weight describe a stretch where other people treat them as the new body and they still feel like the old one. That gap is the head catching up. If it persists or distresses, talk to a professional.

```
