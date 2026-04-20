# Program Checkpoints

Human (founder) decisions logged at plan-defined checkpoints (§13, §16, §20).

## Format
`date | checkpoint | decision | rationale | signed_off_by`

---

## 50-Post Checkpoint (§20)

| Date | Approved Count | Decision | Rationale | Signed Off |
|------|----------------|----------|-----------|------------|
| 2026-04-19 | 51 (post-batch-10) | **continue** | Voice recognizable across 51 posts (per batch 10 verdict: "Strongest batch since batch 7. Voice recognizable across all 5 drafts"). 7/9 drift rules clean and trending; only 3 active rules remain (claim class, inline variety, hero/topic match) — none structural. Anchor set held; no revision required at this checkpoint. Topic spread healthy in last 10-post window. Continue program as designed; proceed to batch 11. | founder (via "진행해" 2026-04-19) |

### Continue Path Conditions
- Anchor set NOT revised at this checkpoint
- Voice drift audit @ post 50 still required before batch 11 drafting begins (per §10)
- Next decision checkpoint: post 100 (program close-out) unless quality-floor pause (§21) triggers earlier

---

## 30-Post Image Pool Checkpoint (§16)

_(retroactive — handled inline at batch closures; no separate log entry needed)_

## 60-Post Image Pool Checkpoint (§16)

| Date | Approved Count | Status |
|------|----------------|--------|
| 2026-04-19 | 61 (post-batch-12) | **binding — archive extraction recommended before batch 13** |

### Pool Audit (post-batch-12)
- Total images in `frontend/public/founder/`: **22**
- Used as heroImage in posts.ts: **22 unique** (full pool deployed)
- All 4 unused-pool images flagged at post-30 checkpoint now deployed: `final-body.jpg` (post 60 — Progress Update #4), `final-portrait.jpg` (post 56), `sleep-reflective-20260106.jpg` (post 48), `start.jpg` (post 42)
- Heroes at 4-use saturation: 2 (per batch 12 reviewer flag)
- **Effective unused-pool: 0**

### Action Required (founder)
Per Plan §16 step 2 ("if <15 unused, trigger new archive extraction"), the pool is now far below threshold. Required before batch 13:
1. Re-extract from `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/` if archive is now present, OR
2. Add fresh photos to `frontend/public/founder/` covering priority lanes (per cover_mapping post-30 note): hunger/appetite, mirror/body image, exercise/training, maintenance
3. Update `blog_cover_mapping_2026-04-16.md` with new mappings

### Operational decision
If neither extraction nor new photos are available before batch 13, continue under tightened reuse budget — strict 5-adjacent rule + no image hits 5-use saturation, AND any image at 4 uses must skip its next 2 publish-eligible slots.

## Progress Update Milestones (§13)

| Approved Count | Post Slug | Status |
|----------------|-----------|--------|
| 20 | progress-update-2-the-body-changed-slower-than-my-head-did | done |
| 40 | progress-update-3-past-the-messy-middle | done |
| 60 | progress-update-4-the-body-finally-stopped-being-the-loud-thing | done (batch 12, hero `final-body.jpg` per post-30 reserve) |
| 80 | _TBD_ | future |
| 100 | _TBD_ | program close |

## Voice Drift Audits (§10)

| Approved Count | Audit File | Composite Score | Status |
|----------------|------------|-----------------|--------|
| 25 | reviews/voice_audit_25.md | _retroactively passed (no recorded composite; reviewer log clean)_ | informal |
| 50 | reviews/voice_audit_50.md | 8.38 (drift delta -1.08) | **PASS-WITH-CORRECTION** 2026-04-19 (Q&A subgenre correction logged in running_style_drift_notes.md) |
| 75 | reviews/voice_audit_75.md | 8.71 (drift delta -0.25) | **PASS (clean)** 2026-04-20 — first clean PASS since formal audits started; triggered EARLY pre-batch-15 per founder request (at post 71, not post 75). Rule 10 Q&A correction confirmed effective across batches 11-14 (4 consecutive clean cycles). No new drift rule added; watch-only note logged for Tier A deep_dive imagery density. |
| 100 | _TBD_ | _future_ | pending |
