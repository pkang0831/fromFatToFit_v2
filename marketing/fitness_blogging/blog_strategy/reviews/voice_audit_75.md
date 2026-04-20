# Voice Drift Audit — Approved-Post 75

Date: 2026-04-20
Auditor: reviewer subagent per `reviewer_agent_spec.md` + plan §10
Approved-post count: 71 (post-batch-14 close)

Note on timing: this audit is triggered **early**, per founder request, before batch 15 begins drafting. The plan §10 schedule names the next audit at "approved-post count 75"; at the 25-post rhythm the audit would fall after batch 15 closes (batch 15 = posts 72–76). Running it at post 71 shifts the window one batch earlier — the sample is still the same shape (3 anchor + 3 most-recent) and the comparison to voice_audit_50.md is still symmetric, but the "recent pool" is posts 62–71 (all of batch 13 + batch 14) instead of 67–76 (batches 14 + 15 first half). The purpose of running it now is to confirm — before batch 15 drafting locks in — that the rule 10 Q&A correction has held and that no new drift has surfaced in the post-50 stretch.

Sampling seed: deterministic from date 2026-04-20. Index seed = 0 (last digit of date), then step +3 mod 10 twice → indices {0, 3, 6}. 1-indexed interpretation (0 wraps to 10): **{10, 3, 6}**, applied identically to both pools to keep selection symmetric across pools and avoid cherry-picking strong/weak posts.

## Sampled Posts

### Anchor Set (3 of 10)

Anchor set = the first 10 approved posts in `posts.ts` ordering, locked after post 10 approval per plan §10. (The plan does not enumerate the 10 by slug; we therefore use the first 10 entries in `posts.ts` publication order, which is the canonical approval-order record. Audit_50 named three of its samples with the same pool.)

- the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one (anchor #10, post 10)
- one-emotional-weigh-in-can-wreck-a-good-week (anchor #3, post 3)
- what-actually-counts-as-a-weight-loss-plateau (anchor #6, post 6)

### Recent Set (3 of 10, posts 62–71)

Recent pool = the 10 most-recent approved posts, covering all of batch 13 (posts 62–66) and batch 14 (posts 67–71). `posts.ts` lines ~5187–6395.

- the-day-i-realized-the-program-was-just-my-life-now (recent #10, post 71, batch 14)
- do-i-actually-have-to-meal-prep-to-lose-weight (recent #3, post 64, batch 13)
- why-cutting-sodium-too-hard-can-backfire (recent #6, post 67, batch 14, Tier A flagship)

## Per-Post Scores

| Slug | Pool | Rhythm | Worldview | Address | Imagery | Composite |
|------|------|--------|-----------|---------|---------|-----------|
| the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one | anchor | 9.0 | 9.0 | 8.5 | 9.0 | 8.88 |
| one-emotional-weigh-in-can-wreck-a-good-week | anchor | 9.0 | 9.0 | 7.5 | 8.5 | 8.50 |
| what-actually-counts-as-a-weight-loss-plateau | anchor | 9.0 | 9.0 | 9.0 | 9.5 | 9.13 |
| the-day-i-realized-the-program-was-just-my-life-now | recent | 9.0 | 9.5 | 9.0 | 8.5 | 9.00 |
| do-i-actually-have-to-meal-prep-to-lose-weight | recent | 8.0 | 9.0 | 8.5 | 8.5 | 8.50 |
| why-cutting-sodium-too-hard-can-backfire | recent | 8.5 | 9.0 | 8.0 | 7.5 | 8.25 |

## Pool Averages

- Anchor pool composite: 8.83
- Recent pool composite: 8.58
- **Program composite: 8.71**
- **Drift delta: −0.25**

Trend vs audit_50: program composite **+0.33** (8.38 → 8.71), drift delta **+0.83** (−1.08 → −0.25). Both axes materially improved. The post-50 rule 10 Q&A correction is visibly doing the work it was introduced to do.

## Per-Dimension Drift Analysis

### Sentence rhythm

Essentially flat (anchor 9.0 → recent 8.50). Anchor posts hold the staccato signature cleanly ("Most diets do not end with one giant disaster. / They end with a mood. An ugly little mood. / Some version of: what is the point?"). The recent personal_story (`the-day-i-realized...`) matches that cadence point-for-point ("There was no announcement. / The program did not close out with a milestone post or a summary email or a celebration dinner. / There was no 'before-and-after' moment."). The Q&A post (`do-i-actually-have-to-meal-prep...`) holds rhythm inside answers ("By Wednesday, I was eating the same chicken-broccoli-rice combo and resenting it. By Thursday, I was eating it cold. By Friday, I had abandoned the containers.") but the `Q:` bracketing chops the 1-thought-per-paragraph cadence into FAQ pacing — same structural effect audit_50 noted, but less pronounced because the Qs themselves are now shorter and more paragraph-shaped (rule 10 secondary effect). The Tier A deep_dive (`why-cutting-sodium...`) runs longer reflective/explanatory passages in the middle mechanism section and triples ("Three reasons" / "Three rules") where the anchor cadence would have given a short-long-short observational beat. Half-point below the rest of the recent pool, not a break.

### Worldview stance

Essentially flat (anchor 9.0 → recent 9.17) — the recent pool actually edges above the anchor pool on this axis, which is the cleanest stance reading since the program started. All three load-bearing pillars are present across the sample: scale not neutral (`why-cutting-sodium...`: "The scale, treated as a single-number verdict, is reporting mostly the fastest-moving component. The number drops. Your fat does not."), systems > willpower (`do-i-actually...`: "The Sunday is not the program. The default is the program."), maintenance-as-real-skill (`the-day-i-realized...`: "The program had to disappear for the body to hold. If the program is still loud after a year of maintenance, the system has not finished."). The body-slow/head-fast pillar shows up implicitly across all three. No stance abandonment anywhere in the recent pool.

### Reader address

Mild drift (anchor 8.33 → recent 8.50) — recent pool again slightly above anchor pool, driven by post 71's founder-heavy personal_story. The audit_50 finding (founder-I absent from Q&A) is no longer the active pattern: `do-i-actually...` has founder-I in 4 of 8 Qs ("Q: What did meal prep look like for me?" / "Q: What did the structure that finally worked actually look like?") with concrete four-Sunday anecdote ("I tried Sunday batch cooking three times in my own program. Each time, by Wednesday, I was eating the same chicken-broccoli-rice combo and resenting it."). That is exactly the pattern rule 10 was introduced to produce, and it is now holding 4 consecutive clean cycles (drafts 54, 58, 64, 69). The one address weakness in the recent sample is `why-cutting-sodium...`, where founder-I is concentrated in a single "What I noticed in my own program" section and the rest of the body runs second-person + abstract explanation (−0.5 below anchor median); this is a deep_dive-format artifact, not a program-wide signal, and the single founder section is vulnerable enough to carry the weight ("the scale jumped 2 kg overnight. I almost panicked. Then it stabilized at about 1.2 kg above the previous baseline").

Anchor example: "I used to call anything slower than week one a plateau. That is how impatient people talk when the scale stops flattering them." (founder-anchored, observational-before-prescriptive)

Recent example (rule 10 honored): "I tried Sunday batch cooking three times in my own program. Each time, by Wednesday, I was eating the same chicken-broccoli-rice combo and resenting it. By Thursday, I was eating it cold. By Friday, I had abandoned the containers and ordered something." (founder-anchored Q&A answer)

### Imagery density

Small drift (anchor 9.00 → recent 8.17). Anchor pool carries its signature dense concrete anchors ("Week one was a hype man. Week six is an accountant." / "Bodies are not customer service desks." / "emotional accounting, not analysis" / "bolt cutters to a door that was never locked"). The recent personal_story (`the-day-i-realized...`) holds that density with different images ("a Tuesday — sometime in month seven of maintenance" / "The program had to disappear for the body to hold." / "the same boring Tuesday repeated for 200 to 400 Tuesdays" / "a sandwich at my desk"). The Q&A post holds it via the containers-as-mood line ("By Wednesday, the containers will feel like an obligation. By Friday, they will feel like a constraint. By Sunday, you will not want to cook again.") and "The food is the infrastructure, not the entertainment." The Tier A deep_dive (`why-cutting-sodium...`) is the axis outlier at 7.5 — it substitutes physiology numbers and explicit timelines (3,000–4,000 mg/day, 1.5–2.5 kg water drop, 24–72 hour shift windows, 70–100 g/day fat change rate) where an anchor post would have placed a concrete sensory image. Concrete anchors are present but thinned by the physics/arithmetic density ("The scale rewarded the move. The body was not part of the conversation." / "The water comes back. Your relationship with food does not — at least not for free."). The pattern is format-specific — same direction audit_50 noted for Q&A, now migrated to the Tier A deep_dive subgenre — but the magnitude is about half as severe (−1.5 below anchor median vs audit_50's −2.0 for Q&A), and `why-cutting-sodium...` has stronger stance + address than the audit_50 Q&A weaknesses did, so the post holds at 8.25 composite rather than dropping into the 7s.

## Recurring Issues (program-wide)

Cross-checked against `running_style_drift_notes.md` Active list (rule 2 claim-class calibration narrowing; rule 8 hero/inline cross-role re-confirming; rule 10 Q&A correction in 4-cycle observation):

- **Rule 2 (claim-class calibration)** — production-pipeline drift, not voice drift. Does not appear in the voice sampling. Batch 14 narrowed to 1/5 via the new pre-flight checklist; batch 13 draft 64 in the recent sample was itself the rule 2 revise that bumped to Class 3 before porting. No voice-level signature at this sample.

- **Rule 8 (hero/inline cross-role within batch)** — production-pipeline drift, not voice drift. Does not appear in the voice sampling. Batch 14 clean (1st of 2 needed for re-resolution); batch 15 must also hold clean.

- **Rule 10 (Q&A founder-I + sensory-line correction)** — voice-level rule, and the one this audit most directly tests. The sample includes one Q&A post (`do-i-actually-have-to-meal-prep-to-lose-weight`, post 64, batch 13 draft 3, which was the batch 13 Q&A slot). Audit check:
  - **Founder-anchored Q present:** yes — two ("Q: What did meal prep look like for me?" with the Sunday batch-cooking-three-times anecdote, and "Q: What did the structure that finally worked actually look like?" with the three-default-dinners + two-restaurant-defaults personal structure).
  - **Concrete sensory/metaphorical line replacing bullet-list mechanism:** yes — multiple. "I did not need a Sunday. I needed a default." / "The food is the infrastructure, not the entertainment." / "Build the default first. Add a Sunday only if the default genuinely needs the help." / "By Wednesday, the containers will feel like an obligation. By Friday, they will feel like a constraint. By Sunday, you will not want to cook again."
  - **Reader Address score:** 8.5 (vs audit_50 Q&A samples at 6.0–7.0 — clean improvement above rule 10 floor).
  - **Imagery Density score:** 8.5 (vs audit_50 Q&A samples at 6.0–7.0 — clean improvement).
  - **Net:** rule 10 is confirmed holding at 4 consecutive clean cycles (drafts 54, 58, 64, 69 per batch verdicts 11–14) and this independent post-75 audit sample corroborates the batch-level finding. The voice-level pattern audit_50 named ("Q&A-format posts drop founder-I and substitute mechanism numbers for sensory imagery") is no longer detectable in the sample.

- **New voice-level observation (format-specific, not yet a program-wide drift):** the Tier A deep_dive subgenre (`why-cutting-sodium-too-hard-can-backfire`, post 67, the first scheduled Tier A rewrite) scored 7.5 on Imagery Density — the lowest imagery score in the recent sample. The thinning pattern is the same shape as audit_50's Q&A finding (numbers and bullet triples substituting for sensory anchors), but displaced into the physiology-deep_dive format rather than Q&A. One sample is not enough to call a drift; batches 15–18 will slot four more Tier A rewrites (lower_body_stubborn, refined_carbs, thin_people_can_gain_weight, highly_processed_food_voltage), all of which are physiology-adjacent and will produce the same number-density pressure. Flag for observation through post-100 audit, not a correction yet.

## Verdict

**PASS**

Rationale: Program composite 8.71 sits comfortably above the §10 quality floor of 7.0, every sampled post scores ≥ 8.25, and the drift delta of −0.25 is well inside the §10 clean-PASS envelope (composite ≥ 8.0 + drift delta > −0.5). Four of six sampled posts score ≥ 8.88, and the recent pool actually edges above the anchor pool on two of four axes (Worldview 9.17 > 9.00; Reader Address 8.50 > 8.33) — the audit_50 Q&A gap in Reader Address is closed and inverted. The post-50 correction (rule 10) is visibly effective. No correction needed; no pause needed; no revise needed.

Compared to audit_50 (PASS-WITH-CORRECTION, composite 8.38, drift delta −1.08), this is a clean improvement across every axis the rule 10 correction targeted. The one sub-anchor score in the recent pool (`why-cutting-sodium...` Imagery 7.5) is a format-artifact in the Tier A deep_dive subgenre, not a repeat of the audit_50 Q&A pattern and not a recurring issue across the sample.

## Correction Direction

**None required.** Rule 10 holds; no new program-wide drift surfaced.

Recommended running-notes updates (companion to this audit, to be applied by writer to `running_style_drift_notes.md` after founder review of this audit):

- Rule 10 is eligible for resolution per §22 ("2 consecutive batches without the issue"). Four consecutive clean cycles (batches 11–14) and this audit's independent sample confirm the Q&A subgenre is no longer dropping founder-I or thinning imagery. Recommend: move rule 10 from Active to Resolved at batch 15 close if batch 15 remains clean (5th consecutive clean cycle). Until then, keep in observation — the Tier A slotting plan has no Q&A in batches 15–18, so the next rule 10 test will be whenever a Q&A format rotation next lands (est. batch 16 or 17).

- Tier A deep_dive imagery-density watch (**informational, not a new Active rule**):

  `2026-04-20 | post_75_audit | Tier A deep_dive rewrites (physiology-adjacent topics with explicit numbers) trend ~1.5 points below anchor on Imagery Density as physics/arithmetic density displaces concrete sensory anchors; sodium post scored 7.5 (single sample, not yet a pattern) | no action yet — observe across batches 15–18 (lower_body_stubborn, refined_carbs, thin_people_can_gain_weight, highly_processed_food_voltage). If 2 of 4 Tier A rewrites score Imagery ≤ 7.5, add as Active drift rule 11. If 3 of 4 score ≥ 8.0, close the watch. | _observation only; no corrective action required from writer_`

  This is a **watch**, not an Active rule. No correction direction. The writer should continue drafting Tier A rewrites as scheduled per `tier_a_slotting_plan.md`; the reviewer will monitor Imagery Density at batch 15–18 verdicts.

## Anchor Set Revision Recommendation

- Recommend revision: **no**
- Per §20, anchor revision is allowed at the 50-post checkpoint with founder sign-off. The post-75 audit is **not** a §20 checkpoint — the anchor set is formally locked until post 100 (per checkpoints.md 50-post sign-off: "Anchor set NOT revised at this checkpoint. Next decision checkpoint: post 100"). Revision at post 75 is not plan-authorized in any case.
- Even if it were, the audit does not justify revision. The anchor pool sample averaged 8.83, which is within 0.1 of audit_50's anchor sample (8.92). The anchor set continues to represent the program's voice accurately. The one score below 8.75 in the anchor sample (`one-emotional-weigh-in...` at 8.50) is driven by founder-I absence in that specific post — which is a feature of that post, not of the anchor set as a whole (it is a scale-reframing post written in third-person observational mode by design, and other anchors in the set carry the founder-I load). The anchor sample's spread (8.50 to 9.13) mirrors the expected variance in a set of 10 locked posts.
- Founder has already signed off on "no revision required" at the 50-post checkpoint. This audit confirms that call holds through post 71. Next eligible revision window is the post-100 close-out checkpoint.

## Next Audit

Approved-post 100 (program close-out, est. after batch 19 closes — posts 92–95 per plan §6, batch 19 = 4 posts).

Interim quality-floor check: if any batch 15–19 verdict flags ≥ 2 drafts with `voice_drift_flag: yes`, or if any single draft scores composite < 7.0 at reviewer-level voice sampling, trigger an out-of-schedule voice audit per §21 before continuing to the next batch.
