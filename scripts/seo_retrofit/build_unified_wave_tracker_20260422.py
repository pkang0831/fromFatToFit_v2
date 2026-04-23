#!/usr/bin/env python3
"""
Build a unified Medium publishing tracker covering ALL waves
(wave_01, wave_02, wave_03, wave_catchup) in one document.

The existing wave_01_tracker.md only covers 6 of the 64 packages.
This generates a single source-of-truth table for everything.

Reads:
  - marketing/.../medium_launch/wave_*_medium_manual_publish_package.md
  - frontend/src/content/blog/posts.ts (mediumUrl + lastModified per post)
  - qa/medium_package_audit_20260422.json (engagement scoring)

Writes:
  marketing/fitness_blogging/blog_strategy/medium_launch/all_waves_tracker_20260422.md
"""

from __future__ import annotations
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/medium_launch"
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
AUDIT = ROOT / "qa/medium_package_audit_20260422.json"
OUT = PKG_DIR / "all_waves_tracker_20260422.md"


def published_map(posts_src: str) -> dict[str, str]:
    """slug -> mediumUrl for posts where mediumUrl is set."""
    out = {}
    for m in re.finditer(r"slug:\s*'([^']+)',\s*\n\s*mediumUrl:\s*'([^']+)'", posts_src):
        out[m.group(1)] = m.group(2)
    return out


def basename(fn: str) -> str:
    return fn.replace("_medium_manual_publish_package.md", "")


def wave_group(fn: str) -> str:
    if fn.startswith("wave_01_"):
        return "Wave 1 (founder + scale + diet basics)"
    if fn.startswith("wave_02_"):
        return "Wave 2 (appetite + plateau + tracking)"
    if fn.startswith("wave_03_"):
        return "Wave 3 (mindset + maintenance + edge cases)"
    if fn.startswith("wave_catchup_"):
        return "Catchup queue (008-032 — high-search-intent Q&A)"
    return "(other)"


def kw_search_volume_proxy(kw: str) -> str:
    """Loose hint at search volume potential. Question-style + 'how to' +
    common-pain-point keywords usually rank higher."""
    kw_l = kw.lower()
    if any(p in kw_l for p in ["why am i", "why does", "why can't", "should i", "how to", "is it", "what is", "do i", "does", "can"]):
        return "high"
    if any(p in kw_l for p in ["weight loss", "diet", "appetite", "binge", "scale", "calorie"]):
        return "medium"
    return "low"


def load_basename_to_slug() -> dict[str, str]:
    """Use the existing first_paragraph_openers_spec.py to build a
    package-basename -> posts.ts-slug map (62 entries)."""
    spec_file = ROOT / "scripts/seo_retrofit/first_paragraph_openers_spec.py"
    loader = importlib.util.spec_from_file_location("spec", spec_file)
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return {entry["package_basename"]: slug for slug, entry in mod.FIRST_PARAGRAPH_OPENERS.items()}


def main() -> None:
    posts_src = POSTS_TS.read_text()
    pub = published_map(posts_src)
    audit = json.loads(AUDIT.read_text())
    audit_by_file = {d["filename"]: d for d in audit}
    bn_to_slug = load_basename_to_slug()

    rows = []
    for path in sorted(PKG_DIR.glob("wave_*_medium_manual_publish_package.md")):
        fn = path.name
        a = audit_by_file.get(fn, {})
        bn = basename(fn)
        is_published = False
        # Heuristic: mediumUrl set on the matching posts.ts entry
        # We don't have a direct slug-to-package map, so check if any
        # mediumUrl contains the basename topic.
        published_slug = bn_to_slug.get(bn)
        if published_slug and published_slug in pub:
            is_published = True
        rows.append({
            "fn": fn,
            "basename": bn,
            "wave": wave_group(fn),
            "title": a.get("seo_title", ""),
            "kw": a.get("primary_kw", ""),
            "kw_volume": kw_search_volume_proxy(a.get("primary_kw", "")),
            "engagement": a.get("predicted_engagement_band", ""),
            "raw": a.get("engagement_raw", 0),
            "words": a.get("body_word_count", 0),
            "h2": a.get("h2_count", 0),
            "tags": a.get("tags", []),
            "flags": a.get("flags", []),
            "is_published": is_published,
            "published_slug": published_slug,
        })

    md = []
    md.append(f"# All-Waves Medium Publishing Tracker — Generated 2026-04-22\n")
    md.append(
        "Single source-of-truth replacing the wave_01-only tracker. Covers "
        f"all {len(rows)} packages across wave_01 (6), wave_02 (13), "
        f"wave_03 (20), wave_catchup (25)."
    )
    md.append("")
    md.append("## Status legend")
    md.append("")
    md.append("- **band** = predicted engagement band on Medium (`high` / `medium` / `low`); see `AUTONOMOUS_SESSION_DASHBOARD_20260422.md` for methodology")
    md.append("- **kw vol** = loose proxy for search-volume potential of the primary keyword (`high` / `medium` / `low`)")
    md.append("- **flags** = unresolved package issues; empty if package is publish-ready")
    md.append("")

    # Group by wave
    by_wave = {}
    for r in rows:
        by_wave.setdefault(r["wave"], []).append(r)

    md.append("## Summary")
    md.append("")
    md.append("| Wave | Total | Published | Ready | Avg engagement raw |")
    md.append("|---|---|---|---|---|")
    for wave in ["Wave 1 (founder + scale + diet basics)",
                 "Wave 2 (appetite + plateau + tracking)",
                 "Wave 3 (mindset + maintenance + edge cases)",
                 "Catchup queue (008-032 — high-search-intent Q&A)"]:
        wrows = by_wave.get(wave, [])
        n = len(wrows)
        published = sum(1 for r in wrows if r["is_published"])
        ready = sum(1 for r in wrows if not r["flags"])
        avg = round(sum(r["raw"] for r in wrows) / n, 1) if n else 0
        md.append(f"| {wave} | {n} | {published} | {ready} | {avg} |")
    md.append("")

    for wave in ["Wave 1 (founder + scale + diet basics)",
                 "Wave 2 (appetite + plateau + tracking)",
                 "Wave 3 (mindset + maintenance + edge cases)",
                 "Catchup queue (008-032 — high-search-intent Q&A)"]:
        wrows = by_wave.get(wave, [])
        if not wrows:
            continue
        md.append(f"## {wave}")
        md.append("")
        md.append("| # | Status | Band | Raw | KW vol | Words | H2 | Title | Primary KW | File |")
        md.append("|---|---|---|---|---|---|---|---|---|---|")
        for i, r in enumerate(wrows, 1):
            status = "✅ published" if r["is_published"] else ("⚠️ flagged" if r["flags"] else "📝 ready")
            md.append(
                f"| {i} | {status} | {r['engagement']} | {r['raw']} | {r['kw_volume']} | "
                f"{r['words']} | {r['h2']} | {r['title']} | `{r['kw']}` | `{r['fn']}` |"
            )
        # Per-wave flag listing
        flagged = [(r['fn'], r['flags']) for r in wrows if r['flags']]
        if flagged:
            md.append("")
            md.append("**Flagged packages in this wave:**")
            md.append("")
            for fn, flags in flagged:
                md.append(f"- `{fn}` — flags: `{', '.join(flags)}`")
        md.append("")

    md.append("## Manual fields (fill in as you publish)")
    md.append("")
    md.append("| File | Date Published | Medium URL | X Status | LinkedIn Status | Facebook Status | Notes |")
    md.append("|---|---|---|---|---|---|---|")
    for r in rows:
        if r["is_published"]:
            url = pub.get(r["published_slug"], "")
            md.append(f"| `{r['fn']}` | (set when published) | {url} | | | | |")
        else:
            md.append(f"| `{r['fn']}` | | | | | | |")
    md.append("")

    OUT.write_text("\n".join(md))
    print(f"Wrote {OUT.relative_to(ROOT)}")
    n_pub = sum(1 for r in rows if r["is_published"])
    n_ready = sum(1 for r in rows if not r["flags"] and not r["is_published"])
    n_flagged = sum(1 for r in rows if r["flags"])
    print(f"  Total: {len(rows)} | Published: {n_pub} | Ready: {n_ready} | Flagged: {n_flagged}")


if __name__ == "__main__":
    main()
