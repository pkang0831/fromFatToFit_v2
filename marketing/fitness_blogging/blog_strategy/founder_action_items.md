# Founder Action Items (blocked on user)

Generated 2026-04-19 during post-batch-13 + cleanup pass. Items here cannot be resolved by the writing/reviewer pipeline; they require founder action on the founder's machine.

---

## 1. ⛔ Run `sudo xcodebuild -license` (blocks all `git` operations)

### Status
- All `git` commands in this worktree currently fail with `"You have not agreed to the Xcode license agreements"`
- Affects: status checks, diffs, commits, push to `prodrepo/main`
- The shell environment cannot execute `sudo` commands (requires interactive password prompt)

### Action
On founder's Mac, in any terminal:
```
sudo xcodebuild -license
```
Read and accept the license. Single one-time action; persists across future sessions.

### Effect after action
- `git status`, `git log`, `git diff` work in this worktree
- Push to `prodrepo/main` becomes possible
- All future agent sessions in this worktree can use `git` normally

### Backlog this unblocks
- Per Plan §17, push to `prodrepo/main` is due (4 batches closed without push: 10, 11, 12, 13). One push catches all of them up.

---

## 2. ⛔ Run AppleScript files for publishing reminders (Mac Calendar/Reminders permissions)

### Status
- Three AppleScript files prepared and verified:
  - `marketing/fitness_blogging/blog_strategy/schedule/setup_reminders_20260417.applescript` (posts 1–19)
  - `marketing/fitness_blogging/blog_strategy/schedule/setup_reminders_posts_30_44.applescript` (posts 20–34)
  - `marketing/fitness_blogging/blog_strategy/schedule/setup_reminders_posts_45_54.applescript` (posts 35–54)
- Cannot be run from agent shell (require Calendar / Reminders system permissions on Mac)

### Action
On founder's Mac:
```
osascript marketing/fitness_blogging/blog_strategy/schedule/setup_reminders_posts_45_54.applescript
```
First-run will prompt for Calendar + Reminders permissions; grant both. Re-running produces idempotent additions (same calendar/list re-used; new events/reminders added).

If Calendar/Reminders has stale entries from prior runs, manually delete the duplicates first.

### Effect after action
- Calendar `Devenira Blog` contains publish events for all 54 posts at 09:00 KST
- Reminders list `Devenira Blog` contains daily 08:00 KST reminders for each
- Founder gets daily reminders to publish to Medium + share to SNS

### Future
A new AppleScript will need to be generated after each batch closes to extend coverage. The pattern is established (`setup_reminders_posts_NN_MM.applescript`).

---

## 3. ⛔ Founder photo assets — image pool saturation by batch 16

### Status
- Pool currently at 22 images; 0 unused; 3 at 4-use saturation; 11 at 3-use
- Per `image_pool_tightened_policy.md` fallback roadmap: pool can absorb batches 14 and 15 without policy violation
- **Batch 16 (approved-post 80) is the binding decision point**

### Action
Choose ONE option before drafting batch 16:

#### Option A — Restore archive
Re-create the path `marketing/fitness_blogging/my_past_photos/extracted_fresh_20260416/Takeout/Google Photos/` in the worktree, populated with the founder photo archive. The agent can then re-extract per the post-30 checkpoint procedure (typically yields 5–8 fresh assets).

#### Option B — Add new photos directly
Drop 5–8 new founder photos into `frontend/public/founder/`. Priority lanes (per `blog_cover_mapping_2026-04-16.md` post-30 note):

1. Hunger / appetite
2. Mirror / body image
3. Exercise / training session
4. Maintenance

After adding, the agent can update `blog_cover_mapping_2026-04-16.md` with new lane mappings.

#### Option C — Pause program at batch 15 close (post-76)
If neither A nor B is feasible by post-76, the program can pause at that point. The 24 posts produced in batches 14–15 keep momentum; resume later when assets are available.

### Cost of doing nothing
By batch 16, the math forces 4 of 5 hero slots into 4-use → 5-use territory; Rule T1 caps at 5-use. Cannot be drafted without rule violation.

---

## 4. 🟡 Tier C draft — `already_thin_still_want_to_diet_publish_ready_TIER_C_HOLD.md`

### Status
- ED-adjacent topic ("I'm already thin but I still want to diet")
- Currently in `marketing/devenira_prelaunch/_archive_pre_blueprint/` with `_TIER_C_HOLD.md` suffix
- Plan §15 Class 4 = human (founder) sign-off required before any port

### Action (only if founder wants this topic published)
Read the old draft. Decide:

- **Approve** (would publish, with current voice rewrite) → Schedule into a future batch with explicit Class 4 tag in `parked_posts.md` Class 4 Sign-off Log
- **Decline** (do not publish in any form) → Move to a permanent `_do_not_publish/` subdirectory; close the loop
- **Defer** (revisit at 75-post or 100-post checkpoint) → Leave as-is in archive

If Approve, the rewrite is heavier than Tier A rewrites — body image / disorder territory needs careful framing. Recommend pairing with a content-warning consideration.

---

## 5. 🟡 50-post checkpoint anchor revision (already declined per `checkpoints.md`)

Already decided "no revision" via founder "진행해" 2026-04-19. No further action needed unless the post-75 voice audit (auto-triggered after batch 15) recommends otherwise.

---

## Summary Table

| Item | Type | Time Cost | Frequency |
|------|------|-----------|-----------|
| 1. Xcode license | one-time | 30 sec | once |
| 2. AppleScript run | per-batch-pair | 10 sec | every ~2 batches |
| 3. Photo assets | one-time + audit | 30 min – 2 hr | once before batch 16 |
| 4. Tier C decision | one-time | 5 min reading + decision | one-time decision |

The first three are blockers for downstream agent work. The fourth is optional editorial.
