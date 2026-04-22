#!/usr/bin/env python3
"""Extract per-post SEO metadata from frontend/src/content/blog/posts.ts.

We read the file as text and walk each top-level post object inside the
`const posts: BlogPost[] = [` block. We are NOT a TypeScript parser; we
exploit the consistent 4-space indentation of post-object braces and the
`slug:` line being unique per post.

Output: scripts/seo_retrofit/post_meta_extracted.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "frontend/src/content/blog/posts.ts"
OUT = ROOT / "scripts/seo_retrofit/post_meta_extracted.json"


def read_string_block(lines: list[str], start_idx: int) -> tuple[str, int]:
    """Read a TS string value starting at lines[start_idx] which has the form
    `      <field>: 'value',` OR
    `      <field>:\n        'value',` OR
    multi-line concatenated string fragments. Returns (full_value, end_idx).
    end_idx points at the line AFTER the value's terminating comma.
    """
    # Strip everything up through the first colon
    line = lines[start_idx]
    after_colon = line.split(":", 1)[1].lstrip()
    chunks: list[str] = []
    if after_colon == "":
        # value starts on next line
        idx = start_idx + 1
        first_already = False
    else:
        # process the inline portion first (substituted into the loop below)
        idx = start_idx
        first_already = True

    # Now collect lines until we hit a line ending with `',` or `",`
    # Each fragment line looks like:   '...some text...'
    # Strip surrounding whitespace, leading quote, trailing quote+optional comma.
    while idx < len(lines):
        if idx == start_idx and first_already:
            s = after_colon
        else:
            raw = lines[idx]
            s = raw.strip()
        if s == "":
            idx += 1
            continue
        # Remove trailing comma if present
        ended = s.endswith(",")
        if ended:
            s = s[:-1].rstrip()
        # Strip surrounding quote
        if (s.startswith("'") and s.endswith("'")) or (
            s.startswith('"') and s.endswith('"')
        ):
            chunks.append(s[1:-1])
        else:
            # Could be a non-string value; abort
            chunks.append(s)
        idx += 1
        if ended:
            break

    # Join chunks. Replace TS escaped apostrophes \' with '.
    joined = "".join(chunks).replace("\\'", "'").replace('\\"', '"')
    return joined, idx


def read_array_of_strings(lines: list[str], start_idx: int) -> tuple[list[str], int]:
    """Read a `keywords: [...]` block. Supports both single-line and multi-line.
    Returns (list, end_idx_exclusive)."""
    line = lines[start_idx]
    after_colon = line.split(":", 1)[1].lstrip()
    accum = after_colon
    idx = start_idx
    if "[" not in accum:
        # advance until we find a [
        while "[" not in accum and idx + 1 < len(lines):
            idx += 1
            accum += lines[idx]
    # Read until matching ]
    while "]" not in accum and idx + 1 < len(lines):
        idx += 1
        accum += lines[idx]
    # Now accum has `[ ... ]` somewhere; extract content
    open_pos = accum.index("[")
    close_pos = accum.index("]", open_pos)
    inner = accum[open_pos + 1 : close_pos]
    # Split on commas not inside quotes — simple regex parse for quoted strings
    items = re.findall(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", inner)
    flat = [a or b for (a, b) in items]
    flat = [s.replace("\\'", "'").replace('\\"', '"') for s in flat]
    return flat, idx + 1


def extract_posts() -> list[dict]:
    text = SRC.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)
    posts = []

    # Locate the `const posts: BlogPost[] = [` line
    start_block = None
    for i, ln in enumerate(lines):
        if ln.startswith("const posts: BlogPost[] = ["):
            start_block = i + 1
            break
    assert start_block is not None, "couldn't find posts array start"

    # The top-level posts are the entries that live as objects opened by `  {`
    # at the 2-space indent (inside the array). We walk and find every line
    # equal to '  {' (post open). The pillar-page entries also live in this
    # array but we want only the 64 actual posts (slug != short cluster id).
    pillar_slugs = {
        "scale", "mirror", "appetite", "binge", "maintenance", "plateau",
        "exercise", "founder-story", "food-structure", "body-composition",
    }

    i = start_block
    while i < len(lines):
        ln = lines[i]
        if ln == "  {":
            # Walk until matching closing `  },` at 2-space indent
            j = i + 1
            entry: dict = {}
            while j < len(lines) and lines[j] not in ("  },", "  }"):
                inner = lines[j]
                stripped = inner.lstrip()
                # We only care about a few fields at the 4-space indent level
                if stripped.startswith("slug:"):
                    val, j = read_string_block(lines, j)
                    entry["slug"] = val
                    continue
                if stripped.startswith("title:"):
                    val, j = read_string_block(lines, j)
                    entry["title"] = val
                    continue
                if stripped.startswith("description:"):
                    val, j = read_string_block(lines, j)
                    entry["description"] = val
                    continue
                if stripped.startswith("socialDescription:"):
                    val, j = read_string_block(lines, j)
                    entry["socialDescription"] = val
                    continue
                if stripped.startswith("seoTitle:"):
                    val, j = read_string_block(lines, j)
                    entry["seoTitle"] = val
                    continue
                if stripped.startswith("metaDescription:"):
                    val, j = read_string_block(lines, j)
                    entry["metaDescription"] = val
                    continue
                if stripped.startswith("keywords:"):
                    val, j = read_array_of_strings(lines, j)
                    entry["keywords"] = val
                    continue
                if stripped.startswith("deck:"):
                    val, j = read_string_block(lines, j)
                    entry["deck"] = val
                    continue
                if stripped.startswith("cluster:"):
                    val, j = read_string_block(lines, j)
                    entry["cluster"] = val
                    continue
                j += 1
            if entry.get("slug") and entry["slug"] not in pillar_slugs:
                posts.append(entry)
            i = j + 1
            continue
        i += 1
    return posts


def main() -> None:
    posts = extract_posts()
    print(f"Extracted {len(posts)} posts")
    OUT.write_text(json.dumps(posts, indent=2, ensure_ascii=False))
    print(f"Wrote {OUT}")
    # Sanity report
    for p in posts[:3]:
        print(f"\n--- {p['slug']}")
        print(f"  seoTitle:        {p.get('seoTitle','<missing>')}")
        print(f"  metaDescription: {p.get('metaDescription','<missing>')}")
        print(f"  keywords[0]:     {(p.get('keywords') or ['<missing>'])[0]}")
        print(f"  description:     {p.get('description','')[:80]}...")


if __name__ == "__main__":
    main()
