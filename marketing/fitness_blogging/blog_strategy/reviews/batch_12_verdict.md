# Batch 12 Verdict — Posts 57–61

Reviewer: subagent per `reviewer_agent_spec.md`
Scope: 5 drafts in `marketing/devenira_prelaunch/`
Context: posts 47–56 (last 10 approved) and 49 currently ported slugs in `frontend/src/content/blog/posts.ts`
New constraint applied: post-50 voice audit Q&A correction (rule 10) — draft 2 is the only Q&A this batch.
Milestone post in batch: draft 4 = Progress Update #4 per plan §13 (approved-post 60).

---

## Draft 1 — the-first-month-of-maintenance-feels-nothing-like-the-diet

```
slug: the-first-month-of-maintenance-feels-nothing-like-the-diet
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: first month of maintenance after diet
keyword_collision: no
format: deep_dive
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Claim class correctly set on first pass. Body carries physiology numbers without naming any hormone — "300 to 600 calories back to your daily intake," "a 1 kg jump on a Tuesday," "the maintenance number is the number you are at," "appetite signal" reframed without invoking leptin/ghrelin. Hormone noun-scan clean. Class 4 escalation not needed. Writer caught the Class 3 floor unprompted, repeating draft 4 of batch 11's behavior.
2. Meta description reads ~204 chars per `wc -c` mental count — 40+ over the 150–160 ceiling. Trim by collapsing the third sentence into the second: "The plate gets bigger and the structure stays. The head expects a finish line that never arrives." That lands at ~160.
3. The "What I needed and did not have" section ("A waist measurement once a week. A photo once a week, same conditions as during the cut. A weekly weight average, not a daily reading. A note about how the week felt overall...") runs four parallel one-line items in a row. Reads as soft list-scaffolding. Voice rescues it ("Each one alone was insufficient. Together, they replaced the single goal-pursuit signal the cut had given me.") but it is the most template-flavored stretch in the batch. Borderline; keep.

Repetition risk: low. Maintenance category was last directly opened at post 51 (`hunger-in-maintenance-is-different-from-hunger-on-a-diet`) and indirectly across `the-kind-of-person-who-stays-at-their-goal-weight` (post 56 in posts.ts). This is the first dedicated "first 30 days of maintenance" angle. Distinct.
Voice drift: none. Anchor-grade. "It feels like the same day with a slightly larger dinner." holds the founder-observation-before-prescription cadence. The two opening sentences ("The diet has a finish line painted on it. Maintenance does not.") are the share-card.
Engagement risk: low. Three quotable candidates: opening pair, "The maintenance scale is the noisiest scale you will ever read.", and "It just stopped looking like a goal."
SEO fixes:
- Trim meta to ~160 chars (see issue 2).
- Primary keyword "first month of maintenance after diet" is honest and uncrowded; no rewrite needed.
- H2 set scans well; "Why 'just eat more' is the wrong frame" is the strongest skim-reward anchor.
Image / flow fixes:
- Hero `long-game-founder-20251221.jpg` exists; lane A (founder/credibility) but the image was tagged for the "long game" / maintenance subgenre at the post-30 checkpoint (used in posts.ts for `do-people-who-have-been-obese-for-years-lose-weight-more-slowly` and `the-friend-who-never-diets-and-never-gains` and `why-people-gain-more-back-than-they-lost`). Lane match for maintenance is exact within the lane-A "long-game founder" subset. Defensible.
- Inline `consistency-editorial-20251229.jpg` exists; anchored to "The plan got bigger. The structure stayed." Anchor verbatim in body. Clean.
Feed fit: opens the maintenance lane for the post-50 stretch. Best published as the first non-progress-update post after Progress Update #4 (draft 4) lands at post 60, so the maintenance lane gets a deep_dive anchor immediately after the milestone.
Suggested internal links: keep as-is. Both `the-kind-of-person-who-stays-at-their-goal-weight` and `hunger-in-maintenance-is-different-from-hunger-on-a-diet` resolve in posts.ts.

---

## Draft 2 — why-does-my-hunger-spike-at-night-when-i-was-fine-all-day

```
slug: why-does-my-hunger-spike-at-night-when-i-was-fine-all-day
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: hunger spike at night dieting
keyword_collision: no
format: qa
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Post-50 Q&A audit correction — explicit check (rule 10):
- Founder-anchored Q present: **yes (two)**. "Q: What did the night spike look like for me?" opens "For most of my first cut, it looked like the same scene three to four nights a week..." with a fully-rendered scene through 9:30 p.m. "Q: What worked for me, in plain terms?" opens "Two changes did most of the work. I moved my dinner later, by about 90 minutes..." Both first-person observation, not prescription.
- Concrete sensory / metaphorical line in place of bullet-list mechanism: **yes (multiple)**. "The day was a number. The evening was a person." (the share-card). "white-knuckling on the couch with the TV up." "Most night-hunger spikes are not psychological. They are scheduling problems wearing psychological clothes." None of the answers degrades into a true bulleted list — the "Three things stack on top of each other in the evening" section uses three short paragraphs (Caloric debt / Decision fatigue / Lower blood sugar) instead of a hard list, and the rescue line "None of those is a failure of character. The evening just stacks the deck against you." restores the founder voice.
- Net: post-50 correction **honored**. Cleaner than batch 11 draft 3 on Reader Address (founder "I" appears in 4 of 8 Q&As) and on equal footing for Imagery Density.

Top 3 issues:
1. Class 3 correctly set on first pass. Body contains physiology numbers — "200 calories moved from earlier in the day," "35 to 45 grams of protein," "150 to 200 calories of yogurt, fruit, or a protein shake," "two extra hours of sleep" — and a "blood sugar in the evening" reference, but no hormone is named (no leptin, ghrelin, cortisol, insulin). Class 4 escalation not needed.
2. Hero `weighin-middle-progress-20240801.jpg` is on a borderline lane match for an appetite/Q&A post. Cover taxonomy lane B (honest proof / mirror / scale / plateau) is its primary lane; the same file is used in posts.ts as the hero for `one-emotional-weigh-in-can-wreck-a-good-week`. The cleaner lane for a hunger Q&A is D (lifestyle / sleep / hunger / routine), but D options are constrained — `hunger-editorial-20260106.jpg` is at saturation (3 uses per post-30 checkpoint), `sleep-reflective-20260106.jpg` is single-use post-batch-10, `sleep-reflective-window-20241217.jpg` is already deployed as the inline on this same draft. The 5-adjacent rule plus saturation pressure make `weighin-middle-progress-20240801.jpg` the cleanest available fallback. The hero alt acknowledges the stretch ("the calm of a clean weekday that quietly sets up the evening hunger spike") and reads as a defensible bridge image rather than a wrong one. Soft note for the reuse-budget log; not a blocker.
3. The "Q: How do I tell whether the spike is real hunger or a behavior loop?" answer ("First: would I be hungry for a chicken-and-rice plate right now?... Second: am I reaching for the same specific food at roughly the same time three or more nights a week?") echoes the apple-test cadence in `am-i-actually-hungry-or-am-i-bored` (post 48). Same heuristic, slightly different food — both work as standalone posts but the cross-batch echo is now visible. Flag for batch 13 to rotate off the "would I eat [specific bland food]" structure.

Repetition risk: medium. Appetite category was opened at post 48 (`am-i-actually-hungry-or-am-i-bored`) and at post 51 (`hunger-in-maintenance-is-different-from-hunger-on-a-diet`) — this is the third appetite-adjacent post in the post-47 window. Within §11 max-3 ceiling but at the limit. Rotate off appetite for at least 2 posts in batch 13.
Voice drift: none. Q&A correction landed. Reader Address and Imagery Density both visibly above the post-50 audit floor.
Engagement risk: low. "The day was a number. The evening was a person." is the share-card. "Diets that fail in the evenings are usually diets that were too tight at lunch." is a second quotable.
SEO fixes:
- Meta description on length (~145 chars). Clean.
- Primary keyword "hunger spike at night dieting" is honest and matches PAA query intent ("why am I starving at night").
- H2 question stems are good for People-Also-Ask harvesting.
Image / flow fixes:
- Hero exists; lane mismatch noted in issue 2 above. Defensible under reuse pressure, soft flag for log.
- Inline `sleep-reflective-window-20241217.jpg` exists; lane D (lifestyle / support); anchored to "The day was a number. The evening was a person." Anchor verbatim in body. Clean.
Feed fit: third appetite post in 14 posts. Best published with at least 2 non-appetite posts on either side. Sits well between the maintenance deep_dive (draft 1) and the plateau myth_buster (draft 3).
Suggested internal links: keep as-is. Both resolve.

---

## Draft 3 — the-plateau-that-was-actually-an-honesty-problem

```
slug: the-plateau-that-was-actually-an-honesty-problem
verdict: pass
claim_class: 3
title_collision: no
primary_keyword: weight loss plateau tracking honesty
keyword_collision: no
format: myth_buster
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

Top 3 issues:
1. Class 3 correctly set on first pass. Body carries physiology numbers — "1,000 to 1,500 calories" of estimation drift, "100 to 300 calories a day" hidden bites, "1,500 to 3,000 calories" weekend amnesia, "100 to 300 calories per day at the worst extreme" for metabolic adaptation — and uses NEAT as a behavioral mechanism rather than a hormone. Hormone noun-scan clean. Class 4 escalation not needed.
2. The "weekend amnesia" framing ("'social' calories that get logged in narrative form ('had dinner with friends') rather than item form") is the strongest mechanism-as-image line in the batch and the share-card candidate. The post earns the myth-buster format because it does not flatten into "you're lying to yourself" — the meta-frame ("Most people I talk to... weekday calories are accurate, weekend calories are vibes") keeps the rude-honest founder voice without crossing into cruelty.
3. The "What this looked like in my own program" section is the founder-anchored beat that keeps the myth-buster honest ("I dropped daily calories by another 200... Still flat. The diet was now well below maintenance for my activity, and I was getting consistently hungry by mid-afternoon, and I was still not losing... I had been under-counting by about 250 to 350 calories a day"). Vulnerable, specific, and earns the post's central claim. This is the post's load-bearing paragraph — protect it under any revise.

Repetition risk: low. Plateau category was last directly opened at post 49 (`why-you-stop-losing-weight-around-month-three`, in posts.ts) and indirectly at post 32 (`a-plateau-is-a-data-point-not-a-failure`) and post 30 (`what-actually-counts-as-a-weight-loss-plateau`). This post's tracking-honesty angle is materially different from "plateau = adaptation" or "plateau = data point" framings. Distinct.
Voice drift: none. Anchor-grade rhythm; "The body does not care what your log says. It is responding to the actual calories." holds.
Engagement risk: low. Three share candidates: "The plateau got smaller as the honesty got bigger.", "Tracking accuracy decays.", and "The diet had not failed. The log had."
SEO fixes:
- Meta description at ~165 chars — slightly over 150–160 ceiling. Trim "the body has not stopped responding. The tracking has stopped being honest." to "The body has not stopped responding. The tracking has." (~155 chars).
- Primary keyword "weight loss plateau tracking honesty" reads slightly machine. Consider promoting secondary "hidden calories plateau" as the indexable head-term while keeping current as the article's sentence.
- H2 set is scannable; "Why this happens to people who think they are tracking" is the strongest skim-reward anchor.
Image / flow fixes:
- Hero `plateau-middle-checkin-20250711.jpg` exists; lane B (honest proof / plateau). Exact lane match. Used as hero in posts.ts for `what-actually-counts-as-a-weight-loss-plateau`, `a-plateau-is-a-data-point-not-a-failure`, and `why-you-stop-losing-weight-around-month-three`. This is its 4th use — at saturation per the post-30 checkpoint reuse budget (3-use ceiling). Soft flag for the reuse log: next plateau post must rotate to `patience-middle-checkin-20250731.jpg` or `weighin-middle-progress-20240801.jpg`.
- Inline `patience-middle-checkin-20250731.jpg` exists; lane B (honest proof). Anchored to "The plateau got smaller as the honesty got bigger." Anchor verbatim. Clean.
Feed fit: best published 2+ posts after `why-you-stop-losing-weight-around-month-three` (already in posts.ts) so the plateau lane does not stack. Sits well as the third post in the batch.
Suggested internal links: keep as-is. Both resolve.

---

## Draft 4 — progress-update-4-the-body-finally-stopped-being-the-loud-thing

```
slug: progress-update-4-the-body-finally-stopped-being-the-loud-thing
verdict: pass
claim_class: 2
title_collision: no
primary_keyword: weight loss progress update maintenance
keyword_collision: no
format: progress_update
checklist_failures: []
must_fix: []
voice_drift_flag: no
```

§13 milestone-post check — explicit:
- Real founder photos: **yes**. Hero `final-body.jpg` deploys the last unused-pool image flagged at the post-30 checkpoint priority list ("Use `/founder/final-body.jpg` for a milestone post (progress update #4 at approved-post ~60)"). Image verified on disk. Reserve fulfilled exactly as planned.
- Concrete numbers: **yes**. "Roughly 5 kg down from the last update. Total down from the highest is now around 50 kg." "Four sessions a week. Same lifts as the messy-middle update." "Sleep is averaging seven hours and twenty minutes for the past four weeks. Up from six and a half during the cut." "5 to 7 percent across the main movements" lift drop. "10 to 12 months" head-catch-up window. All concrete, all founder-rendered, none invented.
- Format `progress_update`: **5th distinct format used in the program**, first since post 35 (`progress-update-3-past-the-messy-middle`). Format rotation §12 satisfied.
- Class 2: **correct**. Personal experience only. No physiology mechanism is explained beyond surface description ("sleep going to bed forty minutes earlier without trying" is observation, not mechanism; "5 to 7 percent" lift drop is acknowledgement, not explanation; "the maintenance cost I was warned about and accepted" stays at experience-level). No hormone names. No prescriptive physiology claim. Class 3 floor not triggered. Class 4 escalation not needed.

Top 3 issues:
1. Strongest draft of the batch and likely the strongest progress-update in the program. The tonic line "I noticed I had stopped checking the mirror on the way out the door" is the share-card and the title's load-bearer in the same beat. The "what the numbers do not say" section ("The numbers describe a body. They do not describe the experience of being inside it.") is the kind of meta-numbers framing the previous progress updates earned but did not always land. This one lands.
2. The "What I would tell the version of me at update 1" section ("The middle is the entire program. The first month is novelty. The last month is photo material. Everything between is the actual work...") is the worldview-pillar restatement the milestone post needs to do without flattening into prescription. Holds. The three-thing structure could be perceived as soft list-scaffolding but the prose density inside each beat keeps it Q-and-A-of-the-self rather than bullet point.
3. The closing CTA paragraph ("Devenira was built for this phase as much as the cut phase, on the theory that the more boring the data gets, the more important it is to keep reading it.") is the most product-mention-restrained CTA of the batch — exactly right for a milestone post, which should not feel like a launch beat. Soft compliance with style_guide §CTA.

Repetition risk: low. Founder/progress category was opened at post 52 (`the-quiet-erosion-of-not-believing-your-progress`) and post 56 (`the-small-wins-between-progress-updates-are-the-real-program`). With this draft, the founder/progress count in the 10-post window 52–61 reaches **3** — exactly at the §11 max-3 ceiling. Batch 13 must rotate off founder/progress for at least 2 posts.
Voice drift: none. Anchor-grade. "Maintenance is not a sequel. It is a different format. The writing is going to follow that." is the program-direction beat that earns the milestone framing.
Engagement risk: low. Four share candidates: title line ("The body finally stopped being the loud thing."), "I noticed I had stopped checking the mirror on the way out the door.", "The numbers describe a body. They do not describe the experience of being inside it.", and "Maintenance is not a sequel. It is a different format."
SEO fixes:
- Meta description at ~166 chars — slightly over ceiling. Trim "Four months past the last update. The numbers moved less. The relationship moved more." to "Four months past the last update. Numbers moved less. The relationship moved more." (~158).
- Primary keyword "weight loss progress update maintenance" is honest. Slightly machine-flavored as a head-term but matches what someone searches when looking for milestone narratives. Acceptable.
- H2 "What this update is not" is the cleanest scannable anchor in the post and earns its placement.
Image / flow fixes:
- Hero `final-body.jpg` exists, deploys the last unused-pool asset, lane C (hard physique proof) — exact lane match for milestone / body transformation. 5-adjacent check vs posts 52–56 heroes: zero overlap. Clean.
- Inline `founder-story-hanok-20260119.jpg` exists; lane A (founder/credibility); anchored to "I noticed I had stopped checking the mirror on the way out the door." Anchor verbatim. Clean. This is also the hero for the post-1 founder-story article in posts.ts; using it as inline here makes a calm visual rhyme between founder origin and milestone arrival rather than a clash.
Feed fit: this is the milestone slot. Schedule at exactly approved-post 60 per plan §13. Should not be moved earlier or later in the publish order.
Suggested internal links: keep as-is. Both resolve. `progress-update-3-past-the-messy-middle` is the natural backward link; `the-quiet-erosion-of-not-believing-your-progress` is the natural in-batch sibling link.

---

## Draft 5 — clothes-tell-you-the-truth-the-mirror-cannot

```
slug: clothes-tell-you-the-truth-the-mirror-cannot
verdict: revise
claim_class: 3  (writer set 2 — undercalibrated)
title_collision: no
primary_keyword: clothes better than scale weight loss
keyword_collision: no
format: personal_story
checklist_failures: [8]
must_fix:
  - bump claim_class 2 → 3 per drift Rule 2. Body contains physiology numbers and a body-composition mechanism without hormone names: "A 1 cm change in waist is meaningful. A 1 kg change on the scale, by itself, is mostly water," "If you are training, you might be losing fat and adding small amounts of muscle simultaneously," "A bad-week scale jump of 1.5 kg," and "a Monday scale drop of 1 kg." Physiology numbers + recomposition mechanism → Class 3 floor regardless of hormone naming. Same pattern flagged in batch 11 draft 2 and batch 10 drafts 2 and 5.
```

Top 3 issues:
1. Claim class undercalibrated (see must_fix). This is the third consecutive batch carrying a Class 2 → 3 bump on a personal_story or myth_buster that touches scale-vs-water-vs-fat heuristics. The pattern is now stable: the writer's Class 2 default works for pure first-person posts (e.g. batch 11 draft 5, this batch's draft 4), but breaks the floor as soon as a recomposition number ("1 kg = mostly water") or composition mechanism ("losing fat and adding muscle simultaneously") enters. Notes addendum recommended for batch 13 prep.
2. The "What one pair of jeans taught me" section runs a six-week / twelve-week / eighteen-week / twenty-six-week / forty-week sequence in five short consecutive paragraphs. Reads as soft list-scaffolding — same shape as batch 11 draft 2's "Lighting / Posture / Time of day" sequence. The rescue line "The jeans had no opinion about my mood." (used twice as deliberate refrain) holds the founder voice. Borderline; keep, but flag the parallel-mini-paragraph pattern as an emerging fingerprint to watch in batch 13.
3. Strong founder-anchored beat at "I bought them about a month before the cut started. They were tight enough at the waist that I had to lie down to button them. I told myself they were aspirational." This is the personal-story payload the post needs. The closing pair ("The closet has been keeping a record the whole time. It just needs to be asked.") earns the title.

Repetition risk: low/medium. Body composition category was last directly opened at post 43 (`losing-weight-is-not-the-same-as-getting-leaner`) and at post 39 (`the-body-looks-different-from-behind`). Different angles — clothes-as-instrument is fresh. Mirror-lane framing overlaps with `progress-photos-can-lie-as-much-as-the-mirror-does` (post 53) and `you-look-different-to-other-people-before-yourself` (in posts.ts) — appropriate cluster, not redundant.
Voice drift: none. Anchor-grade. "The mirror is theatre. The scale is noise. The closet is the receipt." is the share-card and the strongest three-instrument framing of the batch.
Engagement risk: low. Three share candidates: closing instrument trio above, "The jeans had no opinion about my mood." (deliberate refrain — lands twice), and "Most flat-scale weeks are case one. The body moved. The scale missed it. The mirror argued about it. The clothes settled it in 30 seconds."
SEO fixes:
- Meta description on length (~158 chars). Clean.
- Primary keyword "clothes better than scale weight loss" is honest and uncrowded — solid query intent for the "is the scale lying" subgenre.
- H2 "What clothes catch that the scale misses" / "What clothes catch that the mirror misses" parallel pair is voice-true and good for skim. Keep.
Image / flow fixes:
- Hero `body-composition-proof-20251221.jpg` exists; lane C (hard physique proof) — exact lane match for body composition. Used as hero in posts.ts for `the-scale-can-say-normal-and-still-tell-you-nothing-useful`, `losing-weight-is-not-the-same-as-getting-leaner`, and `exercise-isnt-shrinking-you-the-way-you-expected`. This is its 4th use — at saturation per post-30 checkpoint 3-use ceiling. Soft flag for reuse log: next body-composition post must rotate to `transformation-proof-20251119.jpg` or `water-weight-proof-20251031.jpg`.
- Inline `scale-rude-before-20240130.jpg` exists; lane B (honest proof / before). Anchored to "The jeans had no opinion about my mood." Anchor verbatim. Clean.
Feed fit: companion to draft 4 of this batch (Progress Update #4) but should not publish adjacent — the milestone needs its own slot. Recommend post 61 lands at least 1 post after the milestone closes the founder/progress run.
Suggested internal links: keep as-is. Both `losing-weight-is-not-the-same-as-getting-leaner` and `the-same-number-on-the-scale-feels-different-at-30-than-at-20` resolve in posts.ts and anchor cleanly to the clothes-as-composition-instrument framing.

---

## Batch Summary

```
format_distribution: {deep_dive: 1, qa: 1, myth_buster: 1, progress_update: 1, personal_story: 1}
category_distribution: {maintenance: 1, appetite: 1, plateau/consistency: 1, founder/progress: 1, body composition: 1}
recurring_issue: claim_class undercalibration on physiology-numbers/composition-mechanism posts persists at 1 of 5 (draft 5). Holding at 1 of 5 for the second consecutive batch. Pattern is stable, not shrinking. Trigger remains: recomposition numbers ("1 kg is mostly water," "losing fat while adding muscle") in personal_story or myth_buster format.
overall_notes: >
  Strongest batch since batch 11 on format spread — all 5 formats represented in 5 posts
  (the first time in the program this has been achieved in a single batch). Voice
  recognizable across all 5 drafts. Progress Update #4 (draft 4) lands the milestone
  cleanly: real founder photo from the post-30 checkpoint reserve list, concrete numbers
  across weight / training / sleep / lift drop, Class 2 correctly held (no physiology
  mechanism dive), and the "I noticed I had stopped checking the mirror on the way out
  the door" beat is the strongest milestone tonic line in the program.
  Post-50 voice audit Q&A correction (rule 10) honored on draft 2: two founder-anchored
  Qs ("What did the night spike look like for me?" and "What worked for me, in plain
  terms?") plus the share-card sensory line "The day was a number. The evening was a
  person." Reader Address and Imagery Density both visibly above the post-50 audit floor.
  Second consecutive batch with rule 10 honored.
  Zero title collisions. Zero primary-keyword head-term collisions against the 49 ported
  slugs. All 5 hero and 5 inline image paths exist on disk. All 10 internal-link slugs
  (2 per draft) resolve in posts.ts. Banned phrase scan clean across all 5 drafts.
  Hormone noun-scan clean across all 5 drafts despite physiology-adjacent territory in
  drafts 1, 3, and 5. Class 4 escalations: none.
  One revise (draft 5, claim_class bump) and four pure passes. The revise pattern is now
  the same shape as batch 11 (draft 2) and batch 10 (drafts 2 and 5): personal_story or
  myth_buster touching recomposition heuristics, writer defaults to Class 2, reviewer
  bumps to Class 3.
  Format-rotation §12 satisfied: 56 personal_story → 57 deep_dive → 58 qa → 59 myth_buster
  → 60 progress_update → 61 personal_story. No 3-in-a-row. No consecutive same-format
  pairing.
  Category spread within the 47–61 window: maintenance 2, appetite 3 (at §11 ceiling),
  plateau 2, founder/progress 3 (at §11 ceiling), mirror 1, cheat/binge 1, scale 1, body
  composition 1, food 0, exercise/recovery 2. Two categories at ceiling — appetite and
  founder/progress must rotate off in batch 13.
  Reuse-budget pressure starting to show: `body-composition-proof-20251221.jpg` and
  `plateau-middle-checkin-20250711.jpg` both hit 4th use in this batch (over the 3-use
  soft ceiling from the post-30 checkpoint). Pool replenishment at the post-60 checkpoint
  is now the binding constraint on batch 13+ image variety.
```

### Drift Rule Scorecard (batch 12)

| # | Rule | Status |
|---|------|--------|
| 1 | Internal-link slug existence | clean (RESOLVED in batch 9; 4 consecutive clean batches now) |
| 2 | Claim class calibration (physiology floor + hormone noun-scan) | partial fail — draft 5 undercalibrated on the physiology-numbers/composition-mechanism floor (waist cm, water kg, fat-and-muscle simultaneously). Holding at 1 of 5 for the second consecutive batch (down from 2 of 5 in batch 10, holding from 1 of 5 in batch 11). Hormone noun-scan itself: clean across all 5 drafts. Pattern is stable, not shrinking. |
| 3 | Banned phrase keyword | clean (RESOLVED in batch 9; still clean — no banned phrases in any draft, including no meta-mention this batch) |
| 4 | Head-term keyword collision | clean (RESOLVED in batch 9; still clean — 0 of 5 collide with the 49 ported slugs) |
| 5 | Inline image variety within batch | clean (5 unique inlines: consistency-editorial, sleep-reflective-window, patience-middle-checkin, founder-story-hanok, scale-rude-before; zero overlap with batch 11 inlines; **`water-weight-proof-20251031.jpg` does NOT appear as inline in batch 12** — soft flag from batch 11 cleared. **3rd consecutive clean batch on rule 5 — RESOLVED.**) |
| 6 | Hero/inline image existence | clean (RESOLVED in batch 10; 3 consecutive clean batches now — eligible for full retirement) |
| 7 | Hunger-editorial hero rotation | clean — appetite post (draft 2) used `weighin-middle-progress-20240801.jpg` instead of `hunger-editorial-20260106.jpg`, honoring the post-30 saturation flag. Rule continues to hold under deliberate avoidance. |
| 8 | Hero/inline cross-role reuse within batch | clean (heroes: long-game-founder / weighin-middle-progress / plateau-middle-checkin / final-body / body-composition-proof; inlines: consistency-editorial / sleep-reflective-window / patience-middle-checkin / founder-story-hanok / scale-rude-before. Zero hero/inline overlap within batch.) |
| 9 | Hero/topic semantic mismatch via cover taxonomy | clean — 4 of 5 hero choices on-lane exact (long-game-founder=A for maintenance, plateau-middle-checkin=B for plateau, final-body=C for milestone/body-composition, body-composition-proof=C for body composition). Draft 2 hero `weighin-middle-progress-20240801.jpg` is a soft cross-lane match (lane B used for an appetite post that would prefer lane D), but defensible under reuse pressure (lane D options exhausted: hunger-editorial saturated, sleep-reflective-20260106 single-use, sleep-reflective-window deployed as the inline on this same draft). Hero alt acknowledges the bridge framing. **2nd consecutive clean batch on rule 9 — 1 more clean batch needed to resolve.** |
| 10 | Post-50 Q&A founder-I + sensory-line correction | clean — draft 2 is the only Q&A in the batch and meets both halves: 2 founder-anchored Qs ("What did the night spike look like for me?" and "What worked for me, in plain terms?") and multiple concrete sensory/metaphorical lines ("The day was a number. The evening was a person." / "white-knuckling on the couch with the TV up." / "Most night-hunger spikes are not psychological. They are scheduling problems wearing psychological clothes."). **2nd consecutive clean batch on rule 10 — 1 more clean batch needed to resolve.** |

Tracked: 10. Clean: 9. Partial fail: 1 (rule 2). New resolution this batch: rule 5 (inline image variety) — 3 consecutive clean batches achieved. Soft flags raised: cross-batch hero saturation on `body-composition-proof-20251221.jpg` and `plateau-middle-checkin-20250711.jpg` (both hit 4th use against the 3-use post-30 checkpoint ceiling).

### 5-Adjacent Hero Check vs Posts 52–56

- 52–56 heroes: `progress-update-hanok-20260119.jpg`, `mirror-middle-checkin-20250716.jpg`, `cheat-day-founder-20251221.jpg`, `scale-proof-20250919.jpg`, `final-portrait.jpg`
- 57–61 heroes: `long-game-founder-20251221.jpg`, `weighin-middle-progress-20240801.jpg`, `plateau-middle-checkin-20250711.jpg`, `final-body.jpg`, `body-composition-proof-20251221.jpg`
- Overlap check: **zero.** All five heroes in batch 12 are distinct files from all five heroes in batch 11. 5-adjacent rule: **satisfied.**
- Within-batch hero variety: 5 unique heroes across 5 drafts. Clean.

### Milestone Post Acknowledgment (Draft 4)

Progress Update #4 lands at approved-post 60 per plan §13 schedule. All §13 milestone requirements met:

- **Real founder photos**: `final-body.jpg` deploys the post-30 checkpoint reserve image specifically flagged for "milestone post (progress update #4 at approved-post ~60)". Reserve fulfilled exactly as the checkpoint planned.
- **Concrete numbers**: kg lost (5 since update 3, ~50 total from peak), training cadence (4 sessions/week), lift drop (5 to 7 percent across main movements), sleep avg (7h 20m up from 6h 30m), waist measurement steady at "the lowest sustainable" (not the absolute lowest). All real, all founder-rendered.
- **Format**: `progress_update`, the 5th distinct format used in the program in a single batch (first such batch in the run). First progress_update since post 35 (`progress-update-3-past-the-messy-middle`).
- **Class 2 (correct)**: Personal experience only. No physiology mechanism explained. No hormone names. Class 3 floor not triggered. Hormone noun-scan clean across the entire post despite naming maintenance / appetite / sleep / training territory.

Milestone post earns its slot. No revise needed.

### Reuse Budget Note

Per the post-30 checkpoint priority list, the 4 unused-pool deployments planned were:

1. `sleep-reflective-20260106.jpg` — deployed batch 10 draft 2 ✓
2. `start.jpg` — deployed batch 11 draft 2 inline ✓
3. `final-portrait.jpg` — deployed batch 11 draft 5 hero ✓
4. `final-body.jpg` — **deployed batch 12 draft 4 hero (this batch)** ✓ — reserved for Progress Update #4 per checkpoint, exact slot fulfilled.

**All 4 unused-pool images flagged at the post-30 checkpoint are now deployed.** Effective unused-pool count after batch 12: **0**.

Pool status at the post-60 checkpoint (due now per plan §16):

- Pool size: 22 images (unchanged since post-30 checkpoint).
- Used at least once: 22 of 22.
- At or above 3-use saturation ceiling: at minimum 4 images, including `body-composition-proof-20251221.jpg` (4 uses) and `plateau-middle-checkin-20250711.jpg` (4 uses) which both crossed the 3-use ceiling in this batch.
- Effective unused-pool: 0.

**Action flagged to writer:** Per plan §16 step 2, the post-60 checkpoint is now binding. New archive extraction is required before batch 13 close, or the 5-adjacent rule combined with the 3-use saturation ceiling will start producing forced cross-lane hero choices like the draft 2 lane-B-for-appetite borderline match seen this batch. If the archive at `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/` is now available in this worktree (it was missing at the post-30 checkpoint), re-extract and grow the pool before drafting batch 13.

Priority lanes still needing new assets, in order of binding pressure:

1. **Body composition / hard physique proof** — `body-composition-proof-20251221.jpg` at 4 uses, `transformation-proof-20251119.jpg` at 2+, `water-weight-proof-20251031.jpg` at 2+. Lane C is the most saturated.
2. **Plateau / honest middle (lane B)** — `plateau-middle-checkin-20250711.jpg` at 4 uses, no obvious replacement.
3. **Appetite / lifestyle (lane D)** — `hunger-editorial-20260106.jpg` at saturation, `sleep-reflective-*` series partially deployed; an asset purely for the hunger lane is missing.
4. **Maintenance** — `long-game-founder-20251221.jpg` is now the de facto sole maintenance hero; needs at least one alternate.

---

## Final Action Return

**Per-draft verdicts:**
1. `the-first-month-of-maintenance-feels-nothing-like-the-diet` → **pass** (Class 3, port as-is; trim meta to ~160 chars)
2. `why-does-my-hunger-spike-at-night-when-i-was-fine-all-day` → **pass** (Class 3, port as-is; rule 10 honored; soft note on hero lane bridge)
3. `the-plateau-that-was-actually-an-honesty-problem` → **pass** (Class 3, port as-is; trim meta to ~155 chars; hero at saturation, rotate next plateau post)
4. `progress-update-4-the-body-finally-stopped-being-the-loud-thing` → **pass** (Class 2, port as-is; §13 milestone fully met; final-body.jpg reserve deployed)
5. `clothes-tell-you-the-truth-the-mirror-cannot` → **revise** (bump claim_class 2 → 3 per drift rule 2; hero at saturation)

**Batch rule summary:** 9 of 10 drift rules clean. Rule 5 (inline image variety) **RESOLVED this batch** — 3 consecutive clean batches achieved (water-weight-proof cross-batch flag from batch 11 cleared by absence in batch 12). Rule 9 (hero/topic semantic match) and rule 10 (Q&A founder-I correction) both at 2 of 3 consecutive clean batches needed for resolution. Rule 2 (claim_class calibration) holds at 1 of 5 undercalibration for the second consecutive batch — pattern is stable, not shrinking. Cross-batch hero saturation flagged on `body-composition-proof-20251221.jpg` and `plateau-middle-checkin-20250711.jpg` (both at 4 uses against 3-use ceiling). Post-60 image pool checkpoint due — re-extraction strongly recommended before batch 13.

**Class 4 escalations needed:** none. Hormone noun-scan clean across all 5 drafts.

**Strongest / weakest:**
- **Strongest** is draft 4 (`progress-update-4-the-body-finally-stopped-being-the-loud-thing`) — the program's strongest progress_update to date. Real founder photo from the post-30 reserve list deployed exactly as planned, concrete numbers across all four required dimensions (weight / training cadence / lift drop / sleep), Class 2 correctly held against the temptation to dive into physiology, and the tonic line "I noticed I had stopped checking the mirror on the way out the door" is the cleanest milestone-as-behavioral-marker the program has produced. The closing "Maintenance is not a sequel. It is a different format. The writing is going to follow that." also signals the program's next direction without breaking voice.
- **Weakest** is draft 5 (`clothes-tell-you-the-truth-the-mirror-cannot`) — the only revise. Strong founder-anchored personal story with the closing share-card "The mirror is theatre. The scale is noise. The closet is the receipt.", but Class 2 undercalibration on physiology numbers ("1 kg is mostly water," "losing fat and adding muscle simultaneously") repeats the same pattern as batch 11 draft 2 and batch 10 drafts 2 and 5. The week-by-week jeans sequence (week 0 / 6 / 12 / 18 / 26 / 40) also leans toward the soft list-scaffolding shape that has been emerging across batches 10–12 in personal_story format. Voice rescues both — but the Class 3 bump is non-negotiable per drift rule 2.
