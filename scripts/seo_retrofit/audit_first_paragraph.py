#!/usr/bin/env python3
"""
Audit the first paragraph of each Medium publish package against the post's
primary keyword.

Why this matters: Medium has no separate meta-description field. Google's
SERP snippet for a Medium URL is auto-extracted from the article subtitle
or the first paragraph. If the primary keyword doesn't appear in the first
~155 chars, Google has nothing keyword-rich to pluck — and the post is
invisible for that query.

This audit reads each package's `## Markdown` block, extracts the first
*body* paragraph (after the H1 line), and checks for primary-keyword presence.

Output: a markdown report listing posts ranked by paragraph keyword density
and a flagged list of posts that need rewriting.
"""

from __future__ import annotations
import re
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MEDIUM_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"


def extract_first_paragraph(text: str) -> str | None:
    """Extract the first body paragraph from a Medium package's markdown
    block. The block looks like:
        ```md
        # Title
        <subtitle paragraph or empty>
        First body paragraph here.
        Maybe another one.
        ## H2
        ...
        ```
    We want the first non-empty, non-heading line that isn't the title.
    """
    md_match = re.search(r"```md\n(.*?)```", text, re.DOTALL)
    if not md_match:
        return None
    md = md_match.group(1).strip()
    lines = md.split("\n")

    # Skip H1 + blank, then take first non-heading non-empty line.
    started = False
    for line in lines:
        line_strip = line.strip()
        if not started:
            if line_strip.startswith("# ") and not line_strip.startswith("## "):
                started = True
            continue
        if not line_strip:
            continue
        if line_strip.startswith("#"):
            # Hit an H2 before any body — return None.
            return None
        return line_strip
    return None


def primary_keyword(text: str) -> str | None:
    m = re.search(r"^## Primary Keyword\n([^\n]+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else None


def keyword_match_ratio(paragraph: str, keyword: str) -> float:
    """Fraction of keyword's significant words found in the paragraph."""
    stopwords = {
        "a", "an", "the", "is", "are", "do", "does", "i", "my", "you",
        "your", "to", "of", "in", "on", "at", "for", "and", "or", "but",
        "with", "without", "as", "by", "be", "am", "this", "that",
    }
    paragraph_lower = paragraph.lower()
    kw_words = [w.lower() for w in re.findall(r"[A-Za-z']+", keyword)]
    significant = [w for w in kw_words if w not in stopwords]
    if not significant:
        return 1.0  # Pure stopwords → consider trivially matched.
    matched = sum(1 for w in significant if w in paragraph_lower)
    return matched / len(significant)


def main() -> int:
    rows = []
    for path in sorted(MEDIUM_DIR.glob("wave_*.md")):
        if path.name.endswith("tracker.md"):
            continue
        text = path.read_text(encoding="utf-8")
        para = extract_first_paragraph(text)
        kw = primary_keyword(text)
        if not para or not kw:
            print(f"[SKIP] {path.name} — para={'yes' if para else 'no'} kw={'yes' if kw else 'no'}")
            continue
        ratio = keyword_match_ratio(para, kw)
        rows.append({
            "file": path.name,
            "primary_keyword": kw,
            "first_paragraph": para,
            "keyword_match_ratio": round(ratio, 2),
            "paragraph_length": len(para),
        })

    # Sort weakest first.
    rows.sort(key=lambda r: r["keyword_match_ratio"])

    # Render report.
    report_lines = [
        "# Medium First Paragraph Keyword Audit",
        "Generated: 2026-04-21",
        "",
        f"Audited {len(rows)} posts. Each row shows whether the post's primary keyword's",
        "significant words appear in the first body paragraph (which Google uses for",
        "the Medium SERP snippet auto-extract).",
        "",
        "**0.00–0.49 = MISS**: rewrite first paragraph",
        "**0.50–0.74 = WEAK**: lift one or two keyword tokens into the opening",
        "**0.75–0.99 = OK**: minor tweak optional",
        "**1.00 = FULL**: keyword fully present, no action",
        "",
        "---",
        "",
    ]
    for r in rows:
        bucket = (
            "MISS" if r["keyword_match_ratio"] < 0.5
            else "WEAK" if r["keyword_match_ratio"] < 0.75
            else "OK" if r["keyword_match_ratio"] < 1.0
            else "FULL"
        )
        report_lines.append(
            f"### [{bucket}] {r['file']}  (match={r['keyword_match_ratio']:.2f}, paragraph={r['paragraph_length']} chars)"
        )
        report_lines.append(f"- Primary: `{r['primary_keyword']}`")
        report_lines.append(f"- First paragraph: {r['first_paragraph']}")
        report_lines.append("")

    out = ROOT / "marketing/fitness_blogging/blog_strategy/seo_first_paragraph_audit.md"
    out.write_text("\n".join(report_lines), encoding="utf-8")

    counts = {"MISS": 0, "WEAK": 0, "OK": 0, "FULL": 0}
    for r in rows:
        ratio = r["keyword_match_ratio"]
        b = "MISS" if ratio < 0.5 else "WEAK" if ratio < 0.75 else "OK" if ratio < 1.0 else "FULL"
        counts[b] += 1

    print("\n=== Summary ===")
    print(f"Total: {len(rows)}")
    print(f"MISS  (need rewrite):     {counts['MISS']}")
    print(f"WEAK  (lift token):       {counts['WEAK']}")
    print(f"OK    (minor tweak):      {counts['OK']}")
    print(f"FULL  (no action):        {counts['FULL']}")
    print(f"\nReport written to: {out.relative_to(ROOT)}")

    # Also write JSON for downstream scripts.
    json_out = ROOT / "marketing/fitness_blogging/blog_strategy/seo_first_paragraph_audit.json"
    json_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    sys.exit(main())
