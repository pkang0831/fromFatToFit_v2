#!/usr/bin/env python3
"""
Apply Featured Snippet content (answerBox + faq sections) to posts.ts AND
to the corresponding Medium publish-package markdown bodies.

Input: scripts/seo_retrofit/featured_snippets_spec.py
       FEATURED_SNIPPETS keyed by slug → {answerBox, faqItems}
       SCHEMA_TYPES keyed by slug → 'faq'

For each entry:

1. Insert the answerBox section into the posts.ts entry's `sections: [...]`
   array — placed AFTER the first paragraphs section.
2. Insert the faq section into the same entry — placed at the END of the
   sections array, before the closing `]`.
3. Add `schemaType: 'faq'` to the entry's metadata block (alongside other
   SEO fields).
4. Mirror both pieces into the Medium markdown body inside the package
   file's ```md ... ``` block:
     - answerBox renders as a block quote-style "Q + A" section
     - faq renders as a "## FAQ" markdown section with `### Q` + answer

Idempotent: skips entries already containing the marker text.
"""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/featured_snippets_spec.py"

# Marker we add to Medium markdown to detect prior application.
MEDIUM_FAQ_HEADING = "## Frequently Asked Questions"


def load_spec() -> tuple[dict[str, dict], dict[str, str]]:
    spec_loader = importlib.util.spec_from_file_location("featured_snippets_spec", SPEC_FILE)
    if not spec_loader or not spec_loader.loader:
        raise RuntimeError(f"Cannot load spec at {SPEC_FILE}")
    mod = importlib.util.module_from_spec(spec_loader)
    spec_loader.loader.exec_module(mod)
    return mod.FEATURED_SNIPPETS, mod.SCHEMA_TYPES


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


def slug_to_package_path(slug: str) -> Path | None:
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
    # Try the NEW slug, then OLD via redirects map.
    for path in MEDIUM_DIR.glob(f"*_{slug}_medium_manual_publish_package.md"):
        return path
    old_slug = _NEW_TO_OLD_SLUG.get(slug)
    if old_slug:
        for path in MEDIUM_DIR.glob(f"*_{old_slug}_medium_manual_publish_package.md"):
            return path
    return None


def render_section_typescript(section: dict) -> str:
    """Render a BlogSection dict as a TS object literal string."""
    indent = "      "  # inside a sections: [ ... ] array
    if section["type"] == "answerBox":
        return (
            f"{indent}{{\n"
            f"{indent}  type: 'answerBox',\n"
            f"{indent}  question: {js_string(section['question'])},\n"
            f"{indent}  answer:\n"
            f"{indent}    {js_string(section['answer'])},\n"
            f"{indent}}}"
        )
    if section["type"] == "faq":
        items_lines = ["      items: ["]
        for item in section["items"]:
            items_lines.append(f"{indent}  {{")
            items_lines.append(f"{indent}    question: {js_string(item['question'])},")
            items_lines.append(f"{indent}    answer:\n{indent}      {js_string(item['answer'])},")
            items_lines.append(f"{indent}  }},")
        items_lines.append(f"{indent}],")
        return (
            f"{indent}{{\n"
            f"{indent}  type: 'faq',\n"
            f"{indent}  title: {js_string(section.get('title', 'Frequently Asked Questions'))},\n"
            + "\n".join(items_lines)
            + f"\n{indent}}}"
        )
    raise ValueError(f"Unknown section type: {section['type']}")


def update_posts_ts(text: str, slug: str, answer_box: dict, faq_items: list[dict], schema_type: str) -> tuple[str, str]:
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-not-found"

    # Find the entry's sections: [ ... ] block.
    sections_open = text.find("    sections: [", slug_idx)
    if sections_open == -1:
        return text, "no-sections-block"
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    if next_slug_idx != -1 and sections_open > next_slug_idx:
        return text, "no-sections-block"

    # Idempotency check.
    chunk_to_check = text[slug_idx:next_slug_idx if next_slug_idx != -1 else slug_idx + 50000]
    if "type: 'answerBox'" in chunk_to_check or "type: 'faq'" in chunk_to_check:
        return text, "already-present"

    # Find sections array end: matching `\n    ],`
    bracket_depth = 0
    i = sections_open + len("    sections: [")
    sections_end = -1
    while i < len(text):
        ch = text[i]
        if ch == "[":
            bracket_depth += 1
        elif ch == "]":
            if bracket_depth == 0:
                sections_end = i
                break
            bracket_depth -= 1
        i += 1
    if sections_end == -1:
        return text, "no-sections-end"

    # Find first section type's opening brace position so we can insert
    # the answerBox AFTER it.
    first_section_open = text.find("{", sections_open + len("    sections: ["))
    # Find matching closing brace of first section.
    j = first_section_open + 1
    depth = 1
    while j < len(text) and depth > 0:
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
        j += 1
    first_section_end = j  # position right after closing brace
    # Skip ',\n' if present after first section close.
    after_first_section = first_section_end
    if text[after_first_section : after_first_section + 1] == ",":
        after_first_section += 1

    answer_box_ts = render_section_typescript(answer_box)
    faq_section_ts = render_section_typescript({"type": "faq", "items": faq_items})

    # Insert answerBox after first section.
    insertion_after_first = "\n" + answer_box_ts + ","
    text = text[:after_first_section] + insertion_after_first + text[after_first_section:]

    # Recompute sections_end (shift by insertion length).
    sections_end += len(insertion_after_first)

    # Insert faq section before sections_end (i.e., before the `]`).
    # Ensure trailing comma on previous section.
    insertion_before_end = "\n" + faq_section_ts + ",\n    "
    # Find the last `}` before `]` and insert after it.
    last_brace = text.rfind("}", 0, sections_end)
    insert_pos = last_brace + 1
    # If there's already a comma after, skip it.
    if text[insert_pos] == ",":
        insert_pos += 1
    text = text[:insert_pos] + insertion_before_end + text[insert_pos:]

    # Add schemaType to entry metadata. Insert AFTER the keywords array.
    entry_start = slug_idx
    entry_end_for_search = text.find("    sections: [", entry_start)
    if "    schemaType:" not in text[entry_start:entry_end_for_search]:
        kw_end = text.find("    ],\n", text.find("    keywords: [", entry_start))
        if kw_end != -1:
            insertion = f"    schemaType: '{schema_type}',\n"
            text = text[: kw_end + len("    ],\n")] + insertion + text[kw_end + len("    ],\n") :]

    return text, "updated"


def render_section_markdown(answer_box: dict, faq_items: list[dict]) -> str:
    """Render answerBox + FAQ as Medium markdown chunks."""
    parts = []
    parts.append(f"\n> **{answer_box['question']}**")
    parts.append(f">")
    parts.append(f"> {answer_box['answer']}\n")
    parts.append(f"\n{MEDIUM_FAQ_HEADING}\n")
    for item in faq_items:
        parts.append(f"### {item['question']}\n")
        parts.append(f"{item['answer']}\n")
    return "\n".join(parts)


def update_medium_markdown(path: Path, answer_box: dict, faq_items: list[dict]) -> str:
    text = path.read_text(encoding="utf-8")
    if MEDIUM_FAQ_HEADING in text:
        return "already-present"

    # Find the markdown block.
    md_match = re.search(r"```md\n(.*?)```", text, re.DOTALL)
    if not md_match:
        return "no-markdown-block"
    md = md_match.group(1)
    md_start = md_match.start(1)
    md_end = md_match.end(1)

    # Insert answerBox right after the H1 + subtitle (before first ## H2).
    h2_match = re.search(r"\n## ", md)
    if h2_match:
        # answerBox before first H2.
        ab_block = f"\n> **{answer_box['question']}**\n>\n> {answer_box['answer']}\n"
        new_md = md[: h2_match.start()] + ab_block + md[h2_match.start() :]
    else:
        new_md = md + f"\n> **{answer_box['question']}**\n>\n> {answer_box['answer']}\n"

    # Append FAQ at end of body, before the ``` close. Place above the closing
    # bio paragraph if one exists; for simplicity, just append.
    faq_block = f"\n\n{MEDIUM_FAQ_HEADING}\n\n"
    for item in faq_items:
        faq_block += f"### {item['question']}\n\n{item['answer']}\n\n"
    new_md = new_md.rstrip() + "\n\n" + faq_block

    new_text = text[:md_start] + new_md + text[md_end:]
    path.write_text(new_text, encoding="utf-8")
    return "updated"


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"ERROR: spec file not found at {SPEC_FILE}")
        return 2
    spec, schema_types = load_spec()
    print(f"Loaded {len(spec)} featured snippet entries.\n")

    posts_text = POSTS_TS.read_text(encoding="utf-8")
    posts_stats = {"updated": 0, "already-present": 0, "slug-not-found": 0, "no-sections-block": 0, "no-sections-end": 0}
    medium_stats = {"updated": 0, "already-present": 0, "no-markdown-block": 0, "missing-file": 0}

    for slug, entry in spec.items():
        answer_box = entry["answerBox"]
        faq_items = entry["faqItems"]
        schema_type = schema_types.get(slug, "faq")

        posts_text, ps = update_posts_ts(posts_text, slug, answer_box, faq_items, schema_type)
        posts_stats[ps] = posts_stats.get(ps, 0) + 1
        print(f"[POSTS {ps}] {slug}")

        pkg_path = slug_to_package_path(slug)
        if pkg_path is None:
            print(f"  [MEDIUM missing-file] {slug}")
            medium_stats["missing-file"] += 1
            continue
        ms = update_medium_markdown(pkg_path, answer_box, faq_items)
        medium_stats[ms] = medium_stats.get(ms, 0) + 1
        print(f"  [MEDIUM {ms}] {pkg_path.name}")

    POSTS_TS.write_text(posts_text, encoding="utf-8")

    print("\n=== Summary ===")
    print(f"posts.ts entries: {posts_stats}")
    print(f"Medium packages: {medium_stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
