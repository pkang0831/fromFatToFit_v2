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
   `https://devenira.com/blog/exercise-isnt-shrinking-you-the-way-you-expected` — exact
   slug is `exercise-isnt-shrinking-you-the-way-you-expected` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Exercise Is Not Shrinking You the Way You Expected

## SEO Title
Why Am I Working Out but Not Losing Weight?

## Subtitle / Description
If you are working out consistently and still not shrinking, the problem probably is not the workout. It is what the workout is actually doing.

## Meta Description
Why am I working out but not losing weight? Exercise builds composition first, weight loss second. The scale catches up by week 6 to 12, usually.

## Primary Keyword
why am I working out but not losing weight

## Secondary Keywords
- exercise not losing weight
- going to the gym but not losing weight
- exercising every day no weight loss
- why is my scale not moving with exercise
- gym not working weight loss

## Medium Tags
- Weight Loss
- Exercise
- Fitness
- Dieting
- Nutrition

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
# Exercise Is Not Shrinking You the Way You Expected

Why am I working out but not losing weight? Because exercise reshapes the body more than it shrinks it — and the scale doesn't reward that. Exercise is not a shrinking machine. It is a body-composition machine, a metabolism-shaping machine, a stress-processing machine. What it is not, consistently, is a quick way to remove fat.

You have been showing up.

Four days a week. Sometimes five. The workouts feel hard. Your clothes feel about the same.

That is the part nobody warns you about.

> **Why am I working out but not losing weight?**
>
> Because exercise is not a shrinking machine. A full hour of cardio burns 300 to 500 calories, which most people eat back without noticing. Training also raises appetite and retains water in recovering tissue. The workout builds the engine. The plate decides what the engine runs on. The scale catches up last.

## The Principle

Exercise is not a shrinking machine.

It is a body-composition machine, a metabolism-shaping machine, a stress-processing machine. It is many things. What it is not, consistently, is a quick way to remove fat.

A full hour of cardio burns less than people think. Maybe 300 to 500 calories, depending on intensity and your actual body mass. Most people eat that back in a single post-workout snack they did not register as a snack.

This is not a motivational problem. It is an arithmetic problem.

## The Mechanism

When you exercise seriously, three things happen at once.

- You burn a modest amount of additional calories.
- Your body retains more water in the recovering tissue.
- Your appetite tends to quietly nudge up.

The first is small. The second makes the scale lie for a few days. The third is the real reason most working-out-but-not-losing-weight stories exist. Your body tends to be very good at protecting its current weight. The workout asks it to change. Its first response is usually to give you more hunger so you can keep training. That is not sabotage. That is homeostasis.

## What This Means For You

It means the workout alone does not do the shrinking. The workout builds the engine. The plate decides what the engine runs on.

## If You Are Training Hard And Not Changing Shape

- Keep training.
- Stop expecting the scale to move because of the training.
- Watch what your appetite does in the two hours after a session.
- Make the post-workout window a structure, not a reward.

The people who get leanest from exercise are not the ones who train hardest. They are the ones whose eating does not respond dramatically to the training.

## The Quieter Truth

Exercise reshapes you slowly, from the inside. Posture. Stamina. How your shoulders sit. How your gait looks. How quickly you recover from stairs.

If the mirror is not showing it yet, the mirror is behind. The work is there. You can feel it in the stairs.

The scale will catch up. It usually catches up last.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).



## Frequently Asked Questions

### How many calories does a workout actually burn?

Less than people think. A vigorous one-hour gym session burns roughly 300 to 500 calories depending on body mass and intensity. Most fitness trackers overestimate by 20 to 50 percent. A single post-workout snack often covers the entire session's burn.

### Why does the scale go up after I start exercising?

Recovering muscle holds extra water for a few days, which adds 0.5 to 1.5 kg of scale weight that has nothing to do with fat. Appetite also nudges up, so intake often rises slightly. Both effects pass. The scale rarely lies long-term, just short-term.

### Should I do more cardio if the scale isn't moving?

Usually no. Adding cardio to a stalled cut often triggers compensatory eating and lower NEAT later in the day. The session burned 300 calories. The compensation ate them back. Run an honest tracking week, take a diet break, or adjust intake before adding cardio.

### Does lifting weights actually help with fat loss?

Indirectly, yes. Lifting preserves muscle during a deficit so more of the scale loss is fat. It does not burn many calories during the session itself. The long-term composition payoff is real even when the weekly scale change is small.

### How long until exercise shows in the mirror?

Strength changes show up in 6 to 8 weeks. Visible shape change for most recreational lifters is 12 to 16 weeks, sometimes longer. The numbers in the gym move first. The body moves second. Most people quit at week 5 to 9, right before the visual change starts.

```
