# Batch 10 Verdict — Posts 47–51

Reviewer: subagent per `reviewer_agent_spec.md`
Scope: 5 drafts in `marketing/devenira_prelaunch/`
Context: posts 37–46 (last 10 approved) and 39 currently ported slugs in `frontend/src/content/blog/posts.ts`

---

## Draft 1 — why-you-stop-losing-weight-around-month-three

```
slug: why-you-stop-losing-weight-around-month-three
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: weight loss slows month three
keyword_collision: no
format: deep_dive
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues: none material. Opening lands fast, mechanism section (four stacking causes) is the cleanest deep-dive in the batch. Hero `plateau-middle-checkin-20250711.jpg` is exactly on-lane for plateau/consistency. Both internal link targets (`what-actually-counts-as-a-weight-loss-plateau`, `a-plateau-is-a-data-point-not-a-failure`) exist in posts.ts. No hormone tokens, physiology numbers handled at Class 3 correctly. Close delivers on the opening without CTA push.

Suggested internal links: ok as-is.

---

## Draft 2 — am-i-actually-hungry-or-am-i-bored

```
slug: am-i-actually-hungry-or-am-i-bored
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: hungry or bored eating
keyword_collision: no
format: qa
checklist_failures: [8]
must_fix:
  - bump claim_class 2 → 3 (the "wobbly blood sugar gets misread as hunger" line plus the macronutrient-timing / under-fueling pass in Q7 crosses into physiology-adjacent reasoning per drift rule 2)
voice_drift_flag: no
```

Top 3 issues:
1. Claim class under-calibrated (physiology reference to blood sugar + under-fueling mechanism → Class 3 minimum).
2. None voice-related; the "apple test" Q is a strong quotable.
3. Hero `sleep-reflective-20260106.jpg` is off its documented primary lane (post-30 checkpoint assigned it to recovery/rest-focused posts), but it is the correct rotation choice given hunger-editorial is at saturation, so keep it — just note it consumed the reserved rest-post slot for an appetite-category post.

Repetition risk: low. Engagement: strong — "The craving is specific. The hunger is general." is the share-card line. Internal links (`why-appetite-feels-stronger-the-longer-you-diet`, `you-do-not-need-to-love-hunger-you-need-to-understand-it`) both exist.

---

## Draft 3 — how-much-protein-do-i-actually-need-to-lose-fat

```
slug: how-much-protein-do-i-actually-need-to-lose-fat
verdict: revise
claim_class: 3
title_collision: no
primary_keyword: how much protein for fat loss
keyword_collision: no
format: deep_dive
checklist_failures: [6]
must_fix:
  - replace hero: `diet-slip-checkin-20250725.jpg` is a cheat-day / diet-slip lane asset per blog_cover_mapping (taxonomy B, assigned to "Read This Before You Try to Fix Your Diet Slip"). Using it for a food-structure / protein post is a semantic lane mismatch (drift rule 9). `hunger-editorial-20260106.jpg` is over-budget; prefer `transformation-proof-20251119.jpg` (food-structure / composition framing) or move the current inline `water-weight-proof-20251031.jpg` to hero and pick a neutral D-lane inline.
voice_drift_flag: no
```

Top 3 issues:
1. Hero/topic semantic mismatch (diet-slip asset on a protein post).
2. Slight voice flattening in "What adequate protein looks like in practice" — the bullet list of meal sources is the most template-like paragraph in the batch. Consider trimming to 2 sources or converting to running prose.
3. The "kidneys are fine" aside is fine at Class 3 but tighten to one sentence so it does not carry more weight than the preservation argument.

Internal links (`the-quiet-role-vegetables-play-in-staying-full`, `the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one`) both exist. Banned-phrase scan clean. Hormone token scan clean.

---

## Draft 4 — why-your-workouts-feel-harder-when-youre-dieting

```
slug: why-your-workouts-feel-harder-when-youre-dieting
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: workouts feel harder on diet
keyword_collision: no
format: qa
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Cleanest Q&A in the batch. "The fuel is different. The session is not." and "you are a dieting person lifting weights" are both quotable. Week-by-week compounding section earns its length. Hero `consistency-editorial-20251229.jpg` is a soft reach for exercise/recovery (it is a founder/worldview asset), but the alt framing about consistent sessions under a different fuel state holds, and the inline `scale-rude-before-20240130.jpg` is uniquely used in the batch. Internal links exist. Hormone scan clean despite the temptation to name cortisol — writer's self-audit on noun-scan is validated.

---

## Draft 5 — why-your-strength-increases-before-your-shape-changes

```
slug: why-your-strength-increases-before-your-shape-changes
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: strength increases before body changes
keyword_collision: no
format: personal_story
checklist_failures: [8]
must_fix:
  - bump claim_class 2 → 3. "Neural adaptation" with specific timelines (6–8 weeks coordination, 12–16 weeks hypertrophy) is physiology with numbers. Drift rule 2 says physiology → Class 3 minimum even without named hormones.
voice_drift_flag: no
```

Top 3 issues:
1. Claim class. Fix at port.
2. Otherwise strong — the "reps, then feel, then photo" beat is the quotable; "15 kg to my deadlift in six weeks / did not look meaningfully different" is a clean personal-story opening that anchors the mechanism.
3. Hero `patience-middle-checkin-20250731.jpg` is a defensible pull from lane B into exercise/recovery on the "patience before visible change" framing. Inline `weighin-middle-progress-20240801.jpg` is unique in the batch.

Internal links (`when-the-workout-becomes-therapy-not-punishment`, `losing-weight-is-not-the-same-as-getting-leaner`) both exist.

---

## Batch Summary

```
format_distribution: {deep_dive: 2, qa: 2, personal_story: 1}
category_distribution: {plateau/consistency: 1, appetite: 1, food structure: 1, exercise/recovery: 2}
recurring_issue: claim_class undercalibration on physiology-with-numbers posts (drafts 2, 5) — writer's hormone-noun scan caught named tokens correctly but missed the physiology-floor promotion (Class 3 min when physiology is present without named hormones)
overall_notes: >
  Strongest batch since batch 7. Voice recognizable across all 5 drafts, rhythm varied, no
  template fingerprint emerging. Zero title/keyword collisions. All 5 hero and 5 inline
  paths exist on disk. All 10 internal-link slugs (2 per draft) exist in posts.ts. Banned
  phrase scan clean. Hormone noun-scan clean — writer's self-audit validated.
  Two drafts (2, 5) still need claim_class bumped before port; one draft (3) needs a hero swap for lane fit.
  Consecutive-format rule satisfied (no 3-in-a-row same format; posts 50–51 are qa→personal_story).
  Category spread healthy within the 10-post window (plateau 1, appetite 1, food 1, exercise 2
  against preceding sleep/scale/binge/appetite mix in 37–46).
```

### Drift Rule Scorecard (batch 10)

| # | Rule | Status |
|---|------|--------|
| 1 | Internal-link slug existence | clean (already RESOLVED in batch 9) |
| 2 | Claim class calibration (hormone noun-scan) | fail — drafts 2 and 5 undercalibrated on physiology floor, though hormone-name scan itself was clean |
| 3 | Banned phrase keyword | clean (already RESOLVED in batch 9) |
| 4 | Head-term keyword collision | clean (already RESOLVED in batch 9) |
| 5 | Inline image variety within batch | clean (5 unique inlines) |
| 6 | Hero/inline image existence | clean — **RESOLVED** (2 of 2 consecutive clean batches) |
| 7 | Hunger-editorial hero rotation | clean — **RESOLVED** (batch 8 no-hunger, batch 9 no-hunger, batch 10 appetite post used `sleep-reflective-20260106.jpg` instead) |
| 8 | Hero/inline cross-role reuse within batch | clean (hero set and inline set disjoint) |
| 9 | Hero/topic semantic mismatch via cover taxonomy | fail — draft 3 uses diet-slip lane asset on a food-structure/protein post |

### 5-Adjacent Hero Check vs Posts 42–46
- 42–46 heroes: start.jpg, body-composition-proof-20251221.jpg, long-game-founder-20251221.jpg, sleep-reflective-window-20241217.jpg, final-portrait.jpg
- 47–51 heroes: plateau-middle-checkin-20250711.jpg, sleep-reflective-20260106.jpg, diet-slip-checkin-20250725.jpg, consistency-editorial-20251229.jpg, patience-middle-checkin-20250731.jpg
- No overlap. `sleep-reflective-20260106.jpg` is a distinct file from `sleep-reflective-window-20241217.jpg`. Rule 5-adjacent: satisfied.

### Non-Standard Post Type Check
Approved-post count after this batch will be 51. Progress Update #4 is due at count 60 per plan §13 — not yet, but the next two batches should seed one founder/worldview post and one progress-adjacent post to keep pacing. No deep-dive fatigue detected.

---

## Final Action Return

**Per-draft verdicts:**
1. `why-you-stop-losing-weight-around-month-three` → **pass** (Class 3, port as-is)
2. `am-i-actually-hungry-or-am-i-bored` → **revise** (bump claim_class 2→3)
3. `how-much-protein-do-i-actually-need-to-lose-fat` → **revise** (swap hero off diet-slip lane)
4. `why-your-workouts-feel-harder-when-youre-dieting` → **pass** (Class 3, port as-is)
5. `why-your-strength-increases-before-your-shape-changes` → **revise** (bump claim_class 2→3)

**Batch rule summary:** 7/9 drift rules clean. **Rule 6 (hero/inline image existence) RESOLVED** — 2 of 2 consecutive clean batches. **Rule 7 (hunger-editorial hero rotation) RESOLVED** — 3 consecutive clean cycles (batches 8, 9 had no hunger post; batch 10 appetite post rotated off hunger-editorial onto sleep-reflective-20260106). Rules 2 (claim class) and 9 (hero/topic semantic mismatch) remain open.

**Strongest / weakest:** Strongest is draft 1 (month-three) — cleanest mechanism-to-application arc and the most honest close in the batch; weakest is draft 3 (protein) — useful content but carries a cheat-day-lane hero on a food-structure post and its "sources" bullet list is the most template-flavored paragraph in the five.
