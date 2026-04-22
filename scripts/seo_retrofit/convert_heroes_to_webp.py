#!/usr/bin/env python3
"""
Convert all referenced hero images in posts.ts to WebP and update the
posts.ts heroImage paths in one atomic pass.

Steps per image:
1. Read posts.ts; collect every unique heroImage path.
2. For each .jpg / .jpeg / .png hero, run `cwebp -q 80 -resize 1920 0 <src> -o <src.webp>`.
   - `-resize 1920 0` = max-width 1920px, height auto (keeps aspect ratio).
   - `-q 80` = quality 80, the standard sweet spot.
3. After successful conversion, update posts.ts to point to the .webp path.
4. Leave the original .jpg in place (in case you need to revert; .webp is additive).

Idempotent: skips heroes that are already .webp.
"""

from __future__ import annotations
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
PUBLIC_DIR = ROOT / "frontend/public"


def find_hero_paths(text: str) -> list[str]:
    return list(set(re.findall(r"heroImage: '(/founder/[^']+)'", text)))


def convert(src_rel: str) -> tuple[str, str]:
    """Convert one image. Returns (status, new_rel_path)."""
    if src_rel.endswith(".webp"):
        return "already-webp", src_rel
    src = PUBLIC_DIR / src_rel.lstrip("/")
    if not src.exists():
        return "missing", src_rel
    new_rel = re.sub(r"\.(jpg|jpeg|png)$", ".webp", src_rel, flags=re.IGNORECASE)
    new_abs = PUBLIC_DIR / new_rel.lstrip("/")
    if new_abs.exists():
        return "already-converted", new_rel
    try:
        result = subprocess.run(
            [
                "cwebp",
                "-q", "80",
                "-resize", "1920", "0",
                "-quiet",
                str(src),
                "-o", str(new_abs),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"FAILED to convert {src_rel}: {e.stderr}")
        return "convert-error", src_rel
    return "converted", new_rel


def main() -> int:
    if not shutil.which("cwebp"):
        print("ERROR: cwebp not found in PATH. Install via `brew install webp`.")
        return 2

    text = POSTS_TS.read_text(encoding="utf-8")
    paths = find_hero_paths(text)
    print(f"Found {len(paths)} unique hero image paths.\n")

    stats = {"converted": 0, "already-webp": 0, "already-converted": 0, "missing": 0, "convert-error": 0}
    rename_map: dict[str, str] = {}

    for src_rel in sorted(paths):
        status, new_rel = convert(src_rel)
        stats[status] += 1
        if status in {"converted", "already-converted"} and new_rel != src_rel:
            rename_map[src_rel] = new_rel
        # report with old → new size if converted
        if status == "converted":
            old_kb = (PUBLIC_DIR / src_rel.lstrip("/")).stat().st_size // 1024
            new_kb = (PUBLIC_DIR / new_rel.lstrip("/")).stat().st_size // 1024
            saving = round(100 * (1 - new_kb / old_kb)) if old_kb else 0
            print(f"[converted] {src_rel} ({old_kb} KB) → {new_rel} ({new_kb} KB, -{saving}%)")
        else:
            print(f"[{status}] {src_rel}")

    # Update posts.ts in one pass.
    if rename_map:
        for old, new in rename_map.items():
            text = text.replace(f"heroImage: '{old}'", f"heroImage: '{new}'")
        POSTS_TS.write_text(text, encoding="utf-8")
        print(f"\nposts.ts updated: {len(rename_map)} heroImage paths rewritten.")

    print(f"\n=== Summary ===\n{stats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
