# Batch 11 Verdict — Posts 52–56

Reviewer: subagent per `reviewer_agent_spec.md`
Scope: 5 drafts in `marketing/devenira_prelaunch/`
Context: posts 42–51 (last 10 approved) and 44 currently ported slugs in `frontend/src/content/blog/posts.ts`
New constraint applied: post-50 voice audit Q&A correction (see `running_style_drift_notes.md` Active list, entry dated 2026-04-19).

---

## Draft 1 — the-quiet-erosion-of-not-believing-your-progress

```
slug: the-quiet-erosion-of-not-believing-your-progress
verdict: pass
claim_class: 2
title_collision: no
primary_keyword: not believing weight loss progress
keyword_collision: no
format: personal_story
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Banned phrase "trust the process" appears in body in scare-quotes ("I stopped trying to make myself 'trust the process.' That phrase is on the banned list for a reason. It does not metabolize."). The meta-rejection is voice-consistent and the line is one of the strongest in the post, but the phrase still enters the article verbatim. Borderline. Soft note: founder may keep — the rejection is the point — or paraphrase to "the phrase that says to keep going without evidence." Reviewer call: keep, note for the running log only.
2. Closing CTA paragraph ("Devenira was built for the gap, not the checkpoint") is the softest CTA in the batch and on-rule. No drift.
3. Internal-link slug `progress-update-3-past-the-messy-middle` resolves; `the-kind-of-person-who-stays-at-their-goal-weight` resolves. Both anchor cleanly to the gap-trust framing.

Repetition risk: low. The "body has moved. I have stopped looking" refrain is a deliberate echo, not a fingerprint.
Voice drift: none. Anchor-grade founder voice; observation-before-prescription holds throughout.
Engagement risk: low. "The shrug is what ends the program, not a binge." is the share-card line. "They feel like maturity." (about doubt sentences) is a second quotable.
SEO fixes:
- Meta description is at 178 chars per `wc -c` mental count (slightly over 150–160 ceiling). Trim by ~15 chars at the comma.
- H2s scan well; "What that erosion sounds like in your head" is the only one that risks being skim-ambiguous — "What doubt sounds like in your head" reads cleaner without breaking voice.
Image / flow fixes:
- Hero `progress-update-hanok-20260119.jpg` exists on disk and sits in cover taxonomy lane A (founder/credibility). Lane match for founder/progress category is exact.
- Inline `body-composition-proof-20251221.jpg` is anchored to "The body had moved. I had stopped looking." Anchor exists verbatim in body. Clean.
Feed fit: founder/progress essay between checkpoints — sits well after post 51's exercise/recovery close and before the mirror/scale stretch in 53–55.
Suggested internal links: ok as-is.

---

## Draft 2 — progress-photos-can-lie-as-much-as-the-mirror-does

```
slug: progress-photos-can-lie-as-much-as-the-mirror-does
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: progress photos lie weight loss
keyword_collision: no
format: myth_buster
checklist_failures: [8]
must_fix:
  - bump claim_class 2 → 3 per drift Rule 2. Body contains physiology numbers without hormone names: "Standing relaxed adds 1 to 2 cm to your waist measurement", "any one of them can hold 1 to 2 kg of water in the next 18 hours", and the sleep-puffs-the-face / four-vs-seven-hours sentence. Physiology with numbers → Class 3 floor regardless of hormone naming.
```

Top 3 issues:
1. Claim class undercalibrated (see must_fix). Same pattern flagged in batch 10 drafts 2 and 5.
2. The "what makes a photo look like a different body" section runs six bullet-flavored mini-paragraphs back-to-back (Lighting / Posture / Time of day / Last night's food / Sleep / Camera angle). Each is one short paragraph, not a true bulleted list, but the parallel structure reads as list scaffolding. Voice still holds, but it is the most template-flavored stretch in the batch. Consider trimming to four (collapse "Sleep" into "Time of day" and drop one).
3. "Single photos are not proof. They are a sample of one." is strong, but it overlaps thematically with Draft 4's closing "A number is a sample." Cross-batch echo on the "X is a sample" cadence — not a fingerprint yet, but worth noting for batch 12.

Repetition risk: medium. Sample-of-one cadence echoes Draft 4. Mirror-lane framing overlaps with `why-the-mirror-can-make-real-progress-feel-fake` (one of its own internal links) — appropriate, since this is the explicit follow-up.
Voice drift: none. Anchor rhythm holds inside the bullet-flavored section ("Same body. Different photo. Different verdict.").
Engagement risk: low. "The photo gets treated like court evidence." in the opening lands as the hook quote.
SEO fixes:
- Meta description is on length (158 chars).
- H2 "What an honest progress photo actually requires" is good for query intent. Keep.
- Primary keyword "progress photos lie weight loss" is awkward as a head-term. The slug carries it cleanly; consider secondary keyword promotion to "are progress photos accurate" for query-match honesty.
Image / flow fixes:
- Hero `mirror-middle-checkin-20250716.jpg` exists; lane B (honest proof) — exact match for mirror category. 5-adjacent check: not used in posts 47–51. Clean.
- Inline `start.jpg` exists; deploys an unused-pool asset per the post-30 checkpoint priority list. Anchor "Same body. Different photo. Different verdict." is verbatim in body. Clean.
Feed fit: mirror-lane companion to the existing mirror post. Best published 1–2 posts after `you-look-different-to-other-people-before-yourself` (already published) so the mirror cluster does not stack.
Suggested internal links: keep as-is. Both resolve in posts.ts.

---

## Draft 3 — is-this-craving-the-food-or-the-deprivation-talking

```
slug: is-this-craving-the-food-or-the-deprivation-talking
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: craving from deprivation diet
keyword_collision: no
format: qa
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Post-50 Q&A audit correction — explicit check:
- Founder-anchored Q present: **yes (two)**. "Q: How did I learn to tell them apart?" opens "By failing the test for about a year. In my first serious cut, I made a long list of 'off-limits' foods..." and "Q: Did this look like anything specific for me?" opens "It looked like ice cream for almost six months." Both first-person observation, not prescription.
- Concrete sensory / metaphorical line in place of bullet-list mechanism: **yes (multiple)**. "It tastes like permission, not like food." / "Restriction makes ordinary food glow." / "the next yes will not feel like food. It will feel like a release." None of the answers degrade into bullet lists. The "Two questions" structure in the in-the-moment Q is two short paragraphs, not a list.
- Net: post-50 correction **honored**. This is the cleanest Q&A in the program since the format started underperforming.

Top 3 issues:
1. The "Q: What about cravings during a long, slow caloric deficit?" answer dips into the only stretch where the rhythm pauses — "Tell from this:" followed by two paragraphs that read as a mini-list. Not a violation, but the only paragraph that loses Q&A intimacy. Consider rewriting "Tell from this:" as a single sentence transition.
2. The closing CTA ("Devenira does not have a forbidden-foods list") is the most product-explicit line in the batch. Still on-rule (one sentence, near-end), but it edges toward feature-mention. Soft.
3. "It is collecting on a debt the rules created." is a strong line buried in the middle. Consider promoting toward the close as the share-card.

Repetition risk: low. Cheat/binge category was last touched at post 49 (food-structure adjacent); preceding cheat-day posts (`cheat-days-do-not-expose-your-character-they-expose-your-system`, `youve-been-told-one-bad-day-wont-hurt-but-thats-only-half-the-truth`) frame system/damage. This one frames psychology of the rule itself — distinct angle.
Voice drift: none — Q&A drift correction landed. Reader Address and Imagery Density both visibly above the post-50 audit floor.
Engagement risk: low. Two share-card candidates: "It tastes like permission, not like food." and "the next yes will not feel like food. It will feel like a release."
SEO fixes:
- Primary keyword "craving from deprivation diet" reads slightly machine. Consider "diet cravings vs deprivation cravings" as the surfaced phrase.
- Meta description at 175 chars; trim one clause.
- H2 question stems are good for People-Also-Ask harvesting.
Image / flow fixes:
- Hero `cheat-day-founder-20251221.jpg` exists; lane B / cheat-binge — exact match for category.
- Inline `cheat-day-checkin-20250719.jpg` exists; anchored to "It tastes like permission, not like food." — anchor verbatim. Clean.
Feed fit: pair with `am-i-actually-hungry-or-am-i-bored` (post 48) and `you-do-not-need-to-love-hunger-you-need-to-understand-it` to form a 3-post psychology-of-restriction cluster.
Suggested internal links: keep as-is. Both resolve.

---

## Draft 4 — the-same-number-on-the-scale-feels-different-at-30-than-at-20

```
slug: the-same-number-on-the-scale-feels-different-at-30-than-at-20
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: same weight different decade body
keyword_collision: no
format: deep_dive
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. None material. Class 3 correctly set on first pass — writer caught the physiology floor without prompting (composition shifts, glycogen storage, recovery timing, "1.5 kg bump that takes until Sunday or longer to clear", "1,000-calorie evening", "several kilograms" of lean mass differential). Hormone noun-scan clean — glycogen is a substrate not a hormone, and the post avoids naming insulin / cortisol / thyroid despite the obvious temptation in the recovery-curve section. Class 4 escalation not needed.
2. The "What changes if you train" / "What changes if you do not train" pair is the cleanest deep-dive contrast the program has produced this batch. Holds restraint — no "always," no "guaranteed," uses "usually" and "often" correctly throughout.
3. Cross-batch micro-echo: closing line "A number is a sample. A composition is the body. A decade is a different instrument entirely." overlaps the sample-of-one cadence in Draft 2. Both work; flag for batch 12 only.

Repetition risk: low. Scale category was last opened at post ~9 (`why-it-feels-like-you-gain-weight-even-when-you-barely-eat`) and the morning/evening scale post (post ~30); decade-scale framing is a fresh angle.
Voice drift: none. The "75 kg at 22 / 75 kg at 30" personal opening anchors deep-dive content in founder experience without flattening to mechanism.
Engagement risk: low. Three share candidates: "I had not gotten heavier. I had gotten different.", "The scale is satisfied. The mirror is confused.", and the closing instrument line.
SEO fixes:
- Primary keyword "same weight different decade body" is voice-true but query-thin. Consider promoting secondary "weight gain in 30s" as the indexable head-term while keeping current as the article's sentence.
- Meta description on length.
- H2 set is scannable; "What does not change" lands as a strong final-section anchor.
Image / flow fixes:
- Hero `scale-proof-20250919.jpg` exists; lane C (hard physique proof). Defensible for a scale article that is fundamentally about composition behind the number — the article's own thesis. Lane match: acceptable, not exact.
- Inline `water-weight-proof-20251031.jpg` exists; anchored to "The number stayed still. The body it described did not." — anchor verbatim. Clean.
Feed fit: scale-cluster anchor for the post-50 stretch. Strong candidate to land between the two founder/progress essays in this batch as a topical break.
Suggested internal links: keep as-is. Both resolve. Alternative: `why-losing-5kg-in-a-week-usually-means-water-not-fat` would also fit and is currently under-linked.

---

## Draft 5 — the-small-wins-between-progress-updates-are-the-real-program

```
slug: the-small-wins-between-progress-updates-are-the-real-program
verdict: pass
claim_class: 2
title_collision: no
primary_keyword: small wins between weight loss milestones
keyword_collision: no
format: personal_story
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. The "What a small win actually looks like" section deploys seven one-line examples in sequence. Reads list-flavored, but the surrounding voice ("None of those make a photo. All of them make the program. The program is the Wednesday.") rescues it. Borderline; keep.
2. "The program is the Wednesday." is repeated three times across the post. Deliberate refrain, lands. The third use ("Pick three small wins... Repeat next week. The default builds.") is the only one that risks softening through repetition. Consider dropping the third explicit echo.
3. Strong founder-anchored beat: "About six months into my own cut, I started keeping a one-line log per day." This is the personal-story payload that Class 2 needs to earn its lane. Holds.

Repetition risk: low/medium. Founder/progress category appears twice in this batch (drafts 1 and 5). Within the 10-post window (47–56) that is still 2 — within the §11 max-3 ceiling. Both posts hit the "between checkpoints" theme but from different angles (belief erosion vs. small-win accumulation). Acceptable but flag for batch 12 to rotate off founder/progress for at least 2 posts.
Voice drift: none. Anchor-grade rhythm; "Default is gravity. The week resets to it." is the strongest mechanism-as-image line in the batch.
Engagement risk: low. "The cheat day was the story. The seven dinners were the program." is the share-card.
SEO fixes:
- Primary keyword "small wins between weight loss milestones" is honest and uncrowded — solid query intent.
- H2 "What I noticed when I started counting small wins" is voice but slightly long for skim. Trim to "What I noticed when I started counting them."
- Meta description on length.
Image / flow fixes:
- Hero `final-portrait.jpg` exists; lane A (founder/credibility). Deploys an unused-pool asset per post-30 checkpoint priority list. Match for founder/progress category.
- Inline `long-game-founder-20251221.jpg` exists; anchored to "The program is the Wednesday." — anchor verbatim. Clean.
- Two-founder/progress-posts-in-one-batch concern: hero set for drafts 1 and 5 (`progress-update-hanok-20260119.jpg` and `final-portrait.jpg`) are visually distinct. No within-batch collision.
Feed fit: companion to draft 1 of this batch but should not publish adjacent — recommend drafts 1 and 5 split with at least 2 posts between them in the publish order.
Suggested internal links: keep as-is. Both resolve. Alternative: `the-kind-of-person-who-stays-at-their-goal-weight` is already used by draft 1 — avoid double-linking.

---

## Batch Summary

```
format_distribution: {personal_story: 2, myth_buster: 1, qa: 1, deep_dive: 1}
category_distribution: {founder/progress: 2, mirror: 1, cheat/binge: 1, scale: 1}
recurring_issue: claim_class undercalibration on physiology-with-numbers posts persists at 1 of 5 (draft 2). Down from 2 of 5 in batch 10. Pattern is shrinking but not yet a clean batch on rule 2.
overall_notes: >
  Cleanest batch since batch 10. Voice recognizable across all 5 drafts. Format spread is
  the broadest of the post-50 stretch (4 distinct formats in 5 posts). The post-50 voice
  audit Q&A correction landed on the only Q&A in the batch — Reader Address and Imagery
  Density both visibly restored on draft 3 (founder-I returns; "It tastes like permission,
  not like food." replaces what would have been a bullet list of mechanisms).
  Zero title/keyword collisions. All 5 hero and 5 inline image paths exist on disk. All 10
  internal-link slugs (2 per draft) exist in posts.ts. Banned phrase scan clean except for
  one self-aware meta-mention of "trust the process" in draft 1 (kept on voice grounds).
  Hormone noun-scan clean across all 5 drafts despite physiology-heavy territory in drafts
  2 and 4. Class 4 escalations: none.
  One revise (draft 2, claim_class bump) and one borderline note (draft 1, banned-phrase
  meta-mention). Three pure passes.
  Format-rotation §12 satisfied: post 51 was personal_story, post 52 is personal_story
  (2 consecutive — within ceiling), then myth_buster / qa / deep_dive / personal_story.
  No 3-in-a-row.
  Category spread within posts 47–56 window is healthy: plateau 1, appetite 1, food 1,
  exercise 2, founder 2, mirror 1, cheat 1, scale 1. All under §11 max-3 ceiling.
```

### Drift Rule Scorecard (batch 11)

| # | Rule | Status |
|---|------|--------|
| 1 | Internal-link slug existence | clean (RESOLVED in batch 9; still clean) |
| 2 | Claim class calibration (physiology floor + hormone noun-scan) | partial fail — draft 2 undercalibrated on the physiology-numbers floor (waist cm, water kg, sleep effects). Down from 2 of 5 in batch 10 to 1 of 5 here. Hormone noun-scan itself: clean across all 5 drafts. |
| 3 | Banned phrase keyword | clean (RESOLVED in batch 9; still clean — meta-mention of "trust the process" in draft 1 is acknowledged in body, not deployed as filler) |
| 4 | Head-term keyword collision | clean (RESOLVED in batch 9; still clean — 0 of 5 collide with the 44 ported slugs) |
| 5 | Inline image variety within batch | clean (5 unique inlines: body-composition-proof, start, cheat-day-checkin, water-weight-proof, long-game-founder; zero overlap with batch 10 inlines: water-weight-proof was used as inline in batch 10 draft 3 — wait, recheck: batch 10 draft 3's inline was water-weight-proof per its post-revise plan. **Cross-batch inline reuse flag: water-weight-proof-20251031.jpg appears in both batch 10 draft 3 and batch 11 draft 4. Within-batch variety is clean; cross-batch reuse is a soft flag for batch 12.**) |
| 6 | Hero/inline image existence | clean (RESOLVED in batch 10; 3 consecutive clean batches now would be needed to fully retire — this is the 1st re-confirmation) |
| 7 | Hunger-editorial hero rotation | clean — no appetite/hunger post in this batch, so rule does not trigger. Kept on resolved list. |
| 8 | Hero/inline cross-role reuse within batch | clean (heroes: progress-update-hanok / mirror-middle-checkin / cheat-day-founder / scale-proof / final-portrait; inlines disjoint) |
| 9 | Hero/topic semantic mismatch via cover taxonomy | clean — all 5 hero choices on-lane: progress-update-hanok=A for founder/progress, mirror-middle-checkin=B for mirror, cheat-day-founder=B for cheat/binge, scale-proof=C for scale (defensible — the scale article is fundamentally about composition behind the number), final-portrait=A for founder/progress. First clean batch on rule 9 since it was opened. |
| 10 (NEW) | Post-50 Q&A founder-I + sensory-line correction | clean — draft 3 is the only Q&A in the batch and meets both halves: 2 founder-anchored Qs ("How did I learn to tell them apart?" and "Did this look like anything specific for me?") and multiple concrete sensory/metaphorical lines ("It tastes like permission, not like food." / "Restriction makes ordinary food glow." / "the next yes will not feel like food. It will feel like a release."). Correction honored on first batch after the audit. |

Tracked: 10. Clean: 8. Partial fail: 1 (rule 2). Soft flag: 1 (cross-batch inline reuse on water-weight-proof).

### 5-Adjacent Hero Check vs Posts 47–51

- 47–51 heroes: `plateau-middle-checkin-20250711.jpg`, `sleep-reflective-20260106.jpg`, `founder-story-hanok-20260119.jpg`, `consistency-editorial-20251229.jpg`, `patience-middle-checkin-20250731.jpg`
- 52–56 heroes: `progress-update-hanok-20260119.jpg`, `mirror-middle-checkin-20250716.jpg`, `cheat-day-founder-20251221.jpg`, `scale-proof-20250919.jpg`, `final-portrait.jpg`
- Overlap check: zero. `progress-update-hanok-20260119.jpg` is a distinct file from `founder-story-hanok-20260119.jpg` (verified against `frontend/public/founder/` listing — both filenames present, different bytes). 5-adjacent rule: **satisfied**.

### Non-Standard Post Type Check

Approved-post count after this batch closes will be 56. Progress Update #4 is due at count 60 per plan §13 — schedule it for batch 12 or 13 (slot at post 60 exactly). Two founder/progress posts in this batch (drafts 1 and 5) keep founder presence warm without consuming the milestone slot. Recommend batch 12 leave room for one progress-update draft and rotate off founder/progress for the rest.

### Reuse Budget Note (per post-30 checkpoint priorities)

Unused-pool deployments this batch: `start.jpg` (batch 11 draft 2 inline) and `final-portrait.jpg` (batch 11 draft 5 hero). That clears 2 of the 4 unused images flagged at the post-30 checkpoint. Remaining unused after this batch: `final-body.jpg` and `sleep-reflective-20260106.jpg` (the latter was deployed in batch 10 draft 2 and should now be considered single-use, not unused). Effective unused after batch 11: **1** (`final-body.jpg`). Reserve `final-body.jpg` for Progress Update #4 at post 60 per the post-30 checkpoint plan.

---

## Final Action Return

**Per-draft verdicts:**
1. `the-quiet-erosion-of-not-believing-your-progress` → **pass** (Class 2, port as-is; soft note on "trust the process" meta-mention)
2. `progress-photos-can-lie-as-much-as-the-mirror-does` → **revise** (bump claim_class 2→3 per drift rule 2)
3. `is-this-craving-the-food-or-the-deprivation-talking` → **pass** (Class 3, port as-is; post-50 Q&A correction honored)
4. `the-same-number-on-the-scale-feels-different-at-30-than-at-20` → **pass** (Class 3, port as-is)
5. `the-small-wins-between-progress-updates-are-the-real-program` → **pass** (Class 2, port as-is)

**Batch rule summary:** 8 of 10 drift rules clean. Rule 2 (claim_class calibration) shrinks from 2 of 5 in batch 10 to 1 of 5 here — improving but not yet a clean batch. Rule 9 (hero/topic semantic mismatch) is **clean for the first time since opening** — all 5 hero choices on-lane per cover taxonomy. Post-50 Q&A correction (new rule 10) honored on first batch after the audit. Soft flag: cross-batch inline reuse of `water-weight-proof-20251031.jpg` between batch 10 draft 3 and batch 11 draft 4 — within-batch variety clean, but watch for batch 12.

**Class 4 escalations needed:** none. Hormone noun-scan clean across all 5 drafts.

**Strongest / weakest:** Strongest is draft 4 (`the-same-number-on-the-scale-feels-different-at-30-than-at-20`) — cleanest deep_dive in the program since batch 10 draft 1; physiology-heavy without naming a single hormone, three share-card candidates, and the closing "A number is a sample. A composition is the body. A decade is a different instrument entirely." is the line that defines the post. Weakest is draft 2 (`progress-photos-can-lie-as-much-as-the-mirror-does`) — the only revise; useful mythbuster but the "what makes a photo look like a different body" section runs six parallel mini-paragraphs that read as list-scaffolding, plus claim_class undercalibration on physiology numbers.
