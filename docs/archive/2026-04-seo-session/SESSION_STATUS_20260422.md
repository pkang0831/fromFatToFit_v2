# Session Status — 2026-04-22 (paused at Tier 1 A)

## TL;DR

The session is **paused before any file edits** because the git/deploy
state needs human verification. Safe to resume once the two decisions
below are settled.

---

## Critical findings

### 1. Working tree has 5 uncommitted blog posts

| State | Where | Post count |
|---|---|---|
| Working tree (what you see in Cursor) | local files only | **~74** |
| `prodrepo-main` (local) = `v2/main` (remote) = `prodrepo/main` (remote) | last committed blog state | **69** |
| `v2/v2-main` (remote) | feature branch for body morph / mask editor | **0** (no blog folder) |
| HEAD (detached at `1f6ba52`) | "Port batch 9 drafts" | **39** |

The ~5 extra posts in your working tree exist **only on this machine,
only in this merged overlay.** They have never been committed. If this
workspace is deleted, they are gone.

### 2. The site you were looking at probably has 69 posts, not 74

You said "74 올라와있다" earlier. If `devenira.com/blog` deploys from
`v2/main` (the default branch on `v2` remote), the live site has
**69 posts**, not 74. The 5 extras are in this merge overlay only.

If you were looking at `localhost:3000/blog`, that's the working tree
and does show 74 — but that's local, not production.

### 3. Workspace is a manual merge-in-progress

`MERGE_NOTES_20260420.txt`:

```
Base:    GitHub fromFatToFit_v2 main @ 1f6ba524 (detached HEAD)
Overlay: local hhu-prodrepo-main @ 75d3abe + uncommitted local files
```

`git status` shows:
- Detached HEAD (not on any branch)
- 935 files staged as deleted (base files that the overlay removed)
- Entire working tree is "untracked" (overlay files not yet in index)

This is **not a normal working repo** — it's a scratchpad where
someone pasted two versions together with no commit yet.

### 4. `v2/v2-main` ≠ blog deploy source

You selected "v2/v2-main" as the deploy source. But `v2/v2-main` has
**zero blog content** — it's a feature branch for unrelated work
(`d856e07 feat: body morph, mask editor, segmentation lib`).

Most likely the actual deploy source is `v2/main` (default branch),
which has the 69 posts. Please verify in Vercel.

---

## Decisions needed from you

### A. Confirm Vercel deploy source

Open Vercel dashboard → Project → Settings → Git. Confirm:

1. Which **Git repository** is connected? (`fromFatToFit` or `fromFatToFit_v2`?)
2. Which **Production Branch** is set? (`main`, `v2-main`, etc.)
3. When was the last successful deploy, and what commit hash?

Paste the answer back here. This tells me where to push commits so
they reach devenira.com.

### B. Commit strategy for the merge

Option 1 — **Make this the new source of truth on `v2/main`**

```
# 1. Create a fresh branch from the overlay
git checkout -b merge/consolidate-20260422
# 2. Unstage the 935 deletions (they're artifacts of detached HEAD base)
git reset
# 3. Add everything in working tree
git add -A
# 4. Commit the consolidated state
git commit -m "Consolidate v2 main + local prodrepo merge (20260420 snapshot)"
# 5. Rebase/reset onto v2/main and push
git fetch v2
git branch -f v2-main-new v2/main  # start from current remote state
git checkout v2-main-new
# ... then cherry-pick or manually re-apply blog work on top
git push v2 v2-main-new:main
```

Option 2 — **Discard merge, start fresh on `v2/main`**

```
# 1. Check out the real branch
git fetch v2
git checkout -B v2-main v2/main
# 2. Redo the 5 new posts + other pending edits on top
# (this loses whatever overlay changes you don't manually copy)
```

Option 3 — **Only commit blog changes, ignore other merge artifacts**

```
# Only add the blog posts.ts and blog-related changes on top of v2/main
git fetch v2
git checkout -B blog/post-updates v2/main
git checkout HEAD -- frontend/src/content/blog/posts.ts  # nope, HEAD is 1f6ba52
# Actually need to save working tree first, then re-apply on clean base
```

**My recommendation**: **Option 1 variant** —
1. Save the current working tree to a tarball (`tar -czf ~/merge-snapshot.tar.gz .`)
2. Check out a new branch starting from `v2/main` (the actual deploy source)
3. Apply the blog changes from the snapshot to the clean branch
4. Commit there
5. Push to `v2/main` via PR

This keeps the deploy branch clean and gets the blog live.

---

## What was NOT changed in this session

Zero file edits to `posts.ts` or any blog content. Only two new files:

- `SESSION_PLAN.md` (session plan / source of truth)
- `SESSION_STATUS_20260422.md` (this file)

The working tree is exactly where you left it. Nothing to revert.

---

## Resume conditions

Once you confirm (A) deploy source and (B) commit strategy, I can
resume the plan from Tier 1 A onward. The rest of the plan
(`lastModified`, gap fills, schema, etc) is all valid — it's just
blocked on landing the blog on the correct branch first.

---

## Open questions for you

1. **Vercel production branch name** (from dashboard): ________
2. **Are you okay with Option 1 (commit to new branch, PR into
   `v2/main`)**, or do you want a different strategy?
3. **Is the `v2` remote (`github.com/pkang0831/fromFatToFit_v2`) the
   correct deploy repo**, or should we push elsewhere?

When you have answers, reply and we'll resume.
