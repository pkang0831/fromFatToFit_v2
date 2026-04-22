#!/usr/bin/env python3
"""
SEO title pixel-width audit.

Google's SERP truncates titles at roughly 600px of rendered width in a
Roboto/Arial-like sans-serif ~20px weight. Counting characters is a weak
proxy — "iiii" is 4 chars but ~24px, while "WWWW" is 4 chars but ~68px.

This script estimates rendered pixel width using Arial-approximate per-
character weights (calibrated from Google SERP screenshots) and flags
any seoTitle in either:

- Medium publish packages (under `## SEO Title`)
- posts.ts BlogPost `seoTitle` fields

that exceeds 600px. The script reports per-title widths so you can spot
which titles will visibly truncate and rewrite them.
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"

# Arial-approximate per-character widths at 20px font size. Pulled from
# published pixel tables for Arial (close enough to Roboto for SERP
# estimation). Uppercase + lowercase are distinct; digits + punctuation
# mapped by visual inspection.
# Values are in "pixels at 20px Arial-like". Fallback for unknown chars: 11.
WIDTHS: dict[str, float] = {
    " ": 5.6, "!": 5.6, '"': 7.1, "#": 11.1, "$": 11.1, "%": 17.8, "&": 13.3,
    "'": 3.8, "(": 6.7, ")": 6.7, "*": 7.8, "+": 11.7, ",": 5.6, "-": 6.7,
    ".": 5.6, "/": 5.6, ":": 5.6, ";": 5.6, "<": 11.7, "=": 11.7, ">": 11.7,
    "?": 11.1, "@": 20.3, "[": 5.6, "\\": 5.6, "]": 5.6, "^": 9.4, "_": 11.1,
    "`": 6.7, "{": 6.7, "|": 5.2, "}": 6.7, "~": 11.7,
    "0": 11.1, "1": 11.1, "2": 11.1, "3": 11.1, "4": 11.1, "5": 11.1,
    "6": 11.1, "7": 11.1, "8": 11.1, "9": 11.1,
    "A": 13.3, "B": 13.3, "C": 14.4, "D": 14.4, "E": 13.3, "F": 12.2,
    "G": 15.6, "H": 14.4, "I": 5.6,  "J": 10.0, "K": 13.3, "L": 11.1,
    "M": 16.7, "N": 14.4, "O": 15.6, "P": 13.3, "Q": 15.6, "R": 14.4,
    "S": 13.3, "T": 12.2, "U": 14.4, "V": 13.3, "W": 18.9, "X": 13.3,
    "Y": 13.3, "Z": 12.2,
    "a": 11.1, "b": 11.1, "c": 10.0, "d": 11.1, "e": 11.1, "f": 5.6,
    "g": 11.1, "h": 11.1, "i": 4.4,  "j": 4.4,  "k": 10.0, "l": 4.4,
    "m": 16.7, "n": 11.1, "o": 11.1, "p": 11.1, "q": 11.1, "r": 6.7,
    "s": 10.0, "t": 5.6,  "u": 11.1, "v": 10.0, "w": 14.4, "x": 10.0,
    "y": 10.0, "z": 10.0,
    # Em dash / en dash / curly quotes (Unicode, common in our titles)
    "—": 20.0, "–": 11.1, "\u2019": 3.8, "\u2018": 3.8, "\u201C": 7.1, "\u201D": 7.1,
}

# Google's SERP cap is ~600px. We warn at 580px (safety margin), fail at 600.
WARN_PX = 580.0
FAIL_PX = 600.0

# Medium's SEO-title cap is documented at 70 chars; pragmatically titles
# longer than ~60 still truncate in desktop SERPs. Use the same budget.


def pixel_width(text: str) -> float:
    return sum(WIDTHS.get(ch, 11.0) for ch in text)


def audit_medium_packages() -> list[dict]:
    results = []
    seo_re = re.compile(r"^## SEO Title\n(.+)$", re.MULTILINE)
    for path in sorted(MEDIUM_DIR.glob("wave_*.md")):
        if path.name.endswith("tracker.md"):
            continue
        text = path.read_text(encoding="utf-8")
        m = seo_re.search(text)
        if not m:
            continue
        title = m.group(1).strip()
        results.append({
            "source": "medium",
            "file": path.name,
            "title": title,
            "chars": len(title),
            "pixels": round(pixel_width(title), 1),
        })
    return results


def audit_posts_ts() -> list[dict]:
    results = []
    text = POSTS_TS.read_text(encoding="utf-8")
    # Pattern: slug: '...',\n ... seoTitle: '...'
    entry_re = re.compile(
        r"    slug: '(?P<slug>[^']+)',\n(?:.*\n)*?    seoTitle: (?P<q>['\"])(?P<title>.+?)(?P=q),",
        re.MULTILINE,
    )
    for m in entry_re.finditer(text):
        title = m.group("title")
        results.append({
            "source": "posts.ts",
            "slug": m.group("slug"),
            "title": title,
            "chars": len(title),
            "pixels": round(pixel_width(title), 1),
        })
    return results


def classify(px: float) -> str:
    if px >= FAIL_PX:
        return "FAIL"
    if px >= WARN_PX:
        return "WARN"
    return "OK"


def main() -> int:
    medium = audit_medium_packages()
    site = audit_posts_ts()
    all_results = medium + site

    print(f"{'SOURCE':<10} {'STATUS':<6} {'CHARS':>5} {'PIXELS':>8}  TITLE")
    print("-" * 110)
    stats = {"OK": 0, "WARN": 0, "FAIL": 0}
    for r in sorted(all_results, key=lambda x: x["pixels"], reverse=True):
        status = classify(r["pixels"])
        stats[status] += 1
        identifier = r.get("file") or r.get("slug")
        print(f"{r['source']:<10} {status:<6} {r['chars']:>5} {r['pixels']:>8.1f}  {r['title']}  [{identifier}]")

    print("\n=== Summary ===")
    print(f"Total: {len(all_results)}")
    print(f"OK    (<{WARN_PX}px): {stats['OK']}")
    print(f"WARN  (>={WARN_PX}px): {stats['WARN']}")
    print(f"FAIL  (>={FAIL_PX}px): {stats['FAIL']}")

    # Machine-readable output for follow-up scripts.
    out_path = ROOT / "marketing/fitness_blogging/blog_strategy/seo_title_pixel_audit.json"
    out_path.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nReport written to: {out_path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
