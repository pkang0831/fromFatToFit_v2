# Batch 9 Verdict (posts 42–46)

Reviewer: senior editor / SEO strategist subagent
Date: 2026-04-17
Scope: 5 drafts listed below, context via the 10 most recently approved drafts (posts 32–41) plus the 34 currently ported slugs in `frontend/src/content/blog/posts.ts`. Founder image pool validated against `frontend/public/founder/` (22 assets). Drift rules applied per `running_style_drift_notes.md` — batch 9 is the tiebreaker for rules 1, 3, 4 (pending-resolution at 2 consecutive clean batches).

Hero + inline existence hard check (rule 6): all 10 referenced paths verified present in `frontend/public/founder/`. No missing-file regression from batch 8.

---

### the-first-week-of-any-diet-is-the-most-misleading-one
- verdict: pass
- claim_class: 3 (draft says 3 — correctly calibrated)
- title_collision: no
- primary_keyword: first week of diet weight loss
- keyword_collision: no (distinct from `why-losing-5kg-in-a-week-usually-means-water-not-fat` — that post is the water-vs-fat mechanism; this post is the week-one-through-week-three timeline)
- format: deep_dive
- checklist_failures: []
- must_fix:
  - None blocking. Optional: surface the primary keyword `first week of diet weight loss` once literally in an H2 (currently paraphrased as "What week one is actually measuring" and "What the early weeks really are"); a literal anchor helps intent matching.
  - Optional: the meta description is strong and keyword-anchored — keep.
- voice_drift_flag: no
- top_3_issues:
  1. "The real diet begins around day 15" is the share-card line and the cleanest close in the batch — flagging as a keeper.
  2. Numeric claims ("1.5 to 4 kg," "3 grams of bound water per gram of glycogen," "0.2 to 0.5 kg") are correctly hedged and correctly called Class 3 — no hormone naming, so Class 4 is not required. First batch in three where the writer's pre-flight Class audit is clean on physiology numbers.
  3. The deep_dive format rotation is correct — last deep_dive in the approved set was `hunger-in-maintenance-is-different-from-hunger-on-a-diet` (batch 7), well outside the 2-consecutive rule.
- repetition_risk: low. Week-one-vs-week-three timeline is absent from the last 10 approved drafts. Complements `why-losing-5kg-in-a-week-usually-means-water-not-fat` (mechanism) and `a-plateau-is-a-data-point-not-a-failure` (interpretation) without duplicating either.
- voice_drift: none — "The first week is where people decide whether the plan is working. / That decision is almost always based on the wrong evidence." is anchor-set-clean, dry, observational. Short/long sentence alternation intact.
- engagement_risk: low — first 5 lines pull without fake mystery; middle holds through the four-things-in-order-of-size structure; close lands on a calendar beat rather than a motivational one.
- seo_fixes:
  - Primary keyword is a clean long-tail — no collision with any of the 34 ported slugs or titles. Surface it once literally in an H2.
  - SEO title reads like a real search query; keep.
  - Secondary `why diet works fast then slows` is a useful search intent anchor; consider one inline use inside the "What the early weeks really are" section.
- image_flow_fixes:
  - Hero `/founder/start.jpg` exists and is correctly deployed per the post-30 checkpoint priority list (beginner-oriented / "where-you-start" post). Second of four previously-unused pool images to be deployed; good chain from batch 8's deployment of `sleep-reflective-20260106.jpg`.
  - Inline `/founder/weighin-middle-progress-20240801.jpg` exists; unique within this batch. Clean.
- feed_fit: Plateau/consistency lane. Sits adjacent to `what-actually-counts-as-a-weight-loss-plateau` and `the-most-important-reason-you-think-youre-not-losing-weight`. Publish at least 2 posts away from either so the plateau/patience cluster does not compress into a triplet.
- suggested_internal_links: [why-losing-5kg-in-a-week-usually-means-water-not-fat, a-plateau-is-a-data-point-not-a-failure]
- optional_rewrite_suggestion: omit.

---

### losing-weight-is-not-the-same-as-getting-leaner
- verdict: pass
- claim_class: 3 (draft says 3 — correctly calibrated)
- title_collision: no
- primary_keyword: weight loss vs getting leaner
- keyword_collision: no (distinct from `how-to-track-body-transformation-without-obsessing-over-the-scale` — that post is tracking method; this post is the composition-vs-mass distinction)
- format: personal_story
- checklist_failures: []
- must_fix:
  - None blocking. Optional: surface the primary keyword `weight loss vs getting leaner` once literally in an H2 (currently anchored in SEO title and meta only; body uses "the two lines do not always move together" which is voice-clean but not search-anchored).
  - Optional: the 70 kg / 25 percent vs 72 kg / 18 percent line is share-card quality; consider promoting it into the "what matters for most people" section header rather than leaving it mid-paragraph.
- voice_drift_flag: no
- top_3_issues:
  1. The three-line close ("Getting leaner is a composition story told over months. / Losing weight is a mass story told over weeks. / They are not the same number and they are not the same clock.") is the strongest close in the batch — anchor-clean rhythm, quotable, lands the principle.
  2. The eight-week plateau anchor is a personal_story-format use of a real founder experience that complements `progress-update-3-past-the-messy-middle` without duplicating it.
  3. Numeric claim ("fat mass had dropped by about 2.5 kg and the lean mass had risen") is correctly hedged with "by about" and framed as a single measurement, not a population trend. Class 3 is correctly called.
- repetition_risk: low. The scale-vs-leanness distinction is adjacent to `dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight` and `the-scale-can-say-normal-and-still-tell-you-nothing-useful` but hits a different angle: composition as a separate process, not the scale as a bad instrument.
- voice_drift: none — "The scale cannot tell these apart. It weighs everything." is anchor-clean.
- engagement_risk: low — first 5 lines are one of the two sharpest openers in the batch.
- seo_fixes:
  - Primary keyword is clean, no collision with the 34 ported slugs or titles.
  - Surface it literally in an H2 (currently only in SEO title and meta).
  - Secondary `body recomposition basics` and `losing weight but still soft` are both useful search intents — consider one inline use of "body recomposition" inside the "what I did not notice for a while" section (the term already appears there; anchor it into an H3 if H3s are used).
- image_flow_fixes:
  - Hero `/founder/body-composition-proof-20251221.jpg` exists; body-composition lane-appropriate per cover mapping (Hard Physique Proof family). Not in the last 5 approved heroes. Clean.
  - Inline `/founder/transformation-proof-20251119.jpg` exists; unique within this batch. Cross-batch echo: was inline of `you-look-different-to-other-people-before-yourself` (batch 8) and of `progress-update-3-past-the-messy-middle` (batch 7). Not a rule violation but a visual echo on a now-thrice-used image. Acceptable; flag for future batch rotation.
- feed_fit: Body composition lane. Natural pairing with `is-it-bloat-or-is-it-fat` and `how-to-track-body-transformation-without-obsessing-over-the-scale`. Publish at least 2 posts away from either so the body-composition cluster does not compress.
- suggested_internal_links: [how-to-track-body-transformation-without-obsessing-over-the-scale, is-it-bloat-or-is-it-fat]
- optional_rewrite_suggestion: omit.

---

### why-people-gain-more-back-than-they-lost
- verdict: revise
- claim_class: 4 (draft says 3 — under-calibrated; named-hormone content)
- title_collision: no
- primary_keyword: weight loss rebound gain back more
- keyword_collision: no (distinct from `hunger-in-maintenance-is-different-from-hunger-on-a-diet` — that post is appetite in maintenance; this post is rebound physiology)
- format: myth_buster
- checklist_failures: [8 (claim class under-calibrated — named hormone)]
- must_fix:
  - Bump claim_class from 3 to 4 OR strip the hormone name. The draft explicitly names insulin in "Insulin sensitivity and fat storage patterns can be altered after aggressive dieting, potentially making re-gained weight more likely to store as fat than rebuild as muscle." Per drift note #2 and Plan Section 15, named-hormone content is Class 4 and requires human sign-off before port. Two options, equivalent under the rule:
    - Option A (preferred, matches the mitigation taken in batch 7 and batch 8): strip "Insulin sensitivity and" and replace with "Fat storage patterns can be altered after aggressive dieting..." keeping the unnamed physiology claim at Class 3.
    - Option B: escalate to Class 4 and route the draft to human sign-off before port per Plan Section 15. Same gate applied to batch 7's `hunger-in-maintenance-is-different-from-hunger-on-a-diet` and batch 8's `sleep-debt-ruins-a-week-of-dieting-in-three-nights`.
  - This is the one hard gate in the batch.
  - Soft-hedge: "Signals that regulate hunger and fullness tend to shift during weight loss" — good, unnamed hormones, Class 3-safe. Keep "tend to" and "for a period after."
  - Soft-hedge: "NEAT tends to drop" — good. Keep "tends to" and "largely unconscious."
  - Optional: "The signals that were defending the old weight do not shut off at the old weight" — consider "may not shut off" for cadence consistency with the rest of the paragraph's hedging.
- voice_drift_flag: no
- top_3_issues:
  1. Named hormone (insulin) pushes this from Class 3 to Class 4. Third consecutive batch with a hormone-naming drift in the appetite/maintenance/recovery lanes (batch 7: leptin/ghrelin in hunger; batch 8: leptin/ghrelin in sleep; batch 9: insulin in rebound). The writer's pre-flight Class audit is catching physiology numbers (see draft 42) but still missing hormone names — the drift is specifically on hormone-name scanning.
  2. "Maintenance is the diet. The losing part was just the prequel" is the share-card line and the cleanest principle in the batch — flagging as keeper.
  3. Myth_buster format rotation is correct — no other myth_buster in batch 9, and the last myth_buster in the approved set was `the-quiet-role-vegetables-play-in-staying-full` (batch 8). Within the 2-consecutive-same-format rule.
- repetition_risk: low. Rebound physiology is not covered at body-level in the 34 ported posts; only tangential treatment in `hunger-in-maintenance-is-different-from-hunger-on-a-diet` and `the-friend-who-never-diets-and-never-gains`. Strong complement, not duplicate.
- voice_drift: none — "The rebound is not a character failure. It is the three lines crossing at once" is anchor-clean, worldview-consistent ("systems > willpower"), and quotable. "The fix is rarely more willpower. / The fix is understanding that the 'diet is done, now I can relax' frame is the thing that creates the rebound" is the sharpest worldview beat in the batch.
- engagement_risk: low — opening pulls; middle holds through the three-mechanisms structure; close lands.
- seo_fixes:
  - Primary keyword is a long-tail intent phrase; no collision with any of the 34 ported slugs or titles. Clean.
  - Consider surfacing the shorter head term `weight loss rebound` or `yo-yo dieting rebound` (a declared secondary) once in an H2 for higher search anchor weight. Current H2s are voice-clean but SEO-thin.
  - Meta description is accurate; keep.
- image_flow_fixes:
  - Hero `/founder/long-game-founder-20251221.jpg` exists; maintenance/worldview lane-appropriate per cover mapping (Founder / Credibility family). Not in the last 5 approved heroes. Clean.
  - Inline `/founder/patience-middle-checkin-20250731.jpg` exists. **Batch-internal conflict**: this same inline file is also used as the inline of `the-kind-of-person-who-stays-at-their-goal-weight` (Draft 5 in this batch). Drift note #5 violation — inline reuse within a single batch. One of the two drafts must swap. Suggested replacement for this draft: `/founder/consistency-editorial-20251229.jpg` (worldview-adjacent and unused as inline in batch 9) or `/founder/final-body.jpg` (fourth previously-unused pool image per post-30 checkpoint — good deploy opportunity for a maintenance/long-game post).
- feed_fit: Maintenance lane. Sits in a natural triangle with `hunger-in-maintenance-is-different-from-hunger-on-a-diet`, `how-do-you-know-when-youve-reached-your-set-point`, and `the-friend-who-never-diets-and-never-gains`. Publish at least 2 posts away from any of those three so the maintenance cluster does not compress into a quartet.
- suggested_internal_links: [hunger-in-maintenance-is-different-from-hunger-on-a-diet, how-do-you-know-when-youve-reached-your-set-point]
- optional_rewrite_suggestion: omit.

---

### how-do-i-eat-normally-at-social-events
- verdict: revise
- claim_class: 2 (draft says 2 — correctly calibrated; behavioral only, no physiology numbers, no hormones)
- title_collision: no
- primary_keyword: eating at social events dieting
- keyword_collision: no (no overlap with any of the 34 ported slugs or titles — new intent cluster)
- format: qa
- checklist_failures: [6a (hero image semantically mismatched to topic lane per cover mapping), editorial (one broken sentence)]
- must_fix:
  - Replace the hero image. `/founder/water-weight-proof-20251031.jpg` is in the Hard Physique Proof / water-weight lane per the cover mapping taxonomy — semantically wrong for a food-structure/social-events Q&A. Drift note #9 violation, and the exact pattern that landed on batch 8's `the-quiet-role-vegetables-play-in-staying-full` (water-weight-proof on a food-structure post). Regression on the cover-taxonomy-lane rule. Suggested replacements in lane:
    - `/founder/cheat-day-checkin-20250719.jpg` or `/founder/cheat-day-founder-20251221.jpg` (both Honest Proof / Before / Middle, food-event-adjacent per cover mapping) — preferred.
    - `/founder/founder-story-hanok-20260119.jpg` (Founder / Credibility, softer social frame) — alternate.
    - Note: `/founder/consistency-editorial-20251229.jpg` is already Draft 4's inline, so it would trigger rule 8 cross-role conflict if used as this draft's hero — not recommended as hero swap.
  - Fix one broken sentence. "The event is absorbed into the week is total without you needing to do anything dramatic." is ungrammatical. Suggested: "The event is absorbed into the week. The total does not change, and you do not need to do anything dramatic." Minor but block-on-publish.
  - Optional: "If you decide bread is forbidden and then eat bread, your brain often reads that as 'the diet is over, eat everything'" is a clean behavioral frame; keep. No physiology escalation needed.
- voice_drift_flag: no
- top_3_issues:
  1. Hero/topic semantic mismatch — `water-weight-proof-20251031.jpg` on a food-structure post. Exact regression from batch 8, drift rule #9, that batch 9 was supposed to close clean on.
  2. One broken sentence in the "what about after the event?" section. Blocks publication until fixed.
  3. "The dinner is not the threat. / The under-eating before the dinner and the over-correcting after the dinner are the threat" is the share-card close — strong, worldview-consistent ("systems > willpower"), anchor-clean. Keep.
- repetition_risk: low. Social-eating intent is not covered in the 34 ported posts or the last 10 approved drafts. New cluster opener.
- voice_drift: none — Q&A format keeps the calm, direct tone. "There is no secret move" and "The events themselves are not the threshold. The threshold is whether the days around them return to the plan" are both anchor-clean.
- engagement_risk: low — Q&A format gives scannable units; each answer is 2–5 short paragraphs; middle does not dip.
- seo_fixes:
  - Primary keyword is clean long-tail, no collision with the 34 ported slugs or titles.
  - Surface `eating at social events` literally once in an H2 or H3 (currently only in the intro and SEO title).
  - Secondary `restaurant diet strategy` is a useful search intent — consider one inline use inside the "what should I actually do at the event?" section.
- image_flow_fixes:
  - Hero must change (see must_fix).
  - Inline `/founder/consistency-editorial-20251229.jpg` exists; unique within this batch. Lane-appropriate (calm, structure-forward). Clean. Keep.
- feed_fit: Food structure lane, second entry in the lane after `the-quiet-role-vegetables-play-in-staying-full` (batch 8). Social-eating is a distinct sub-intent; not a duplicate. Publish at least 2 posts away from the vegetables post so the food-structure cluster does not compress.
- suggested_internal_links: [cheat-days-do-not-expose-your-character-they-expose-your-system, the-quiet-role-vegetables-play-in-staying-full]
- optional_rewrite_suggestion: omit.

---

### the-kind-of-person-who-stays-at-their-goal-weight
- verdict: revise
- claim_class: 1 (draft says 1 — correctly calibrated; personal experience / subjective observation only)
- title_collision: no
- primary_keyword: keeping weight off long term
- keyword_collision: no (distinct from `how-do-you-know-when-youve-reached-your-set-point` — that post is set-point identification; this post is the behavioral portrait of long-term maintainers)
- format: personal_story
- checklist_failures: [5 (inline image reused across two drafts in this batch)]
- must_fix:
  - Swap the inline image. `/founder/patience-middle-checkin-20250731.jpg` is also used as the inline of `why-people-gain-more-back-than-they-lost` (Draft 3 in this batch). Drift note #5 violation — inline-inline reuse within a single batch, the exact pattern that batch 7 and batch 8 both tripped on a variant of. One of the two drafts must swap; recommend swapping here rather than on Draft 3 so Draft 3 can absorb a previously-unused pool asset. Suggested replacement for this draft:
    - `/founder/founder-story-hanok-20260119.jpg` (Founder / Credibility, calm steady-state portrait) — preferred for the "what they actually look like" anchor.
    - `/founder/progress-update-hanok-20260119.jpg` (Founder / Credibility) — alternate.
    - Note: `/founder/long-game-founder-20251221.jpg` is Draft 3's hero, so would trigger rule 8 cross-role conflict — not recommended. `/founder/final-body.jpg` is the last previously-unused pool image per post-30 checkpoint but is earmarked for a milestone post at approved-post ~60; hold unless Draft 3 also rotates.
  - Optional: "I have met people who held their weight off for five, ten, fifteen years" is Class-1-appropriate as personal observation. The "I have met" framing keeps this anecdotal rather than population-level. Keep.
  - Optional: "The kind of person who holds weight off is not a more disciplined version of the person who loses it. It is a quieter version" — one of the batch's two candidate share-card closes. Consider promoting it to the meta description or an H2 if the current meta feels generic at publication.
- voice_drift_flag: no
- top_3_issues:
  1. "A quieter version" close is the strongest voice-anchored line in the batch — calmly rude-honest, worldview-consistent ("maintenance is the real skill, not loss"), quotable, and genuinely new in the corpus.
  2. Batch-internal inline reuse with Draft 3 on `patience-middle-checkin-20250731.jpg`. The only drift-rule violation on this draft.
  3. Format rotation: 2 personal_story in batch 9 (Drafts 2 and 5), non-adjacent within the batch (Drafts 2, 3, 4, 5 sequence = personal_story, myth_buster, qa, personal_story — one format between them). Within Plan Section 12's max-2-consecutive rule. At publish, place the two personal_story drafts non-adjacently.
- repetition_risk: low. The behavioral-portrait-of-long-term-maintainers angle is absent from the 34 ported posts. Complements `the-friend-who-never-diets-and-never-gains` (which is about lifestyle defaults of never-dieters) without duplicating — this post is about the post-loss maintainer, the other is about the never-loser.
- voice_drift: none — "They do not dramatize food. Pizza is pizza. Salad is salad. Dessert is dessert. No food is a moral event" is anchor-set-clean, dry, slightly rude-honest. Short/long sentence alternation is textbook. "Not the photo. The ordinary week" is anchor-quality cadence.
- engagement_risk: low — opening ("I have met people who held their weight off for five, ten, fifteen years. / They do not look like the motivational content suggests. / They do not post. They do not moralize food. They do not seem to be working that hard. They seem, most of the time, a little bored.") is the sharpest opener in the batch; middle holds through the observation-by-observation structure; close lands on the "ordinary week" reframe that delivers on the opening promise.
- seo_fixes:
  - Primary keyword is a mid-to-high-volume head term; confirmed no collision with any of the 34 ported slugs or titles. Clean.
  - Surface `keeping weight off long term` literally in an H2 (currently only in SEO title and meta). The H2s are voice-clean but SEO-thin.
  - Secondary `weight loss maintenance traits` is a strong search intent — consider one inline use inside "what they actually look like."
- image_flow_fixes:
  - Hero `/founder/final-portrait.jpg` exists; correctly deployed per the post-30 checkpoint priority list (founder-story / worldview post adjacent to milestones). Third of four previously-unused pool images deployed this batch — good chain.
  - Inline must change (see must_fix).
- feed_fit: Maintenance lane. Sits in the same triangle as Draft 3 of this batch plus `hunger-in-maintenance-is-different-from-hunger-on-a-diet`, `how-do-you-know-when-youve-reached-your-set-point`, and `the-friend-who-never-diets-and-never-gains`. Maintenance lane is now at 5 posts (well-distributed); at publish, do not place this adjacent to Draft 3 of batch 9 — target at least 3 posts between them so the maintenance cluster does not read as a block.
- suggested_internal_links: [how-do-you-know-when-youve-reached-your-set-point, hunger-in-maintenance-is-different-from-hunger-on-a-diet]
- optional_rewrite_suggestion: omit.

---

## Batch 9 Summary

- format_distribution: { deep_dive: 1, personal_story: 2, myth_buster: 1, qa: 1, progress_update: 0 }
- category_distribution: { plateau/consistency: 1, body composition: 1, maintenance: 2, food structure: 1 }
- feed_level_repetition_risk: low on structure, opening beats, and keyword intent. Medium on one specific inline (`patience-middle-checkin-20250731.jpg` appears as Drafts 3 and 5 inline — rule 5 violation). No hero collision against the last 5 approved heroes.
- topic_spread_narrowing: no — 4 distinct categories across 5 drafts; maintenance at 2 is within Plan Section 11's max-3-per-10-post-window. Maintenance lane total post count is now at 5 across the 41-post approved run — still healthy distribution.
- strong_hook_candidate_present: yes — `the-kind-of-person-who-stays-at-their-goal-weight` ("They seem, most of the time, a little bored") and `losing-weight-is-not-the-same-as-getting-leaner` ("I weighed the same for eight weeks. / My clothes stopped fitting anyway.") are both anchor-quality openers. `why-people-gain-more-back-than-they-lost` has the strongest close of the batch ("Maintenance is the diet. The losing part was just the prequel.") but is blocked by the Class 4 gate.
- non_standard_post_type_needed_soon: no — next progress update is due at approved-post 60 per Plan Section 13 (currently at 41 post-batch-close). Q&A rotation refreshed by Draft 4. All 5 formats present across the last 15 approved drafts.
- recurring_issue: "Class calibration (rule 2) tripped for the third consecutive batch, specifically on hormone-name scanning (batch 7: leptin/ghrelin; batch 8: leptin/ghrelin; batch 9: insulin). The writer's pre-flight audit is now reliably catching physiology numbers — draft 42's Class 3 call on glycogen/water/salt is correct without prompting — but still missing hormone names. The drift is specifically on noun-scanning, not on mechanism-hedging. Separately, inline reuse within batch (rule 5) regressed (Drafts 3 and 5 share patience-middle-checkin-20250731.jpg). And hero/topic semantic mismatch (rule 9) regressed in exactly the pattern batch 8 flagged — Draft 4's water-weight-proof-20251031.jpg on a food-structure post, same asset on the same lane mismatch as batch 8's vegetables draft. Internal-link slugs (rule 1), banned-phrase keyword drift (rule 3), head-term collision (rule 4), hero/inline file existence (rule 6), hunger-editorial rotation (rule 7), and hero/inline cross-role within batch (rule 8) are all CLEAN."
- voice_drift_flag_batch: no — voice, rhythm, worldview, and reader address intact across all 5 drafts. No banned phrases in body copy. No performative first person. CTAs stay soft ("Devenira smooths the first week into a trendline on purpose," "Devenira keeps weight, measurements, and photos in parallel," "Devenira is built around the maintenance phase on purpose," "Devenira logs the week, not the meal," "Devenira is built around the ordinary week"). Short/long sentence alternation is anchor-set-consistent across all 5. The maintenance-as-real-skill worldview beat is cleanly load-bearing in Drafts 3 and 5 without ever repeating the same sentence.
- overall_notes:
  - Drift compliance: **6 of 9 active drift rules CLEAN this batch.**
    - Rule 1 (internal-link slug validity in posts.ts): **CLEAN** — all 10 link targets (draft 42: why-losing-5kg-in-a-week-usually-means-water-not-fat, a-plateau-is-a-data-point-not-a-failure; draft 43: how-to-track-body-transformation-without-obsessing-over-the-scale, is-it-bloat-or-is-it-fat; draft 44: hunger-in-maintenance-is-different-from-hunger-on-a-diet, how-do-you-know-when-youve-reached-your-set-point; draft 45: cheat-days-do-not-expose-your-character-they-expose-your-system, the-quiet-role-vegetables-play-in-staying-full; draft 46: how-do-you-know-when-youve-reached-your-set-point, hunger-in-maintenance-is-different-from-hunger-on-a-diet) exist in posts.ts. **3 consecutive clean batches (7, 8, 9) → RULE 1 RESOLVED.**
    - Rule 2 (claim class calibration): **VIOLATED** — Draft 3 names insulin without Class 4. Third consecutive batch with this pattern; OPEN and trending toward a hard-correction note in running_style_drift_notes.md.
    - Rule 3 (banned-phrase keyword): **CLEAN** — primary keywords are "first week of diet weight loss," "weight loss vs getting leaner," "weight loss rebound gain back more," "eating at social events dieting," "keeping weight off long term" — none contain "journey," "hack," "unlock," "game changer," "trust the process," "no excuses," "fitness goals," or "at the end of the day." **3 consecutive clean batches (7, 8, 9) → RULE 3 RESOLVED.**
    - Rule 4 (head-term keyword collision): **CLEAN** — no primary keyword collides with any of the 34 ported slugs or titles. Checked each literal phrase against the slug list and the title list. **3 consecutive clean batches (7, 8, 9) → RULE 4 RESOLVED.**
    - Rule 5 (inline image variety within batch): **VIOLATED** — Drafts 3 and 5 both use /founder/patience-middle-checkin-20250731.jpg as inline. One must swap.
    - Rule 6 (hero + inline image existence): **CLEAN** — all 10 referenced paths (5 heroes + 5 inlines) resolve to files in frontend/public/founder/. Ls'd the directory at review start; the 22 files present cover every path. Batch 8's kitchen-prep-composed regression did not recur.
    - Rule 7 (hunger-editorial hero rotation): **CLEAN** — no batch 9 post uses hunger-editorial-20260106.jpg. Second consecutive clean batch (batch 8 was clean by default — no hunger-lane post). Rule 7 needs one more consecutive clean batch (batch 10) to hit the 3-batch resolution threshold. **NOT YET RESOLVED.**
    - Rule 8 (hero/inline cross-role within batch): **CLEAN** — no hero in batch 9 appears as an inline in another batch 9 draft, and no inline appears as a hero in another batch 9 draft. Heroes: start, body-composition-proof-20251221, long-game-founder-20251221, water-weight-proof-20251031, final-portrait. Inlines: weighin-middle-progress-20240801, transformation-proof-20251119, patience-middle-checkin-20250731 (×2 — rule 5 violation, not rule 8), consistency-editorial-20251229. No intersection.
    - Rule 9 (hero/topic semantic match per cover taxonomy): **VIOLATED** — Draft 4 uses water-weight-proof-20251031.jpg (Hard Physique Proof lane) on a food-structure Q&A. Exact regression of batch 8's water-weight-proof on vegetables-draft pattern. Same asset, same lane mismatch.
  - **Compliance rate: 6/9 rules clean. Resolved this batch: rules 1, 3, 4. Rule 7 at 2 consecutive clean, needs batch 10 for resolution.**
  - Hero images: all 5 exist in frontend/public/founder/. Three of the four previously-unused pool images from the post-30 checkpoint were deployed across batches 8 and 9 (sleep-reflective-20260106.jpg in batch 8, start.jpg and final-portrait.jpg in batch 9). Only final-body.jpg remains unused; checkpoint earmarks it for a milestone post at approved-post ~60. Good execution of the checkpoint priority list.
  - Inline images: all 5 exist. The one batch-internal issue is the duplicate inline (rule 5).
  - Keyword discipline: primary keywords are clean across all 5. No banned-phrase family drift, no head-term collisions against the 34 ported slugs or titles. Third consecutive clean batch on both rules 3 and 4, and the pre-flight grep practice is clearly embedded in the writer's workflow.
  - Claim-class discipline: improving on numbers (draft 42 is the first correct Class 3 call on pure physiology numbers without hormones in three batches) but still drifting on hormone names (draft 44). The writer's pre-flight audit should add an explicit noun-scan for: insulin, leptin, ghrelin, cortisol, thyroid, glucagon, estrogen, testosterone, T3, T4 — any mention of any of these triggers Class 4 automatically.
  - Format rotation: 2 personal_story in one batch (Drafts 2 and 5) is within Plan Section 12 (max 2 consecutive). Non-adjacent at publish.
  - **Strongest post**: the-kind-of-person-who-stays-at-their-goal-weight — sharpest opener in the batch, anchor-quality voice throughout, share-card close ("a quieter version"), worldview-consistent, correctly-called Class 1, and opens a genuinely new angle in the maintenance lane. The only reason it's a revise rather than a pass is the inline image reuse — a one-line swap away from clean. Alternate strong pick: the-first-week-of-any-diet-is-the-most-misleading-one — the one pure pass of the batch, cleanest on every drift rule, and the timeline frame ("the real diet begins around day 15") is the most structurally new piece of content in the batch.
  - **Weakest post**: how-do-i-eat-normally-at-social-events — hero/topic semantic mismatch is the exact regression from batch 8 on the same asset (water-weight-proof-20251031.jpg) and the same lane mismatch (Hard Physique Proof hero on a food-structure post), plus a genuinely broken sentence that blocks publication. The writing itself is anchor-clean; the image and one editorial line are the only things holding it back.
  - Drift-stream trajectory: batch 6 had 6 issues across 6 rules. Batch 7 had 2 issues across 2 rules. Batch 8 had 3 issues across 3 rules (regression on claim calibration and hero existence). Batch 9 has 3 issues across 3 rules (rules 2, 5, 9), with rule 6 recovered (clean) and three rules fully resolved (1, 3, 4). Net: compliance rate improved from 4/7 (batch 8) to 6/9 (batch 9), and the rule set stabilized at 9 tracked rules — no new rules flagged this batch. The writer's SEO and slug discipline has hardened; the remaining drift is concentrated on image-lane matching and hormone-name scanning.
  - Writer should update running_style_drift_notes.md to: (a) move rules 1, 3, 4 to the ## Archive section as RESOLVED, (b) note rule 2 as open for third consecutive batch with the hormone-noun-scan correction direction above, (c) note rule 5 as still open (batch 9 violation), (d) note rule 7 at 2 consecutive clean, (e) note rule 9 as still open (batch 9 violation, same pattern as batch 8).
