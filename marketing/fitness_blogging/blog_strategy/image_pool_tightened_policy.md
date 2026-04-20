# Image Pool Tightened Reuse Policy (post-60 checkpoint)

Generated 2026-04-19 after the post-60 image checkpoint went binding (per `checkpoints.md` and Plan §16). All 4 unused-pool images flagged at the post-30 checkpoint are now deployed; no fresh archive extraction has happened yet.

This policy governs hero image selection for batch 13 onward, until either:
1. New photos are added to `frontend/public/founder/`, OR
2. The archive at `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/` is restored to the worktree

## Current Pool Status (as of post-batch-12 close)

- Total images: 22
- Use distribution: 3 images at 4 uses, 6 images at 3 uses, 11 images at 2 uses, 2 images at 1 use, 0 unused

### Retired (T1 5-use ceiling reached — cannot be used again as hero or inline)
- `long-game-founder-20251221.jpg` — retired after **batch 14 close** at 5-use (T1 ceiling).
- `body-composition-proof-20251221.jpg` — retired after **batch 15 close** at 5-use (T1 ceiling). Used as hero on post 73 (`why-lower-body-fat-feels-so-stubborn`, Tier A body-composition flagship), the single strongest lane-C match for a regional-clearance argument.

### 4-use saturation (must skip next 2 publish-eligible slots after each use)
- `plateau-middle-checkin-20250711.jpg` (last used post 59)

### 3-use approaching saturation
- `consistency-editorial-20251229.jpg`, `hunger-editorial-20260106.jpg`, `mirror-middle-checkin-20250716.jpg`, `patience-middle-checkin-20250731.jpg`, `progress-update-hanok-20260119.jpg`, `scale-proof-20250919.jpg`

### 1-use, prefer rotating in
- `final-body.jpg` (just used post 60 milestone — RESERVED for milestone slots only)
- `start.jpg` (last used post 42 as inline)

## Tightened Rules (effective batch 13)

### Rule T1 — Saturation cap
No image may exceed 5 uses across the program. Any image at 5 uses is retired from the hero pool until either retroactive consolidation or new photo additions reset budget.

### Rule T2 — 4-use skip-2 rule
When an image hits 4 uses, it must skip its next 2 publish-eligible slots before being eligible as hero again. ("Publish-eligible slots" = posts in subsequent batches; not counting the same batch's other slots.)

### Rule T3 — Lane balance preference
When two candidates are tied on use count and 5-adjacent eligibility, prefer the candidate whose taxonomy lane (A/B/C/D per `blog_cover_mapping_2026-04-16.md`) hasn't appeared in the last 3 hero slots.

### Rule T4 — Inline rotation
Inline images follow Rule 5 (intra-batch uniqueness, already RESOLVED) plus a soft preference for not reusing the same image as inline within 4 batches if alternatives exist.

### Rule T5 — Reserved slot honored
`final-body.jpg` is reserved for milestone posts only (Progress Update #4 already consumed one slot — it's now usable for Progress Update #5 at post 80, etc.).

## Batch 13 Pre-Cleared Hero Set (sample plan)

For posts 62–66, the following hero set satisfies all rules above and 5-adjacent vs posts 57–61:

| Slot | Hero | Current Use Count | Lane | Notes |
|------|------|-------------------|------|-------|
| 62 | `cheat-day-checkin-20250719.jpg` | 2 → 3 | B | Last used post 32. Cheat lane semantic match. |
| 63 | `founder-story-hanok-20260119.jpg` | 2 → 3 | A | Last used post 49. Soft for mirror/discipline. |
| 64 | `sleep-reflective-window-20241217.jpg` | 2 → 3 | D | Last used post 45. Lifestyle/routine fit. |
| 65 | `transformation-proof-20251119.jpg` | 2 → 3 | C | Last used post 42. Composition/exercise fit. |
| 66 | `scale-rude-before-20240130.jpg` | 2 → 3 | B | Last used post 30. Scale lane semantic match. |

Lane sequence: B-A-D-C-B — no 3-in-a-row, breaks the consecutive-B-lane risk.

After batch 13: 0 images at 4 uses → 0 images at 4 uses, 11 images at 3 uses, 6 images at 2 uses, 2 images at 1 use. Pool spread improves from 3-image-at-4-uses to 0-image-at-4-uses by promoting 5 of the 2-use images into the 3-use bucket. Healthier distribution.

## Decision Required Before Batch 14

If pool stays at 22 images: batch 14 will start consuming the 3-use pool, pushing several images to 4 uses. By batch 16 we hit the same saturation we just exited. **Founder must add new assets or restore archive before approved-post 80 (~batch 16).**

## Logged Audit

| Date | Approved Count | Pool Health | Action |
|------|----------------|-------------|--------|
| 2026-04-17 (post-30) | 30 | 4 unused | Operational continue |
| 2026-04-19 (post-60) | 61 | 0 unused, 3 at 4-use | **Tightened policy effective batch 13** |
| TBD (post-80) | 80 | TBD | Mandatory pool refresh point |


---

## Fallback Roadmap — No New Assets Through Batch 16

Generated post-batch-13 close (2026-04-19), assuming no founder photos are added before batch 16 (approved-post 80).

### Use distribution after batch 13 close

After batch 13's 5 hero deployments (cheat-day-checkin, founder-story-hanok, sleep-reflective-window, transformation-proof, scale-rude-before — each going from 2-use to 3-use), the pool is:

- 0 images at 4-use (the three that were at 4 are now in T2 skip-2)
- 11 images at 3-use
- 6 images at 2-use
- 2 images at 1-use (`final-body.jpg` reserved-for-milestones, `start.jpg`)

### Batch 14 (posts 67–71) projection

5 hero slots needed. Constraints:
- Avoid heroes from posts 62–66 (5-adjacent): cheat-day-checkin, founder-story-hanok, sleep-reflective-window, transformation-proof, scale-rude-before
- Rule T2: 4-use images (body-composition-proof, long-game-founder, plateau-middle-checkin) are still in skip-2 — they used post 57, 59, 61 respectively, so they're eligible again at posts 60, 62, 64. By batch 14 (67+), all three are eligible. They will go from 4-use to 5-use if used. **Per Rule T1, no image may exceed 5 uses.** They can be used at most 1 more time each across the entire program.
- Preferred order: 1-use (start) → 2-use (cheat-day-founder, diet-slip-checkin, final-portrait, sleep-reflective-20260106, water-weight-proof, weighin-middle-progress) → 3-use group last

Pre-cleared batch 14 hero set (preserves the strict-5 ceiling on 4-use images and uses no 4-use slots):

| Slot | Hero | Current Use → After | Lane |
|------|------|---------------------|------|
| 67 | `start.jpg` | 1 → 2 | A |
| 68 | `weighin-middle-progress-20240801.jpg` | 2 → 3 | B/D |
| 69 | `cheat-day-founder-20251221.jpg` | 2 → 3 | B |
| 70 | `diet-slip-checkin-20250725.jpg` | 2 → 3 | B |
| 71 | `final-portrait.jpg` | 2 → 3 | A |

After batch 14: 0 at 4-use, 16 at 3-use, 4 at 2-use, 0 at 1-use (start.jpg consumed).

### Batch 15 (posts 72–76) projection

By batch 15, almost the entire pool is at 3-use. To stay under T1 (5-use cap), the policy must use 4-use slots VERY sparingly.

Available 2-use heroes (4 left after batch 14): water-weight-proof, sleep-reflective-20260106, scale-proof (wait — scale-proof is at 3-use already after batch 11). Recheck: actually scale-proof = 3-use after batch 11. Updated remaining 2-use = `water-weight-proof-20251031.jpg`, `sleep-reflective-20260106.jpg`, `scale-rude-before-20240130.jpg` (already used batch 13 → now 3), and any others. Need to recompute live at the time.

Pre-cleared batch 15 hero set (will need re-verification at the time):

| Slot | Hero | Current Use → After | Lane |
|------|------|---------------------|------|
| 72 | `water-weight-proof-20251031.jpg` | 2 → 3 | B/C |
| 73 | `sleep-reflective-20260106.jpg` | 2 → 3 | D |
| 74 | `mirror-middle-checkin-20250716.jpg` | 3 → 4 | B |
| 75 | `consistency-editorial-20251229.jpg` | 3 → 4 | A |
| 76 | `progress-update-hanok-20260119.jpg` | 3 → 4 | A |

After batch 15: 3 at 4-use (newly: mirror-middle-checkin, consistency-editorial, progress-update-hanok), 13 at 3-use, 1 at 2-use, 0 at 1-use.

### Batch 16 (posts 77–81)

Approved-post 80 is the §16 mandatory checkpoint. Critical decision point:

**If founder has NOT added new assets by then**:
- Almost the entire pool is at 3-4 uses
- T2 (4-use skip-2) means 3 images that just hit 4 in batch 15 are in skip-2 for posts 77–78, 79–80, 80–81 respectively
- Available 3-use pool: ~10 images, all of which would push to 4-use after this batch
- Hero variety drops sharply
- **Recommendation: pause drafting at batch 16 or program-pause until founder adds new assets**

**If founder has added 5+ new assets by then**:
- Reset reuse budget for new images (start at 0-use)
- Cover_mapping update needed: assign new lanes
- Continue without policy tightening

### Critical action item for founder

**ESCALATED post-batch-15 (2026-04-20):** the post-80 mandatory pool refresh point is now **BINDING at batch 16 START**, not at batch 16 close as previously scoped. Batch 15's 8 simultaneous 3→4 use crossings (vs the policy file's pre-batch-15 forecast of 3 crossings) plus the second T1 retirement (`body-composition-proof-20251221.jpg`) means batch 16 starts under materially tighter hero availability than the fallback roadmap projected. Drafting batch 16 without new assets in hand will exhaust the 3-use bucket within the batch and force multiple defensible-but-soft lane-bridge hero assignments.

Add 5–8 founder photos to `frontend/public/founder/` covering these priority lanes (per `blog_cover_mapping_2026-04-16.md` post-30 note), in order of binding pressure:

1. **Body composition / hard physique proof (lane C)** — **MOST URGENT.** `body-composition-proof-20251221.jpg` retires after batch 15 close at 5-use. The lane is now down to `transformation-proof-20251119.jpg` (3-use) and `scale-proof-20250919.jpg` (4-use, in T2 skip-2 through batch 16). Batch 17's scheduled Tier A slot 83 is `thin-people-can-gain-weight-too-here-is-why-that-matters`, which also needs lane-C imagery — without a fresh lane-C asset by batch 17, that Tier A flagship will face the same T1-ceiling pressure that batch 15's lower-body post just absorbed.
2. **Maintenance (lane A)** — unchanged from batch 14 escalation. `long-game-founder-20251221.jpg` retired after batch 14; `final-portrait.jpg` is the sole remaining maintenance hero (at 3-use after batch 14, eligible for batch 16 but will hit 4-use immediately on use).
3. **Plateau / honest middle (lane B)** — `plateau-middle-checkin-20250711.jpg` held at 4-use through all of batches 13–15 by skip-2; still no obvious replacement. `patience-middle-checkin-20250731.jpg` and `mirror-middle-checkin-20250716.jpg` both crossed to 4-use in batch 15 and enter T2 skip-2 for batch 16.
4. **Hunger / appetite (lane D)** — `hunger-editorial-20260106.jpg` at 3-use saturation; still missing a pure hunger-lane asset.

Or restore the source archive at `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/` and re-extract per the 30-post checkpoint procedure.

### Logged Audit (continued)

| Date | Approved Count | Pool Health | Action |
|------|----------------|-------------|--------|
| 2026-04-19 (post-66, post-batch-13) | 66 | 0 at 4-use, 11 at 3-use, 6 at 2-use, 2 at 1-use | Fallback roadmap drafted; batch 14 pre-cleared without 4-use additions |
| TBD (post-71, post-batch-14) | 71 | 0 at 4-use, 16 at 3-use, 4 at 2-use, 0 at 1-use | start.jpg fully deployed; one round of T1 headroom remaining |
| 2026-04-20 (post-76, post-batch-15) | 76 | 2 retired, 9 at 4-use, ~9 at 3-use, ~2 at 2-use, 0 at 1-use | Actual pool tighter than forecast due to writer deviation on 4 of 5 pre-cleared slots; batch 16 pre-cleared plan needs re-verification. Post-80 mandatory refresh now BINDING at batch 16 start. |
| TBD (post-80, post-batch-16) | 80 | mathematically tight | **Mandatory founder action point** |
