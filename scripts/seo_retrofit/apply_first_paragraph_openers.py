#!/usr/bin/env python3
"""
Apply SEO opener rewrites to first paragraphs of:

- Medium publish packages (the markdown body inside ```md ... ``` block)
- posts.ts entries (sections[0].paragraphs[0])

Input: scripts/seo_retrofit/first_paragraph_openers_spec.py
       (a Python dict FIRST_PARAGRAPH_OPENERS keyed by slug → spec)

Each spec entry has:
  - package_basename
  - primary_keyword
  - current_first
  - opener
  - new_first  (== opener + " " + current_first)

Idempotent: skips already-rewritten posts (where the current first
paragraph already starts with the opener).
"""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/first_paragraph_openers_spec.py"


def load_spec() -> dict[str, dict]:
    spec_loader = importlib.util.spec_from_file_location("first_paragraph_openers_spec", SPEC_FILE)
    if not spec_loader or not spec_loader.loader:
        raise RuntimeError(f"Cannot load spec at {SPEC_FILE}")
    mod = importlib.util.module_from_spec(spec_loader)
    spec_loader.loader.exec_module(mod)
    return mod.FIRST_PARAGRAPH_OPENERS


def js_string(s: str) -> str:
    if "'" in s and '"' not in s:
        return f'"{s}"'
    if "'" in s:
        return "'" + s.replace("'", "\\'") + "'"
    return f"'{s}'"


REDIRECTS_JS = ROOT / "frontend/src/content/blog/redirects.js"


def _load_new_to_old() -> dict[str, str]:
    text = REDIRECTS_JS.read_text(encoding="utf-8")
    matches = re.findall(
        r"\{\s*from:\s*'([^']+)',\s*to:\s*'([^']+)'\s*\}",
        text,
    )
    return {to: frm for frm, to in matches}


_NEW_TO_OLD_SLUG = _load_new_to_old()


def slug_to_package_path(slug: str, basename_hint: str | None) -> Path | None:
    if basename_hint:
        candidate = MEDIUM_DIR / f"{basename_hint}_medium_manual_publish_package.md"
        if candidate.exists():
            return candidate
    # Try the NEW slug first.
    for path in MEDIUM_DIR.glob(f"*_{slug}_medium_manual_publish_package.md"):
        return path
    # Fall back to the OLD slug (Medium filenames weren't renamed).
    old_slug = _NEW_TO_OLD_SLUG.get(slug)
    if old_slug:
        for path in MEDIUM_DIR.glob(f"*_{old_slug}_medium_manual_publish_package.md"):
            return path
    # Last resort: any file containing either slug as substring.
    for path in MEDIUM_DIR.glob("*.md"):
        if slug in path.name or (old_slug and old_slug in path.name):
            return path
    return None


def update_medium_first_paragraph(path: Path, current_first: str, new_first: str) -> str:
    text = path.read_text(encoding="utf-8")
    if new_first in text:
        return "no-op"
    if current_first not in text:
        return "current-not-found"
    new_text = text.replace(current_first, new_first, 1)
    path.write_text(new_text, encoding="utf-8")
    return "updated"


def update_posts_ts_first_paragraph(text: str, slug: str, current_first: str, new_first: str) -> tuple[str, str]:
    """Replace the first paragraph string in the post entry's first
    paragraphs section."""
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-not-found"
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    entry_end = next_slug_idx if next_slug_idx != -1 else len(text)
    entry_text = text[slug_idx:entry_end]

    if new_first in entry_text:
        return text, "no-op"

    # Look for the current_first as a quoted string in the entry. The string
    # may use either ' or " quotes, and apostrophes inside may be escaped.
    candidates = [
        f"'{current_first}'",
        f'"{current_first}"',
        "'" + current_first.replace("'", "\\'") + "'",
    ]
    for candidate in candidates:
        if candidate in entry_text:
            new_literal = js_string(new_first)
            new_entry_text = entry_text.replace(candidate, new_literal, 1)
            return text[:slug_idx] + new_entry_text + text[entry_end:], "updated"

    return text, "current-not-found"


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"ERROR: spec file not found at {SPEC_FILE}")
        return 2
    spec = load_spec()
    print(f"Loaded {len(spec)} opener entries.\n")

    posts_text = POSTS_TS.read_text(encoding="utf-8")
    medium_stats = {"updated": 0, "no-op": 0, "current-not-found": 0, "missing-file": 0}
    posts_stats = {"updated": 0, "no-op": 0, "current-not-found": 0, "slug-not-found": 0}

    for slug, entry in spec.items():
        current_first = entry.get("current_first") or entry.get("current_first_paragraph")
        new_first = entry.get("new_first") or entry.get("new_first_paragraph")
        basename_hint = entry.get("package_basename")
        if not current_first or not new_first:
            print(f"[SKIP] {slug} — missing current_first or new_first")
            continue

        pkg_path = slug_to_package_path(slug, basename_hint)
        if pkg_path is None:
            print(f"[MEDIUM missing-file] {slug}")
            medium_stats["missing-file"] += 1
        else:
            ms = update_medium_first_paragraph(pkg_path, current_first, new_first)
            medium_stats[ms] += 1
            print(f"[MEDIUM {ms}] {pkg_path.name}")

        posts_text, ps = update_posts_ts_first_paragraph(posts_text, slug, current_first, new_first)
        posts_stats[ps] += 1
        print(f"  [POSTS {ps}] {slug}")

    POSTS_TS.write_text(posts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Medium packages: {medium_stats}")
    print(f"posts.ts entries: {posts_stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
