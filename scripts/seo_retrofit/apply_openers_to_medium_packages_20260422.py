#!/usr/bin/env python3
"""
Phase B2-Medium — apply the same first-paragraph SEO openers used on
posts.ts to the corresponding wave_*_medium_manual_publish_package.md
files, so the Medium-published versions also front-load the primary
keyword in the first 100 body words.

Why: the SEO audit on 2026-04-22 found that 38 of 64 Medium packages
have the primary keyword absent from the first paragraph (semantic
match included). The owned-site posts already received this treatment
(Phase B2, PR #31) but the Medium packages were not synced.

Source of openers: scripts/seo_retrofit/first_paragraph_openers_spec.py
(62 entries, voice-consistent, banned-phrase-free, audited 2026-04-21).

Strategy per package:

  1. Lookup the package by `package_basename` (matches the prefix of
     `wave_XX_NN_<topic>_medium_manual_publish_package.md`).
  2. Locate the markdown body inside the ```md ... ``` fence.
  3. Find the first body paragraph (after the H1).
  4. If `new_first` already present anywhere in body → skip (idempotent).
  5. If `current_first` exists in body → replace it with `new_first`.
  6. Otherwise prepend the opener to the existing first paragraph
     (force mode) — same fallback used in apply_force_openers_20260422.py.

Output:
  - In-place edit of matched packages.
  - Summary printed: matched / replaced / force-prepended / skipped.
"""

from __future__ import annotations
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
SPEC_FILE = ROOT / "scripts/seo_retrofit/first_paragraph_openers_spec.py"


def load_spec() -> dict[str, dict]:
    loader = importlib.util.spec_from_file_location("spec", SPEC_FILE)
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod.FIRST_PARAGRAPH_OPENERS


def find_package(basename: str) -> Path | None:
    matches = list(PKG_DIR.glob(f"{basename}_medium_manual_publish_package.md"))
    if matches:
        return matches[0]
    return None


def patch_markdown_body(md_text: str, current_first: str, new_first: str, opener: str) -> tuple[str, str]:
    """Return (new_md_text, status). Status one of:
        skipped-already-applied / replaced / force-prepended / no-h1 / not-found"""

    if new_first in md_text:
        return md_text, "skipped-already-applied"

    if opener and opener in md_text:
        return md_text, "skipped-already-applied"

    if current_first and current_first in md_text:
        return md_text.replace(current_first, new_first, 1), "replaced"

    # Fallback: prepend opener to the first paragraph after the H1.
    h1_match = re.search(r"^#\s+.+$", md_text, re.MULTILINE)
    if not h1_match:
        return md_text, "no-h1"
    after_h1 = md_text[h1_match.end():]
    paragraphs = re.split(r"\n\s*\n", after_h1, maxsplit=1)
    if len(paragraphs) < 2:
        return md_text, "no-first-paragraph"
    blank, rest = paragraphs[0], paragraphs[1]
    rest_paras = re.split(r"\n\s*\n", rest, maxsplit=1)
    first_para = rest_paras[0]
    rest_after_first = rest_paras[1] if len(rest_paras) > 1 else ""
    new_first_para = f"{opener} {first_para}".strip()
    new_after_h1 = f"{blank}\n\n{new_first_para}"
    if rest_after_first:
        new_after_h1 += f"\n\n{rest_after_first}"
    new_md = md_text[: h1_match.end()] + new_after_h1
    return new_md, "force-prepended"


def patch_package(path: Path, current_first: str, new_first: str, opener: str) -> str:
    text = path.read_text(encoding="utf-8")
    fence = re.search(r"```(?:md|markdown)?\s*\n(.*?)\n```", text, re.DOTALL)
    if not fence:
        return "no-fence"
    md_body = fence.group(1)
    new_md, status = patch_markdown_body(md_body, current_first, new_first, opener)
    if status in {"skipped-already-applied", "no-h1", "no-first-paragraph", "not-found"}:
        return status
    new_text = text[: fence.start(1)] + new_md + text[fence.end(1):]
    path.write_text(new_text, encoding="utf-8")
    return status


def main() -> int:
    spec = load_spec()
    stats = {"replaced": 0, "force-prepended": 0, "skipped-already-applied": 0,
             "missing-package": 0, "no-fence": 0, "no-h1": 0, "no-first-paragraph": 0,
             "not-found": 0}
    for slug, entry in spec.items():
        basename = entry["package_basename"]
        path = find_package(basename)
        if not path:
            stats["missing-package"] += 1
            print(f"[missing] no package for basename {basename}  (slug={slug})")
            continue
        status = patch_package(
            path,
            current_first=entry.get("current_first", ""),
            new_first=entry.get("new_first", ""),
            opener=entry.get("opener", ""),
        )
        stats[status] = stats.get(status, 0) + 1
        if status not in {"skipped-already-applied"}:
            print(f"[{status:>17}] {path.name}")

    print("\n=== Summary ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        if v:
            print(f"  {k:>22}  {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
