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
   `https://devenira.com/blog/do-people-who-have-been-obese-for-years-lose-weight-more-slowly` — exact
   slug is `do-people-who-have-been-obese-for-years-lose-weight-more-slowly` — verify against `posts.ts` (the file name's topic part is a hint, not always the exact slug)
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
Do People Who Have Been Obese for Years Lose Weight More Slowly?

## SEO Title
Do Obese People Lose Weight Slower Than Others?

## Subtitle / Description
Do obese people lose weight slower than others? On the scale, sometimes the opposite — but the fat under it tells a longer story. If weight came on slowly over years, more of it is usually true fat rather than temporary water. That can make the process feel heavier, but it does not mean your body is uniquely cursed.

## Meta Description
Do obese people lose weight slower than others? Not slower per pound — but more of it is true fat, not water. Here's why the first month feels heavier.

## Primary Keyword
do obese people lose weight slower than others

## Secondary Keywords
- harder to lose weight after obesity
- long-term obesity weight loss rate
- slower fat loss after being obese
- how fast can obese people lose weight
- obesity duration weight loss speed

## Medium Tags
- Weight Loss
- Dieting
- Health
- Mindset
- Fitness

## Canonical URL
**DO NOT set a canonical URL in Medium's story settings.**

Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site with effectively zero Domain Rating. Pointing Medium's canonical at it redirects Medium's DR ~95 authority into a site that cannot rank, so both pages lose. Leaving Medium self-canonical means Medium keeps its ranking power while the owned-site mirror re-points its own canonical to Medium via `generateMetadata` (see `seo_optimization_rules.md`).

If Medium ever auto-sets canonical during an Import-from-URL workflow, edit the story settings and clear the canonical field before publishing.

## Cover Direction
- Use the owned-site hero image family already assigned to this post.
- Goal: keep the Medium version readable and human, not product-heavy.
- Avoid UI-heavy or hard-sell imagery.
- Current owned-site hero: `/founder/long-game-founder-20251221.jpg`

## Optional Link Back
- Use once, at the very end only:
  - `[Devenira](https://devenira.com/blog)`

## Markdown
```md
# Do People Who Have Been Obese for Years Lose Weight More Slowly?

Do obese people lose weight slower than others? On the scale, sometimes the opposite — but the fat under it tells a longer story. If weight came on slowly over years, more of it is usually true fat rather than temporary water. That can make the process feel heavier, but it does not mean your body is uniquely cursed.

This question usually sounds scientific on the surface.

Underneath, it is often a fairness question.

If I have been overweight for a long time, am I just stuck with a worse deal? Did I wait too long? Is this going to take forever because I was this size for years?

That is what people really want to know.

> **Do obese people lose weight slower than others?**
>
> Not slower per pound, often faster early. But more of the loss is true fat instead of water, so it takes longer to feel and see. Weight gained slowly over years is mostly fat, and fat moves slower than water. Long-term obesity is also a long-term habit pattern. Both take time to change.

## Quick Gain and Quick Loss Are Usually Talking About Water

There is a reason people say weight gained quickly is lost quickly. Sometimes that is true. But usually it is true because the weight was not mostly fat in the first place.

Holiday eating. Travel. Several days of more sodium and carbohydrates than usual. The scale goes up 3, 4, 5 kg and everyone starts speaking in apocalyptic language.

A lot of that is water. And because it is water, it can leave relatively quickly too.

That is not the same story as body fat built up over a year, or five years, or ten.

## Fat Gained Slowly Is Usually Slower To Remove Because It Is Fat

This is the plain answer nobody likes because it refuses to be dramatic.

If weight came on slowly over a long period, more of it is likely to be actual body fat rather than temporary water. And body fat usually changes more slowly than water.

So yes, in a practical sense, long-term weight gain can take longer to change than a short-term water spike.

But that does not mean slowly accumulated fat burns with some mystical reluctance because it has tenure.

## The Longer the Pattern, the Harder the Pattern Is to Change

This is the real issue.

If you gained weight over years, then your eating habits, routines, stress responses, and comfort behaviors had years to become normal.

That is why long-term obesity often feels harder to undo. Not because your body signed a secret contract against you. Because your habits got furniture.

What gets sticky is not just the fat. It is the lifestyle that kept feeding it.

## This Is Also Why People Get Too Hopeless Too Early

They assume their current thoughts are permanent facts.

I hate exercise. I will always crave this stuff. I could never live differently for the long term.

Maybe. Or maybe that is just how your mind sounds in the body and routine you have now.

Because when the body changes, the mind often changes with it.

## What to Do With This Information

- Stop comparing fat loss to water loss.
- Treat habit change as part of the fat-loss job.
- Do not assume your current cravings are your permanent identity.

People who have been overweight for a long time often do not need more shame. They need proof that long-term change is still readable.

## Closing

If the long game is your game, then you need tools that reward reading patterns, not panicking over one week.

A better weekly check-in matters here because the process is slower and easier to misjudge emotionally.

This is harder, yes. But harder is not the same as hopeless.

If this piece felt familiar, the rest of my writing lives on [Devenira](https://devenira.com/blog).

I'm pkang, a fitness and diet writer who lost 50 kg over five years and later turned that transformation into a professional modelling career. I write about appetite, body image, and the slow work of learning how to read the body without panic.



## Frequently Asked Questions

### Why does 'gained quickly, lost quickly' not apply here?

That phrase is usually about water. Holiday eating, travel, and a few salty days can move 3 to 5 kg of water that comes off fast. Fat built up over years is a different story. The body did not store it overnight, and it does not leave overnight.

### Is the metabolism actually broken?

Usually no. The fat itself is not stubborn because it has been there longer. The pattern around it is. Years of certain meals, routines, and stress responses became normal, and that is what feels hardest to change. The body is not signing secret contracts against you.

### Will I always crave the foods I crave now?

Probably not. Most cravings shift as the body and routine change. The thoughts that feel permanent today are usually thoughts produced by the body and lifestyle you have right now. When the body changes, the mind tends to follow, even if it lags by months.

### What's a realistic rate of fat loss after long-term obesity?

Roughly 0.5 to 1 percent of body weight per week is sustainable for most people. The first month often shows more because of water. Then the rate steadies into a quieter, less photogenic version. The total trajectory matters more than any single week's number.

### How should I track if the long game is mine?

Use weekly check-ins, not daily verdicts. Photos, fit, waist measurements, and a rolling weight average over three to four weeks. The body is moving slower than emotion is. Daily readings make panic more persuasive than progress, which is the worst combination over years.

```
