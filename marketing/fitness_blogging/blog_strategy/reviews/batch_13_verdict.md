# Batch 13 Verdict — Posts 62–66

Reviewer: subagent per `reviewer_agent_spec.md`
Scope: 5 drafts in `marketing/devenira_prelaunch/`
Context: posts 52–61 (last 10 approved) and 54 currently ported slugs in `frontend/src/content/blog/posts.ts`
New constraints applied:
- post-50 voice audit Q&A correction (rule 10) — draft 3 is the only Q&A this batch
- tightened image policy from `image_pool_tightened_policy.md` (Rule T2: 4-use skip-2 — three 4-use images barred from batch 13 hero slots)
- rule 9 resolution candidate: batch 13 must be the 3rd consecutive clean batch on hero/topic semantic match

---

## Draft 1 — the-bad-weekend-that-finally-taught-me-something

```
slug: the-bad-weekend-that-finally-taught-me-something
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: bad diet weekend lessons
keyword_collision: no
format: personal_story
checklist_failures: [8]
must_fix:
  - bump claim_class 2 → 3 per drift Rule 2. Body contains a recomposition / water-vs-fat decomposition with concrete numbers: "About 0.5 kg of actual fat by the math, the rest of the scale jump being water from the carb load and the sodium and the alcohol." Plus calorie-arithmetic at scale ("Total weekend overshoot: somewhere around 4,000 calories," "1,400 over and my framing only allowed for 0 over or 4,000 over"), and a multi-day fat-vs-water reading framework ("The actual fat addition was small enough that, treated as a 200-calorie deduction across the next week, it disappeared into the trend within ten days"). Per drift rule 2: physiology numbers + water/fat decomposition → Class 3 floor regardless of hormone naming. Same trigger pattern flagged on batch 11 draft 2, batch 10 drafts 2 and 5, batch 12 draft 5.
```

Top 3 issues:
1. Claim class undercalibrated (see must_fix). Third batch in a row carrying a Class 2 → 3 bump on a personal_story that touches the water-vs-fat-vs-scale heuristic. The writer's pre-flight Class audit reliably catches hormone names (none here — clean) but continues to mis-judge "scale jump = mostly water + small fat" decomposition as Class 2. This is the same pattern noted in batches 10, 11, 12. Pattern is no longer shrinking; it has stayed at exactly this trigger across four batches now.
2. The "What the weekend actually contained" section runs Friday → Saturday → Sunday in three short consecutive paragraphs followed by an explicit "Total weekend overshoot" arithmetic line. Reads close to the soft list-scaffolding shape flagged on batch 11 draft 2 ("Lighting / Posture / Time of day") and batch 12 draft 5 ("week 0 / 6 / 12 / 18 / 26 / 40 jeans"). The rescue line "The food was a small story. The pattern was the whole story." holds the founder voice and earns the jump to the principle section. Borderline; keep, but flag the day-by-day-with-arithmetic structure as the third batch in a row of "founder accounts for damage in serial paragraphs" — emerging fingerprint.
3. The "Why the binary framing felt safer" → "What I changed the next Monday" pivot is the load-bearing turn of the post. "I had to give up the satisfaction of a clean daily grade to get a system that did not collapse under one bad meal." is the share-card and the principle. The closing pair ("A weekend cannot ruin a program that has a recovery mode. A perfect program with no recovery mode can be ruined by a single Friday.") earns the title. Voice unimpeachable.

Repetition risk: low. Cheat/binge category was last directly opened at post 38 (`cheat-days-do-not-expose-your-character-they-expose-your-system`, in posts.ts) and post 41 (`read-this-before-you-try-to-fix-your-diet-slip`). The "tolerance band / weekly unit / recovery mode" angle is materially fresher than either prior cheat-lane piece. Distinct.
Voice drift: none. Anchor-grade. "I did not stop having Friday dinners. I stopped having them in a system that could not survive them." is the second share-card.
Engagement risk: low. Three quotable candidates: closing pair above, "I did not stop having Friday dinners…", and "A perfect program with no recovery mode can be ruined by a single Friday."
SEO fixes:
- Meta description on length (~155 chars). Clean.
- Primary keyword "bad diet weekend lessons" is honest and uncrowded; matches "what to learn from a bad weekend" intent. No collision with the 54 ported slugs.
- H2 set scans well; "Why the binary framing felt safer" reads slightly editorial — minor, keep.
Image / flow fixes:
- Hero `cheat-day-checkin-20250719.jpg` exists; lane B (honest proof / cheat-day) — exact lane match for cheat/binge per cover taxonomy and per the pre-cleared hero set in `image_pool_tightened_policy.md`. 5-adjacent check vs posts 57–61 heroes: zero overlap. T2 compliant (not one of the three 4-use saturated images). Clean.
- Inline `diet-slip-checkin-20250725.jpg` exists; lane B (honest proof). Anchored to "The food was a small story. The pattern was the whole story." Anchor verbatim in body. Clean.
Feed fit: opens the cheat/binge lane for the post-60 stretch and earns the slot directly after the milestone-then-clothes pair (60–61). Best published as the first post after Progress Update #4's afterglow.
Suggested internal links: keep as-is. Both `cheat-days-do-not-expose-your-character-they-expose-your-system` and `read-this-before-you-try-to-fix-your-diet-slip` resolve in posts.ts.

---

## Draft 2 — how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud

```
slug: how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud
verdict: pass
claim_class: 2
title_collision: no
primary_keyword: mirror diet weight loss anxiety
keyword_collision: no
format: deep_dive
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Claim class correctly set on first pass. Body avoids physiology numbers and recomposition arithmetic entirely — argues at the behavioral / attention-loop / instrument-selection level. References "water from the cumulative stress of dieting through the week" once but does not enter water-vs-fat decomposition territory or invoke a recomposition split. Hormone noun-scan clean: zero of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4} named. Class 3 floor not triggered. Class 4 escalation not needed. Cleanest Class 2 hold of the batch.
2. The "Look less. Look better. Look in fewer states." three-rule refrain (introduced as the "what a mirror diet actually looks like" section, restated at the end) is the share-card and the spine of the post. The deliberate echo ("The line worth keeping" closes on the same triplet) is the kind of refrain-as-architecture move the program does well. Holds.
3. The "What I did during my own loud phase" section ("I covered a mirror.") is the founder-anchored beat the deep_dive needs to keep its honesty. Specific (full-length bedroom mirror, three weeks, smaller bathroom mirror retained as the structured check) and earns the post's broader argument. This is the load-bearing personal paragraph — protect it under any revise.

Repetition risk: low. Mirror category was directly opened at post 53 (`progress-photos-can-lie-as-much-as-the-mirror-does`) and earlier in posts.ts (`why-the-mirror-can-make-real-progress-feel-fake`). The "mirror diet as protocol with three rules and a window" framing is materially different from either: those posts argue the mirror is unreliable; this post argues for an active reduction protocol with explicit conditions. Distinct angle.
Voice drift: none. Anchor-grade. "The mirror is not an instrument. It is a feedback loop." holds the founder-observation-before-prescription cadence. "Treating the body well sometimes means turning down the loudest instrument in the room." is the second share-card.
Engagement risk: low. Three quotable candidates: the three-rule refrain, "The mirror is not an instrument. It is a feedback loop.", and "That mirror diet did more for body image than any pep talk ever did."
SEO fixes:
- Meta description ~160 chars. Clean.
- Primary keyword "mirror diet weight loss anxiety" is unusual but honest; the article literally coins / uses "mirror diet" as the term and earns it. Matches the "stop checking the mirror" PAA cluster. No collision.
- H2 set scans well; "What a mirror diet actually looks like" is the strongest skim-reward anchor.
Image / flow fixes:
- Hero `founder-story-hanok-20260119.jpg` exists; lane A (founder/credibility). Pre-cleared in `image_pool_tightened_policy.md` as a "soft for mirror/discipline" assignment. Cover taxonomy lane for mirror is primarily B (honest proof / mirror); A is a defensible bridge under reuse pressure (the obvious lane-B mirror hero `mirror-middle-checkin-20250716.jpg` is at 3-use saturation and would push toward 4-use). Hero alt acknowledges the bridge framing ("the calm of stepping back from constant mirror checking during a loud phase"). Soft cross-lane for rule 9 — same generosity standard the reviewer applied to batch 12 draft 2 (lane-B for appetite). Defensible bridge, not a wrong lane.
- Inline `sleep-reflective-20260106.jpg` exists; lane D (lifestyle / support); anchored to "Look less. Look better. Look in fewer states." Anchor verbatim in body. Clean. Second deployment of `sleep-reflective-20260106.jpg` (first was batch 10 draft 2 hero). Within rule T4 soft preference but past 4-batch window (batches 10 → 13 = 3 batches gap, technically 1 short of the 4-batch soft window — flag as cross-batch soft note, not a blocker).
Feed fit: best published with at least 1 non-mirror post on either side. Cover taxonomy lane for mirror is currently saturated; this is the dedicated mirror post that earns the lane.
Suggested internal links: keep as-is. Both `why-the-mirror-can-make-real-progress-feel-fake` and `progress-photos-can-lie-as-much-as-the-mirror-does` resolve in posts.ts.

---

## Draft 3 — do-i-actually-have-to-meal-prep-to-lose-weight

```
slug: do-i-actually-have-to-meal-prep-to-lose-weight
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: do i have to meal prep to lose weight
keyword_collision: no
format: qa
checklist_failures: [6, 8]
must_fix:
  - bump claim_class 2 → 3 per drift Rule 2. Body contains a canonical sports-nutrition heuristic with numbers: "am I hitting 1.6 to 2.2 grams of protein per kg of body weight on most days under my current system?" Per blueprint §15: "Class 3: behavioral science / nutrition heuristic with reasoning." A protein-per-kg recommendation is the textbook example of a Class 3 nutrition heuristic. Hormone noun-scan: clean (no named hormones). Class 4 escalation not needed.
  - swap inline image. `cheat-day-checkin-20250719.jpg` is already deployed as the hero on draft 1 of this batch. Using it as inline on draft 3 violates rule 8 (hero/inline cross-role reuse within batch) — rule 8 was RESOLVED in batch 10 with 3 consecutive clean batches. Cleanest swap candidates, in order of preference: (a) `consistency-editorial-20251229.jpg` (lane A, currently 3-use; the "default is the program" theme matches editorial-consistency framing), (b) `start.jpg` (lane A, 1-use, last used post 42 as inline; "build the default first" anchor candidate), (c) `final-portrait.jpg` (lane A, 1-use, last used post 56). Either (a) or (b) is the cleanest under-saturation-pressure swap. Update the inline anchor sentence accordingly.
```

Post-50 Q&A audit correction — explicit check (rule 10):
- Founder-anchored Q present: **yes (two)**. "Q: What did meal prep look like for me?" opens "Honestly? Mostly it didn't." and continues into the three-Sundays anecdote with concrete details ("By Wednesday, I was eating the same chicken-broccoli-rice combo and resenting it. By Thursday, I was eating it cold. By Friday, I had abandoned the containers and ordered something."). "Q: What did the structure that finally worked actually look like?" opens "For my own program, the working structure was: A short list of three default dinners that I rotated through, plus two restaurant defaults…" Both first-person observation, not prescription.
- Concrete sensory / metaphorical line in place of bullet-list mechanism: **yes (multiple)**. "I did not need a Sunday. I needed a default." (the share-card). "The food is the infrastructure, not the entertainment." "By Wednesday, the containers will feel like an obligation. By Friday, they will feel like a constraint. By Sunday, you will not want to cook again." None of the answers degrades into a true bulleted list — the "Three problems at the same time, usually" section uses three short paragraphs (Decision fatigue / Macro reliability / Friction reduction) instead of a hard list, matching the precedent from batch 12 draft 2's "Caloric debt / Decision fatigue / Lower blood sugar" treatment.
- Net: post-50 correction **honored**. Reader Address has founder-I in 4 of 8 Qs (matches batch 12 draft 2 footprint exactly). Imagery Density carried by the Sunday/Wednesday/Friday/Sunday containers-as-mood line and the "infrastructure not entertainment" framing.
- 3rd consecutive clean cycle. Per running notes ("Revisit at post-75 audit"), rule 10 stays in observation rather than resolving early.

Top 3 issues:
1. Claim class undercalibrated (see must_fix). The protein-per-kg heuristic is the canonical Class 3 nutrition heuristic — the writer's pre-flight Class 2 default for personal Q&A breaks here. Same pattern shape as draft 1 of this batch and the four-batch trail of similar bumps.
2. Inline image violates rule 8 (see must_fix). Re-opens a rule that was RESOLVED in batch 10 and held clean across 3 consecutive batches. This is the only intra-batch image violation across the trailing 4 batches. Pre-flight should have caught it: the hero file path on draft 1 and the inline file path on draft 3 are byte-identical strings. Recommend writer adds a script-level grep before next batch.
3. The post is the longest draft of the batch (eight Qs plus the closing principle). The "Q: What about the protein question specifically?" section is the strongest mechanism-as-question turn — earns its placement and is where the post pivots from "do I have to" to "what is the actual underlying question." Hold this section under any revise; the bulk of the trim, if any, can come from compressing the "Q: When does meal prep actually help?" three-cases section into a single denser paragraph if length becomes a SEO concern. Voice rescues the length: each Q is founder-rendered rather than mechanism-only.

Repetition risk: low/medium. Food structure category has not been directly opened in the post-47 window (closest was post 50 at the post-50 audit boundary). This is the dedicated food-structure post for the post-50 stretch — fresh angle for the lane and overdue per §11 spread.
Voice drift: none. Q&A correction landed. Reader Address and Imagery Density both visibly above the post-50 audit floor.
Engagement risk: low. Three share candidates: "I did not need a Sunday. I needed a default.", "The food is the infrastructure, not the entertainment.", and "Build the default first. Add a Sunday only if the default genuinely needs the help."
SEO fixes:
- Meta description on length (~150 chars). Clean.
- Primary keyword "do i have to meal prep to lose weight" reads slightly conversational but matches the question's literal phrasing — strong PAA / voice-search candidate. No collision.
- H2 question stems are all good for People-Also-Ask harvesting and are the structural justification for the Q&A format.
Image / flow fixes:
- Hero `sleep-reflective-window-20241217.jpg` exists; lane D (lifestyle / support) — defensible match for food structure / weeknight default framing. Last used post 45 per pre-cleared plan. T2 compliant. 5-adjacent check vs posts 57–61: zero overlap. Clean.
- Inline `cheat-day-checkin-20250719.jpg` violates rule 8 (cross-role reuse within batch). See must_fix.
Feed fit: this is the food-structure anchor for the post-50 stretch. Best published 2+ posts after the cheat/binge draft (draft 1) so the lane spread holds.
Suggested internal links: keep as-is. Both `the-quiet-role-vegetables-play-in-staying-full` and `how-much-protein-do-i-actually-need-to-lose-fat` resolve in posts.ts.

---

## Draft 4 — why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think

```
slug: why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: cardio backfires on diet
keyword_collision: no
format: deep_dive
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Claim class correctly set on first pass — **writer caught the Class 3 floor unprompted on a physiology-numbers post for the second time in three batches** (first was batch 11 draft 4). Body carries physiology numbers — "300 calories of cardio gets met with a modest compensation," "the same 300 calories of cardio that gave you 250 net during maintenance often gives you 80 net during a cut," "100 to 200 calories" deficit-vs-cardio swap, "200-calorie-per-day drift" — and uses NEAT as a behavioral mechanism rather than a hormone. Hormone noun-scan clean: zero of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4}. Class 4 escalation not needed. This is the strongest pre-flight Class calibration of the batch.
2. The "Why the body answers harder during a cut than during maintenance" section is the load-bearing mechanism paragraph. The maintenance-vs-cut compensation framing ("In maintenance, the body has spare energy. Adding 300 calories of cardio gets met with a modest compensation… In a cut, the body does not have spare energy.") is the share-card mechanism and the post's central explanation. The closing line of that section ("This is not a quirk. This is the body doing exactly what an energy-conserving system is supposed to do under restriction.") is the principle restatement that earns the deep_dive format.
3. The "What I did when my own cut stalled" founder-anchored paragraph is the personal-story payload the deep_dive needs to keep the principle from floating ("I did not add cardio. I ran an honest tracking week. The week revealed a 200-calorie-per-day drift in my logging, mostly from oil and rice estimation."). Specific, vulnerable, and earns the post's central argument that cardio addition is rarely the cheapest first move.

Repetition risk: low. Exercise/recovery category was last directly opened at post 36 (`why-your-workouts-feel-harder-when-youre-dieting`, in posts.ts) and indirectly at post 47 (`exercise-isnt-shrinking-you-the-way-you-expected`). The "added cardio under-performs because of compensation" angle is materially different from either prior exercise-lane piece. Distinct.
Voice drift: none. Anchor-grade. "Cardio is not the wrong tool. Cardio is rarely the cheapest tool." is the share-card and the second-strongest line in the batch.
Engagement risk: low. Four share candidates: "The cardio adds expenditure. The body answers.", "Cardio is not the wrong tool. Cardio is rarely the cheapest tool.", "A stalled cut is rarely a movement deficit.", and "Run the cheaper interventions first. Save cardio for when it is filling a real hole, not when it is filling an emotional one."
SEO fixes:
- Meta description on length (~158 chars). Clean.
- Primary keyword "cardio backfires on diet" is honest and uncrowded; matches the "why is cardio not working" PAA cluster. No collision.
- H2 set is the strongest scannable spine of the batch; "What to try before adding cardio" is the most skim-rewarding anchor.
Image / flow fixes:
- Hero `transformation-proof-20251119.jpg` exists; lane C (hard physique proof) — defensible match for exercise/recovery / composition-context framing. Last used post 42 per pre-cleared plan. T2 compliant (currently 2-use, rising to 3-use after this slot). 5-adjacent check vs posts 57–61: zero overlap. Clean.
- Inline `patience-middle-checkin-20250731.jpg` exists; lane B (honest proof / patience). Anchored to "The cardio adds expenditure. The body answers." Anchor verbatim in body. Clean.
Feed fit: this is the exercise/recovery anchor for the post-50 stretch. Best published with at least 1 non-deep_dive post on either side (the batch satisfies this — draft 3 qa precedes, draft 5 myth_buster follows).
Suggested internal links: keep as-is. Both `why-your-workouts-feel-harder-when-youre-dieting` and `exercise-isnt-shrinking-you-the-way-you-expected` resolve in posts.ts.

---

## Draft 5 — weighing-yourself-every-day-can-be-a-trap-not-a-discipline

```
slug: weighing-yourself-every-day-can-be-a-trap-not-a-discipline
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: daily weigh in trap weight loss
keyword_collision: no
format: myth_buster
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Claim class correctly set on first pass — writer caught the Class 3 floor unprompted on a recomposition-numbers post (the second self-correction of the batch alongside draft 4). Body carries the canonical water-vs-fat-vs-muscle decomposition: "1 to 2 kg in either direction across 24 hours from water alone, with no change in fat or muscle," "A 0.5 kg per week loss is about 70 grams per day on average — well below the noise floor of the daily fluctuation," and the gut-content vs water-weight breakdown in "What the daily reading is mostly measuring." Hormone noun-scan: post references "hormonal fluctuation" generically as one of several water-shift drivers but does not name any of {insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4}. Generic "hormonal fluctuation" does not trigger Class 4 per drift rule 2 phrasing ("any of {…} named"). Class 3 stands. Class 4 escalation not needed.
2. The "what an emotional response to a daily reading actually costs" section is the load-bearing behavioral-cost paragraph. The two-direction analysis ("Either toward over-restriction… or toward defeat-eating") plus the closing "The body is not graded on either. The body is responding to the average across two weeks. The day is just weather." is the share-card mechanism and the post's central reframing.
3. The "What I did" founder-anchored section is the personal-story payload that keeps the myth-buster honest ("I weighed daily for the first three months of my cut. It was a slow disaster. … I switched to weekly weighing — Wednesday morning, post-bathroom, fasted — for the next three months. The trend continued at exactly the same rate. The mood improved noticeably."). Specific, vulnerable, and earns the title's "trap, not discipline" pivot.

Repetition risk: low/medium. Scale category was last directly opened earlier in posts.ts (`one-emotional-weigh-in-can-wreck-a-good-week`, `the-scale-lies-differently-in-the-morning-than-in-the-evening`). The "weekly is more disciplined than daily" angle is a deliberate inversion of the prevailing "daily weighing for trend" advice — fresh contrarian framing. Distinct.
Voice drift: none. Anchor-grade. "The daily number is not data. It is weather." is the share-card and the strongest single line of the batch.
Engagement risk: low. Four share candidates: "The daily number is not data. It is weather.", "Reading weather every morning and reacting to it like a forecast about your character is the trap.", "The actually disciplined version is harder than either.", and "The cadence should match the signal you are trying to read."
SEO fixes:
- Meta description on length (~155 chars). Clean.
- Primary keyword "daily weigh in trap weight loss" is honest and matches "should I weigh myself every day" PAA query intent. No collision.
- H2 set scans well; "What the daily reading is mostly measuring" is the strongest skim-reward anchor.
Image / flow fixes:
- Hero `scale-rude-before-20240130.jpg` exists; lane B (honest proof / scale) — exact lane match for scale category. Last used post 30 per pre-cleared plan. T2 compliant (currently 2-use, rising to 3-use). 5-adjacent check vs posts 57–61: zero overlap. Clean.
- Inline `water-weight-proof-20251031.jpg` exists; lane C (hard physique proof / water-weight). Anchored to "The daily number is not lying. It is also not telling you what you think." Anchor verbatim in body. Clean. **Cross-batch soft note**: `water-weight-proof-20251031.jpg` was deployed as inline in batch 11, cleared in batch 12, redeployed as inline this batch — a 2-batch gap inside the rule T4 soft 4-batch window. Soft preference violated, not a blocker. Flag for log.
Feed fit: this is the scale anchor for the post-50 stretch and the strongest myth_buster of the batch. Best published as a stand-alone — pairs naturally with `one-emotional-weigh-in-can-wreck-a-good-week` (already in posts.ts) for an internal-link cluster.
Suggested internal links: keep as-is. Both `the-scale-lies-differently-in-the-morning-than-in-the-evening` and `one-emotional-weigh-in-can-wreck-a-good-week` resolve in posts.ts.

---

## Batch Summary

```
format_distribution: {personal_story: 1, deep_dive: 2, qa: 1, myth_buster: 1, progress_update: 0}
category_distribution: {cheat/binge: 1, mirror: 1, food structure: 1, exercise/recovery: 1, scale: 1}
recurring_issue: claim_class undercalibration on physiology-numbers / nutrition-heuristic posts is now at 2 of 5 (drafts 1 and 3) — up from 1 of 5 in batches 11 and 12. Pattern is no longer holding flat; it is widening. Trigger expanded from water-vs-fat decomposition (draft 1) to also include canonical sports-nutrition heuristics with per-kg numbers (draft 3, protein-per-kg). Counter-evidence: drafts 4 and 5 both self-corrected to Class 3 unprompted on physiology-numbers content — the writer can do it; the issue is the pre-flight default still defaults to 2.
overall_notes: >
  Strongest topic-spread batch in the program to date. All 5 drafts hit 5 distinct
  categories (cheat/binge, mirror, food structure, exercise/recovery, scale) — and combined
  with posts 57–61 (maintenance, appetite, plateau, founder/progress, body composition),
  the 10-post window 57–66 covers all 10 §11 lanes exactly once each. This is the cleanest
  topic spread possible under §11 — every category at 1, all under the §11 max-3 ceiling
  with the maximum possible margin.
  Voice recognizable across all 5 drafts. Three program-tier share-cards in one batch:
  "The daily number is not data. It is weather." (draft 5), "Cardio is not the wrong tool.
  Cardio is rarely the cheapest tool." (draft 4), and "I did not need a Sunday. I needed
  a default." (draft 3). The mirror-diet refrain "Look less. Look better. Look in fewer
  states." (draft 2) and the recovery-mode framing "A weekend cannot ruin a program that
  has a recovery mode." (draft 1) round out a batch where every post produced at least
  one quotable.
  Post-50 voice audit Q&A correction (rule 10) honored on draft 3: two founder-anchored
  Qs ("What did meal prep look like for me?" and "What did the structure that finally
  worked actually look like?") plus the share-card "I did not need a Sunday. I needed a
  default." 3rd consecutive clean cycle on rule 10. Per running notes, rule 10 remains in
  observation through post-75 audit rather than resolving early.
  Tightened image policy from `image_pool_tightened_policy.md` (Rule T2: 4-use skip-2)
  fully honored: zero of the three saturated images (`body-composition-proof-20251221.jpg`,
  `long-game-founder-20251221.jpg`, `plateau-middle-checkin-20250711.jpg`) appear as
  batch 13 heroes. Pool spread improves from 3-images-at-4-uses to 0-images-at-4-uses
  by promoting 5 of the 2-use images into the 3-use bucket, exactly as the pre-cleared
  plan projected.
  Format-rotation §12 satisfied within the batch: 62 personal_story → 63 deep_dive →
  64 qa → 65 deep_dive → 66 myth_buster. No 3-in-a-row. Cross-batch: post 61 was
  personal_story and post 62 is personal_story — exactly 2 consecutive same format,
  at the §12 max-2 ceiling. Allowed but at the limit. Batch 14 must rotate off
  personal_story for at least 1 post.
  Two revises this batch (drafts 1 and 3) and three pure passes (drafts 2, 4, 5). The
  revise pattern on draft 1 is the same as batch 12 draft 5 / batch 11 draft 2 / batch 10
  drafts 2 and 5: personal_story touching water-vs-fat decomposition, writer defaults to
  Class 2, reviewer bumps to Class 3. The revise pattern on draft 3 expands the trigger:
  protein-per-kg nutrition heuristic is the new addition to the pre-flight blind spot.
  Zero title collisions. Zero primary-keyword head-term collisions against the 54 ported
  slugs. All 5 hero and 5 inline image paths exist on disk. Banned phrase scan clean
  across all 5 drafts. Hormone noun-scan clean across all 5 drafts despite physiology-
  adjacent territory in drafts 1, 3, 4, and 5. Class 4 escalations: none.
  One intra-batch image violation (draft 3 inline reuses draft 1 hero file) — see rule 8
  scorecard entry. This is the only re-opening of a previously-RESOLVED rule across the
  trailing 4 batches.
```

### Drift Rule Scorecard (batch 13)

| # | Rule | Status |
|---|------|--------|
| 1 | Internal-link slug existence | clean (RESOLVED in batch 9; 5 consecutive clean batches now) |
| 2 | Claim class calibration (physiology floor + hormone noun-scan) | partial fail — drafts 1 and 3 undercalibrated on physiology-numbers / nutrition-heuristic floor (water-vs-fat decomposition + protein-per-kg). **2 of 5 this batch — up from 1 of 5 in batches 11 and 12.** Pattern is widening, not shrinking. Counter-evidence: drafts 4 and 5 both self-corrected to Class 3 unprompted, so writer can hit the floor when the trigger is salient enough. Hormone noun-scan: clean across all 5 drafts. Recommend writer notes addendum before batch 14: "If body contains kg-per-week, calorie-arithmetic, water-vs-fat split, or per-kg-bodyweight nutrition number, default to Class 3 regardless of post format." |
| 3 | Banned phrase keyword | clean (RESOLVED in batch 9; still clean — no banned phrases in any draft) |
| 4 | Head-term keyword collision | clean (RESOLVED in batch 9; still clean — 0 of 5 collide with the 54 ported slugs) |
| 5 | Inline image variety within batch | clean (5 unique inlines: diet-slip-checkin-20250725 / sleep-reflective-20260106 / cheat-day-checkin-20250719 / patience-middle-checkin-20250731 / water-weight-proof-20251031). Intra-batch uniqueness holds. (RESOLVED in batch 12.) |
| 6 | Hero/inline image existence | clean (RESOLVED in batch 10; 4 consecutive clean batches now — fully retired) |
| 7 | Hunger-editorial hero rotation | clean — no hunger / appetite post in batch 13 (deliberate rotation off the §11 ceiling-pressed appetite lane). Rule continues to hold under category rotation. |
| 8 | Hero/inline cross-role reuse within batch | **fail — RE-OPENED.** `cheat-day-checkin-20250719.jpg` is the hero on draft 1 AND the inline on draft 3. Same byte-identical file path used in two slots inside the same batch. Rule 8 was RESOLVED in batch 10 with 3 consecutive clean batches (eligible for full retirement at the post-12 close). This batch reopens it. Single occurrence; not a structural regression yet, but must close cleanly in batch 14 to begin the 3-batch reset toward re-resolution. **Recommended fix on draft 3:** swap inline to `consistency-editorial-20251229.jpg` (lane A, 3-use, "default is the program" anchor candidate) or `start.jpg` (lane A, 1-use, "build the default first" anchor candidate). |
| 9 | Hero/topic semantic mismatch via cover taxonomy | clean — 4 of 5 hero choices on-lane exact (cheat-day-checkin=B for cheat/binge, sleep-reflective-window=D for food structure, transformation-proof=C for exercise/recovery, scale-rude-before=B for scale). Draft 2 hero `founder-story-hanok-20260119.jpg` is a soft cross-lane match (lane A used for a mirror post that would prefer lane B), but defensible under reuse pressure (lane B mirror options exhausted: `mirror-middle-checkin-20250716.jpg` already at 3-use saturation). Hero alt acknowledges the bridge framing. Same generosity standard applied to batch 12 draft 2 (lane-B-for-appetite bridge). **3rd consecutive clean batch on rule 9 — RESOLVED.** |
| 10 | Post-50 Q&A founder-I + sensory-line correction | clean — draft 3 is the only Q&A in the batch and meets both halves: 2 founder-anchored Qs ("What did meal prep look like for me?" and "What did the structure that finally worked actually look like?") and multiple concrete sensory/metaphorical lines ("I did not need a Sunday. I needed a default." / "The food is the infrastructure, not the entertainment." / "By Wednesday, the containers will feel like an obligation. By Friday, they will feel like a constraint. By Sunday, you will not want to cook again."). **3rd consecutive clean cycle on rule 10.** Per running notes, observation continues to post-75 audit rather than resolving at 3 cycles. |

Tracked: 10. Clean: 8. Partial fail: 1 (rule 2, widening). Re-opened: 1 (rule 8). New resolution this batch: **rule 9 (hero/topic semantic match) — 3 consecutive clean batches achieved.**

### Image Policy Compliance (Tightened Policy, batch 13)

**Rule T2 — 4-use skip-2 rule: PASS.**

Three images at 4-use saturation per `image_pool_tightened_policy.md` were barred from batch 13 hero slots:
- `body-composition-proof-20251221.jpg` (last used post 61) — **not used as batch 13 hero.** ✓
- `long-game-founder-20251221.jpg` (last used post 57) — **not used as batch 13 hero.** ✓
- `plateau-middle-checkin-20250711.jpg` (last used post 59) — **not used as batch 13 hero.** ✓

All three saturated images skipped their next 2 publish-eligible slots as required. Batch 13 heroes drawn entirely from the 1-use, 2-use, and 3-use buckets per the pre-cleared plan.

**Rule T1 — saturation cap (no image >5 uses): PASS.** Highest hero use post-batch-13 will be 3 uses on each newly-promoted image. No image crosses 4 uses this batch.

**Rule T3 — lane balance preference: PASS.** Lane sequence for batch 13 heroes: B (cheat) → A (founder) → D (lifestyle) → C (composition) → B (scale). No lane appears 3 times in a row. Matches the pre-cleared plan exactly.

**Rule T4 — inline rotation: PARTIAL.** Five unique inlines (intra-batch uniqueness holds — clean for rule 5). Cross-batch soft preference: `water-weight-proof-20251031.jpg` deployed as inline in batch 11, cleared in batch 12, redeployed as inline in batch 13 — 2-batch gap, inside the soft 4-batch window. Soft note for log; not a blocker.

**Rule T5 — `final-body.jpg` reserved for milestone slots: PASS.** Not used in batch 13 (next milestone is Progress Update #5 at post 80).

**Pool projection after batch 13:** 0 images at 4 uses, 11 images at 3 uses, 6 images at 2 uses, 2 images at 1 use, 0 unused. Distribution improves as projected. Batch 14 will start consuming the 3-use pool, so the post-80 mandatory pool refresh point flagged in the policy file remains binding.

### 5-Adjacent Hero Check vs Posts 57–61

- 57–61 heroes: `long-game-founder-20251221.jpg`, `weighin-middle-progress-20240801.jpg`, `plateau-middle-checkin-20250711.jpg`, `final-body.jpg`, `body-composition-proof-20251221.jpg`
- 62–66 heroes: `cheat-day-checkin-20250719.jpg`, `founder-story-hanok-20260119.jpg`, `sleep-reflective-window-20241217.jpg`, `transformation-proof-20251119.jpg`, `scale-rude-before-20240130.jpg`
- Overlap check: **zero.** All five heroes in batch 13 are distinct files from all five heroes in batch 12. 5-adjacent rule: **satisfied.**
- Within-batch hero variety: 5 unique heroes across 5 drafts. Clean.

### Topic Spread Acknowledgment (Posts 57–66, 10-Post Window §11)

| Post | Category |
|------|----------|
| 57 | maintenance |
| 58 | appetite |
| 59 | plateau |
| 60 | founder/progress |
| 61 | body composition |
| 62 | cheat/binge |
| 63 | mirror |
| 64 | food structure |
| 65 | exercise/recovery |
| 66 | scale |

**10 of 10 §11 lanes hit, exactly 1 post each.** This is the cleanest possible topic spread under §11 — maximum margin under the max-3 ceiling for every lane. First time in the program a single 10-post window has hit all 10 lanes at exactly 1 each. Earns explicit acknowledgment.

### Reuse Budget Note

Per the post-60 checkpoint policy in `image_pool_tightened_policy.md`:

- All 3 four-use images held at 4 uses through batch 13 (T2 skip-2 honored).
- 5 of the 2-use images promoted to 3-use this batch (`cheat-day-checkin-20250719.jpg`, `founder-story-hanok-20260119.jpg`, `sleep-reflective-window-20241217.jpg`, `transformation-proof-20251119.jpg`, `scale-rude-before-20240130.jpg`).
- Effective unused-pool: still 0.
- Pool size: still 22 images.

**Action flagged to writer:** Per `image_pool_tightened_policy.md` "Decision Required Before Batch 14" section — by batch 16 the pool will hit the same 4-use saturation it just exited unless new assets land. The post-80 mandatory refresh point remains binding. If the archive at `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/` is still missing from this worktree, founder must add new assets to `frontend/public/founder/` before approved-post 80 (~batch 16).

Priority lanes still needing new assets, in order of binding pressure (unchanged from batch 12 verdict):
1. **Body composition / hard physique proof** (lane C) — most saturated; `body-composition-proof-20251221.jpg` held at 4 uses by skip-2.
2. **Plateau / honest middle** (lane B) — `plateau-middle-checkin-20250711.jpg` held at 4 uses by skip-2; no obvious replacement.
3. **Maintenance** (lane A) — `long-game-founder-20251221.jpg` held at 4 uses by skip-2; sole maintenance hero.
4. **Appetite / lifestyle** (lane D) — `hunger-editorial-20260106.jpg` at 3-use saturation; an asset purely for the hunger lane is still missing.

---

## Final Action Return

**Per-draft verdicts:**
1. `the-bad-weekend-that-finally-taught-me-something` → **revise** (bump claim_class 2 → 3 per drift rule 2; soft note on day-by-day arithmetic structure)
2. `how-to-go-on-a-mirror-diet-when-the-real-diet-is-getting-loud` → **pass** (Class 2 correctly held; soft note on lane-A-for-mirror hero bridge under reuse pressure)
3. `do-i-actually-have-to-meal-prep-to-lose-weight` → **revise** (bump claim_class 2 → 3 per drift rule 2 protein-per-kg trigger; swap inline image to remove hero/inline cross-role reuse with draft 1; rule 10 honored)
4. `why-adding-cardio-to-a-cut-can-backfire-faster-than-you-think` → **pass** (Class 3 correctly self-set on first pass — second self-correction this batch)
5. `weighing-yourself-every-day-can-be-a-trap-not-a-discipline` → **pass** (Class 3 correctly self-set on first pass; "The daily number is not data. It is weather." is the strongest single line of the batch)

**Batch rule summary:** 8 of 10 drift rules clean. **Rule 9 (hero/topic semantic match) RESOLVED this batch** — 3 consecutive clean batches achieved (batches 11, 12, 13 all clean, with the same lane-bridge generosity standard applied). Rule 10 (Q&A founder-I correction) at 3 consecutive clean cycles but stays in observation through post-75 audit per running notes. Rule 2 (claim_class calibration) widens from 1 of 5 to 2 of 5 — pattern is no longer holding flat; trigger expanded to include protein-per-kg nutrition heuristics. Rule 8 (hero/inline cross-role reuse within batch) re-opened — single occurrence (`cheat-day-checkin-20250719.jpg` as hero on draft 1 + inline on draft 3); recommended fix: swap draft 3 inline to `consistency-editorial-20251229.jpg` or `start.jpg`. Rule T2 (4-use skip-2 image policy) fully honored — all three saturated images skipped batch 13 hero slots. 5-adjacent hero check: zero overlap with posts 57–61.

**Class 4 escalations needed:** none. Hormone noun-scan clean across all 5 drafts (one generic "hormonal fluctuation" reference in draft 5 does not trigger Class 4 per drift rule 2 phrasing — no specific hormone named).

**Strongest / weakest:**
- **Strongest** is draft 5 (`weighing-yourself-every-day-can-be-a-trap-not-a-discipline`) — the cleanest myth_buster of the batch and the program's strongest scale post since `one-emotional-weigh-in-can-wreck-a-good-week`. Class 3 self-corrected on first pass, hormone noun-scan clean despite naming "hormonal fluctuation" generically, the "1 to 2 kg in 24 hours from water alone" decomposition is the cleanest water-vs-fat-vs-muscle framing in the program, and the share-card "The daily number is not data. It is weather." is the single strongest line of the batch. The "What I did" founder section (three months daily, three months weekly, same trend rate, better mood) is the kind of vulnerable A-vs-B founder evidence the myth_buster format earns its keep on. Honorable mention to draft 4 (cardio) for the second pre-flight Class 3 self-correction of the batch.
- **Weakest** is draft 3 (`do-i-actually-have-to-meal-prep-to-lose-weight`) — the only revise carrying two checklist failures (claim_class undercalibration + rule 8 hero/inline cross-role reuse). The post itself is structurally strong (rule 10 cleanly honored, founder-I in 4 of 8 Qs, multiple share-card sensory lines including "I did not need a Sunday. I needed a default."), but the protein-per-kg nutrition heuristic should have been pre-flight Class 3, and the inline image reuse with draft 1's hero is the only intra-batch image violation across the trailing 4 batches. Voice rescues the post — but both fixes are non-negotiable per drift rules 2 and 8.
