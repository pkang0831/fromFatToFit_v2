# 100-Post Program Plan (final, v4)

## 0. Current State
- 26 publish-ready drafts in `marketing/devenira_prelaunch/`
- 74 remaining to reach 100
- Existing 26 = retroactive batches 1–5 plus 1 carryover
- Next batch = batch 6, posts 27–31
- Writer = main Cursor AI agent. Reviewer = subagent launched per cycle.

## 1. Pre-Build Sanity Check (run once before batch 6 starts)
Writer confirms, before drafting batch 6:
- `reviewer_agent_spec.md` exists
- `style_guide.md`, `blog_post_blueprint.md`, `blog_cover_mapping_2026-04-16.md` exist
- `running_style_drift_notes.md` exists or gets created empty
- Medium package generator script exists; if missing, writer creates it before porting
- posts.ts slug list can be read
- Hero image pool count ≥ 15 unused
If any item missing, writer fixes first, then starts batch 6.

## 2. Roles
- Writer: drafts, applies revisions, updates notes, ports approved batches, commits
- Reviewer: audits per `reviewer_agent_spec.md`, returns verdict per schema
- Human (founder): Class 4 sign-off, 50-post checkpoint, quality-floor pause, unresolved conflict

## 3. Approval Definition
A draft is `approved` when one of:
- Verdict = `pass`
- Verdict = `revise`: writer applies fixes, self-certifies against checklist items, no re-review
- Verdict = `rewrite`: writer rewrites, reviewer re-reviews that single post; must land `pass` or `revise`

## 4. Reviewer Verdict Schema
Per draft:
```
slug: ...
verdict: pass | revise | rewrite
claim_class: 1 | 2 | 3 | 4
title_collision: yes | no
primary_keyword: <phrase>
keyword_collision: yes | no
format: personal_story | deep_dive | myth_buster | qa | progress_update
checklist_failures: [ids]
must_fix: [concrete actions]
voice_drift_flag: yes | no
```
Per batch:
```
format_distribution: {...}
category_distribution: {...}
recurring_issue: <string or null>
overall_notes: <string>
```

## 5. Reviewer Output Delivery
Reviewer subagent writes verdict to:
`marketing/fitness_blogging/blog_strategy/reviews/batch_<N>_verdict.md`
Writer reads that file to process. No response-only verdicts.

## 6. Batching and Cadence
- Standard batch size: 5
- Final batch size: last batch may be partial (size 4 for 100-post target; pattern: batches 6–19, with batch 19 = 4 posts)
- Writer drafts entire batch, then pauses, then triggers review
- One batch at a time

## 7. Port Policy
- Port at batch closure only (no per-draft porting)
- Closure requires all posts in batch `approved`
- If a post is parked due to unresolved conflict, that batch stays "pending-close" but next batch can still begin drafting
- Parked posts accumulate in `parked_posts.md`; human resolves in periodic sweeps; resolved posts port with next closed batch

## 8. Reviewer Independence
- Fresh subagent per cycle
- Reads only these paths:
  - reviewer_agent_spec.md
  - style_guide.md
  - blog_post_blueprint.md
  - blog_cover_mapping_2026-04-16.md
  - running_style_drift_notes.md
  - 5 current draft paths
  - last 10 approved draft paths (context only)
  - posts.ts slug list path
- Writer's reasoning is never passed
- Prompt template in Section 23

## 9. Writer-Reviewer Conflict Resolution
- Writer may dispute a verdict once per draft
- Dispute format: reason + proposed alternative + challenged checklist item
- Reviewer re-confirmation binding on writer
- If writer still disagrees: post parked per Section 7

## 10. Voice Drift Protection
- Anchor set: first 10 `approved` posts, locked after post 10 approval
- Anchor revision allowed only at 50-post checkpoint, requires human sign-off
- Audits at approved-post count 25, 50, 75, 100
- Audit method: reviewer samples 3 random anchor-set posts + 3 most-recent approved posts
- Voice consistency score 0–10 per dimension: sentence rhythm, worldview stance, reader-address, imagery density
- Composite <7 = writer updates notes with correction direction, next batch must reflect correction
- Running notes file: `marketing/fitness_blogging/blog_strategy/running_style_drift_notes.md`
- Entry format: `date | batch# | recurring_issue | correction_direction | resolved_batch#`
- Compression at post 50 and 100: resolved entries move to `## Archive` section in same file

## 11. Topic Spread
10 categories: scale, mirror, appetite, food structure, cheat/binge, plateau/consistency, exercise/recovery, body composition, maintenance, founder/progress.
- Max 3 posts per category within any 10-post window
- Min 5 posts per category by post 80
- New category allowed if reviewer flags saturation

## 12. Format Rotation
- 5 formats
- Max 2 consecutive same format
- Reviewer audits per batch

## 13. Milestone Posts
- Progress Update at approved-post count 20, 40, 60, 80, 100
- Real founder photos + concrete numbers

## 14. SEO and Internal Linking
- Writer greps existing titles + primary keywords before drafting
- Collision = rejected before reviewer
- Each new post: 2–3 outbound internal links to earlier posts
- Every existing post gets ≥1 inbound link by post 80
- Retroactive linking pass scheduled at post 40 and 80 (writer amends earlier approved posts to receive missing inbound links)
- Self-cannibalization check at audits

## 15. Claim Risk Classes
- Class 1: personal experience / subjective → AI sufficient
- Class 2: general wellness, no numbers → AI sufficient
- Class 3: behavioral science / nutrition heuristic with reasoning → AI sufficient
- Class 4: physiology / medical / hormonal / pharmacological / ED-adjacent → human sign-off before port

## 16. Image Pool Management
- No hero reused within 5 adjacent posts
- Hero per blog_cover_mapping taxonomy
- Expansion checkpoints at approved-post 30 and 60
- Checkpoint actions:
  1. count unused candidates
  2. if <15, trigger new archive extraction
  3. update cover mapping

## 17. Port Process (concrete steps at batch closure)
1. For each approved draft:
   - extract SEO title, description, primary keyword, body sections
   - pick hero from blog_cover_mapping (validate not reused in last 5)
   - add 2–3 internal links to earlier posts
2. Insert into posts.ts as new entry (top of array)
3. Generate Medium package via script → `marketing/fitness_blogging/blog_strategy/medium_launch/`
4. Commit: `Port batch N drafts to owned-site blog (posts X-Y)`
5. Every 2 closed batches: push to prodrepo/main

## 18. Reminder Expansion
- At approved-post 20, regenerate Calendar/Reminders for posts 20–40 via AppleScript
- Repeat at 40, 60, 80

## 19. Language
- English-first for 100
- Korean deferred to phase 2

## 20. 50-Post Checkpoint
- Triggered at 50 `approved`
- Human decision: continue / deepen / pivot
- Human unavailable >72 h: auto-pause, writer drafts phase-2 options doc
- Anchor set revision allowed here if warranted

## 21. Quality Floor
- 3 consecutive `rewrite` verdicts in a single batch or across 2 consecutive batches = automatic pause
- Pause: topic backlog redesign + human review

## 22. Writer Feedback Loop
- After review: writer updates running notes
- Before next batch: writer reads running notes
- Writer marks an entry `resolved` when 2 consecutive batches lack the issue

## 23. Reviewer Prompt Template
```
Role: You are the reviewer subagent defined in reviewer_agent_spec.md.

Read first:
- marketing/fitness_blogging/blog_strategy/reviewer_agent_spec.md
- marketing/fitness_blogging/blog_strategy/style_guide.md
- marketing/fitness_blogging/blog_strategy/blog_post_blueprint.md
- marketing/fitness_blogging/blog_strategy/blog_cover_mapping_2026-04-16.md
- marketing/fitness_blogging/blog_strategy/running_style_drift_notes.md

Review these 5 drafts:
- <path1> ... <path5>

Context only (do not review):
- last 10 approved draft paths (provided)
- posts.ts slug list (provided)

Return:
- Per-draft verdicts in the schema from Section 4 of 100_post_program_plan.md
- Per-batch summary in the schema from Section 4

Write the complete verdict to:
marketing/fitness_blogging/blog_strategy/reviews/batch_<N>_verdict.md

Flag all title/keyword collisions. Tag claim class per draft. Voice-drift flag if recurring issue across ≥2 drafts.
```

## 24. Failure Modes
- Reviewer resource-exhausted: retry once with 2-min backoff, then split batch 3+2
- Invalid reviewer format: re-run once with format reminder
- Persistent writer disagreement: post parked per Section 7
- Image exhaustion: pause drafting until expansion
- Running notes bloat: compressed at 50 and 100
- Anchor drift discovered mid-run: flagged at audit, revision only at 50-post checkpoint

## 25. Success Metrics
- 100 approved drafts
- No category saturation at any 10-post window
- Voice drift composite ≥7 at every audit
- 100% Medium package coverage
- 100% posts.ts port coverage
- ≥2 outbound internal links per post by post 80
- ≥1 inbound internal link per post by post 80

## 26. First Action (executed immediately after plan finalization)
1. Run Section 1 Pre-Build Sanity Check
2. Draft batch 6: posts 27–31
3. Trigger reviewer subagent via Section 23 template
4. Read verdict file, process per Section 3
5. Update running_style_drift_notes
6. Close batch: Section 17 port process
7. Proceed to batch 7
