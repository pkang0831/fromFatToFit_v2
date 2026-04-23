#!/usr/bin/env python3
"""
Re-encode the 4 webp hero files that exceed the 200 KB LCP budget.

Inputs (as found by audit_seo_full_20260422.py):
  - /founder/progress-update-hanok-20260119.webp  (269 KB)
  - /founder/hunger-editorial-20260106.webp       (223 KB)
  - /founder/sleep-reflective-20260106.webp       (212 KB)
  - /founder/consistency-editorial-20251229.webp  (201 KB; just over the bucket)

Strategy: re-encode in place using cwebp at quality 72 with a 1600 px max
width. This typically halves filesize while remaining visually
indistinguishable on retina mobile (where LCP matters most). Each file is
backed up to <name>.bak.webp before overwrite, so revert is one mv away.

Idempotent: skips if file is already <= 160 KB.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "frontend/public"

TARGETS = [
    "founder/progress-update-hanok-20260119.webp",
    "founder/hunger-editorial-20260106.webp",
    "founder/sleep-reflective-20260106.webp",
    "founder/consistency-editorial-20251229.webp",
]

QUALITY = 72
MAX_WIDTH = 1600
SOFT_TARGET_KB = 160


def reencode(rel: str) -> tuple[str, int, int]:
    src = PUBLIC_DIR / rel
    if not src.exists():
        return ("missing", 0, 0)

    src_kb = src.stat().st_size // 1024
    if src_kb <= SOFT_TARGET_KB:
        return ("already-small", src_kb, src_kb)

    backup = src.with_suffix(".bak.webp")
    if not backup.exists():
        shutil.copy2(src, backup)

    tmp_out = src.with_suffix(".reencode.webp")
    cmd = [
        "cwebp",
        "-q", str(QUALITY),
        "-resize", str(MAX_WIDTH), "0",
        "-quiet",
        str(src),
        "-o", str(tmp_out),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        if tmp_out.exists():
            tmp_out.unlink()
        return (f"convert-error:{e.stderr.strip()[:80]}", src_kb, src_kb)

    new_kb = tmp_out.stat().st_size // 1024
    # Only adopt if actually smaller (sanity)
    if new_kb >= src_kb:
        tmp_out.unlink()
        return ("no-improvement", src_kb, new_kb)

    shutil.move(str(tmp_out), str(src))
    return ("reencoded", src_kb, new_kb)


def main() -> int:
    if not shutil.which("cwebp"):
        print("ERROR: cwebp not found. brew install webp")
        return 2

    total_before = 0
    total_after = 0
    for rel in TARGETS:
        status, before, after = reencode(rel)
        total_before += before
        total_after += after
        if status == "reencoded":
            print(f"[reencoded]    {rel:55s} {before} KB -> {after} KB  (-{round(100*(1-after/before))}%)")
        else:
            print(f"[{status}] {rel}")

    if total_before > 0:
        print(f"\nTotal: {total_before} KB -> {total_after} KB  (-{round(100*(1-total_after/total_before))}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
