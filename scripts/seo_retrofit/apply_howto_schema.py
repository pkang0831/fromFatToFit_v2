#!/usr/bin/env python3
"""
Apply HowTo schema content to posts.ts entries.

Input: scripts/seo_retrofit/howto_schema_spec.py
       HOWTO_SCHEMAS keyed by slug → {name, description, steps[]}
       SCHEMA_TYPES keyed by slug → 'howto'

Per post:
- Set schemaType: 'howto' (overriding prior 'faq' on this slug; FAQ
  schema still emits because BlogStructuredData auto-harvests faq sections)
- Insert howToSteps array as a posts.ts field

Idempotent.
"""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/howto_schema_spec.py"


def load_spec() -> tuple[dict[str, dict], dict[str, str]]:
    spec_loader = importlib.util.spec_from_file_location("howto_schema_spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(spec_loader)
    spec_loader.loader.exec_module(mod)
    return mod.HOWTO_SCHEMAS, mod.SCHEMA_TYPES


def js_string(s: str) -> str:
    if "'" in s and '"' not in s:
        return f'"{s}"'
    if "'" in s:
        return "'" + s.replace("'", "\\'") + "'"
    return f"'{s}'"


def render_howto_steps_ts(steps: list[dict]) -> str:
    lines = ["    howToSteps: ["]
    for step in steps:
        lines.append("      {")
        lines.append(f"        name: {js_string(step['name'])},")
        lines.append(f"        text:\n          {js_string(step['text'])},")
        lines.append("      },")
    lines.append("    ],")
    return "\n".join(lines)


def update_post(text: str, slug: str, schema_type: str, steps: list[dict]) -> tuple[str, str]:
    slug_line = f"    slug: '{slug}',"
    slug_idx = text.find(slug_line)
    if slug_idx == -1:
        return text, "slug-not-found"
    next_slug_idx = text.find("    slug: '", slug_idx + len(slug_line))
    entry_end = next_slug_idx if next_slug_idx != -1 else len(text)

    # Idempotency: already has howToSteps?
    chunk = text[slug_idx:entry_end]
    if "    howToSteps: [" in chunk:
        return text, "already-present"

    # 1) Update or insert schemaType.
    schema_pattern = re.compile(r"    schemaType: '[^']+',\n")
    if schema_pattern.search(chunk):
        chunk = schema_pattern.sub(f"    schemaType: '{schema_type}',\n", chunk, count=1)
    else:
        # Insert schemaType after the keywords array.
        keywords_end = chunk.find("    ],\n", chunk.find("    keywords: ["))
        if keywords_end == -1:
            return text, "no-keywords-block"
        insert_pos = keywords_end + len("    ],\n")
        chunk = chunk[:insert_pos] + f"    schemaType: '{schema_type}',\n" + chunk[insert_pos:]

    # 2) Insert howToSteps after schemaType (or after keywords if no schemaType existed).
    howto_block = render_howto_steps_ts(steps) + "\n"
    schema_match = re.search(r"    schemaType: '[^']+',\n", chunk)
    if schema_match:
        insert_at = schema_match.end()
        chunk = chunk[:insert_at] + howto_block + chunk[insert_at:]
    else:
        return text, "schemaType-missing-after-update"

    return text[:slug_idx] + chunk + text[entry_end:], "updated"


def main() -> int:
    if not SPEC_FILE.exists():
        print(f"ERROR: spec not found: {SPEC_FILE}")
        return 2
    schemas, schema_types = load_spec()
    text = POSTS_TS.read_text(encoding="utf-8")
    stats = {"updated": 0, "already-present": 0, "slug-not-found": 0,
             "no-keywords-block": 0, "schemaType-missing-after-update": 0}
    for slug, entry in schemas.items():
        st = schema_types.get(slug, "howto")
        text, status = update_post(text, slug, st, entry["steps"])
        stats[status] = stats.get(status, 0) + 1
        print(f"[{status}] {slug}")
    POSTS_TS.write_text(text, encoding="utf-8")
    print(f"\n=== Summary ===\n{stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
