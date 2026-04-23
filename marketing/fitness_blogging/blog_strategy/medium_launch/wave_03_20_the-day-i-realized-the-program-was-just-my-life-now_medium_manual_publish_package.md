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
   `https://devenira.com/blog/the-day-i-realized-the-program-was-just-my-life-now` — exact
   slug is `the-day-i-realized-the-program-was-just-my-life-now` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
The Day I Realized the Program Was Just My Life Now

## SEO Title
When Does a Diet Become a Lifestyle?

## Subtitle / Description
When does a diet become a lifestyle? Quietly. You usually notice weeks after it has already happened. There is a quiet moment when the program stops being a project and starts being your life. The shift is not announced. It is noticed weeks later, by accident.

## Meta Description
When does a diet become a lifestyle? You don't notice on the day. You notice the Tuesday weeks later when you didn't think about food once.

## Primary Keyword
when does a diet become a lifestyle

## Secondary Keywords
- diet to lifestyle change
- diet vs lifestyle difference
- sustainable weight loss habits
- how long until diet becomes habit
- weight loss lifestyle change mindset

## Medium Tags
- Weight Loss
- Maintenance Phase
- Lifestyle Change
- Long Game
- Habits

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/final-portrait.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# The Day I Realized the Program Was Just My Life Now

When does a diet become a lifestyle? Quietly. You usually notice weeks after it has already happened. There is a quiet moment when the program stops being a project and starts being your life. The shift is not announced. It is noticed weeks later, by accident.

There was no announcement.

The program did not close out with a milestone post or a summary email or a celebration dinner. There was no "before-and-after" moment. There was no day I marked on a calendar.

What there was, instead, was a Tuesday — sometime in month seven of maintenance — where I noticed I had not consciously thought about my food, my training, or my weight all day. The day was halfway over. I had eaten my normal breakfast, made my normal lunch, gone to my normal training session, and not framed any of it as part of "the program."

The program had stopped being a thing I was running. It had become a default I was living.

That moment, when I noticed it, was the actual end of the project. The numbers had landed months earlier. The behaviors had taken longer.

> **When does a diet become a lifestyle?**
>
> Usually between month 6 and month 12 of consistent practice, sometimes longer. There is no announcement. The moment is noticed weeks later, by accident — a Tuesday where you have not consciously thought about food, training, or weight all day. The transition is a fade, not a celebration. The defaults stop feeling like effort.

## What the moment looked like

It was nothing.

That is the whole story.

I had finished a meeting. I made a sandwich. I ate it at my desk while reading something. Halfway through, I realized I had not thought once about whether the sandwich was "on plan." It was just lunch. The bread was the bread I keep in the kitchen. The protein was the protein I default to. The portion was the portion I have been making for months without measuring.

There was no satisfaction in the moment. No triumph. No checkpoint.

What there was, instead, was a quiet realization that the program — the daily structure, the cooking defaults, the training cadence, the sleep target, the weighing rhythm — had moved from foreground to background. It had stopped being a project I was running. It had become a default I was living.

The defaults had become the floor. The floor was now lower-effort than getting off it. There was no longer a "discipline" being applied. There was just a Tuesday.

## When this kind of moment is possible

This is not a six-week event. The early months of any program are necessarily effortful. The behaviors are new. The defaults are not yet defaults. Every meal is a decision. Every training session is a choice. Every weigh-in carries weight.

The transition to "this is just my life" usually arrives somewhere between month 6 and month 12 of consistent practice. For me it was month seven of maintenance, which was about month fifteen of the overall program counting the cut.

Three things have to happen first.

The cooking defaults have to become unconscious. Three to five meals you make on autopilot, with the right macros, that you do not get sick of. This usually takes 6 to 9 months of running them.

The training default has to be set. A weekly cadence — three or four sessions, specific days, predictable structure — that runs whether you feel motivated or not. This usually takes 4 to 6 months of consistent practice.

The weighing rhythm has to be calm. Weekly or biweekly readings that you can take without emotion. This usually takes 6 to 12 months of recovering from the daily-weighing habit, if you ever had one.

When all three are in place, the conscious effort drops to near-zero. The program runs in the background. You stop being someone "doing a diet" and become someone whose default behaviors happen to maintain the body the diet built.

## What the moment did not look like

It did not look like graduation.

I had spent a lot of time during the cut imagining what the end would feel like. Crossing a finish line. Unbuttoning a tight feeling. A specific day where the project closed and life resumed.

That is not what happened. There was no crossing.

The actual transition was the absence of an event. The program faded from foreground to background, slowly, across many ordinary days. The point at which I noticed the fade was just one of those days.

If I had been waiting for the finish-line moment, I would have missed the transition entirely. Most people I have talked to about this say the same thing. The program either fades, or it gets abandoned. There is rarely a celebration in the middle.

## What changed about how I think about the body

Before the transition, the body was a project. Something I worked on. Something with a current state, a target state, and a delta to close.

After the transition, the body is a body. It is something I take care of, the way I take care of my teeth or my apartment or my sleep. It is not a thing with a target. It is a thing that requires consistent maintenance, none of which is dramatic, all of which I now do without specifically thinking of it as "the program."

This is a calmer relationship with the body than I have ever had. Not because the body is at a particular weight or composition. Because the body has stopped being something I am trying to fix.

The cut was about reaching a different body. The maintenance was about learning to live with that body. The transition is about stopping the framing of "this is a body I am running a program on."

It is just my body now. Same as everyone else's relationship with their body, mostly.

## What I would tell someone in month four

You will not feel this transition coming.

It will not be a milestone. There will not be a date. The work will not "feel done" the way you expect.

What will happen is that, somewhere between month 6 and month 12 of maintenance, you will have a Tuesday where the program is no longer the foreground of your day. You will not notice it on the day. You will notice it weeks later, by accident.

The work that produces this moment is not glamorous. It is the same boring Tuesday repeated for 200 to 400 Tuesdays. The defaults, the meals, the sessions, the sleep, the weighing — all of them, run on quiet repeat, without fanfare, until they stop being conscious.

If you are in month four and the program still feels like a project, that is correct. It is supposed to feel that way at month four. The transition is not at month four. It is at month fifteen, by surprise.

## Why the program had to fade for the body to hold

The body the cut produced was not the project's output.

The lifestyle was the project's output. The body was a downstream effect of the lifestyle.

If the lifestyle had stayed effortful — if I had kept treating each meal as a "diet meal" and each session as a "training session for the project" — the body would have eventually drifted. Effortful systems do not hold for years. They hold for months and then break.

The body holds because the system stopped being effortful. The defaults run in the background. The body runs along with them.

This is the part that the cut narrative does not warn you about. The cut sells the body change as the achievement. The actual achievement is the lifestyle change that is supposed to support the body change. If the lifestyle change does not happen, the body change does not last.

## The line worth keeping

The program had to disappear for the body to hold.

If the program is still loud after a year of maintenance, the system has not finished. The transition is not a celebration. It is a fade.

When you notice the fade — and you will, eventually, on a Tuesday halfway through lunch — that is the actual end of the work.

The body will already be there. The relationship to it is what took the longest.

---

I write about weight loss, appetite, body image, and the slow work of learning how to read the body without panic.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).



## Frequently Asked Questions

### How long before diet habits feel automatic?

Three habit layers each take their own time: cooking defaults usually 6 to 9 months, training cadence 4 to 6 months, calm weighing rhythm 6 to 12 months. When all three run unconsciously, conscious effort drops to near-zero. That is when the diet becomes a lifestyle.

### Why doesn't the transition feel like a milestone?

Because it is the absence of an event. The program fades from foreground to background slowly, across many ordinary days. The point you notice the fade is just one of those days. People waiting for a finish-line moment usually miss the transition entirely.

### Can a diet become unsustainable if it never becomes a lifestyle?

Yes. Effortful systems do not hold for years. They hold for months and break. If maintenance still feels like a project at month twelve, the system has not finished converting. The body change does not last without the lifestyle change underneath it.

### What does the lifestyle phase actually look like?

Boring. Same breakfast most mornings. Same training cadence most weeks. Calm weekly weigh-ins. Meals you do not frame as 'diet meals.' Sessions you do not frame as 'training for the project.' The body is just your body now. The work happens in the background.

### How do I know I'm not just on a longer diet?

If you still consciously frame meals as 'on plan' or 'off plan,' you are still in diet mode. If meals just happen, with the right macros, without you naming them as part of a program, the transition has started. The naming fades before the behaviors do.

```
