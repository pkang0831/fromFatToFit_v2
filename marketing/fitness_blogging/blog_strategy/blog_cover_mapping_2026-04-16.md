# Blog Cover Mapping 2026-04-16

This file defines a practical cover-image mapping system for the founder-led blog.

Primary goal:

- stop the feed from feeling visually repetitive
- preserve real founder proof
- give different topic lanes distinct visual signals
- make it easy to apply the same system in `fromFatToFit_v2` on `prodrepo/main`

Primary source archive:

- `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/Takeout/Google Photos/`

## Core Diagnosis

The current blog feed repeats too few founder images across too many posts.

Result:

- mirror / scale / plateau / binge posts start looking like the same article
- founder trust exists, but editorial differentiation is weak
- the archive feels smaller than it actually is

The fix is not to make every post visually random.

The fix is:

- define a cover taxonomy
- assign image families by topic lane
- prevent the same exact image from appearing in nearby cards

## Cover Taxonomy

### A. Founder / Credibility
Use for:

- founder story
- worldview
- personal updates
- authority / trust-heavy articles

Best image pool:

- `Photos from 2025/20251221_152946.jpg`
- `Photos from 2025/20251221_153653.jpg`
- `Photos from 2025/20251229_181316.jpg`
- `Photos from 2025/20251229_181233.jpg`
- `Photos from 2026/20260106_120635.jpg`
- `Photos from 2026/20260119_124926.jpg`
- `Photos from 2026/20260119_125140.jpg`

### B. Honest Proof / Before / Middle
Use for:

- mirror posts
- weigh-in interpretation
- plateau
- cheat day / binge recovery
- hard-middle articles

Best image pool:

- `Photos from 2024/IMG_1240.JPG`
- `Photos from 2024/IMG_1775.JPG`
- `Photos from 2025/20250711_085020.jpg`
- `Photos from 2025/20250716_064040.jpg`
- `Photos from 2025/20250719_083352.jpg`
- `Photos from 2025/20250725_074508.jpg`
- `Photos from 2025/20250731_140405.jpg`

### C. Hard Physique Proof
Use for:

- body transformation tracking
- body composition
- water weight vs fat
- progress proof
- milestone posts

Best image pool:

- `Photos from 2025/20250919_180642.jpg`
- `Photos from 2025/20251031_213544.jpg`
- `Photos from 2025/20251119_193305.jpg`
- `Photos from 2025/20251221_171125.jpg`
- `Photos from 2024/IMG_1873.PNG`

### D. Lifestyle / Support
Use for:

- reflective essays
- sleep / hunger / routine posts
- softer founder writing
- visual breaks in long-form articles

Best image pool:

- `Photos from 2024/IMG_1930.JPG`
- `Photos from 2024/IMG_1968.JPG`
- `Photos from 2024/IMG_1697.JPG`
- `Photos from 2024/IMG_2084.JPG`
- `Photos from 2026/20260106_120640.jpg`
- `Photos from 2026/20260106_120643.jpg`
- `Photos from 2026/20260120_223429.jpg`
- `Photos from 2026/20260121_172719.jpg`
- `Photos from 2026/20260124_134306.jpg`

## Current 4 Posts

These are the strongest hero assignments for the 4 posts currently defined in `frontend/src/content/blog/posts.ts`.

### 1. Why I Built Devenira for the Weeks Where You Want to Quit
- Recommended hero:
  - `Photos from 2026/20260119_125140.jpg`
- Why:
  - founder story needs trust and personal presence first
  - this feels mature and credible without looking like a gym ad
- Alternate:
  - `Photos from 2025/20251221_153653.jpg`

### 2. Why the Mirror Can Make Real Progress Feel Fake
- Recommended hero:
  - `Photos from 2025/20250716_064040.jpg`
- Why:
  - this is the cleanest honest middle-state check-in image
  - matches the article’s argument about visual proof
- Alternate:
  - `Photos from 2025/20250719_083352.jpg`

### 3. One Emotional Weigh-In Can Wreck a Good Week
- Recommended hero:
  - `Photos from 2024/IMG_1775.JPG`
- Why:
  - stronger than reusing the rawest before shot
  - still communicates vulnerable middle-stage interpretation
- Alternate:
  - `Photos from 2025/20250711_085020.jpg`

### 4. How to Track Body Transformation Without Obsessing Over the Scale
- Recommended hero:
  - `Photos from 2025/20251119_193305.jpg`
- Why:
  - strongest transformation-proof image in the archive
  - ideal for a tracking / evidence / body-change article
- Alternate:
  - `Photos from 2025/20251031_213544.jpg`

## Recommended Mapping For Next Wave Posts

These are suggested hero assignments for the larger blog inventory so the feed stops repeating the same three visuals.

### Cheat-day / Binge / Damage Lane

#### Cheat Days Do Not Expose Your Character. They Expose Your System.
- Recommended hero:
  - `Photos from 2025/20250725_074508.jpg`
- Alternate:
  - `Photos from 2025/20250719_083352.jpg`

#### You’ve Been Told “One Bad Day Won’t Hurt” But That’s Only Half the Truth
- Recommended hero:
  - `Photos from 2024/IMG_1240.JPG`
- Alternate:
  - `Photos from 2025/20250711_085020.jpg`

#### Read This Before You Try to “Fix” Your Diet Slip
- Recommended hero:
  - `Photos from 2025/20250716_064040.jpg`
- Alternate:
  - `Photos from 2024/IMG_1775.JPG`

### Scale / Plateau / Progress Lane

#### What Actually Counts as a Weight Loss Plateau?
- Recommended hero:
  - `Photos from 2025/20250711_085020.jpg`
- Alternate:
  - `Photos from 2025/20250731_140405.jpg`

#### Why Losing 5kg in a Week Usually Means Water, Not Fat
- Recommended hero:
  - `Photos from 2025/20251031_213544.jpg`
- Alternate:
  - `Photos from 2025/20251119_193305.jpg`

#### Why It Feels Like You Gain Weight Even When You Barely Eat
- Recommended hero:
  - `Photos from 2024/IMG_1240.JPG`
- Alternate:
  - `Photos from 2024/IMG_1775.JPG`

#### One Emotional Weigh-In Can Wreck a Good Week
- Recommended hero:
  - `Photos from 2024/IMG_1775.JPG`
- Alternate:
  - `Photos from 2025/20250711_085020.jpg`

### Mirror / Body Interpretation Lane

#### Why the Mirror Can Make Real Progress Feel Fake
- Recommended hero:
  - `Photos from 2025/20250716_064040.jpg`
- Alternate:
  - `Photos from 2025/20250719_083352.jpg`

#### How to Track Body Transformation Without Obsessing Over the Scale
- Recommended hero:
  - `Photos from 2025/20251119_193305.jpg`
- Alternate:
  - `Photos from 2025/20251221_171125.jpg`

### Founder / Worldview Lane

#### Why I Built Devenira for the Weeks Where You Want to Quit
- Recommended hero:
  - `Photos from 2026/20260119_125140.jpg`
- Alternate:
  - `Photos from 2025/20251221_153653.jpg`

#### The Most Reliable Way to Succeed at Dieting Is Still the Least Dramatic One
- Recommended hero:
  - `Photos from 2025/20251229_181316.jpg`
- Alternate:
  - `Photos from 2026/20260106_120635.jpg`

#### Progress Update #2: The Body Changed Slower Than My Head Did
- Recommended hero:
  - `Photos from 2025/20251221_171125.jpg`
- Alternate:
  - `Photos from 2026/20260119_124926.jpg`

#### You Do Not Need to Love Hunger. You Need to Understand It.
- Recommended hero:
  - `Photos from 2026/20260106_120635.jpg`
- Alternate:
  - `Photos from 2026/20260106_120643.jpg`

#### If Your Diet Broke Your Sleep, It Is Not Discipline Anymore
- Recommended hero:
  - `Photos from 2026/20260106_120643.jpg`
- Alternate:
  - `Photos from 2024/IMG_2084.JPG`

## Priority Image Set

If only 8 images should anchor the entire blog first, use these:

1. `Photos from 2024/IMG_1240.JPG`
2. `Photos from 2024/IMG_1775.JPG`
3. `Photos from 2025/20250716_064040.jpg`
4. `Photos from 2025/20250725_074508.jpg`
5. `Photos from 2025/20251119_193305.jpg`
6. `Photos from 2025/20251221_152946.jpg`
7. `Photos from 2025/20251229_181316.jpg`
8. `Photos from 2026/20260119_125140.jpg`

This set alone is enough to break the current repetition pattern.

## Repetition Rules

Follow these rules when assigning covers:

- do not use the exact same hero image on adjacent posts
- do not let more than 2 posts in one screenful use the same image family
- reserve `IMG_1240.JPG` for only the highest-emotion early-state posts
- reserve `20250716_064040.jpg` for mirror / check-in / hard-middle posts
- rotate `20251031_213544.jpg`, `20251119_193305.jpg`, and `20251221_171125.jpg` across hard-proof articles
- rotate `20251221_*`, `20251229_*`, `20260106_*`, and `20260119_*` across worldview / founder / authority posts
- use food, skyline, or table images as support, not as primary hero images, unless the article is specifically about routine or lifestyle

## Implementation Note

The current `posts.ts` structure stores:

- `heroImage`
- `heroAlt`

So implementation is simple:

1. copy selected source images into the public founder asset set
2. assign a unique public path per chosen hero
3. update `heroImage` and `heroAlt` per post

## Best Next Step

Apply this file in two passes:

1. update the current 4 live posts first
2. apply the same taxonomy to the next 8-12 posts before publishing them

That will solve the “why do all the blog photos look the same?” problem before the archive grows larger.
