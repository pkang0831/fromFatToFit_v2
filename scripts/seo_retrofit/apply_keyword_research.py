#!/usr/bin/env python3
"""
Apply the 2026-04-21 keyword research to all 64 posts.

Input:  marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md
Output: Medium packages + posts.ts updated with new primary/secondary keywords.

For each post the research file contains:

    ### Post: <basename-without-.md>
    Current primary: ...
    Current secondary: ...

    Decision: KEEP | REFINE | REPLACE | NOT RANKABLE

    New primary: ...
    New secondary:
    - ...
    - ...

We extract (basename, new_primary, new_secondary) for every block, then:

1. In each Medium package file: replace the `## Primary Keyword\n<value>`
   block and the `## Secondary Keywords\n- a\n- b\n...` block.
2. In posts.ts: replace the `keywords: [...]` array with the new primary +
   secondaries, preserving the slug association via the cluster map.

Idempotent: re-running is safe. If the new primary already matches the
existing primary keyword, we skip that post's updates.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_FILE = ROOT / "marketing/fitness_blogging/blog_strategy/seo_keyword_research_2026-04-21.md"
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"


def parse_research() -> list[dict]:
    """Parse the research markdown into a list of per-post specs."""
    text = RESEARCH_FILE.read_text(encoding="utf-8")
    # Stop parsing at "## Posts marked NOT RANKABLE" / "## Cannibalization map" / "## Summary"
    # because the summary section may re-use `### Post:` labels in table form.
    cutoff = text.find("\n## Posts marked NOT RANKABLE")
    if cutoff == -1:
        cutoff = text.find("\n## Cannibalization map")
    if cutoff == -1:
        cutoff = text.find("\n## Summary")
    body = text[:cutoff] if cutoff != -1 else text

    # Split into blocks that start with "### Post:".
    blocks = re.split(r"(?m)^### Post: ", body)[1:]  # first chunk is preamble

    results: list[dict] = []
    for raw in blocks:
        # First line is the basename. Read until the next blank-line or `---`.
        m = re.match(
            r"(?P<basename>[^\n]+)\n"
            r"Current primary: (?P<cur_primary>[^\n]+)\n"
            r"Current secondary: (?P<cur_secondary>[^\n]+)\n"
            r"\n"
            r"Decision: (?P<decision>[^\n]+)\n"
            r"\n"
            r"New primary: (?P<new_primary>[^\n]+)\n"
            r"New secondary:\n"
            r"(?P<new_secondary_block>(?:- [^\n]+\n)+)",
            raw,
        )
        if not m:
            # Some NOT-RANKABLE entries may not have New primary / New secondary;
            # in that case we skip them. The summary tables are parsed separately if needed.
            continue

        basename = m.group("basename").strip()
        decision = m.group("decision").strip()
        new_primary = m.group("new_primary").strip()
        new_secondaries = [
            line[2:].strip()
            for line in m.group("new_secondary_block").splitlines()
            if line.startswith("- ")
        ]

        results.append(
            {
                "basename": basename,
                "decision": decision,
                "new_primary": new_primary,
                "new_secondary": new_secondaries,
            }
        )

    return results


# --- Medium package update ----------------------------------------------------

PKG_PRIMARY_RE = re.compile(
    r"(## Primary Keyword\n)(?P<val>[^\n]+)(\n)",
    re.MULTILINE,
)

PKG_SECONDARY_RE = re.compile(
    r"(## Secondary Keywords\n)(?P<list>(?:- [^\n]+\n)+)",
    re.MULTILINE,
)


def update_medium_package(path: Path, new_primary: str, new_secondary: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    changed = False

    # Primary keyword.
    m = PKG_PRIMARY_RE.search(text)
    if m:
        current = m.group("val").strip()
        if current != new_primary:
            text = PKG_PRIMARY_RE.sub(lambda _: f"## Primary Keyword\n{new_primary}\n", text, count=1)
            changed = True
    else:
        return "no-primary-block"

    # Secondary keywords.
    m = PKG_SECONDARY_RE.search(text)
    if m:
        current_block = m.group("list")
        new_block = "".join(f"- {kw}\n" for kw in new_secondary)
        if current_block != new_block:
            text = PKG_SECONDARY_RE.sub(lambda _: f"## Secondary Keywords\n{new_block}", text, count=1)
            changed = True
    else:
        return "no-secondary-block"

    if not changed:
        return "no-op"

    path.write_text(text, encoding="utf-8")
    return "updated"


# --- posts.ts update ----------------------------------------------------------

# Basename → slug inference by suffix ("..._package" prefix removed, handles both naming schemes).
# The research file uses Medium package basenames; posts.ts uses slugs.
# We load the mapping from posts.ts first (which has all 64 slugs) and match
# basename endings.


def resolve_package_path(basename: str) -> Path | None:
    """Given a basename from the research file (which may or may not end with
    `_medium_manual_publish_package`), return the actual file path if it exists.
    """
    candidates = [
        MEDIUM_DIR / f"{basename}.md",
        MEDIUM_DIR / f"{basename}_medium_manual_publish_package.md",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# Hardcoded map for packages whose basenames are short thematic labels and
# don't contain the slug (wave_01 and wave_02_01).
WAVE_01_MAP = {
    "wave_01_01_consistency": "the-most-reliable-way-to-succeed-at-dieting-is-still-the-least-dramatic-one",
    "wave_01_02_founder_story": "why-i-built-devenira-for-the-weeks-where-you-want-to-quit",
    "wave_01_03_mirror": "why-the-mirror-can-make-real-progress-feel-fake",
    "wave_01_04_weighin": "one-emotional-weigh-in-can-wreck-a-good-week",
    "wave_01_05_binge_repair": "read-this-before-you-try-to-fix-your-diet-slip",
    "wave_01_06_cheat_day": "cheat-days-do-not-expose-your-character-they-expose-your-system",
    "wave_02_01_appetite_louder": "why-appetite-feels-stronger-the-longer-you-diet",
}


def basename_to_slug(basename: str, all_slugs: list[str]) -> str | None:
    """Match a package basename to a posts.ts slug.

    The research file uses two conventions inconsistently:
    - full: `wave_02_03_<slug>_medium_manual_publish_package`
    - short: `wave_02_03_<slug>`
    And wave_01_* uses short thematic labels ("consistency", "founder_story")
    that don't contain the slug at all.
    """
    # Normalize: strip the suffix if present.
    normalized = basename.removesuffix("_medium_manual_publish_package")

    # Try wave_01 lookup first.
    if normalized in WAVE_01_MAP:
        return WAVE_01_MAP[normalized]

    # For wave_02 / wave_03 / wave_catchup, the slug is everything after the
    # "wave_XX_NN_" prefix (where XX is 02|03|catchup and NN is a number).
    m = re.match(r"^wave_(?:0[23]|catchup)_\d+_(?P<slug>.+)$", normalized)
    if m:
        candidate = m.group("slug")
        if candidate in all_slugs:
            return candidate

    return None


def js_string(s: str) -> str:
    """Render a Python string as a JS single- or double-quoted literal preserving apostrophes."""
    if "'" in s and '"' not in s:
        return f'"{s}"'
    if "'" in s:
        return "'" + s.replace("'", "\\'") + "'"
    return f"'{s}'"


def update_posts_ts_keywords(text: str, slug: str, new_primary: str, new_secondary: list[str]) -> tuple[str, str]:
    """Replace the keywords: [...] array for a given slug.

    Two-step scan (avoids pathological regex backtracking on 6000-line files):
    1. Locate the slug line.
    2. From that offset, search forward line-by-line for `    keywords: [`
       and then for the matching `    ],` terminator.
    """
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-or-keywords-not-found"

    keywords_marker = "    keywords: ["
    kw_start = text.find(keywords_marker, slug_idx)
    if kw_start == -1:
        return text, "slug-or-keywords-not-found"

    # Stop looking for keywords if we've already passed the next slug line;
    # that would mean THIS slug's entry doesn't have a keywords block.
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    if next_slug_idx != -1 and kw_start > next_slug_idx:
        return text, "slug-or-keywords-not-found"

    # Find the closing `    ],` for this keywords array.
    term = text.find("\n    ],", kw_start)
    if term == -1:
        return text, "slug-or-keywords-not-found"
    # The full old block spans from kw_start to end of `    ],\n`.
    block_end = term + len("\n    ],\n")

    # Compose new block.
    new_lines = [f"      {js_string(kw)}" for kw in [new_primary, *new_secondary]]
    new_block = keywords_marker + "\n" + ",\n".join(new_lines) + ",\n    ],\n"

    if text[kw_start:block_end] == new_block:
        return text, "no-op"

    new_text = text[:kw_start] + new_block + text[block_end:]
    return new_text, "updated"


def main() -> int:
    specs = parse_research()
    print(f"Parsed {len(specs)} per-post specs from research file.\n")

    # Load posts.ts once for slug inference.
    posts_ts_text = POSTS_TS.read_text(encoding="utf-8")
    all_slugs = re.findall(r"    slug: '([^']+)',", posts_ts_text)
    print(f"posts.ts contains {len(all_slugs)} slugs.\n")

    medium_stats = {"updated": 0, "no-op": 0, "missing-file": 0, "no-primary-block": 0, "no-secondary-block": 0}
    posts_stats = {"updated": 0, "no-op": 0, "slug-not-found": 0, "slug-or-keywords-not-found": 0}

    for spec in specs:
        pkg_path = resolve_package_path(spec["basename"])
        if pkg_path is None:
            print(f"[MEDIUM missing-file] {spec['basename']}")
            medium_stats["missing-file"] += 1
            continue
        status = update_medium_package(pkg_path, spec["new_primary"], spec["new_secondary"])
        medium_stats[status] += 1
        print(f"[MEDIUM {status}] {pkg_path.name}  ({spec['decision']}) → {spec['new_primary']}")

        slug = basename_to_slug(spec["basename"], all_slugs)
        if slug is None:
            posts_stats["slug-not-found"] += 1
            print(f"  [POSTS slug-not-found] cannot map basename → slug")
            continue
        posts_ts_text, post_status = update_posts_ts_keywords(
            posts_ts_text, slug, spec["new_primary"], spec["new_secondary"]
        )
        posts_stats[post_status] += 1
        print(f"  [POSTS {post_status}] slug={slug}")

    POSTS_TS.write_text(posts_ts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"Medium packages: {medium_stats}")
    print(f"posts.ts entries: {posts_stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
