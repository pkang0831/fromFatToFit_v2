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
   `https://devenira.com/blog/the-week-my-appetite-came-back-during-maintenance` — exact
   slug is `the-week-my-appetite-came-back-during-maintenance` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
The Week My Appetite Came Back During Maintenance

## SEO Title
Why Appetite Returns During Maintenance After Weight Loss

## Subtitle / Description
When appetite returns during maintenance after weight loss, it isn't failure. It is the body finishing what the cut started. Five months into maintenance, my appetite came back. Not as failure. As a normal part of the body finishing the work the cut started. Here is what that week actually looked like — and what I almost did wrong.

## Meta Description
Appetite returns during maintenance after weight loss — usually 4 to 6 months in. It isn't failure. Here's the week it hit and what I almost did wrong.

## Primary Keyword
appetite returns during maintenance after weight loss

## Secondary Keywords
- hungry during maintenance phase
- increased appetite after weight loss
- hormonal hunger after dieting
- ghrelin increase weight loss maintenance
- appetite rebound after cut

## Medium Tags
- Weight Loss
- Maintenance Phase
- Appetite
- Founder Story
- Hunger

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/weighin-middle-progress-20240801.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# The Week My Appetite Came Back During Maintenance

When appetite returns during maintenance after weight loss, it isn't failure. It is the body finishing what the cut started. Five months into maintenance, my appetite came back. Not as failure. As a normal part of the body finishing the work the cut started. Here is what that week actually looked like — and what I almost did wrong.

The appetite came back in week 22 of maintenance.

The first 21 weeks had been quiet. The body had settled. The scale was holding. The food choices that had taken months of work to default into were running on autopilot. I had started to think the appetite story was over.

Then a Tuesday in week 22 showed up with the loud, specific, mid-afternoon hunger that I had not felt since the second month of the cut. By Friday, I was eating an extra 600 calories a day without planning to. By the next week, the body was up 0.8 kg.

I almost ran the cut playbook on it. Tighten. Restrict. Punish. That instinct was wrong. The fix was different.

## What the week actually looked like

Tuesday at 3 p.m., a hunger I had not felt in months. Specific — not boredom, not a craving for one food. A general, body-level hunger that wanted a real meal. I had a snack, ate dinner an hour earlier than usual. By bedtime the day was 400 calories above maintenance.

Wednesday felt similar but louder. Lunch was barely satiating. Mid-afternoon hunger again. Dinner was bigger. By the end of the day, 700 calories above plan.

Thursday morning, the scale was up 0.6 kg. I noticed myself starting to script the response. Cut tomorrow. Tighten the structure. Bring back the cut-era discipline. The familiar reflex.

I did not. Friday, same pattern. The body was telling me, loudly and consistently across three days, that something needed to be different.

By Sunday, I was up 0.8 kg total. The week had been about 2,000 calories over maintenance.

The cut had taught me to override hunger. Maintenance was teaching me to listen to it.

## What I did instead of restricting

I let the week happen.

The next Monday, I did not cut calories. I did not skip meals to make up for it. I did not weigh myself daily. I went back to the maintenance plan as written, with one change: I added 200 calories to the daily target, distributed mostly into protein at lunch and a small evening snack.

The body needed more than I had been giving it. Not because the maintenance number was wrong before, but because something — training cycle, sleep, season, life stress, some combination of all four — had shifted what maintenance meant for the body that week.

The scale leveled off within ten days at the new slightly-higher set point. The 0.8 kg jump did not become a slide. The new calorie target held. Maintenance resumed.

If I had run the cut playbook on it — tighten, restrict, punish — the most likely outcome would have been a binge by week 23, a 2 kg spike, and a month of recovery from a problem I had created by ignoring the body's signal.

## Why the cut playbook is wrong here

The cut playbook is built on a different premise.

In the cut, the goal is to maintain a planned deficit despite hunger. Hunger is friction the system absorbs by design. The discipline is to keep eating the planned amount even when the body asks for more.

In maintenance, there is no planned deficit. The goal is to match intake to the body's actual energy needs — needs that fluctuate week to week as the body adjusts to lower weight, training cycles, sleep, stress, hormonal shifts, season, and dozens of small variables.

When appetite rises in maintenance, it is usually saying "the body needs slightly more." The right response is to give slightly more, then watch what happens. If the appetite resolves at the new level, the body had a real need. If it keeps rising, something else is going on (sleep debt, under-protein at meals, life stress) and the fix is downstream of the calorie adjustment.

Running the cut playbook on a maintenance appetite spike is overriding a signal that the system is supposed to respect. The cost is not "you ate too much that week." The cost is teaching the body, again, that its signals do not get respected, which is the exact pattern that broke the diet five months ago.

## What the appetite was actually responding to

I went back through the prior two weeks looking for the trigger.

Three things had shifted at once.

Sleep had drifted from a steady 7 hours 20 minutes to about 6 hours 45 minutes for nine of the prior fourteen nights. Travel and a stretched work week.

Training volume had ticked up. I had added a fourth session and pushed the lifting numbers slightly. The weekly training calorie cost had risen modestly without the food side adjusting.

Outside temperature had dropped. The body was burning more energy on baseline thermoregulation. Small effect alone, real effect on top of the other two.

Stacked, those three small shifts had produced an appetite signal that was not random. It was the body asking for the energy it had started spending more of.

The fix was not "be more disciplined about food." The fix was to give the body the energy it was asking for and to repair the sleep that was probably the largest of the three drivers.

## Why I am writing this down

Because the version of me at week 21 would not have known the difference.

That version of me would have read the appetite return as failure. Would have run the cut playbook. Would have produced the binge that the playbook produces when the underlying need is not met. Would have written a different post — about how the program "failed" — instead of this one.

The skill maintenance is teaching me is not to eat less. It is to read the appetite signal as data instead of as a moral test.

That skill was inverted during the cut. The cut required treating hunger as friction. Maintenance requires treating hunger as a signal worth respecting.

Both modes are correct in their phase. Switching between them is the part nobody warned me about.

## What to watch for if you are in early maintenance

The appetite return tends to arrive somewhere between weeks 12 and 26 of maintenance. Sometimes earlier, sometimes later. It is not a one-time event. It can come back periodically — usually following a stretch of training cycle changes, sleep degradation, life stress, or seasonal shift.

The pattern is almost always the same:

- A few days of low-grade higher-than-usual hunger
- A small upward scale drift, usually 0.5 to 1 kg over a week
- A reflexive urge to "fix it" with restriction
- A dilemma about whether to listen or resist

The right response is almost always: feed the body, watch where it stabilizes, fix the upstream variable (sleep, training mismatch, stress).

The wrong response is to apply cut-era discipline to a maintenance signal. That move turns a 0.8 kg adjustment into a 3 kg recovery cycle.

## The line worth keeping

The cut taught me to override hunger.

Maintenance is teaching me to listen to it.

Both modes have their place. The hard part — and the part nobody warns you about — is knowing which mode you are in this week, and switching cleanly.

If your appetite came back during maintenance and you are reaching for the cut playbook, pause first. The body is probably not failing. It is probably asking for the conversation you stopped having during the cut.

---

I write about weight loss, appetite, body image, and the slow work of learning how to read the body without panic.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).
```
