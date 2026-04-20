# Voice Drift Audit — Approved-Post 50

Date: 2026-04-19
Auditor: reviewer subagent per `reviewer_agent_spec.md` + plan §10
Approved-post count: 51 (post-batch-10 close)
Sampling seed: deterministic from date 2026-04-19. Index seed = 9 (last digit of date), then step +3 mod 10 twice → indices {9, 2, 7} (1-indexed) applied identically to both pools to keep selection symmetric across pools and avoid cherry-picking strong/weak posts.

## Sampled Posts

### Anchor Set (3 of 10)
- why-it-feels-like-you-gain-weight-even-when-you-barely-eat (anchor #9)
- why-i-built-devenira-for-the-weeks-where-you-want-to-quit (anchor #2)
- why-appetite-feels-stronger-the-longer-you-diet (anchor #7)

### Recent Set (3 of 10, posts 42–51)
- why-your-workouts-feel-harder-when-youre-dieting (recent #9, post 50)
- losing-weight-is-not-the-same-as-getting-leaner (recent #2, post 43)
- am-i-actually-hungry-or-am-i-bored (recent #7, post 48)

## Per-Post Scores

| Slug | Pool | Rhythm | Worldview | Address | Imagery | Composite |
|------|------|--------|-----------|---------|---------|-----------|
| why-i-built-devenira-for-the-weeks-where-you-want-to-quit | anchor | 9.0 | 9.0 | 9.0 | 8.0 | 8.75 |
| why-it-feels-like-you-gain-weight-even-when-you-barely-eat | anchor | 9.0 | 9.0 | 9.0 | 9.0 | 9.00 |
| why-appetite-feels-stronger-the-longer-you-diet | anchor | 9.0 | 9.0 | 9.0 | 9.0 | 9.00 |
| losing-weight-is-not-the-same-as-getting-leaner | recent | 9.0 | 9.0 | 9.0 | 8.0 | 8.75 |
| am-i-actually-hungry-or-am-i-bored | recent | 8.0 | 9.0 | 7.0 | 7.0 | 7.75 |
| why-your-workouts-feel-harder-when-youre-dieting | recent | 8.0 | 8.0 | 6.0 | 6.0 | 7.00 |

## Pool Averages

- Anchor pool composite: 8.92
- Recent pool composite: 7.83
- **Program composite: 8.38**
- **Drift delta: −1.08**

## Per-Dimension Drift Analysis

### Sentence rhythm
Mild drift (anchor 9.0 → recent 8.33). Anchor posts and the non-Q&A recent (`losing-weight-is-not-the-same-as-getting-leaner`) keep the staccato signature ("Looser around the waist. Tighter around the shoulders. The same number. A different body."). The two recent Q&A posts hold rhythm inside paragraphs ("This is not weakness. This is an arithmetic problem. The fuel is different. The session is not.") but the bracketing `Q:` headers + frequent bullet-lists chop the 1-thought-per-paragraph cadence into something closer to FAQ pacing. Not a serious break, but visible.

### Worldview stance
Essentially flat (anchor 9.0 → recent 8.67). The recent pool still hits the load-bearing pillars: scale not neutral (`losing-weight...`), systems > willpower (`am-i-actually-hungry...` — "Noticing... without self-flagellating, is the entire skill"), body slow / head fast (`why-your-workouts-feel-harder...` — "Pay it, do not fight it"). One soft point in `why-your-workouts-feel-harder...` where the prescriptive section ("Keep the big lifts. Reduce total volume. Drop the junk.") leans closer to coaching than to founder observation, but stance is not abandoned.

### Reader address
This is the strongest drift dimension (anchor 9.0 → recent 7.33). Anchor posts hold a 1:1 ratio of first-person observation to second-person address ("I did not build Devenira because AI is interesting." / "Let me be fair before I get more specific."). The two recent Q&A posts almost entirely vacate the founder "I" — `why-your-workouts-feel-harder...` contains zero first-person founder anchoring across the entire body, and `am-i-actually-hungry...` only one passing reference. The "you" rate climbs because Q&A naturally addresses the reader, but the calibration warning in style_guide §"Reader Address" ("you sparingly, for key hits") is no longer being respected inside the Q&A subgenre.

Anchor example: "I did not need another quote. I did not need another calorie target. I did not need another app trying to be everything at once. I needed better evidence." (founder-anchored, observational-before-prescriptive)

Recent example: "Keep the big lifts. Squats, deadlifts, presses, rows, pull-ups — keep doing them at reasonable intensities." (no founder, pure prescription)

### Imagery density
Real drift (anchor 8.67 → recent 7.0). Anchor pool is dense with concrete sensory and metaphorical anchors: "panic wearing activewear", "security footage", "ordinary food can start glowing like forbidden treasure", "freedom, revenge, and a tiny vacation from the personality you have been forced to perform all week." The non-Q&A recent post still carries one concrete anchor ("Looser around the waist. Tighter around the shoulders."). The two Q&A recent posts trade sensory anchors for numbers and bullet checklists — `why-your-workouts-feel-harder...` substitutes "5 to 10 percent", "200 to 400 more calories", "2 to 3 low-intensity sessions a week" where an earlier post would have given a felt observation. The mechanism is more accurate; the imagery is thinner.

## Recurring Issues (program-wide)

Cross-checked against `running_style_drift_notes.md` Active list (claim-class calibration, inline image variety, hero/topic semantic match):

- None of those three active drift rules show up in the sampled posts as a voice-level issue. They are production-pipeline drifts, not voice drifts.
- The voice-level drift this audit surfaces is **format-specific**, not program-wide: the Q&A format is currently underperforming on `Reader Address` and `Imagery Density` relative to anchor voice. Personal-story and mechanism-explainer formats in the recent pool still hold anchor-grade voice (see `losing-weight-is-not-the-same-as-getting-leaner` at 8.75).

## Verdict

**PASS-WITH-CORRECTION**

Rationale: Program composite 8.38 sits comfortably above the §10 quality floor of 7.0, and four of the six sampled posts score ≥ 8.75 — voice is recognizably pkang across 51 posts. However, drift delta of −1.08 crosses the §10 −1.0 threshold, driven entirely by the two Q&A-format posts in the recent pool (`am-i-actually-hungry-or-am-i-bored`, `why-your-workouts-feel-harder-when-youre-dieting`). Both lose the founder "I" almost completely and substitute numbers/bullet prescriptions where anchor posts would have placed a concrete sensory or emotional image. The fix is targeted (Q&A subgenre only), not structural — anchor voice is otherwise intact.

## Correction Direction

`2026-04-19 | post_50_audit | Q&A-format posts drop founder-I and substitute mechanism numbers for sensory imagery, dragging Reader Address and Imagery Density ~2 points below anchor | every Q&A post must include at least one founder-anchored Q (first-person observation, not prescription) and at least one concrete sensory/metaphorical line replacing a bullet-list mechanism; if the Q&A would otherwise contain zero "I", reframe one Q as "Q: What did this look like for me?" | _open_`

## Anchor Set Revision Recommendation

- Recommend revision: **no**
- Per §20, anchor revision is allowed at this checkpoint with founder sign-off, but the audit does not justify it. The anchor pool sample averaged 8.92 with no post below 8.75. The voice drift is happening in the recent pool's Q&A subgenre, not in the anchor pool's representativeness. Replacing anchor posts now would mask the real signal (Q&A format underperformance) rather than correct it. Founder has already signed off on "no revision required" in `checkpoints.md`; this audit confirms that call.

## Next Audit

Approved-post 75 (after batch 15 closes, est. 2026-05-XX).
