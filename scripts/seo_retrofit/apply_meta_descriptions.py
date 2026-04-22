#!/usr/bin/env python3
"""
Apply rewritten meta descriptions to Medium packages + posts.ts.

Input: scripts/seo_retrofit/meta_descriptions_spec.py
       (a Python dict META_DESCRIPTIONS keyed by slug → new metaDescription)

For each entry:
- Update `## Meta Description\\n<value>` block in the matching Medium package
- Update `metaDescription: '...'` in posts.ts entry

Idempotent.
"""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/meta_descriptions_spec.py"

# Slug → Medium package basename map. Built dynamically from posts.ts +
# Medium directory at runtime to handle both slug-derived and short-label
# package basenames.
#
# Important caveat (2026-04-21 slug rename): posts.ts now uses NEW slugs,
# but Medium package filenames still contain OLD slugs. We resolve by
# loading the redirects map (new → old) and looking up packages by old.

REDIRECTS_JS = ROOT / "frontend/src/content/blog/redirects.js"


def load_new_to_old_slug_map() -> dict[str, str]:
    """Parse redirects.js to build new_slug -> old_slug map."""
    text = REDIRECTS_JS.read_text(encoding="utf-8")
    matches = re.findall(
        r"\{\s*from:\s*'([^']+)',\s*to:\s*'([^']+)'\s*\}",
        text,
    )
    return {to: frm for frm, to in matches}


def load_spec() -> dict[str, str]:
    spec_path = SPEC_FILE.resolve()
    spec_loader = importlib.util.spec_from_file_location("meta_descriptions_spec", spec_path)
    if not spec_loader or not spec_loader.loader:
        raise RuntimeError(f"Cannot load spec at {spec_path}")
    mod = importlib.util.module_from_spec(spec_loader)
    spec_loader.loader.exec_module(mod)
    return mod.META_DESCRIPTIONS


def js_string(s: str) -> str:
    if "'" in s and '"' not in s:
        return f'"{s}"'
    if "'" in s:
        return "'" + s.replace("'", "\\'") + "'"
    return f"'{s}'"


_NEW_TO_OLD_SLUG = load_new_to_old_slug_map()


def slug_to_package_path(slug: str) -> Path | None:
    # Wave_01 + wave_02_01 short labels (no slug in basename).
    short_label_map = {
        "how-to-stick-to-a-diet-when-progress-slows": "wave_01_01_consistency",
        "how-i-lost-50-kg-middle-of-diet": "wave_01_02_founder_story",
        "why-cant-i-see-weight-loss-in-the-mirror": "wave_01_03_mirror",
        "should-i-weigh-myself-every-day-on-a-diet": "wave_01_04_weighin",
        "what-to-do-after-a-binge-on-a-diet": "wave_01_05_binge_repair",
        "are-cheat-days-bad-for-weight-loss": "wave_01_06_cheat_day",
        "why-is-my-appetite-stronger-on-a-diet": "wave_02_01_appetite_louder",
    }
    if slug in short_label_map:
        candidate = MEDIUM_DIR / f"{short_label_map[slug]}_medium_manual_publish_package.md"
        if candidate.exists():
            return candidate

    # Look up the OLD slug from redirects (Medium files still use old slugs).
    old_slug = _NEW_TO_OLD_SLUG.get(slug, slug)

    for path in MEDIUM_DIR.glob(f"*_{old_slug}_medium_manual_publish_package.md"):
        return path
    # Last resort: scan all files containing the slug substring.
    for path in MEDIUM_DIR.glob("*.md"):
        if old_slug in path.name or slug in path.name:
            return path
    return None


def update_medium_meta_description(path: Path, new_desc: str) -> str:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"^## Meta Description\n([^\n]+)$", re.MULTILINE)
    m = pattern.search(text)
    if not m:
        return "no-meta-block"
    if m.group(1).strip() == new_desc:
        return "no-op"
    new_text = pattern.sub(lambda _: f"## Meta Description\n{new_desc}", text, count=1)
    path.write_text(new_text, encoding="utf-8")
    return "updated"


def update_posts_ts_meta(text: str, slug: str, new_desc: str) -> tuple[str, str]:
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-not-found"
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    entry_end = next_slug_idx if next_slug_idx != -1 else len(text)
    entry_text = text[slug_idx:entry_end]

    # Match metaDescription:\n      '<val>',  (multi-line)
    pattern = re.compile(
        r"    metaDescription:\n\s+(?P<q>['\"])(?P<val>.+?)(?P=q),",
        re.DOTALL,
    )
    sm = pattern.search(entry_text)
    if not sm:
        return text, "meta-not-found"

    current_unescaped = sm.group("val").replace("\\'", "'").replace("\\n", "\n")
    if current_unescaped == new_desc:
        return text, "no-op"

    new_literal = js_string(new_desc)
    new_entry_text = pattern.sub(
        f"    metaDescription:\n      {new_literal},", entry_text, count=1
    )
    return text[:slug_idx] + new_entry_text + text[entry_end:], "updated"


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"ERROR: spec file not found at {SPEC_FILE}")
        return 2
    spec = load_spec()
    print(f"Loaded {len(spec)} meta description entries.\n")

    posts_text = POSTS_TS.read_text(encoding="utf-8")
    medium_stats = {"updated": 0, "no-op": 0, "no-meta-block": 0, "missing-file": 0}
    posts_stats = {"updated": 0, "no-op": 0, "slug-not-found": 0, "meta-not-found": 0}

    for slug, new_desc in spec.items():
        if not isinstance(new_desc, str) or len(new_desc) > 160:
            print(f"[WARN] {slug} — meta length {len(new_desc) if isinstance(new_desc, str) else '?'} > 160; skipping")
            continue

        pkg_path = slug_to_package_path(slug)
        if pkg_path is None:
            print(f"[MEDIUM missing-file] {slug}")
            medium_stats["missing-file"] += 1
        else:
            ms = update_medium_meta_description(pkg_path, new_desc)
            medium_stats[ms] += 1
            print(f"[MEDIUM {ms}] {pkg_path.name}")

        posts_text, ps = update_posts_ts_meta(posts_text, slug, new_desc)
        posts_stats[ps] += 1
        print(f"  [POSTS {ps}] {slug}")

    POSTS_TS.write_text(posts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Medium packages: {medium_stats}")
    print(f"posts.ts entries: {posts_stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
