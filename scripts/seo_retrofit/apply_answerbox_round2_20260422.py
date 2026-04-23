#!/usr/bin/env python3
"""
Phase B-snippet — insert answerBox sections into the 15 article-typed
posts that currently lack one. Each new answerBox sits between the
post's first 'paragraphs' section and the next section, mirroring the
established pattern (see e.g. does-one-bad-day-ruin-a-diet).

Why: answerBox is the structural hook for Google's position-0
featured snippet on Q&A queries. Article posts currently expose only
Article schema. Adding a 40-60 word direct answer:

  1. Renders an on-page direct-answer block (good UX + dwell time)
  2. Lets BlogStructuredData emit FAQPage JSON-LD (one-question form)
     when faqItems are otherwise absent — actually it doesn't here
     because schemaType stays 'article', but the on-page block still
     wins position 0 via Google's regular FAQ heuristics.

Spec: scripts/seo_retrofit/answerbox_spec_round2_20260422.py
Idempotent: skips posts that already have type: 'answerBox'.
"""

from __future__ import annotations
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/answerbox_spec_round2_20260422.py"


def load_spec() -> dict[str, dict[str, str]]:
    loader = importlib.util.spec_from_file_location("spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod.ANSWERBOX_SPEC


def js_string_double(s: str) -> str:
    """Render as a double-quoted JS string literal (escaping " and \\)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def find_post_block(text: str, slug: str) -> tuple[int, int] | None:
    """Return (start, end_brace_index_inclusive) of the post object whose
    slug matches. Returns None if not found."""
    needle = f"    slug: '{slug}',"
    idx = text.find(needle)
    if idx < 0:
        return None
    # Walk back to the opening "{" of the object
    open_brace = text.rfind("{", 0, idx)
    if open_brace < 0:
        return None
    # Walk forward to find the matching closing brace, with quote/backtick
    # awareness.
    depth = 0
    in_s = False; sc = None; in_t = False; esc = False
    for i in range(open_brace, len(text)):
        c = text[i]
        if esc:
            esc = False; continue
        if c == "\\":
            esc = True; continue
        if in_s:
            if c == sc: in_s = False
            continue
        if in_t:
            if c == "`": in_t = False
            continue
        if c in ("'", '"'):
            in_s = True; sc = c; continue
        if c == "`":
            in_t = True; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_brace, i
    return None


def first_paragraphs_section_end(post_block: str) -> int:
    """Return the index in post_block at which the first 'paragraphs'
    section's closing '}' sits (index of the '}' character). Returns -1
    if not found."""
    idx = post_block.find("type: 'paragraphs'")
    if idx < 0:
        return -1
    # Walk back to the opening "{" of this section object
    obj_start = post_block.rfind("{", 0, idx)
    if obj_start < 0:
        return -1
    depth = 0
    in_s = False; sc = None; in_t = False; esc = False
    for j in range(obj_start, len(post_block)):
        c = post_block[j]
        if esc:
            esc = False; continue
        if c == "\\":
            esc = True; continue
        if in_s:
            if c == sc: in_s = False
            continue
        if in_t:
            if c == "`": in_t = False
            continue
        if c in ("'", '"'):
            in_s = True; sc = c; continue
        if c == "`":
            in_t = True; continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
    return -1


def build_answerbox_text(question: str, answer: str) -> str:
    return (
        "      {\n"
        "        type: 'answerBox',\n"
        f"        question: {js_string_double(question)},\n"
        f"        answer:\n"
        f"          {js_string_double(answer)},\n"
        "      },"
    )


def insert_answerbox(text: str, slug: str, question: str, answer: str) -> str | None:
    """Insert the answerBox object after the first paragraphs section.
    Returns the new text on success, None on no-op."""
    block_range = find_post_block(text, slug)
    if not block_range:
        print(f"  [missing] post slug not found: {slug}")
        return None
    bstart, bend = block_range
    post_block = text[bstart:bend + 1]

    if "type: 'answerBox'" in post_block:
        return None  # already present

    end_idx = first_paragraphs_section_end(post_block)
    if end_idx < 0:
        print(f"  [no-paragraphs] {slug}")
        return None

    # The closing '}' of the first paragraphs section. The next char is ',',
    # then a newline. We want to insert the answerBox object on a new line
    # right after that ',\n'.
    after = end_idx + 1  # position right after the closing '}'
    # Expect ',\n' at this point
    if post_block[after:after + 2] != ",\n":
        print(f"  [unexpected-tail at {slug}]: {post_block[after:after+10]!r}")
        return None

    insertion_point = after + 2  # right after ",\n"
    ab_text = build_answerbox_text(question, answer) + "\n"
    new_post_block = post_block[:insertion_point] + ab_text + post_block[insertion_point:]
    return text[:bstart] + new_post_block + text[bend + 1:]


def main() -> int:
    spec = load_spec()
    text = POSTS_TS.read_text(encoding="utf-8")
    inserted = skipped = missing = 0

    for slug, entry in spec.items():
        new_text = insert_answerbox(text, slug, entry["question"], entry["answer"])
        if new_text is None:
            # Could be already present or missing slug
            block_range = find_post_block(text, slug)
            if not block_range:
                missing += 1
            else:
                pb = text[block_range[0]:block_range[1] + 1]
                if "type: 'answerBox'" in pb:
                    skipped += 1
                    print(f"  [skipped-already-present] {slug}")
                else:
                    print(f"  [skipped-other] {slug}")
        else:
            inserted += 1
            text = new_text
            print(f"  [inserted] {slug}")

    if inserted > 0:
        POSTS_TS.write_text(text, encoding="utf-8")

    print(f"\n=== Summary ===")
    print(f"  inserted: {inserted}")
    print(f"  skipped (already-present): {skipped}")
    print(f"  missing (slug not found): {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
