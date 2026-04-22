#!/usr/bin/env python3
"""
Canonical flip (2026-04-21): change every Medium publish package from
"set canonical to devenira.com/blog/..." (bad — DR 0 site eats Medium's
DR 95) to "do NOT set a canonical on Medium" (good — Medium ranks on its
own and devenira.com site re-points its canonical to the Medium URL).

Idempotent: skips files already updated.
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"

# Old shape: "## Canonical URL\n`https://devenira.com/blog/[slug]`\n"
# New shape: "## Canonical URL\nLeave empty on Medium ..."

OLD_RE = re.compile(
    r"## Canonical URL\n`https://devenira\.com/blog/[^`]+`\n",
    re.MULTILINE,
)
NEW_MARKER = "**DO NOT set a canonical URL in Medium's story settings.**"

REPLACEMENT = (
    "## Canonical URL\n"
    f"{NEW_MARKER}\n"
    "\n"
    "Rationale (2026-04-21 canonical flip): devenira.com is a new-domain site "
    "with effectively zero Domain Rating. Pointing Medium's canonical at it "
    "redirects Medium's DR ~95 authority into a site that cannot rank, so "
    "both pages lose. Leaving Medium self-canonical means Medium keeps its "
    "ranking power while the owned-site mirror re-points its own canonical "
    "to Medium via `generateMetadata` (see `seo_optimization_rules.md`).\n"
    "\n"
    "If Medium ever auto-sets canonical during an Import-from-URL workflow, "
    "edit the story settings and clear the canonical field before publishing.\n"
)


def process(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if NEW_MARKER in text:
        return "already-flipped"
    if not OLD_RE.search(text):
        return "no-canonical-block"
    new_text = OLD_RE.sub(REPLACEMENT, text)
    path.write_text(new_text, encoding="utf-8")
    return "flipped"


def main() -> int:
    stats = {"flipped": 0, "already-flipped": 0, "no-canonical-block": 0}
    for path in sorted(MEDIUM_DIR.glob("wave_*.md")):
        if path.name.endswith("tracker.md"):
            continue
        status = process(path)
        stats[status] += 1
        print(f"[{status}] {path.name}")
    print("\n=== Summary ===")
    print(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
