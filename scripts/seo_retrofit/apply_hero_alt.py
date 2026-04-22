#!/usr/bin/env python3
"""Apply rewritten heroAlt to posts.ts for all 64 posts."""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/hero_alt_spec.py"


def load_spec() -> dict[str, str]:
    spec_loader = importlib.util.spec_from_file_location("hero_alt_spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(spec_loader)
    spec_loader.loader.exec_module(mod)
    return mod.HERO_ALT


def js_string(s: str) -> str:
    if "'" in s and '"' not in s:
        return f'"{s}"'
    if "'" in s:
        return "'" + s.replace("'", "\\'") + "'"
    return f"'{s}'"


def update(text: str, slug: str, new_alt: str) -> tuple[str, str]:
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-not-found"
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    entry_end = next_slug_idx if next_slug_idx != -1 else len(text)
    entry = text[slug_idx:entry_end]

    pattern = re.compile(r"    heroAlt: (?P<q>['\"])(?P<val>.+?)(?P=q),")
    m = pattern.search(entry)
    if not m:
        return text, "no-heroAlt"
    if m.group("val") == new_alt:
        return text, "no-op"
    new_literal = js_string(new_alt)
    new_entry = pattern.sub(f"    heroAlt: {new_literal},", entry, count=1)
    return text[:slug_idx] + new_entry + text[entry_end:], "updated"


def main() -> int:
    spec = load_spec()
    print(f"Loaded {len(spec)} hero alt entries.\n")
    text = POSTS_TS.read_text(encoding="utf-8")
    stats = {"updated": 0, "no-op": 0, "slug-not-found": 0, "no-heroAlt": 0}
    for slug, alt in spec.items():
        text, status = update(text, slug, alt)
        stats[status] += 1
        print(f"[{status}] {slug}")
    POSTS_TS.write_text(text, encoding="utf-8")
    print(f"\n=== Summary ===\n{stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
