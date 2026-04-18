# Batch 8 Verdict (posts 37–41)

Reviewer: senior editor / SEO strategist subagent
Date: 2026-04-17
Scope: 5 drafts listed below, context via the 10 most recently approved drafts (posts 27–36) plus the 29 currently ported slugs in `frontend/src/content/blog/posts.ts`. Founder image pool validated against `frontend/public/founder/` (22 assets). Drift rules applied per `running_style_drift_notes.md` (batch 3 of drift-tracking stream).

---

### the-scale-lies-differently-in-the-morning-than-in-the-evening
- verdict: revise
- claim_class: 3 (draft says 2 — under-calibrated)
- title_collision: no
- primary_keyword: morning weight vs evening weight
- keyword_collision: no (distinct from `why-losing-5kg-in-a-week-usually-means-water-not-fat` and `one-emotional-weigh-in-can-wreck-a-good-week`)
- format: deep_dive
- checklist_failures: [8 (claim class under-calibrated — physiology), 5 (inline image reused as another draft's hero in this batch)]
- must_fix:
  - Bump claim_class from 2 to 3. The body makes explicit physiology claims with specific numbers: "0.8 to 1.8 kg higher" evening weight, "6 to 30 hours" digestive transit, "3 grams of water per gram of stored glycogen." Per drift note #2, physiology/demographic claims require Class 3 minimum. No named hormones, so Class 4 is not required.
  - Swap the inline image. `/founder/water-weight-proof-20251031.jpg` is also used as the **hero** of `the-quiet-role-vegetables-play-in-staying-full` in this same batch. Drift note #5 violation (batch-internal image reuse, cross-role). Suggested replacement: `/founder/weighin-middle-progress-20240801.jpg` (fits the "morning baseline" frame) or `/founder/plateau-middle-checkin-20250711.jpg`.
  - Soft-hedge: "Morning weight is the lowest you will weigh that day, under usual conditions" already hedged; keep. "Evening weight is typically 0.8 to 1.8 kg higher than your morning number, for most adults" is good — keep "typically" and "for most adults."
- voice_drift_flag: no
- top_3_issues:
  1. Claim class under-calibrated (2 → 3). Physiology numbers trigger drift note #2.
  2. Batch-internal image reuse: inline `water-weight-proof` is another draft's hero.
  3. "The lie is not the scale. The scale is just reporting water, food, and timing" is the strongest quotable line in the draft but sits mid-section; consider surfacing earlier or in meta.
- repetition_risk: low. Intra-day variance is not covered in the last 10 approved drafts — complements `why-losing-5kg-in-a-week-usually-means-water-not-fat` without duplicating (that post is about week-scale water; this is about hour-scale water).
- voice_drift: none — "The scale is honest at every time of day. It is just answering a different question each time" is anchor-consistent, dry, observational.
- engagement_risk: low — opening ("Most people weigh themselves at one specific time and treat that number as the truth. / It is not the truth. It is one sample.") is clean.
- seo_fixes:
  - Primary keyword `morning weight vs evening weight` is clean, no collision with any of the 29 ported slugs/titles; surface it literally in an H2 (currently only in SEO title and meta).
  - SEO title "Why Your Weight Is Different Morning vs Evening" reads like a real search query; keep.
  - Add H2 "Morning weight vs evening weight: what each one actually measures" for keyword anchoring.
- image_flow_fixes:
  - Hero `/founder/scale-rude-before-20240130.jpg` exists; fits the Honest Proof / Before taxonomy and is not in the last 5 approved heroes. Clean.
  - Swap inline per must_fix.
- feed_fit: Scale lane. Sits adjacent to `dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight` and `one-emotional-weigh-in-can-wreck-a-good-week`. Publish at least 2 posts away from either so the scale cluster does not compress.
- suggested_internal_links: [dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight, one-emotional-weigh-in-can-wreck-a-good-week]
- optional_rewrite_suggestion: omit.

---

### sleep-debt-ruins-a-week-of-dieting-in-three-nights
- verdict: revise
- claim_class: 4 (draft says 3 — under-calibrated; named-hormone content)
- title_collision: no
- primary_keyword: sleep and weight loss
- keyword_collision: no (distinct from `if-your-diet-broke-your-sleep-it-is-not-discipline-anymore` — that post is framed as worldview/discipline; this post is mechanism)
- format: personal_story
- checklist_failures: [8 (claim class under-calibrated — named hormones)]
- must_fix:
  - Bump claim_class from 3 to 4. The post explicitly names leptin and ghrelin: "Leptin drops. Ghrelin rises." Per drift note #2 and Plan Section 15, named-hormone content is Class 4 and requires human sign-off before port. This is the gate for the draft. Same category of issue as batch 7's `hunger-in-maintenance-is-different-from-hunger-on-a-diet`.
  - Soft-hedge: "Under-sleeping for even two or three nights tends to push appetite hormones in ways that make food feel louder" — keep "tends to."
  - Optional: "Nine times out of ten, the sleep explains it" is close to absolute; consider "Most of the time, the sleep explains it" for cadence consistency.
- voice_drift_flag: no
- top_3_issues:
  1. Named hormones (leptin, ghrelin) push this from Class 3 to Class 4. This is the one hard gate in the batch. Second consecutive batch with this pattern — the writer is drifting into hormone-naming in recovery/appetite lanes.
  2. The opening three lines ("I had a clean Monday, Tuesday, and Wednesday of eating. / By Saturday, the week looked like a disaster. / Three bad nights of sleep were the reason.") is the batch's sharpest hook — flagging as a keeper pattern.
  3. "It was my nervous system collecting an unpaid bill from three nights earlier" is a strong share line but "nervous system" is a slight physiological leap that `can` language would soften.
- repetition_risk: low structurally. The "delayed bill" metaphor is new in the corpus.
- voice_drift: none — "My weight did not move. My appetite moved" is anchor-set-clean. Short/long sentence alternation intact.
- engagement_risk: low — first 5 lines pull; middle holds via the specific-week narrative; close lands on the reframe.
- seo_fixes:
  - Primary keyword `sleep and weight loss` is a high-volume head term. Confirmed no collision with any of the 29 ported slugs/titles. Clean.
  - Surface `sleep and weight loss` literally in the body (currently only in SEO title and meta).
  - Meta description is tight; keep.
- image_flow_fixes:
  - Hero `/founder/sleep-reflective-20260106.jpg` exists; correct deployment of one of the 4 previously-unused pool images per the post-30 checkpoint. This is the right call — fresh asset for a recovery-lane post.
  - Inline `/founder/patience-middle-checkin-20250731.jpg` exists; unique within this batch. No repeat of the batch 7 drift-rule-5 violation. Clean.
- feed_fit: Exercise/recovery lane; semantic sibling of `if-your-diet-broke-your-sleep-it-is-not-discipline-anymore`. Publish at least 2 posts away from that one so the sleep pair does not read as a doublet.
- suggested_internal_links: [if-your-diet-broke-your-sleep-it-is-not-discipline-anymore, the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one]
- optional_rewrite_suggestion: omit.

---

### the-quiet-role-vegetables-play-in-staying-full
- verdict: revise
- claim_class: 3
- title_collision: no
- primary_keyword: vegetables for weight loss
- keyword_collision: no
- format: myth_buster
- checklist_failures: [6 (inline image file does not exist), 5 (hero image reused as another draft's inline in this batch), 6a (hero image semantically mismatched to topic)]
- must_fix:
  - Replace the inline image. `/founder/kitchen-prep-composed-20250816.jpg` does not exist in `frontend/public/founder/`. This is the exact regression drift note #6 is meant to prevent. Writer must ls `frontend/public/founder/` and pick a real file. Suggested replacement: `/founder/long-game-founder-20251221.jpg` (worldview adjacency) or `/founder/sleep-reflective-window-20241217.jpg` (softer lifestyle frame).
  - Replace the hero image. `/founder/water-weight-proof-20251031.jpg` is also used as the inline of `the-scale-lies-differently-in-the-morning-than-in-the-evening` in this same batch (drift note #5). Separately, it is from the Hard Physique Proof / water-weight lane per the cover mapping — semantically wrong for a food-structure/vegetables post. Suggested replacement hero: `/founder/cheat-day-checkin-20250719.jpg` (food-adjacent) or any uncontested Founder / Lifestyle asset.
  - Optional: "They add fiber, which physically slows digestion and flattens the blood-sugar curve after a meal" is Class-3-appropriate but close to physiology; keep — do not escalate with more mechanism detail or this becomes Class 4.
- voice_drift_flag: no
- top_3_issues:
  1. Two image-flow violations in one draft: non-existent inline and batch-internal hero reuse. Drift notes #5 and #6 both tripped on this post alone.
  2. Hero/topic semantic mismatch: `water-weight-proof` is a body-composition asset, not a food/volume asset. The cover mapping lane is wrong.
  3. "Disproportionately large vegetable component. 'Disproportionate' is the part people skip" is the best beat; consider promoting it to the section header instead of burying mid-paragraph.
- repetition_risk: low — vegetable-structure framing is absent from the existing 29 ported posts and the last 10 approved drafts.
- voice_drift: none — "Protein gets all the press. / Fats get the moral arguments. Carbs get the fear. Vegetables get a vague 'eat more of them' and then nothing" is anchor-clean and quotable. "The vegetables are quietly making the rest of the diet survivable" is a clean myth_buster close.
- engagement_risk: low — hook is strong; middle holds; close lands.
- seo_fixes:
  - Primary keyword `vegetables for weight loss` is a mid-volume head term, no collision with the 29 ported slugs/titles. Clean.
  - Surface `vegetables for weight loss` literally in an H2 (currently only in SEO title).
  - Secondary `volume eating weight loss` is useful — consider one inline use.
- image_flow_fixes:
  - Hero must change (see must_fix).
  - Inline must change to a file that exists (see must_fix).
- feed_fit: Food structure lane; first post of the program in this lane at the body-level (distinct from the binge/cheat cluster). Slot as a pair-opener for food-structure posts to come.
- suggested_internal_links: [you-do-not-need-to-love-hunger-you-need-to-understand-it, why-appetite-feels-stronger-the-longer-you-diet]
- optional_rewrite_suggestion: omit.

---

### how-do-i-stop-a-binge-from-becoming-a-binge-week
- verdict: revise
- claim_class: 3 (draft says 2 — under-calibrated; specific physiology numbers)
- title_collision: no
- primary_keyword: stop binge from becoming binge week
- keyword_collision: no
- format: qa
- checklist_failures: [8 (claim class under-calibrated — physiology numbers)]
- must_fix:
  - Bump claim_class from 2 to 3. The post contains specific physiology numbers: "1,500 to 3,500 calories above your plan," "0.2 to 0.5 kg of actual fat over the course of days," "1 to 2 kg you see on the scale the next morning is almost entirely water, salt, and food volume," "craving usually drops by half within 30 to 60 minutes." Per drift note #2, physiology/demographic claims require Class 3 minimum. No named hormones; Class 4 not required.
  - Optional hedge: "This is the most common professional intervention for broken diet weeks" — good, keeps the claim honest. Keep "often," "usually," "tends to" throughout; they are already calibrated.
- voice_drift_flag: no
- top_3_issues:
  1. Claim class under-calibrated (2 → 3). Specific numbers trigger drift note #2 even without named hormones.
  2. "One binge is a meal. A binge week is a choice. The choice happens in the 24 hours after" is the share-card line and the cleanest close in the batch — flagging as keeper.
  3. The Q&A format rotation is correct (last Q&A was batch 7's `how-do-you-know-when-youve-reached-your-set-point`); two posts away is within the 5-format-rotation rule.
- repetition_risk: low — the "24 hours after" frame is new. Complements `read-this-before-you-try-to-fix-your-diet-slip` (mechanics) and `cheat-days-do-not-expose-your-character-they-expose-your-system` (worldview) without overlap.
- voice_drift: none — "Act as if yesterday was yesterday and today is today. Because that is literally what they are" is anchor-set-clean, dry, slightly rude-honest.
- engagement_risk: low — Q&A format gives scannable units; each answer is 2–5 short paragraphs.
- seo_fixes:
  - Primary keyword `stop binge from becoming binge week` is long-tail, no collision. Clean. Surface it once literally in an H2 (currently paraphrased).
  - Consider secondary phrase `how to recover from a binge` (higher search volume, related intent) — include once as a natural secondary.
  - SEO title is strong; meta is accurate; slug is clean.
- image_flow_fixes:
  - Hero `/founder/diet-slip-checkin-20250725.jpg` exists; cheat/binge lane-appropriate per cover mapping. Not in last 5 approved heroes. Clean.
  - Inline `/founder/consistency-editorial-20251229.jpg` exists; unique within this batch. Minor echo: this was the hero of `when-the-workout-becomes-therapy-not-punishment` (batch 7). Not a rule violation for inlines, but a cross-batch visual echo. Acceptable.
- feed_fit: Cheat/binge lane; natural Q&A pairing with the cheat-day cluster. Publish at least 2 posts away from `read-this-before-you-try-to-fix-your-diet-slip` and `cheat-days-do-not-expose-your-character-they-expose-your-system` so the three do not read as a triple.
- suggested_internal_links: [read-this-before-you-try-to-fix-your-diet-slip, cheat-days-do-not-expose-your-character-they-expose-your-system]
- optional_rewrite_suggestion: omit.

---

### you-look-different-to-other-people-before-yourself
- verdict: pass
- claim_class: 2 (draft says 1 — mildly under-calibrated; general-wellness claim with specific timing)
- title_collision: no
- primary_keyword: other people notice weight loss before you
- keyword_collision: no
- format: myth_buster
- checklist_failures: []
- must_fix:
  - None blocking. Optional: bump claim_class from 1 to 2. The post is mostly personal experience (Class 1) but includes "Expect the head to run about three to six months behind the body. This is often cited by people who work with post-weight-loss body image professionally, though the exact timing varies." That is a general-wellness claim with specific timing, which fits Class 2. The hedge is already in place; the bump is for accurate tagging, not for language change. Not a gate.
  - Optional: "Third, the delay in your own perception is normal and expected" is calmly stated; keep. No rewrite needed.
- voice_drift_flag: no
- top_3_issues:
  1. "You are the least well-positioned observer of your own transformation" is the share-card line — anchor-set-clean and genuinely new in the corpus.
  2. The mirror-post lane now has three entries (`why-the-mirror-can-make-real-progress-feel-fake`, `the-body-looks-different-from-behind`, this one); within Plan Section 11's max-3-per-category-per-10-post-window. Next batch should avoid a fourth mirror post for at least 4 posts.
  3. The close "Give it time" is short and lands; if it reads thin on publication, "Give it the months it needs" is a cleaner fallback. Minor.
- repetition_risk: low. The "outside observer is the clearer reader" frame is distinct from the other two mirror posts (which are about self-perception / rear-view).
- voice_drift: none — "The outside world is seeing a body your head is still catching up to" and "When the internal map and the external evidence disagree, the evidence is more current than the map" are both anchor-clean, calm, observational.
- engagement_risk: low — first 5 lines ("People you have not seen in a few months will notice your body has changed. / You will not have noticed yet. / This is not modesty. It is not vanity. It is how your brain is built.") is the strongest opener of the batch alongside the sleep-debt draft.
- seo_fixes:
  - Primary keyword `other people notice weight loss before you` is long-tail and clean, no collision with the 29 ported slugs/titles.
  - Consider surfacing the shorter phrase `weight loss body image lag` as a secondary-keyword anchor inside an H2 — closer to how people search.
  - Meta description is strong; keep.
- image_flow_fixes:
  - Hero `/founder/mirror-middle-checkin-20250716.jpg` exists; mirror-lane-appropriate per cover mapping. Already the hero of `why-the-mirror-can-make-real-progress-feel-fake` (post 2 in posts.ts) — well outside the 5-adjacent rule. Clean.
  - Inline `/founder/transformation-proof-20251119.jpg` exists; unique within this batch. Cross-batch echo: was inline of `progress-update-3-past-the-messy-middle` (batch 7). Not a rule violation but a visual echo. Acceptable; consider `/founder/body-composition-proof-20251221.jpg` as an alternate if the feed compresses.
- feed_fit: Mirror lane; third post in the lane. Place at least 3 posts after the more recent mirror post to avoid lane-compression.
- suggested_internal_links: [why-the-mirror-can-make-real-progress-feel-fake, the-body-looks-different-from-behind]
- optional_rewrite_suggestion: omit.

---

## Batch 8 Summary

- format_distribution: { deep_dive: 1, personal_story: 1, myth_buster: 2, qa: 1, progress_update: 0 }
- category_distribution: { scale: 1, exercise/recovery: 1, food structure: 1, cheat/binge: 1, mirror: 1 }
- feed_level_repetition_risk: low on structure and opening beats. Medium on one specific image (`water-weight-proof-20251031.jpg` appears as Draft 1 inline AND Draft 3 hero — the batch-internal role-crossover variant of the batch 7 inline-inline issue). No hero collision against the last 5 approved heroes (progress-update-hanok, consistency-editorial, hunger-editorial, long-game-founder, scale-proof).
- topic_spread_narrowing: no — all 5 drafts land in distinct categories. Mirror lane now at 3 of 41 posts; monitor but within Plan Section 11 window rule.
- strong_hook_candidate_present: yes — `sleep-debt-ruins-a-week-of-dieting-in-three-nights` ("My weight did not move. My appetite moved.") and `you-look-different-to-other-people-before-yourself` ("You are the least well-positioned observer of your own transformation") are both anchor-quality openers.
- non_standard_post_type_needed_soon: no — next progress update is due at approved-post 60 per Plan Section 13. Q&A rotation freshened by Draft 4.
- recurring_issue: "Claim-class under-calibration on 3 of 5 drafts (Drafts 1, 2, 4 — physiology numbers and named hormones). This is the same drift note #2 pattern that landed on batch 7 Draft 3 — NOT clean for a second consecutive batch; the writer is systematically under-calling Class on physiology-adjacent content. Separately, one non-existent inline image (Draft 3) and one batch-internal hero/inline image collision (Drafts 1 and 3 sharing water-weight-proof). Internal-link slugs: clean across all 10 references. Banned-phrase keyword drift: clean. Head-term collision against the 29 ported slugs/titles: clean. Hero image existence: clean (inline in Draft 3 is the one missing-file violation)."
- voice_drift_flag_batch: no — voice, rhythm, worldview, and reader address intact across all 5 drafts. No banned phrases in body copy. No performative first person. CTAs stay soft ("Devenira's weight view smooths the daily chaos...," "Devenira logs binges without judgment..."). Short/long sentence alternation is anchor-set-consistent.
- overall_notes:
  - Drift compliance: 4 of 7 active drift rules followed.
    - Rule 1 (internal-link slug validity): CLEAN — all 10 link targets exist in posts.ts.
    - Rule 2 (claim class calibration): VIOLATED — Drafts 1, 2, 4 all under-called. Draft 2 is the hard gate (Class 4 human sign-off required for named hormones).
    - Rule 3 (banned-phrase keyword): CLEAN — no "journey," "hack," "unlock," "game changer," "trust the process," or "no excuses" in any primary keyword.
    - Rule 4 (head-term keyword collision): CLEAN — no collisions with the 29 ported slugs or titles.
    - Rule 5 (inline image variety within batch): VIOLATED — Draft 1 inline (water-weight-proof) is Draft 3 hero. Role crossover, same batch.
    - Rule 6 (hero image existence — extended to inlines): VIOLATED — Draft 3 inline `/founder/kitchen-prep-composed-20250816.jpg` does not exist in `frontend/public/founder/`. Regression to the batch 6 pattern that was clean for batch 7.
    - Rule 7 (hunger-editorial hero rotation): CLEAN — no batch 8 post uses hunger-editorial-20260106.jpg.
  - Hero images: all 5 exist in `frontend/public/founder/`. Draft 2's use of the previously-unused `sleep-reflective-20260106.jpg` correctly executes the post-30 checkpoint priority (deploy unused pool first). Draft 3's hero is the one that needs swapping — not for existence but for semantic lane mismatch plus batch-internal reuse.
  - Inline images: Draft 3's inline is the non-existent file. All other inlines resolve. The only batch-internal image collision is water-weight-proof (Draft 1 inline / Draft 3 hero) — flagged under rule 5 as a role-crossover variant.
  - Keyword discipline: primary keywords are clean across all 5. No banned-phrase family drift, no head-term collisions.
  - Claim-class discipline: the systematic pattern of the batch. Three of five drafts under-call Class. Draft 2 (leptin/ghrelin) is the hard gate requiring human sign-off. Drafts 1 and 4 need automatic Class 3 bumps without language change. The writer should add a pre-flight check: "does this draft state specific physiology numbers or name hormones?" → bump Class before finalizing.
  - Format rotation: 2 myth_buster in one batch (Drafts 3 and 5) is within Plan Section 12 (max 2 consecutive same format). Adjacency matters at publish; place Drafts 3 and 5 non-adjacently.
  - Strongest post: `you-look-different-to-other-people-before-yourself` — clean on all 7 drift rules (only optional Class 1 → 2 bump for accuracy), strong hook, share-card close, opens the mirror lane's third distinct frame. Alternate strong pick: `sleep-debt-ruins-a-week-of-dieting-in-three-nights` for hook quality, but pulled down by the Class 4 gate.
  - Weakest post: `the-quiet-role-vegetables-play-in-staying-full` — two drift-rule violations in one draft (missing inline file + batch-internal hero reuse + semantic hero mismatch). The writing itself is sharp; the image-flow is the only thing holding it back from a clean pass.
  - Drift-stream trajectory: batch 6 had 6 issues across 6 rules. Batch 7 had 2 issues across 2 rules (clean improvement). Batch 8 has 3 issues across 3 rules — a regression on claim calibration (recurring) and hero existence (recovered issue re-opened). The writer should update `running_style_drift_notes.md` to mark rule 6 as re-opened and to note rule 2 as still-open across two batches.
