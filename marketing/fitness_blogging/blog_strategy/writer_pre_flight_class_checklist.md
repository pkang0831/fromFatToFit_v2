# Writer Pre-Flight Class Checklist

**Purpose**: Catch claim-class undercalibration BEFORE the reviewer does. Corrective action introduced after batch 13 verdict (Rule 2 widened to 2/5; pattern persistent across batches 10–13).

Run this checklist on every draft BEFORE marking it `publish_ready` and BEFORE writing the front-matter `**Claim Class**:` field.

---

## Step 1 — Hormone Noun Scan (already reliable, keep doing it)

Search the draft body for any of:

`insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4`

If ANY named hormone appears in the body → **Class 4** → human (founder) sign-off required before port.

If no hormone names → continue.

## Step 2 — Physiology-Numbers Floor Scan (NEW — addresses Rule 2 gap)

Search the draft body for any of these triggers. If ANY appear, the floor is **Class 3 minimum**, regardless of hormone naming:

### A. Water-vs-fat decomposition language
Triggers — any of these cadences:
- "X kg of that was water, the rest was fat"
- "Most of the scale jump was water, gut content, glycogen"
- "Of that 2.4 kg, only ~0.5 kg was actual fat"
- "[number] kg over [period] was about [smaller number] kg of true fat"

This is a physiological mechanism with numbers. Even without naming hormones, it's Class 3.

### B. Protein-per-kg heuristic (and other macro-per-kg quantities)
Triggers — any of:
- "1.6 to 2.2 g of protein per kg of bodyweight"
- "[number] g of protein per kg of lean mass"
- "[number] kcal per kg of bodyweight for maintenance"
- Any per-kg or per-lb dosing recommendation

These are canonical sports-nutrition heuristics. Class 3 floor per blueprint §15.

### C. Multi-day calorie arithmetic across days/weeks
Triggers — any of:
- "Total weekend overshoot: ~X calories" with day-by-day breakdown
- "A 100-calorie-per-day error compounds to ~Y kg over a month"
- "Adaptation typically reduces expenditure by 100–300 cal/day"
- Any explicit calorie-arithmetic spanning 2+ days that is being used to make a behavioral or physiological claim

If the arithmetic is the load-bearing mechanism for the post → Class 3.

### D. Recomposition or composition-shift numbers
Triggers — any of:
- "Lost X kg of fat while gaining Y kg of muscle"
- "[number] cm waist drop without scale change"
- "Beginners can gain ~1 kg of muscle per month while losing fat"
- "Lean mass / fat mass split changed by [percentages]"

Class 3 floor.

### E. Aging / decade / sex-difference physiology
Triggers — any of:
- "Body composition shifts by [number]% per decade"
- "Sleep need rises/falls by [hours] across [age band]"
- "Hormonal fluctuation across [phase] adds [kg] of water"
  - Even if no specific hormone named, "hormonal fluctuation" + numbers = Class 3
- "Recovery time scales with age by [factor]"

Class 3 floor. If a specific phase is named (perimenopause, post-menopause, andropause) → consider Class 4.

### F. Specific physiological timelines with numbers
Triggers:
- "Neural adaptation lasts 6–8 weeks"
- "Hypertrophy timeline is 12–16 weeks"
- "Glycogen stores 3 g of bound water per gram"
- "Visible muscle loss begins ~3–4 weeks into prolonged deficit"

Class 3 floor.

## Step 3 — If you self-bumped to Class 3 in step 2

Add a one-line footnote to the front matter under `**Claim Class**: 3`:

```
**Claim Class**: 3
**Class 3 Trigger**: <which of A/B/C/D/E/F triggered, in 5 words>
```

Example:
```
**Claim Class**: 3
**Class 3 Trigger**: A — water-vs-fat scale-jump decomposition
```

This makes the reviewer's audit faster (they can verify the trigger directly) and creates a writer self-awareness habit.

## Step 4 — Borderline Class 2 vs Class 3

If you genuinely believe the post is Class 2 but it touches one of the triggers above:

- Re-read the trigger sentence. Could it be removed without losing the post's central argument?
- If yes → remove it, hold Class 2.
- If no → bump to Class 3. The trigger IS the argument, which is why it's Class 3.

When in doubt, bump. Class 3 is not a punishment. It is a labeling honesty about what the post is doing.

## Step 5 — Banned Phrase Scan

Search for: `game changer, unlock, your journey, at the end of the day, hack, fitness goals, trust the process, no excuses`.

If any appear → either remove or wrap in self-aware meta-mention (acknowledged in body, not deployed as filler).

## Step 6 — Internal Link Validation

For each `**Suggested Internal Links**:` entry, confirm the slug exists in `frontend/src/content/blog/posts.ts`:

```bash
grep "slug: '<your-slug-candidate>'" frontend/src/content/blog/posts.ts
```

If grep returns nothing, replace with a real slug.

## Step 7 — Hero/Inline Image Validation

Confirm both image paths exist in `frontend/public/founder/`:

```bash
ls frontend/public/founder/<your-image-name>.jpg
```

Confirm the inline image is NOT the same file as any other batch draft's hero (rule 8). Quick check: list all hero + inline image paths across the 5 drafts in the batch; the 10 paths should all be distinct.

## Step 8 — Image Pool Saturation Check (per `image_pool_tightened_policy.md`)

If any candidate hero is at 4 uses (per current count): skip — Rule T2 forbids.
If any candidate hero is at 3 uses: still legal, but prefer 1-use or 2-use candidates if available.
If you must use a 4-use image as inline (legal): note in image plan.

---

## Quick Self-Audit Form

Before marking a draft `publish_ready`, fill this in mentally:

| Check | Answer |
|-------|--------|
| Hormone names? | [ ] none / [ ] yes → Class 4 |
| Triggers from §2 A–F? | [ ] none / [ ] yes → bump to Class 3 + add trigger note |
| Banned phrases? | [ ] none / [ ] yes → remove or wrap |
| Internal links resolve in posts.ts? | [ ] both / [ ] need fix |
| Hero & inline files exist on disk? | [ ] both / [ ] need swap |
| Hero against 5-adjacent rule? | [ ] safe / [ ] swap needed |
| Hero against image policy T2 (4-use skip-2)? | [ ] safe / [ ] swap needed |
| Inline distinct from any other batch draft's hero? | [ ] safe / [ ] swap needed |

If any cell is on the wrong side, fix before saving.

---

## Why This Exists

Batches 10, 11, 12, 13 each had 1–2 drafts where the writer set Class 2 and the reviewer bumped to Class 3 on physiology-numbers floor. The pattern was not a writing problem — the drafts themselves were good. It was a categorization problem. The triggers above are the exact sentences that have been bumped across 4 batches.

This checklist exists so that the bump happens at the writer step, not the reviewer step. Two benefits:

1. Reviewer cycles get one less must_fix item per batch (faster close)
2. Writer's own model of Class 2 vs Class 3 gets calibrated against the actual triggers, not against intuition

If the writer self-bumps correctly, batch 14 should hit 0/5 on Rule 2 — the trend reversal that has not happened yet.
