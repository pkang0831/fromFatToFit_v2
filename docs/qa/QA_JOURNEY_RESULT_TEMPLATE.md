# Transformation Journey — QA Result Template

Copy one block per test case. Fill in after running a journey generation.

---

## Test case: _______________

**Date:** ____-__-__  
**Tester:** _______________  
**Fixture:** F__ (see SMOKE_TEST_FIXTURES.md)  

### Inputs

| Field | Value |
|-------|-------|
| Gender | |
| Current BF (estimated) | |
| Target BF | |
| Weight (kg) | |
| Muscle gains (total kg) | |
| Activity level | |

### Results

| Check | Pass | Fail | Notes |
|-------|------|------|-------|
| **Mode correct** (cut/recomp/lean_bulk/mass_gain) | | | |
| **Visual directionality correct** — stages move in the right direction | | | |
| **Identity preserved** — same person across all stages | | | |
| **Clothing preserved** — same outfit in every stage | | | |
| **Background preserved** — same scene, no artifacts | | | |
| **Lighting preserved** — no color shift or shadow changes | | | |
| **Progression believable** — changes are gradual, not jumpy | | | |
| **No fantasy physique** — no unrealistic muscularity or leanness | | | |
| **Higher BF = softer, not athletic** (if mass_gain) | | | |
| **Cut = no added muscle size** (if cut mode) | | | |
| **Warnings appropriate** — clamped targets, partial failures shown | | | |
| **Disclaimer visible** at bottom of results | | | |
| **Stage labels ordered** — Original, Early, Mid, Late, Final | | | |
| **Week numbers monotonic** | | | |
| **Nutrition plan present and mode-appropriate** | | | |
| **Workout plan present and mode-appropriate** | | | |
| **Credits deducted correctly** (30 credits, once) | | | |
| **Loading state shown** during generation | | | |
| **Value worth 30 credits?** | Yes / No | | |

### Stage image notes

| Stage | BF% | Week | Quality notes |
|-------|-----|------|---------------|
| 0 (Original) | | 0 | (uploaded photo) |
| 1 (Early) | | | |
| 2 (Mid) | | | |
| 3 (Late) | | | |
| 4 (Final) | | | |

### Overall assessment

- [ ] Ship-ready
- [ ] Needs minor fixes (describe below)
- [ ] Needs major fixes (describe below)

**Notes:**

---
