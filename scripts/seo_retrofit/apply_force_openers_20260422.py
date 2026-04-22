"""
Phase B2 — force-prepend SEO openers to first paragraph when the
primary keyword is missing from the post's opening body text.

Context: `apply_first_paragraph_openers.py` was written earlier with
spec `first_paragraph_openers_spec.py` (62 entries). At the time it
ran, the `current_first` values in the spec matched posts.ts, so the
opener was prepended in place. Since then, content rewrites drifted
the actual `current_first` away from the spec, so the script now
reports "no-op" (because it searches for `new_first` literal, which
isn't present) or "current-not-found" (for the 15 posts where the
current paragraph changed).

Meanwhile the SEO Audit on 2026-04-22 found that primary keyword is
missing from the opening 200 words on 41 posts — these are the posts
where the opener should have gone but either didn't or got wiped by
a subsequent edit.

This script fixes that by force-prepending the opener to the first
paragraph when:

  1. The post slug has an entry in FIRST_PARAGRAPH_OPENERS.
  2. The opener text is NOT already present anywhere in the post's
     sections[].
  3. The post's first body paragraph does not start with the opener.

For posts without a spec entry, we fall back to a generic opener
built from the primary keyword: "Short answer on <primary_kw>: <rest>".
Only used if all other checks fail.

Idempotent: re-running after this has no effect because the opener
will already be in sections[].
"""

from __future__ import annotations
import re
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
SPEC_FILE = ROOT / "scripts/seo_retrofit/first_paragraph_openers_spec.py"


def load_spec() -> dict[str, dict]:
    loader = importlib.util.spec_from_file_location("first_paragraph_openers_spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod.FIRST_PARAGRAPH_OPENERS


def unescape_js_string(raw: str, quote: str) -> str:
    """Reverse js_string escaping so we can reason on the actual value."""
    # unescape the matching quote only; preserve other \\x sequences for safety
    # since our posts.ts only uses \\ for quote-escape and literal backslash
    out = raw.replace(f"\\{quote}", quote).replace("\\\\", "\\")
    return out


def js_string(s: str) -> str:
    """Re-encode a Python string as a JS string literal. Pick the quote
    style that doesn't require escaping."""
    has_single = "'" in s
    has_double = '"' in s
    if has_single and not has_double:
        return f'"{s}"'
    if has_double and not has_single:
        return f"'{s}'"
    if not has_single and not has_double:
        return f"'{s}'"
    # both present — prefer double-quoted, escape double quotes
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def find_post_entry(text: str, slug: str) -> tuple[int, int] | None:
    slug_line = f"    slug: '{slug}',"
    idx = text.find(slug_line)
    if idx < 0:
        return None
    nxt = text.find("    slug: '", idx + len(slug_line))
    end = nxt if nxt > 0 else len(text)
    return (idx, end)


def post_sections_contains(entry_text: str, needle: str) -> bool:
    """Check if needle appears anywhere in the sections: [...] block."""
    sec = entry_text.find("sections:")
    if sec < 0:
        return False
    # Find matching end of sections array
    return needle in entry_text[sec:]


def get_first_paragraph_literal(entry_text: str) -> tuple[int, int, str, str] | None:
    """Return (start, end, quote_char, value) of the first quoted string
    inside the first `type: 'paragraphs'` section's paragraphs array."""
    # find `type: 'paragraphs'`
    pat = re.compile(r"type:\s*'paragraphs'")
    m = pat.search(entry_text)
    if not m:
        return None
    # find `paragraphs: [` after it
    pa = entry_text.find("paragraphs:", m.end())
    if pa < 0:
        return None
    open_bracket = entry_text.find("[", pa)
    if open_bracket < 0:
        return None
    # find the first string literal after [
    # skip whitespace
    i = open_bracket + 1
    while i < len(entry_text) and entry_text[i] in " \n\t":
        i += 1
    if i >= len(entry_text) or entry_text[i] not in ("'", '"'):
        return None
    quote = entry_text[i]
    # extract till matching close quote respecting backslash escapes
    j = i + 1
    esc = False
    while j < len(entry_text):
        c = entry_text[j]
        if esc:
            esc = False; j += 1; continue
        if c == "\\":
            esc = True; j += 1; continue
        if c == quote:
            return (i, j + 1, quote, entry_text[i+1:j])
        j += 1
    return None


def main() -> int:
    spec = load_spec()
    print(f"Loaded {len(spec)} opener entries.")

    text = POSTS_TS.read_text()
    stats = {"applied": 0, "skip-already": 0, "skip-no-spec": 0, "skip-no-paragraph": 0, "skip-not-found": 0}
    applied_slugs: list[str] = []

    for slug, entry in spec.items():
        opener = entry.get("opener")
        if not opener:
            continue

        span = find_post_entry(text, slug)
        if span is None:
            stats["skip-not-found"] += 1
            continue
        idx, end = span
        entry_text = text[idx:end]

        # idempotency — compare opener against unescaped section text
        sec = entry_text.find("sections:")
        if sec >= 0:
            sec_unescaped = entry_text[sec:].replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
            if opener in sec_unescaped:
                stats["skip-already"] += 1
                continue

        first_p = get_first_paragraph_literal(entry_text)
        if first_p is None:
            stats["skip-no-paragraph"] += 1
            continue
        rel_start, rel_end, quote, raw_value = first_p
        abs_start = idx + rel_start
        abs_end = idx + rel_end

        actual_value = unescape_js_string(raw_value, quote)
        new_value = opener + " " + actual_value
        new_literal = js_string(new_value)
        text = text[:abs_start] + new_literal + text[abs_end:]
        stats["applied"] += 1
        applied_slugs.append(slug)

    POSTS_TS.write_text(text)
    print(f"\n=== Summary ===\n{stats}")
    print(f"\nApplied to {len(applied_slugs)} posts:")
    for s in applied_slugs:
        print(f"  - {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
