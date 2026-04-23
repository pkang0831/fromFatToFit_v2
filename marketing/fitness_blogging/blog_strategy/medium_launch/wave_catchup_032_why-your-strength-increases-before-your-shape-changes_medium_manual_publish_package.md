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
   `https://devenira.com/blog/why-your-strength-increases-before-your-shape-changes` — exact
   slug is `why-your-strength-increases-before-your-shape-changes` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Why Your Strength Increases Before Your Shape Changes

## SEO Title
Why Does Strength Increase Before Muscle Size?

## Subtitle / Description
Your strength improves before your shape does. The first six weeks of lifting are mostly neural. This is what that looks like from the inside.

## Meta Description
Why does strength increase before muscle size? The first 6 weeks of lifting are mostly neural, not visual. Numbers move first. Shape moves second.

## Primary Keyword
why does strength increase before muscle size

## Secondary Keywords
- neural adaptation beginner lifting
- strength gains without visible muscle
- first 6 weeks lifting results
- newbie gains neural adaptation
- strength vs hypertrophy timeline

## Medium Tags
- Weight Loss
- Strength Training
- Fitness
- Exercise Science
- Body Composition

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/patience-middle-checkin-20250731.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# Why Your Strength Increases Before Your Shape Changes

Why does strength increase before muscle size? The nervous system gets organized weeks before the body looks different.

I added 15 kg to my deadlift in my first six weeks of training.

I did not look meaningfully different.

If you were showing up in a mirror expecting week-by-week change, you would think the gym was broken.

> **Why does strength increase before muscle size?**
>
> Because the first six to eight weeks of lifting are mostly neural, not visual. The nervous system learns to recruit muscle you already have. Coordination improves. Stabilizers wake up. The motor pattern cleans up. The numbers move first because the body upgrades the existing tissue before deciding to commit resources to growing new tissue.

## What The First Six Weeks Actually Are

For most people starting or returning to lifting, the first six to eight weeks are not mostly about muscle growth.

They are about your nervous system learning to recruit the muscle you already have.

This is called neural adaptation. Your body gets better at firing the right muscles at the right time in the right order. Coordination improves. Stabilizer muscles wake up. The motor pattern cleans up.

All of that shows up in the numbers fast. Lifts go up. Reps get easier. You can hold better positions for longer.

But you are not yet adding meaningful muscle tissue. You are using your existing muscle more completely.

## Why The Neural Curve Comes First

Building muscle is expensive. The body does not add it casually. Before it commits resources to growing new tissue, it tries to see if the existing tissue can do the job.

If the answer is yes, it quietly upgrades recruitment patterns and calls it done.

If the workouts persist and the stimulus accumulates, then the body eventually starts adding tissue, slowly, as a second-stage response.

This is why a beginner can deadlift 180 kg by week ten while still looking mostly the same as week one. The muscle did not grow to support that lift. The coordination did.

## Why This Makes Most People Quit

The feedback loop is backward from what people expect.

They expected to see shape changes first and lift numbers second. That matches how transformation content is edited. Body before. Body after. Numbers quietly changing in the background.

Reality: the numbers are going up in week three. The body still looks like week one.

So beginners who judge the program on visual change usually conclude it is not working, and quit, right before the shape changes would have started showing.

Strength adaptation is 6 to 8 weeks. Visible hypertrophy for most recreational lifters is 12 to 16 weeks, sometimes longer. Most people quit at week 5 to 9.

## What I Noticed From The Inside

Week one, the lifts felt awkward.

Week three, I was hitting weights I did not think I would hit for months. The bar speed was wrong. I assumed my form was worse than it was.

Week six, the lifts kept climbing. My shoulders started looking different in mirrors, slightly. My legs felt denser when I walked.

Week ten, other people started noticing. Small comments. Family members asking if I had lost weight, even though I was not on a cut. What they were actually seeing was the first real shape change.

Week fourteen, the mirror started catching up to the strength graph.

The order was reps, then feel, then photo.

## What To Do In The Early Phase

Stop judging the program on the mirror. Judge it on three things.

- Are the working weights going up week to week, gradually?
- Are the reps feeling more controlled?
- Is your form holding on the last set?

If yes to those three, the program is working. The body will follow. Log the numbers. Look at them in groups of four weeks, not day by day.

## The Piece Most Beginners Miss

You are not doing the visual program yet.

You are doing the coordination program. The visual program starts later.

If you quit before the coordination program finishes, you never get to the visual one.

This is why consistency beats intensity for beginners. Your job in the first six weeks is not to have a transformative workout. Your job is to show up 3 or 4 times a week and let the nervous system do its quiet first pass.

The second pass is where the body actually changes. That pass runs on the foundation the first pass builds.

## The Line I Wish I Had Read Earlier

Your muscles learn to fire before they learn to grow.

The numbers move first. The body moves second.

If you stay long enough, both move.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### When does visible muscle growth actually start?

For most recreational lifters, somewhere between week 12 and week 16, sometimes longer. Strength changes show up in 6 to 8 weeks. Visible shape change runs on a slower clock. Most people quit at week 5 to 9, right before the visual change starts.

### Why doesn't the body just build muscle right away?

Because muscle is expensive to build. The body tries the existing tissue first. If it can do the job through better recruitment, it quietly upgrades coordination and stops there. Only when the workouts persist and the stimulus accumulates does the body start adding new tissue as a second-stage response.

### How should I judge the program in the early weeks?

Not on the mirror. Judge it on three things. Are working weights going up week to week, gradually? Are reps feeling more controlled? Is form holding on the last set? If yes to those, the program is working. The body will follow. The mirror is behind.

### Why do beginners gain strength so fast?

Because they have a lot of unrecruited muscle to wake up. The first six weeks of any program produce the steepest neural learning curve a lifter ever has. Lifts climb fast not because tissue grew, but because the body finally started using what was already there.

### Does this mean light weights are pointless early on?

No, but consistency matters more than intensity in the first weeks. Your job is to show up three or four times a week and let the nervous system do its first pass. The visual program runs on the foundation that pass builds. Quit early, never get to it.

```
