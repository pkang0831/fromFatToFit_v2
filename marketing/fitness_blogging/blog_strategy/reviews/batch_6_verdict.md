# Batch 6 Verdict (posts 27–31)

Reviewer: senior editor / SEO strategist subagent
Date: 2026-04-17
Scope: 5 drafts listed below, context via most recent 10 approved drafts plus `frontend/src/content/blog/posts.ts`.

---

### exercise-isnt-shrinking-you-the-way-you-expected
- verdict: pass
- claim_class: 2
- title_collision: no
- primary_keyword: exercise not losing weight
- keyword_collision: no
- format: myth_buster
- checklist_failures: [5 (broken internal-link slugs)]
- must_fix:
  - replace the two internal-link suggestions with real existing slugs: `working-out-harder` (no such slug — real slug is `/working-out-harder-is-not-always-the-answer`) and `real-fat-loss-vs-fake-progress` (no such slug — real slug is `/how-to-tell-real-fat-loss-from-fake-progress`).
  - surface the exact primary keyword phrase once, literally (e.g. "working out but not losing weight") inside the body — currently only paraphrased.
- voice_drift_flag: no
- top_3_issues:
  1. Internal-link slugs do not match any real slug in posts.ts or the draft set.
  2. Primary keyword only appears paraphrased, never verbatim.
  3. "Your body is very good at protecting its current weight" reads a touch absolute; "tends to protect" matches the claim-language rule.
- repetition_risk: low; "workout builds the engine / plate decides the fuel" is a fresh frame, not a recycled opener.
- voice_drift: none — short/long sentence mix and dry observational tone match anchor set.
- engagement_risk: low — first 5 lines pull, middle holds, close lands on the stairs image.
- seo_fixes:
  - Consider a slightly shorter slug (`exercise-not-shrinking-you-as-expected`) if URL length matters, otherwise keep.
  - Add one H2 containing the primary keyword phrase verbatim ("why exercise is not making you lose weight yet") for skim-scan SEO.
- image_flow_fixes:
  - Inline image `session-side-profile-20250714.jpg` is also used in the middle and plateau drafts this batch. Pick a different founder training frame for one of them to avoid batch-internal repetition.
- feed_fit: Sits in the exercise/recovery lane opposite `working-out-harder-is-not-always-the-answer`; publish at least 2 posts away from that one.
- suggested_internal_links: [working-out-harder-is-not-always-the-answer, how-to-tell-real-fat-loss-from-fake-progress]
- optional_rewrite_suggestion: omit.

---

### the-unglamorous-middle-of-transformation
- verdict: revise
- claim_class: 1
- title_collision: no
- primary_keyword: middle of weight loss journey
- keyword_collision: no (but banned-adjacent: the word "journey" sits against the style guide's ban on "your journey")
- format: personal_story
- checklist_failures: [1 (banned-phrase risk in keyword), 5 (broken internal-link slug), 6 (inline image shared across batch)]
- must_fix:
  - Change the primary keyword off "journey." "Weight loss messy middle" or "middle phase of weight loss" keeps the intent without drifting toward banned language.
  - Replace `real-fat-loss-vs-fake-progress` with the actual slug `how-to-tell-real-fat-loss-from-fake-progress`.
  - Pick one inline image that isn't reused in the exercise or plateau drafts in this same batch.
- voice_drift_flag: no
- top_3_issues:
  1. Primary keyword brushes the banned "journey" family; easy fix but must happen before port.
  2. Internal-link suggestion is a filename fragment, not a slug that exists anywhere.
  3. Inline `session-side-profile-20250714.jpg` duplicates other posts in this batch.
- repetition_risk: medium on inline images this batch; low on structural fingerprint.
- voice_drift: none — the "photo I never posted was the one from July" is the strongest first-person beat in the batch.
- engagement_risk: low — the opening (before/after/middle) is a real hook, the middle delivers, the close earns the title.
- seo_fixes:
  - Swap primary keyword to `weight loss messy middle` (already a secondary); drop "journey" entirely.
  - Tighten the meta description: "Before-and-after photos make transformations look linear. The middle is where most people quit. This is what it actually looked like."
- image_flow_fixes:
  - Keep hero `/founder/mirror-middle-checkin-20250716.jpg` (cover_mapping prescribes 20250716_064040 for mirror/middle — correct mapping).
  - Replace one inline to reduce batch-internal photo repetition.
- feed_fit: Highest-hook draft in the batch; good candidate for the lead slot of batch 6 release.
- suggested_internal_links: [why-i-built-devenira-for-the-weeks-where-you-want-to-quit, how-to-tell-real-fat-loss-from-fake-progress]
- optional_rewrite_suggestion: omit.

---

### is-it-bloat-or-is-it-fat
- verdict: pass
- claim_class: 3
- title_collision: no
- primary_keyword: bloat vs fat
- keyword_collision: no
- format: qa
- checklist_failures: []
- must_fix:
  - Optional softening on "The body cannot synthesize 1.5 kg of fat in one day" → "The body generally cannot synthesize..." to match claim-language rules. Not a gate.
- voice_drift_flag: no
- top_3_issues:
  1. One absolute physiology claim could use the hedge wording the style guide prescribes.
  2. Shared inline image `weighin-middle-progress-20240801.jpg` also appears in the middle-of-transformation draft — minor batch-internal repetition.
  3. Meta description is accurate but uses "practical guide" which is slightly generic; could be sharper.
- repetition_risk: low — the Q&A format is missing from the last 10 approved drafts, so this diversifies the feed.
- voice_drift: none; dry, direct, with "waiting does not cost you anything" as a clean close.
- engagement_risk: low — each Q is a scannable unit and payoffs arrive fast.
- seo_fixes:
  - Add "bloat vs fat weight" as a secondary keyword for broader pickup.
  - Meta description could be sharpened: "How to tell if that 1.5 kg overnight is bloat, salt, or actual fat — and why waiting is almost always the honest answer."
- image_flow_fixes:
  - Hero `morning-vs-evening-comparison-20260108.jpg` is a strong, novel choice; confirm the asset actually exists before port.
  - Replace the weighin inline with something unique to avoid duplication with the middle draft.
- feed_fit: Clean complement to `why-losing-5kg-in-a-week-usually-means-water-not-fat`; publish them at least 3 posts apart so they stop reading as twins.
- suggested_internal_links: [why-losing-5kg-in-a-week-usually-means-water-not-fat, one-emotional-weigh-in-can-wreck-a-good-week]
- optional_rewrite_suggestion: omit.

---

### plateau-is-a-data-point-not-a-failure
- verdict: revise
- claim_class: 3
- title_collision: no (headline distinct from `what-actually-counts-as-a-weight-loss-plateau`)
- primary_keyword: weight loss plateau
- keyword_collision: yes — head-term identical to existing `what-actually-counts-as-a-weight-loss-plateau` in posts.ts. This will cannibalize.
- format: deep_dive
- checklist_failures: [4 (SEO keyword collision), 5 (internal-link slug mismatch), 8 (claim class under-calibrated)]
- must_fix:
  - Change primary keyword to something the existing post does not already own. Suggested: `weight loss plateau meaning` or `weight loss plateau is not failure`. Keep `stuck at same weight` as secondary.
  - Bump claim_class from 2 to 3: post references NEAT drop, cortisol water retention, metabolism compression, and "body most naturally defends" — all set-point / physiology territory.
  - Replace `set-point-feeling-stuck` with the real slug `why-your-body-starts-feeling-stuck-at-the-same-weight`.
- voice_drift_flag: no
- top_3_issues:
  1. Primary keyword cannibalizes an already-ported post. This is the gate.
  2. Claim class marked too low for the physiology actually present in the body copy.
  3. One suggested internal link does not resolve to any existing slug.
- repetition_risk: low structurally; the three-tier plateau framing (early/middle/late) is new in the corpus.
- voice_drift: none; "a plateau is a report, not a verdict" is the strongest share line of the batch.
- engagement_risk: low — middle does not dip, close is calm.
- seo_fixes:
  - Narrow primary keyword to avoid head-term collision (see above).
  - Add H2 or lead sentence that contains the new keyword literally.
  - Cross-link from the existing `what-actually-counts-as-a-weight-loss-plateau` to this post once ported so the pair reads as a cluster, not as duplicates.
- image_flow_fixes:
  - Hero `/founder/reflection-steady-20251010.jpg` fits the lane; confirm asset exists.
  - Inline `session-side-profile-20250714.jpg` is reused in two other drafts this batch; pick a different frame.
- feed_fit: Bridge post between the plateau / consistency cluster and the mirror cluster; place between batch-mid and batch-end.
- suggested_internal_links: [what-actually-counts-as-a-weight-loss-plateau, why-your-body-starts-feeling-stuck-at-the-same-weight]
- optional_rewrite_suggestion: omit.

---

### the-body-looks-different-from-behind
- verdict: revise
- claim_class: 3 (draft says 1 — under-calibrated)
- title_collision: no
- primary_keyword: body looks different from behind
- keyword_collision: no
- format: personal_story
- checklist_failures: [5 (internal-link slug mismatch), 8 (claim class under-calibrated), 8 (demographic physiology claim needs hedging)]
- must_fix:
  - Soften the line "especially women and East Asian bodies" — this is a specific demographic physiology claim and the style guide's claim rules require `may`, `can`, or `often` here. Proposed wording: "For many people — and often for women or East Asian builds — the back changes first."
  - Bump claim_class from 1 to 3. The post makes physiological claims about visceral fat, lower-belly fat, and demographic fat-distribution patterns. Class 1 (personal experience only) is wrong for this piece.
  - Replace `softer-body-at-lower-weight` with the actual slug `why-your-body-can-look-softer-even-at-a-lower-weight`.
- voice_drift_flag: no
- top_3_issues:
  1. Claim class is mis-tagged; the body makes demographic physiology claims that require a higher class.
  2. Demographic sentence is too absolute for the style guide's claim-language rule.
  3. Internal-link suggestion does not resolve to any existing slug.
- repetition_risk: low; the back-view angle is novel in the corpus.
- voice_drift: none — "Then my brother took a photo of me from behind at a wedding. It was a different body." is the single best hook of the batch.
- engagement_risk: low — opening is a real story, not a staged hook.
- seo_fixes:
  - Primary keyword is acceptable but awkward; consider `check body progress from back` (already secondary) as a stronger-volume alternate.
  - Make sure H2s actually contain the primary keyword phrase once.
- image_flow_fixes:
  - Hero `/founder/back-profile-progress-20251005.jpg` is a strong, non-repeated pick; confirm asset exists.
  - Inline `back-silhouette-20260120.jpg` and `side-profile-reveal-20250822.jpg` are novel — good.
- feed_fit: Best place to publish between a mirror-cluster post and a body-composition post; strongest quotable opener in the batch, good for social.
- suggested_internal_links: [why-the-mirror-can-make-real-progress-feel-fake, why-your-body-can-look-softer-even-at-a-lower-weight]
- optional_rewrite_suggestion: omit.

---

## Batch 6 Summary

- format_distribution: { personal_story: 2, myth_buster: 1, qa: 1, deep_dive: 1, progress_update: 0 }
- category_distribution: { exercise/recovery: 1, founder/progress: 1, body composition: 1, plateau/consistency: 1, mirror: 1 }
- feed_level_repetition_risk: low on structure and opening beats; medium on inline image reuse within the batch (`session-side-profile-20250714.jpg` appears in 3 of 5 drafts; `weighin-middle-progress-20240801.jpg` appears in 2). No hero image collision against the last 5 approved posts.
- topic_spread_narrowing: no — all 5 drafts land in distinct categories; the 10-post window stays well under the 3-per-category cap.
- strong_hook_candidate_present: yes — `the-body-looks-different-from-behind` (wedding photo) and `the-unglamorous-middle-of-transformation` (photo I never posted) both carry real openers.
- non_standard_post_type_needed_soon: yes — progress_update. Per the 100-post plan (Section 13), a progress update was scheduled at approved-post count 20 and at 40. No progress_update format appears in either the last 10 approved drafts or this batch. Recommend placing one in batch 7 or batch 8.
- recurring_issue: "Internal-link suggestions are written as filename-style shorthand, not as actual existing slugs. 4 of 5 drafts contain at least one broken internal-link target. Separately, claim_class is under-calibrated on 2 of 5 drafts where physiology or demographic statements appear."
- voice_drift_flag_batch: no — voice, rhythm, and worldview are intact and in some places sharper than the last 10 approved drafts. Format shift from the old "Blog N Publish-Ready" scaffold to the new blueprint front matter is a format migration, not voice drift, and should be noted as progress in `running_style_drift_notes.md`.
- overall_notes:
  - Hero images: no overlap with the last 5 approved hero images. `20260119_125140.jpg` appears twice in the last 10 approved (maintenance + refined carbs) but those are not adjacent and no batch-6 draft reuses it. The 5-adjacent rule is clean.
  - Inline images: shared asset reuse across the batch is the one real image-flow issue. Ask the writer to pick unique inline frames where possible.
  - Keyword discipline: two drafts need keyword edits before port — `middle` (drift toward banned "journey" family) and `plateau` (head-term cannibalization).
  - Claim-class discipline: two drafts need a bump or recheck because of physiology/demographic content.
  - Strongest post: `the-body-looks-different-from-behind` on hook, `is-it-bloat-or-is-it-fat` on publish-readiness.
  - Weakest post: `plateau-is-a-data-point-not-a-failure` — good writing but has the one real SEO collision in the batch.
  - Format rotation: two `personal_story` posts in one batch is within spec, but do not publish them back-to-back in the calendar.
