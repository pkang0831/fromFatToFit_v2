#!/usr/bin/env python3
"""
Retrofit all wave_*_medium_manual_publish_package.md files with a new
"How to publish" section at the top that directs the user to use
Medium's Import-from-URL feature instead of copy-pasting the raw
markdown block. Reason: Medium's editor does not parse markdown, so
pasting the raw markdown leaves `##`, `#`, and `-` as literal
characters in the body, which destroys heading hierarchy and causes
Medium's feed algorithm to throttle the story (observed 2026-04-23
on wave_01_01 and wave_01_02 — 0 views).

The new top-of-file section:

  1. Recommends Import-from-URL workflow using the devenira.com slug
  2. Falls back to manual paste only if import fails
  3. Is explicit that copy-pasting the ```md block is the bug

Idempotent: skips files that already have the new section.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"

MARKER = "## How to publish on Medium (READ FIRST)"


def slug_from_filename(fn: str) -> str | None:
    """wave_XX_NN_<topic>_medium_manual_publish_package.md → best-guess slug.
    For wave_catchup_NNN files, the topic after the number IS the slug."""
    base = fn.replace("_medium_manual_publish_package.md", "")
    # wave_01_01_consistency -> maps to slug via spec file; we can't always guess.
    # Instead, just reference the devenira.com/blog path using a placeholder
    # and let the user swap in the actual slug from all_waves_tracker.
    # Simpler: extract the topic part after the NN_ prefix.
    parts = base.split("_")
    if len(parts) < 3:
        return None
    # wave / NN / NN or catchup / NNN / ...
    if parts[0] == "wave" and parts[1] == "catchup":
        topic_parts = parts[3:]
    elif parts[0] == "wave":
        topic_parts = parts[3:]
    else:
        return None
    return "-".join(topic_parts) if topic_parts else None


def patch_one(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return "already-patched"

    slug_guess = slug_from_filename(path.name)
    if not slug_guess:
        # Fall back to a placeholder
        slug_line = "`<the post's slug on devenira.com — find it in `frontend/src/content/blog/posts.ts`>`"
    else:
        # Use the guessed topic slug. This won't be 100% correct for every file
        # (wave_01_01_consistency → real slug "how-to-stick-to-a-diet-when-progress-slows"),
        # so we point the user at posts.ts as the source of truth.
        slug_line = (
            f"`{slug_guess}` — verify against `posts.ts` (the file name's "
            f"topic part is a hint, not always the exact slug)"
        )

    section = f"""{MARKER}

**DO NOT copy-paste the ```md block below into Medium's editor.**
Medium's editor does not parse markdown — `##`, `#`, `-`, and other
prefixes will appear as literal characters and destroy the heading
hierarchy. Observed 2026-04-23: wave_01_01 and wave_01_02 were
published this way and got 0 views because Medium's feed algorithm
throttles stories with no heading structure.

### Recommended workflow: Import from URL

1. In Medium: click your avatar → **Stories** → the "…" next to
   "Write a story" → **Import a story**. (Or visit
   https://medium.com/p/import directly.)
2. Paste the owned-site URL:
   `https://devenira.com/blog/{slug_guess or '<slug>'}` — exact
   slug is {slug_line}
3. Click **Import**. Medium converts the rendered HTML into its
   native format; H1/H2/lists/answerBox all transfer cleanly.
4. Before publishing:
   - Verify **Title** and **Subtitle** (they come from the page meta
     but may need the Medium-friendly versions — see **Title** and
     **Subtitle / Description** sections in this file).
   - Add the 5 **Medium Tags** from this file exactly.
   - Verify the **Cover image** is correct (it auto-pulls the hero
     webp from devenira.com).
   - **Canonical URL**: clear it per the canonical-flip policy
     below. Medium may auto-set it during import; clear the field
     in Story settings → SEO before publishing.
5. Publish.
6. Copy the new Medium URL → paste into `posts.ts` for the matching
   slug (the `mediumUrl:` field) → commit & push.

### Fallback: manual paste (only if import fails)

If Medium's importer rejects the URL (rare — only happens for posts
that haven't propagated to Vercel yet), use the markdown block below
but **manually convert each heading**:

- Every line starting with `# X` → delete the `# ` and apply Medium's
  **Large Heading** (T1) style
- Every line starting with `## X` → delete the `## ` and apply Medium's
  **Medium Heading** (T2) style
- Every line starting with `- X` → delete the `- ` and apply Medium's
  bulleted-list style
- `> X` blockquotes → delete `> ` and apply quote style

This is slow and error-prone. Prefer import whenever possible.

---

"""

    # Insert the new section right after the "# Medium Manual Publish Package"
    # title line (which is always at the top).
    m = re.match(r"(# Medium Manual Publish Package\n\n)", text)
    if not m:
        return "no-title-line"
    new_text = text[: m.end()] + section + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    return "patched"


def main() -> None:
    stats = {"patched": 0, "already-patched": 0, "no-title-line": 0}
    for path in sorted(PKG_DIR.glob("wave_*_medium_manual_publish_package.md")):
        status = patch_one(path)
        stats[status] += 1
        if status == "patched":
            print(f"[patched] {path.name}")
        elif status == "no-title-line":
            print(f"[NO-TITLE] {path.name}")
    print(f"\n=== Summary: {stats} ===")


if __name__ == "__main__":
    main()
