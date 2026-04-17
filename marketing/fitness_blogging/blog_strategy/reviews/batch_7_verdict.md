# Batch 7 Verdict (posts 32–36)

Reviewer: senior editor / SEO strategist subagent
Date: 2026-04-17
Scope: 5 drafts listed below, context via the 10 most recently approved drafts plus the 24 currently ported slugs in `frontend/src/content/blog/posts.ts`. Founder image pool validated against `frontend/public/founder/`.

---

### progress-update-3-past-the-messy-middle
- verdict: pass
- claim_class: 1
- title_collision: no (intentional series sibling to `progress-update-2-the-body-changed-slower-than-my-head-did`)
- primary_keyword: progress update after weight loss middle
- keyword_collision: no
- format: progress_update
- checklist_failures: []
- must_fix:
  - None blocking. Optional: "It takes another six to twelve months past goal for the head to catch up" is already hedged with "I am told" — keep.
- voice_drift_flag: no
- top_3_issues:
  1. Numbers are concrete but slightly generic ("roughly 15 kg since the last update", "two pant sizes"). One hyper-specific detail (a measurement, a date, a named garment) would give the milestone more texture.
  2. The middle sections ("What the middle did to the head / plan") re-state themes from Progress Update #2. Series continuity is fine; one fresh beat would keep it from reading as recap.
  3. The CTA closes on "Devenira's weekly check-in is built for exactly that phase" — clean, but "refusing to renegotiate the plan every three weeks" in the preceding sentence is the stronger anchor; consider foregrounding it.
- repetition_risk: low structurally. The "stayed bored" frame is new in the corpus.
- voice_drift: none — "Every compliment still felt early" and "the head adapts slower than the body" are dry, short-sentence hits consistent with the anchor set.
- engagement_risk: low — "This is a check-in, not a before-and-after" works; close lands calm.
- seo_fixes:
  - Primary keyword `progress update after weight loss middle` is fine; surface it once literally in an H2 or the first paragraph for skim-scan pickup.
  - Meta description could sharpen to "Four months past the messy middle. Down ~15 kg. What actually changed, what did not, and what the head is still catching up on."
  - Slug is clean and short.
- image_flow_fixes:
  - Hero `/founder/progress-update-hanok-20260119.jpg` exists and matches Founder / Credibility taxonomy — correct for a milestone post.
  - Inline `/founder/transformation-proof-20251119.jpg` exists but is already the hero of `the-body-looks-different-from-behind` (the most recent approved post). Not a hero collision, but a cross-batch echo worth noting. Consider `/founder/body-composition-proof-20251221.jpg` as a less-recently-used alternate.
- feed_fit: This is the scheduled milestone per Plan Section 13 (progress update at approved-post 40). Publish at the front of batch 7's release window; it earns the lead slot.
- suggested_internal_links: [the-unglamorous-middle-of-transformation, progress-update-2-the-body-changed-slower-than-my-head-did]
- optional_rewrite_suggestion: omit.

---

### when-the-workout-becomes-therapy-not-punishment
- verdict: pass
- claim_class: 1
- title_collision: no
- primary_keyword: exercise as self-care not punishment
- keyword_collision: no
- format: personal_story
- checklist_failures: [5 (inline image shared with another draft in this batch)]
- must_fix:
  - Swap the inline image. `/founder/patience-middle-checkin-20250731.jpg` is also used as the inline in `how-do-you-know-when-youve-reached-your-set-point` this same batch. Drift note #5 says inline frames should vary within a batch. Suggested replacement: `/founder/sleep-reflective-window-20241217.jpg` or `/founder/scale-proof-20250919.jpg`.
- voice_drift_flag: no
- top_3_issues:
  1. Shared inline image with another draft in this batch (see must_fix).
  2. "Checking the scale post-workout is the most receipt-shaped thing you can do" is the strongest quotable line in the batch but sits buried mid-section; consider foregrounding it.
  3. "Body changes came more steadily once I stopped using the body as collateral" — "as collateral" is doing a lot of metaphoric work right where the reader needs a plainer landing. Minor.
- repetition_risk: low. The "workout as receipt" frame does not appear in the last 10 approved drafts.
- voice_drift: none — "morally dangerous" and the panic-wearing-activewear register is anchor-set-consistent; dry, observational, slightly rude.
- engagement_risk: low — the first five lines ("For most of my life, the workout was a receipt" through "It cannot produce peace") are the strongest opener of the batch after the progress update.
- seo_fixes:
  - Primary keyword `exercise as self-care not punishment` is clean; no banned-phrase drift, no collision. Surface once literally in body (currently paraphrased as "therapy-training" / "maintenance of your nervous system").
  - Add one H2 that literally contains "exercise as self-care" for primary-keyword anchoring.
  - SEO title "What Changes When You Stop Using Exercise as Punishment" is strong; keep.
- image_flow_fixes:
  - Hero `/founder/consistency-editorial-20251229.jpg` exists and fits the softer Founder / Lifestyle taxonomy — correct.
  - Swap inline as noted in must_fix.
- feed_fit: Best placed between a scale/plateau post and an appetite post to diversify the exercise/recovery lane after `exercise-isnt-shrinking-you-the-way-you-expected`. Do not publish adjacent to that post.
- suggested_internal_links: [exercise-isnt-shrinking-you-the-way-you-expected, the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one]
- optional_rewrite_suggestion: omit.

---

### hunger-in-maintenance-is-different-from-hunger-on-a-diet
- verdict: revise
- claim_class: 4 (draft says 3 — under-calibrated)
- title_collision: no
- primary_keyword: hunger after weight loss
- keyword_collision: no (distinct from `you-do-not-need-to-love-hunger-you-need-to-understand-it` and `why-appetite-feels-stronger-the-longer-you-diet`)
- format: deep_dive
- checklist_failures: [8 (claim class under-calibrated — physiology-heavy)]
- must_fix:
  - Bump claim_class from 3 to 4. The post names specific hormones (leptin, ghrelin) and makes explicit hormonal-recalibration claims. Per drift note #2 and Plan Section 15, named-hormone / physiology-heavy content is Class 4 and requires human sign-off before port. This is the gate for the draft.
  - Soft-hedge: "This recalibration is not instant. It often takes weeks to months" → add "for many people" to stay inside the style guide's `may / can / often / tends to` cadence.
  - Optional: "They will not. But it takes a few weeks for the signal to recalibrate" → "For most people, it takes a few weeks to months."
- voice_drift_flag: no
- top_3_issues:
  1. Claim class is under-tagged; named-hormone physiology belongs in Class 4, not Class 3. This is the one gate in the batch.
  2. The "How to tell which hunger you are reading" heuristic list is the body's best moment but arrives after three sections of exposition; consider pulling it up.
  3. Hero `hunger-editorial-20260106.jpg` is now being used on a third post in the hunger cluster (also heroes `you-do-not-need-to-love-hunger` and `why-appetite-feels-stronger-the-longer-you-diet`). Visual over-use of the lane is emerging.
- repetition_risk: low — maintenance-phase hunger is a lane the corpus has not fully covered; complements existing hunger posts without duplicating.
- voice_drift: none. "Waiting out the recalibration window is the actual skill of early maintenance" is the share line.
- engagement_risk: low — the opening ("Most people treat hunger like it is one thing. / It is not.") is anchor-consistent.
- seo_fixes:
  - Primary keyword `hunger after weight loss` has decent search volume and no collision; surface it literally in H1 or first paragraph (currently paraphrased).
  - Meta: "Maintenance hunger is not the same signal as dieting hunger. It usually settles by month three or four, but most people panic at week five and restart the diet."
  - Add an H2 containing `maintenance hunger` verbatim.
- image_flow_fixes:
  - Hero `/founder/hunger-editorial-20260106.jpg` exists but is the third use in the hunger cluster. Do not publish adjacent to the other two. Consider rotating the next hunger post to a different cover.
  - Inline `/founder/mirror-middle-checkin-20250716.jpg` exists — good, unique in this batch.
- feed_fit: Maintenance-lane post; sits opposite the appetite/deficit posts. Place in the back half of batch 7 so it follows the progress update rather than leading it.
- suggested_internal_links: [why-appetite-feels-stronger-the-longer-you-diet, you-do-not-need-to-love-hunger-you-need-to-understand-it]
- optional_rewrite_suggestion: omit.

---

### the-friend-who-never-diets-and-never-gains
- verdict: pass
- claim_class: 3
- title_collision: no
- primary_keyword: friend who never gains weight
- keyword_collision: no
- format: myth_buster
- checklist_failures: []
- must_fix:
  - None blocking. Optional: "Gut microbiome, hormones, sleep architecture, and a half-dozen other factors can tilt the baseline" is Class-4-adjacent because it names hormones and microbiome. If Class 3 is kept, swap "hormones" for "hormonal differences can play a role" to stay honest with the class tag.
- voice_drift_flag: no
- top_3_issues:
  1. Opening beat "Everyone has that friend. / Eats whatever. Never seems to gain." is good but the "You do not, and you are furious about it" line is the real hook — consider leading with the emotional punch.
  2. "They fidget more." as a standalone line is strong; the rest of the observation list is good but "They eat the same kinds of things most days" feels softer than "They do not dramatize food."
  3. The close "The answer is usually: more of them than you think" is one of the best landings in the batch — flagging because it's a model for future myth_buster closes.
- repetition_risk: low — the "naturally slim friend" frame is new in the corpus. Opens a body-composition / NEAT lane that complements `do-people-who-have-been-obese-for-years-lose-weight-more-slowly` without duplicating.
- voice_drift: none — "You are comparing a diet to a personality. That comparison is rigged" is a share-card line and worldview-consistent.
- engagement_risk: low — first five lines pull, middle holds, close earns the title.
- seo_fixes:
  - Primary keyword `friend who never gains weight` is clean, no collision; surface literally in body (currently only in title and meta).
  - Secondary `naturally slim people habits` already included — good.
  - Slug is short and honest.
- image_flow_fixes:
  - Hero `/founder/long-game-founder-20251221.jpg` exists and matches Founder / Worldview lane. Already used as hero for `do-people-who-have-been-obese-for-years-lose-weight-more-slowly` (post 18); well outside the 5-adjacent rule. OK.
  - Inline `/founder/sleep-reflective-20260106.jpg` exists — unique in the batch. Good.
- feed_fit: Body-composition lane; complements `the-scale-can-say-normal-and-still-tell-you-nothing-useful` and the NEAT thread. Strong hook candidate for social.
- suggested_internal_links: [why-it-feels-like-you-gain-weight-even-when-you-barely-eat, the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one]
- optional_rewrite_suggestion: omit.

---

### how-do-you-know-when-youve-reached-your-set-point
- verdict: revise
- claim_class: 3
- title_collision: no
- primary_keyword: reached set point weight
- keyword_collision: no
- format: qa
- checklist_failures: [5 (inline image shared with another draft in this batch)]
- must_fix:
  - Swap the inline image. `/founder/patience-middle-checkin-20250731.jpg` is also used as inline in `when-the-workout-becomes-therapy-not-punishment` this same batch. Drift note #5 violation. Suggested replacement: `/founder/plateau-middle-checkin-20250711.jpg` (fits the "steady state" frame) or `/founder/consistency-editorial-20251229.jpg`.
  - Optional claim-language: "If you hold a new weight for 12 to 24 months, that weight often becomes the new defended range" — keep "often"; consider "for many people" as added hedge.
- voice_drift_flag: no
- top_3_issues:
  1. Inline image duplicates Draft 2 in this batch — minor but batch 6's recurring issue flagged this exact pattern.
  2. The Q "Is the set point really immovable?" is the weakest Q in the sequence; the answer is good but the question is almost rhetorical. Consider tightening or cutting.
  3. Primary keyword `reached set point weight` is grammatically awkward; `how to know your body's set point` reads more like a real search query.
- repetition_risk: low — Q&A format is correct rotation (no Q&A in the last 5 approved; `is-it-bloat-or-is-it-fat` was the previous one). Set point is under-covered as a topic.
- voice_drift: none. "The set point is not a verdict. It is information" is the share line and cleanest call-back to the title.
- engagement_risk: low — each Q is a scannable unit; answers deliver within 2–4 short paragraphs.
- seo_fixes:
  - Consider swapping primary keyword to `how to know your body's set point` (better grammar, closer to a natural search query). Keep current phrase as secondary.
  - Add H2 containing the chosen primary keyword verbatim.
  - Meta description is good; no change needed.
- image_flow_fixes:
  - Hero `/founder/scale-proof-20250919.jpg` exists and fits the "steady state / read the body" frame. Already used as hero for `dont-trust-the-scale-heres-what-actually-proves-youre-losing-weight` — more than 5 adjacent posts away. Rule clean.
  - Swap inline per must_fix.
- feed_fit: Maintenance-lane post; pairs well with the plateau pair (`what-actually-counts-as-a-weight-loss-plateau` + `a-plateau-is-a-data-point-not-a-failure`). Publish at least 2 posts away from either so the three do not read as a cluster-triple.
- suggested_internal_links: [what-actually-counts-as-a-weight-loss-plateau, a-plateau-is-a-data-point-not-a-failure]
- optional_rewrite_suggestion: omit.

---

## Batch 7 Summary

- format_distribution: { progress_update: 1, personal_story: 1, deep_dive: 1, myth_buster: 1, qa: 1 }
- category_distribution: { founder/progress: 1, exercise/recovery: 1, appetite: 1, body composition: 1, maintenance: 1 }
- feed_level_repetition_risk: low on structure and opening beats. Medium on one specific inline image (`patience-middle-checkin-20250731.jpg` appears in 2 of 5 drafts). No hero image reuse within the batch. No hero collision against the last 5 approved posts.
- topic_spread_narrowing: no — all 5 drafts land in distinct categories. All 5 formats represented for the first time in a single batch; this is a progress signal, not drift.
- strong_hook_candidate_present: yes — `when-the-workout-becomes-therapy-not-punishment` ("the workout was a receipt") and `the-friend-who-never-diets-and-never-gains` ("you are comparing a diet to a personality") are both sharp openers.
- non_standard_post_type_needed_soon: no — `progress-update-3-past-the-messy-middle` is the scheduled milestone per Plan Section 13 (approved-post 40). This batch resolves the batch 6 recommendation. Next milestone due at approved-post 60.
- recurring_issue: "One batch-internal inline-image reuse (drift note #5) affecting Drafts 2 and 5. Separately, claim_class is under-calibrated on Draft 3 (names specific hormones; belongs in Class 4, not Class 3). No internal-link slug mismatches, no banned-phrase keyword drift, no head-term collisions, no missing hero images. Clear improvement over batch 6 — 4 of the 6 active drift rules are now clean with zero violations; 1 rule has a single violation (inline image); 1 rule has a single under-calibration."
- voice_drift_flag_batch: no — voice, rhythm, worldview, and reader address are intact. Sentence rhythm is anchor-set-consistent across all 5 drafts. No performative first person. No banned phrases in body. CTAs stay soft.
- overall_notes:
  - Drift compliance: rules 1 (slug validity), 3 (banned-phrase keyword), 4 (head-term collision), 6 (hero image existence) all clean. Rule 5 (inline variety) violated once. Rule 2 (claim calibration) under-called on Draft 3. Net: 5/6 drift rules followed; 1 inline-image violation plus 1 claim-class recalibration needed.
  - Hero images: all 5 exist in `frontend/public/founder/`. The hunger cluster (`hunger-editorial-20260106.jpg`) is now on a third post; do not publish adjacent to the other two and plan a different cover for the next hunger post.
  - Inline images: batch-internal reuse of `patience-middle-checkin-20250731.jpg` on Drafts 2 and 5 is the one image-flow issue.
  - Keyword discipline: no primary keyword drifts into banned-phrase family. No head-term collisions with the 24 currently ported slugs. Draft 5's primary keyword is grammatically awkward and would benefit from a swap.
  - Claim-class discipline: Draft 3 should be Class 4, not Class 3. Others are correctly tagged.
  - Format rotation: first batch in the program with one post per format. Within spec; no rotation issue.
  - Milestone standard (progress_update): concrete numbers (~15 kg, 4 days/week, two pant sizes) present; real founder photo in hero and inline; non-generic — meets Plan Section 13.
  - Strongest post: `when-the-workout-becomes-therapy-not-punishment` on hook strength and voice; `the-friend-who-never-diets-and-never-gains` on share-ability and topic freshness.
  - Weakest post: `hunger-in-maintenance-is-different-from-hunger-on-a-diet` — good writing but the one claim-class mis-tag of the batch and the third use of the hunger hero pull it down. The claim class is the only hard gate in the batch.
  - Writer is visibly incorporating batch 6 feedback: internal-link slugs are all real, no banned-phrase keywords, no head-term collisions, no missing hero assets. The two remaining issues are narrower versions of the same drift patterns, not fresh regressions.
