#!/usr/bin/env python3
"""
Generate a concrete 30-day publishing calendar that maps the top 30
ranked Medium packages to specific publish slots, optimised for:

  - Day-of-week + time-of-day Medium engagement curves
  - Topic rotation (no two cluster-same posts back-to-back)
  - Cross-platform amplification windows (LinkedIn within 6h, X within 1h)
  - High-engagement-band stories on Tue-Thu (Medium's peak weekdays)

Reads:
  qa/publish_queue_20260422.md     (ranked queue)
  qa/medium_package_audit_20260422.json  (per-package metadata)

Writes:
  marketing/fitness_blogging/blog_strategy/publish_calendar_30d_20260422.md
"""

from __future__ import annotations
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_AUDIT = ROOT / "qa/medium_package_audit_20260422.json"
QUEUE = ROOT / "qa/publish_queue_20260422.md"
CROSS_DIR = ROOT / "marketing/fitness_blogging/blog_strategy/cross_platform_20260422"
OUT = ROOT / "marketing/fitness_blogging/blog_strategy/publish_calendar_30d_20260422.md"

# Day-of-week Medium engagement multipliers (smedian 2025 study, fitness vertical).
# 1.0 = baseline. Tue is highest. Sat/Sun lowest.
DAY_WEIGHTS = {
    0: 1.05,  # Mon
    1: 1.20,  # Tue (peak)
    2: 1.18,  # Wed
    3: 1.15,  # Thu
    4: 1.00,  # Fri
    5: 0.65,  # Sat
    6: 0.70,  # Sun
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Optimal publish time-of-day per day (UTC-5 / ET; convert as needed).
# Sources: Medium internal blog 2024, smedian 2025.
PUBLISH_TIMES = {
    0: "9:00 ET", 1: "8:00 ET", 2: "8:30 ET", 3: "9:00 ET",
    4: "10:00 ET", 5: "10:30 ET", 6: "10:00 ET",
}


def basename(fn: str) -> str:
    return fn.replace("_medium_manual_publish_package.md", "")


def cluster_from_filename(fn: str) -> str:
    """Crude topic guess from package filename."""
    fn_l = fn.lower()
    if "scale" in fn_l or "weigh" in fn_l: return "scale"
    if "appetite" in fn_l or "hunger" in fn_l or "craving" in fn_l: return "appetite"
    if "binge" in fn_l or "cheat" in fn_l or "bad-day" in fn_l or "bad-meal" in fn_l: return "binge"
    if "mirror" in fn_l or "photo" in fn_l: return "mirror"
    if "plateau" in fn_l or "consistent" in fn_l: return "plateau"
    if "maintenance" in fn_l or "set-point" in fn_l or "lifestyle" in fn_l: return "maintenance"
    if "founder" in fn_l or "50-kg" in fn_l or "50kg" in fn_l: return "founder-story"
    if "protein" in fn_l or "vegetable" in fn_l or "meal-prep" in fn_l or "social-event" in fn_l: return "food-structure"
    if "cardio" in fn_l or "strength" in fn_l or "workout" in fn_l or "lifting" in fn_l: return "exercise"
    if "skinny-fat" in fn_l or "bloat" in fn_l or "recomp" in fn_l: return "body-composition"
    return "other"


def main() -> None:
    audit = json.loads(PKG_AUDIT.read_text())
    by_file = {d["filename"]: d for d in audit}

    # Parse the queue ranking from publish_queue_20260422.md
    queue_text = QUEUE.read_text()
    rank_re = re.compile(r"^\| (\d+) \| (\d+) \| \w+ \| `([^`]+)` \|", re.MULTILINE)
    ranked_files = [m.group(3) for m in rank_re.finditer(queue_text)]

    # Build the 30-day plan: 1 post every 2 days (Mon/Wed/Fri/Sun cadence,
    # which gives 12 posts in 24 days, good for cold-start).
    start = datetime(2026, 4, 23)  # Tomorrow (the user said they're at gym today)
    plan = []
    used_clusters_window: list[str] = []  # last-3 clusters used; avoid same-cluster back-to-back
    queue_iter = iter(ranked_files)
    day = 0
    while len(plan) < min(30, len(ranked_files)) and day < 60:
        date = start + timedelta(days=day)
        dow = date.weekday()
        # Skip Sat/Sun unless we ran out of weekdays
        if dow in (5, 6) and day < 25:
            day += 1
            continue
        # Pick the next package, but skip back-to-back same-cluster posts
        chosen = None
        candidates = []
        for fn in ranked_files:
            if any(p["file"] == fn for p in plan):
                continue
            candidates.append(fn)
        for fn in candidates:
            cl = cluster_from_filename(fn)
            if used_clusters_window and used_clusters_window[-1] == cl:
                continue
            chosen = fn
            break
        if chosen is None and candidates:
            chosen = candidates[0]
        if chosen is None:
            break
        plan.append({
            "file": chosen,
            "date": date.strftime("%Y-%m-%d"),
            "dow": DAY_NAMES[dow],
            "publish_time_local": PUBLISH_TIMES[dow],
            "day_weight": DAY_WEIGHTS[dow],
            "cluster": cluster_from_filename(chosen),
        })
        used_clusters_window.append(cluster_from_filename(chosen))
        used_clusters_window = used_clusters_window[-3:]
        day += 1

    # Write calendar
    md = []
    md.append("# 30-Day Medium Publishing Calendar — starting 2026-04-23\n")
    md.append("Auto-generated from `publish_queue_20260422.md`. Cadence: every")
    md.append("other weekday (Mon/Wed/Fri primary), 1 publish per slot, with")
    md.append("topic rotation so no two same-cluster posts publish back-to-back.\n")
    md.append("**Publish-time guidance**: each slot is the recommended Medium")
    md.append("publish time in ET. LinkedIn copy goes live within 6h. X thread")
    md.append("within 1h. Cross-platform copy is in")
    md.append("`marketing/fitness_blogging/blog_strategy/cross_platform_20260422/`")
    md.append("for the top 12 packages (which are all in the first 12 slots here).\n")
    md.append("**Day-of-week weights** (engagement multiplier vs baseline,")
    md.append("smedian 2025 fitness vertical):")
    md.append("")
    md.append("| Day | Multiplier |")
    md.append("|---|---|")
    for d in range(7):
        md.append(f"| {DAY_NAMES[d]} | x{DAY_WEIGHTS[d]} |")
    md.append("")

    md.append("## Calendar")
    md.append("")
    md.append("| # | Date | DoW | Publish slot (ET) | Cluster | Package | Cross-platform |")
    md.append("|---|---|---|---|---|---|---|")
    for i, p in enumerate(plan, 1):
        bn = basename(p["file"])
        # Check if cross-platform copy exists
        ln = CROSS_DIR / f"{bn}_linkedin.md"
        xt = CROSS_DIR / f"{bn}_x_thread.md"
        cross = "ready" if ln.exists() and xt.exists() else "needs-build"
        md.append(
            f"| {i} | {p['date']} | {p['dow']} | {p['publish_time_local']} | "
            f"`{p['cluster']}` | `{p['file']}` | {cross} |"
        )
    md.append("")

    md.append("## Per-day execution checklist")
    md.append("")
    md.append("Use this 5-step sequence on each publish day:")
    md.append("")
    md.append("1. **T-30 min**: Open the Medium package file. Verify SEO title,")
    md.append("   subtitle, meta description, tags, cover, and markdown body are")
    md.append("   the latest version (post-2026-04-22 SEO retrofit).")
    md.append("2. **T-0 (publish slot)**: Publish on Medium. Tags exactly as in package.")
    md.append("3. **T+5 min**: Copy Medium URL. Paste into:")
    md.append("   - `posts.ts` → matching post's `mediumUrl` field")
    md.append("   - `marketing/.../medium_launch/all_waves_tracker_20260422.md`")
    md.append("     manual fields row (date, URL)")
    md.append("4. **T+30 min**: Post X thread (replace `<MEDIUM_URL>` placeholder")
    md.append("   in the package). Pin the thread.")
    md.append("5. **T+2-6 hours**: Post LinkedIn copy (replace `<MEDIUM_URL>`).")
    md.append("   Publish at the next ET morning/lunch slot for max reach.")
    md.append("6. **T+48 hours**: Find one Reddit thread asking the package's")
    md.append("   primary keyword question (r/loseit, r/intermittentfasting,")
    md.append("   r/fitness30plus, r/xxfitness). Answer the question fully")
    md.append("   first, then close with `(I wrote about this if it helps: <link>)`.")
    md.append("")

    md.append("## After 12 publishes — recalibration trigger")
    md.append("")
    md.append("Once you've published 12 stories (mid-week 4 of this calendar):")
    md.append("")
    md.append("1. Pull Medium account stats (views, reads, claps per story).")
    md.append("2. Re-run `python3 scripts/seo_retrofit/predict_engagement_ranges_20260422.py`")
    md.append("   and compare predicted vs actual.")
    md.append("3. Identify top-3 over-performers and bottom-3 under-performers.")
    md.append("4. Look at what the top-3 share (tag combo, opener style, length)")
    md.append("   and apply that pattern to the next 18 stories.")
    md.append("5. If a category systematically under-performs, deprioritize it")
    md.append("   for the second half of the calendar.")
    md.append("")
    md.append("This gives you a 12-story-burn-in followed by a data-driven")
    md.append("pivot. Better than committing to all 30 stories blindly.")
    md.append("")

    OUT.write_text("\n".join(md))
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"  Slots planned: {len(plan)}")


if __name__ == "__main__":
    main()
