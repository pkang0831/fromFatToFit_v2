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
   `https://devenira.com/blog/how-do-i-eat-normally-at-social-events` — exact
   slug is `how-do-i-eat-normally-at-social-events` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
How Do I Eat Normally at Social Events

## SEO Title
How to Eat at Social Events on a Diet

## Subtitle / Description
A practical Q&A on how to eat at dinners, parties, and events without overcompensating before or after. Most of the damage is not at the event.

## Meta Description
How to eat at social events on a diet: the dinner is rarely the problem. The under-eating before and over-correcting after are. Here's the fix.

## Primary Keyword
how to eat at social events on a diet

## Secondary Keywords
- eating out while dieting
- social eating weight loss
- how to go to a party on a diet
- diet at restaurants tips
- eating at dinner party diet

## Medium Tags
- Weight Loss
- Dieting
- Social Eating
- Habits
- Nutrition

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/sleep-reflective-window-20241217.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# How Do I Eat Normally at Social Events

Here's how to eat at social events on a diet without making the dinner the villain. The damage usually happens around the dinner.

Most people think a dinner out is where the diet breaks.

Usually, the dinner is the smallest part of the problem.

The damage usually happens before and after the event, not at it.

> **How do I eat at social events on a diet?**
>
> Eat normally around the event, not before and after. Most damage happens in the under-eating before and the over-correcting after, not at the dinner itself. Skip the breakfast-skipping. Skip the morning-after restriction. Arrive not-hungry. Eat what you want at the event. Return to your plan at the next meal, not next Monday.

## Q: Should I Eat Less During The Day To Save Up For Dinner?

No.

This is the single most common mistake around social eating. It is also the one that creates the biggest overshoot at the event.

When you undereat during the day, you arrive at the dinner hungry, under-fueled, and with your appetite cranked up. That is the worst possible state for making food choices around a large spread of calorie-dense options.

You will eat more, faster, and feel less full than if you had eaten normally during the day. You also risk drinking on an emptier stomach, which makes the whole thing worse.

Eat your normal meals that day. Protein at each of them. Normal breakfast. Normal lunch. Arrive at the dinner not-hungry, not-full.

## Q: Should I Eat A Protein Bar Before Going Out?

If the event is later than your usual dinner time, yes. A small, protein-forward snack 60 to 90 minutes before arriving changes the dynamic.

It is not about filling up. It is about not arriving starved.

## Q: What Should I Actually Do At The Event?

Three things, in rough order.

- Eat slower than you normally would at home. Social eating is a marathon, not a sprint. You want your fullness signal to arrive while the food is still in front of you, not 30 minutes after.
- Start with vegetables, salad, or protein. Not because carbs are bad. Because starting there moderates how hungry your blood sugar is by the time dessert shows up.
- Drink water between drinks, if you are drinking. Alcohol suppresses hunger-regulation signals and tends to make the whole night feel less metered.

That is most of it. There is no secret move.

## Q: Should I Avoid Certain Foods?

Not categorically. The avoidance frame is usually what wrecks the event.

If you decide bread is forbidden and then eat bread, your brain often reads that as the diet is over, eat everything. If you decide bread is fine and you eat one piece, your brain reads it as I ate bread and stops there.

The foods that trigger a specific person vary. But the general rule is avoid the frame where one food equals failure. That frame is more dangerous than any of the foods.

## Q: What About After The Event?

This is where most of the actual damage happens. Three patterns wreck the next week.

Pattern one: drastic morning-after restriction. Skipping breakfast, cutting calories hard, trying to cancel the dinner out. This almost always leads to a second overeat later that day.

Pattern two: giving up on the week. I already messed up Friday, so this weekend does not count. Most people turn one event into three days.

Pattern three: obsessive scale-checking. Weighing every morning post-event and panicking at water retention that takes three to five days to leave.

The next morning, eat your normal breakfast. Drink water. Do not weigh yourself for three to five days. Return to your plan at lunch as if the event was last week.

The event is absorbed into the week. The total does not change, and you do not need to do anything dramatic.

## Q: How Often Can I Do Social Events Without Losing Progress?

More than most people think.

One event a week, handled with the above approach, usually has no meaningful effect on a fat-loss phase. Two events a week starts to compress the deficit. Three events a week is effectively a maintenance phase, which is fine if that is what you want that week.

The events themselves are not the threshold. The threshold is whether the days around them return to the plan.

## Q: What If I Know My Next Event Is Going To Be Huge?

Treat that specific day as a planned high-calorie day. Eat normally before. Eat normally at breakfast and lunch. Go to the event. Eat what you want. Stop when done.

Do not diet for two days before to make room. Do not diet for three days after to compensate. Both responses generate more damage than the event itself.

One high day in a week of normal eating is absorbed. Six days of anxiety around one meal is not.

## The Quiet Summary

The dinner is not the threat.

The under-eating before the dinner and the over-correcting after the dinner are the threat.

Eat normally around the event. Eat normally at the event. Eat normally the day after.

---

This is one piece of a larger body of writing about scale noise, visual proof, and the messy psychology of dieting.

The fuller body of this writing lives at [Devenira](https://devenira.com/blog).

## Frequently Asked Questions

### Should I save calories during the day for the event?

No. Saving calories almost always backfires. You arrive hungry, under-fueled, and with appetite cranked up — the worst possible state for making food choices around a calorie-dense spread. Eat your normal breakfast. Eat your normal lunch. Arrive not-hungry, not-full.

### What should I actually do at the event?

Eat slower than you would at home. Start with vegetables, salad, or protein before the dense carbs and sweets. Drink water between alcoholic drinks. Stop when done, not when the plate is empty. There is no secret move. The slowness is most of it.

### Should I avoid certain foods at the event?

Not categorically. The avoidance frame usually wrecks the night. If you label bread as forbidden and then eat bread, the brain often reads it as the diet is over. Decide bread is fine and one piece stops there. The avoidance framing is more dangerous than any single food.

### What should I do the morning after?

Eat your normal breakfast. Drink water. Do not weigh yourself for three to five days while the sodium clears. Return to your plan at lunch, as if the event was last week. The drastic morning-after restriction is what turns one event into three days off plan.

### How often can I do social events without losing progress?

One a week, handled this way, has almost no effect on a fat-loss phase. Two a week starts compressing the deficit. Three a week is essentially a maintenance phase. The events themselves are not the threshold. Whether the days around them return to plan is the threshold.

```
