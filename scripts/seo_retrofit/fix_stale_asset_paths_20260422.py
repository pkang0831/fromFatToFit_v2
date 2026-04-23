#!/usr/bin/env python3
"""
Three Medium publish packages reference cover images at a stale path
prefix (`extracted_fresh_20260416/`) that no longer exists. The actual
image files exist at the older `extracted/` prefix. This script
rewrites those references in place.

It also surfaces the one truly missing asset (`pkang_0011 1.jpg`,
referenced from wave_01_01_consistency) so the user knows to either
add the asset or update the package's "Recommended asset" line.
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"

STALE_PREFIX = "extracted_fresh_20260416/"
NEW_PREFIX = "extracted/"


def main() -> None:
    fixed = 0
    truly_missing = []
    for path in sorted(PKG_DIR.glob("wave_*.md")):
        text = path.read_text(encoding="utf-8")
        new_text = text.replace(STALE_PREFIX, NEW_PREFIX)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            fixed += 1
            print(f"[fixed] {path.name}")
        # Detect remaining truly-missing assets
        for asset in re.findall(r"`([^`]*\.(?:jpg|jpeg|png|webp))`", new_text):
            candidate = ROOT / asset
            frontend = ROOT / "frontend/public" / asset.lstrip("/")
            if not candidate.exists() and not frontend.exists():
                truly_missing.append((path.name, asset))

    print(f"\n=== Fixed {fixed} packages with stale extracted_fresh_20260416/ prefix ===")
    if truly_missing:
        print(f"\n=== Truly missing assets ({len(truly_missing)}) ===")
        for fn, asset in truly_missing:
            print(f"  {fn}")
            print(f"    -> {asset}")
    else:
        print("\nNo missing assets.")


if __name__ == "__main__":
    main()
