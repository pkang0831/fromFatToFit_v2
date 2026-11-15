# Transformation Journey — Manual QA Checklist

Manual test scenarios for the AI Body Transformation Journey feature.
Run through these before each release that touches the transformation pipeline.

## Prerequisites

- A test user with sufficient credits (>= 30)
- A full-body photo for upload
- Access to the `/body-scan` page, "Transformation Journey" tab

---

## 1. Mode Paths

| # | Scenario | Inputs | Expected |
|---|----------|--------|----------|
| 1.1 | **Cut** | Current ~25% BF male, target 12% | Mode shows "Fat Loss". Stages show decreasing BF%. Images get progressively leaner. No muscle size increase in descriptors. |
| 1.2 | **Mass gain** | Current ~15% BF male, target 25% | Mode shows "Weight Gain". Stages show increasing BF%. Images get softer/fuller. No "defined" / "muscular" / "athletic" in descriptors. |
| 1.3 | **Lean bulk** | Current 12% male, target 15%, muscle gains > 0 in form | Mode shows "Lean Bulk". Stages show slight BF increase with subtle size gains. |
| 1.4 | **Recomp** | Current 20% male, target 18%, muscle gains > 0 | Mode shows "Body Recomposition". Subtle changes. Timeline is long (recomp is slow). |

## 2. Gender Paths

| # | Scenario | Expected |
|---|----------|----------|
| 2.1 | Female cut (30% -> 22%) | Female-specific descriptors. BF floor at 14% if target is extreme. |
| 2.2 | Male cut (25% -> 12%) | Male-specific descriptors. BF floor at 6%. |

## 3. Edge Cases

| # | Scenario | Expected |
|---|----------|----------|
| 3.1 | Extreme low BF: male target 3% | Warning banner visible. Target clamped to 6%. |
| 3.2 | Extreme low BF: female target 10% | Warning banner visible. Target clamped to 14%. |
| 3.3 | Higher target BF (15% -> 25%) | Mass-gain mode. NO lean/athletic descriptors. Softness increases. |
| 3.4 | Nearly identical BF (20% -> 20.2%) | Warning about "nearly identical". Journey still generates (recomp mode). |
| 3.5 | Above ceiling (target 50%) | Warning about "outside supported range". |

## 4. Optional Input Combinations

| # | Scenario | Expected |
|---|----------|----------|
| 4.1 | Only gender + target BF | Journey generates with defaults for weight/height/age/activity. |
| 4.2 | All fields filled (weight, height, age, activity, muscle gains) | More accurate nutrition plan (real TDEE). Weight projections appear per stage. |
| 4.3 | Muscle gains set to 0 everywhere | No muscle-size language in cut/mass_gain descriptors. |

## 5. Image Generation

| # | Scenario | Expected |
|---|----------|----------|
| 5.1 | All 4 stages succeed | 5 stages in carousel (original + 4 generated). No warning about failures. Credits deducted once (30). |
| 5.2 | 1 stage fails (simulate: network glitch) | If < 3 stages succeed: error message, no credits charged. If >= 3 succeed: partial warning shown, credits charged. |
| 5.3 | All stages fail | Error message "stage images generated successfully. No credits were charged." displayed. Balance unchanged. |

## 6. Loading State

| # | Scenario | Expected |
|---|----------|----------|
| 6.1 | Click "Generate My Journey" | Button shows loading spinner. Message "Generating 4 stage images + diet & workout plan..." visible. UI is non-interactive during generation. |
| 6.2 | Generation completes | Loading state clears. Carousel appears with stage images. |

## 7. Credit Deduction

| # | Scenario | Expected |
|---|----------|----------|
| 7.1 | Sufficient credits (>= 30) | Balance decreases by 30 after successful generation. |
| 7.2 | Insufficient credits (< 30) | "Not enough credits" error. No generation attempted. "Get Credits" button shown. |
| 7.3 | Retry after failure | No double charge. Only charged on successful generation. |

## 8. Warnings and Disclaimers

| # | Scenario | Expected |
|---|----------|----------|
| 8.1 | Clamped BF target | Warning banner at top of results: "Target body fat X% is below the safe minimum..." |
| 8.2 | Partial stage failure | Warning in results: "N of 4 stage image(s) failed to generate." |
| 8.3 | Disclaimer | Visible at bottom of results: "AI-generated visual estimate ... not medical advice ..." |

## 9. Stage Carousel

| # | Scenario | Expected |
|---|----------|----------|
| 9.1 | Carousel navigation | Left/right arrows navigate between stages. Dots below show progress. Stage 0 = "Original" with uploaded photo. |
| 9.2 | Stage labels | "Original", "Early", "Mid", "Late", "Final" in order. Week numbers increase monotonically. |
| 9.3 | BF% display | Each stage shows its BF%. Values are monotonic (decreasing for cut, increasing for gain). |
| 9.4 | Body composition details | Expandable section per stage. Shows face, waist, abdomen, chest, arms, shoulders, legs descriptors. Shows weight/lean/fat deltas if weight was provided. |

## 10. Nutrition and Workout Plans

| # | Scenario | Expected |
|---|----------|----------|
| 10.1 | Nutrition section | Collapsible. Shows daily calories, protein, carb/fat ranges, meal structure, weekly adjustment, check-in cadence, stage notes, assumptions, disclaimer. |
| 10.2 | Workout section | Collapsible. Shows split type, sessions/week, exercise list with muscle groups, sets/reps guidance, progression, cardio, recovery, deload, stage adjustments. |
| 10.3 | Mode-appropriate plans | Cut: deficit calories, strength maintenance. Lean bulk: surplus, progressive overload. Mass gain: larger surplus, consistency focus. Recomp: maintenance calories, high protein. |

---

## Sign-off

| Tester | Date | Result | Notes |
|--------|------|--------|-------|
| | | | |
