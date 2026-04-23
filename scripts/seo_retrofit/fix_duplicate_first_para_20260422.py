#!/usr/bin/env python3
"""
After opener injection, ~35 of the 38 modified Medium packages exhibit a
pre-existing content redundancy: the first paragraph (now `opener +
current_first`) is followed by paragraphs 2-4 that are short, broken-up
restatements of the `current_first` summary. The redundancy was already
in the source packages from how the author split a one-paragraph summary
into bite-sized Medium paragraphs.

This script trims the duplicate content out of paragraph 1 by reducing
it to just the opener, leaving the broken-up paragraphs 2-4 intact (so
the body keeps the Medium-friendly short-paragraph rhythm and zero
content is lost).

Logic per package:

  1. Load the spec entry to know `opener` and `current_first`.
  2. If the body's first paragraph still equals `opener + " " + current_first`
     AND the body's NEXT paragraph is a substring of `current_first` (or
     vice-versa, indicating the broken-up form is present):
       -> rewrite paragraph 1 to be just `opener`.
  3. Otherwise: leave the package alone.

Idempotent: if paragraph 1 is already just the opener, this is a no-op.
"""

from __future__ import annotations
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
SPEC_FILE = ROOT / "scripts/seo_retrofit/first_paragraph_openers_spec.py"


def load_spec():
    loader = importlib.util.spec_from_file_location("spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod.FIRST_PARAGRAPH_OPENERS


def split_paragraphs(body: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def has_redundancy(p1: str, current_first: str, paragraphs_after: list[str]) -> bool:
    """Return True if the broken-up form of current_first is in paragraphs_after."""
    if not current_first:
        return False
    p1_l = p1.lower()
    cf_l = current_first.lower()
    # Look at next 5 paragraphs; if any non-trivial one is a substring of P1
    # (i.e. the broken-up form is present), redundancy exists.
    for p in paragraphs_after[:5]:
        if p.startswith("#"):
            continue
        p_l = p.lower()
        if len(p.split()) < 3:
            continue
        if p_l in p1_l or p_l in cf_l:
            return True
        # Also check sentence-by-sentence: if any sentence in p appears in cf
        for sent in re.split(r"(?<=[.!?])\s+", p_l):
            if len(sent.split()) >= 4 and sent in cf_l:
                return True
    return False


def fix_one(path: Path, opener: str, current_first: str) -> str:
    text = path.read_text(encoding="utf-8")
    fence = re.search(r"```(?:md|markdown)?\s*\n(.*?)\n```", text, re.DOTALL)
    if not fence:
        return "no-fence"
    md = fence.group(1)

    # Locate H1 and split body
    h1m = re.match(r"(#\s+.+\n\s*\n)", md)
    if not h1m:
        return "no-h1"
    head = h1m.group(1)
    body = md[h1m.end():]
    paras = split_paragraphs(body)
    if not paras:
        return "empty-body"

    p1 = paras[0]
    if p1.strip() == opener.strip():
        return "already-just-opener"

    # The expected form is "opener + ' ' + current_first" (one paragraph)
    expected_full = f"{opener.strip()} {current_first.strip()}".strip()
    if p1.strip() != expected_full:
        # Maybe whitespace differs slightly; use loose match
        norm = re.sub(r"\s+", " ", p1.strip())
        if norm != re.sub(r"\s+", " ", expected_full):
            return "first-para-shape-changed"

    # Now check redundancy with following paragraphs
    if not has_redundancy(p1, current_first, paras[1:]):
        return "no-redundancy-leave-alone"

    # Trim P1 down to just the opener.
    new_paras = [opener.strip()] + paras[1:]
    new_body = "\n\n".join(new_paras) + "\n"
    new_md = head + new_body
    new_text = text[: fence.start(1)] + new_md + text[fence.end(1):]
    if new_text == text:
        return "no-change"
    path.write_text(new_text, encoding="utf-8")
    return "trimmed"


def main() -> None:
    spec = load_spec()
    stats = {}
    for slug, entry in spec.items():
        bn = entry["package_basename"]
        matches = list(PKG_DIR.glob(f"{bn}_medium_manual_publish_package.md"))
        if not matches:
            continue
        path = matches[0]
        status = fix_one(path, entry.get("opener", ""), entry.get("current_first", ""))
        stats[status] = stats.get(status, 0) + 1
        if status == "trimmed":
            print(f"[trimmed] {path.name}")

    print("\n=== Summary ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k:>32}  {v}")


if __name__ == "__main__":
    main()
