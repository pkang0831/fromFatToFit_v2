#!/usr/bin/env python3
"""
Fix the "photos are rotated sideways / upside-down" bug on the blog.

Root cause: source JPEGs (shot on phones in portrait) had EXIF
Orientation != 1 (typically 6 = rotate 90° CW, or 8 = rotate 90°
CCW). When they were converted to WebP in an earlier session via
cwebp *without* pre-rotating the pixel data, the WebP pixels ended
up in raw-sensor orientation. Browsers don't reliably honor EXIF
orientation on WebP, so they display the pixel matrix as-is — which
is sideways or upside-down.

Fix: reload each source JPEG with PIL.ImageOps.exif_transpose()
(which physically rotates/flips the pixel matrix per the EXIF tag),
resize to max-width 1600, save as WebP at quality 72 (matches
reencode_heavy_webp_20260422.py). Overwrites the existing WebP in
place after backing it up.

Idempotent: if the source JPEG already has Orientation == 1 AND the
existing WebP already matches the JPEG's aspect ratio, skip.
"""

from __future__ import annotations
import re
import shutil
from pathlib import Path
from PIL import Image, ImageOps, ExifTags

ROOT = Path(__file__).resolve().parents[2]
POSTS_TS = ROOT / "frontend/src/content/blog/posts.ts"
PUBLIC_DIR = ROOT / "frontend/public"

QUALITY = 72
MAX_WIDTH = 1600


def get_exif_orientation(img: Image.Image) -> int:
    try:
        raw = img.getexif()
        if not raw:
            return 1
        for k, v in raw.items():
            if ExifTags.TAGS.get(k) == "Orientation":
                return int(v) if v else 1
    except Exception:
        pass
    return 1


def reencode_one(webp_path: Path) -> tuple[str, dict]:
    jpg_path = webp_path.with_suffix(".jpg")
    if not jpg_path.exists():
        jpg_path = webp_path.with_suffix(".jpeg")
    if not jpg_path.exists():
        return "no-source-jpg", {}

    with Image.open(jpg_path) as jpg:
        ori = get_exif_orientation(jpg)
        src_w, src_h = jpg.size
        # Physically apply EXIF rotation to the pixel matrix.
        fixed = ImageOps.exif_transpose(jpg)
        fw, fh = fixed.size
        # Resize to MAX_WIDTH if wider
        if fw > MAX_WIDTH:
            new_h = int(fh * MAX_WIDTH / fw)
            fixed = fixed.resize((MAX_WIDTH, new_h), Image.LANCZOS)
        out_w, out_h = fixed.size

        # Compare old webp dims to the about-to-write dims
        old_size = webp_path.stat().st_size if webp_path.exists() else 0
        old_dims = None
        if webp_path.exists():
            with Image.open(webp_path) as oldw:
                old_dims = oldw.size

        # Back up old webp
        if webp_path.exists():
            bak = webp_path.with_suffix(".orient-bak.webp")
            if not bak.exists():
                shutil.copy2(webp_path, bak)

        # Convert to RGB before webp save (in case JPG has CMYK/mode issues)
        if fixed.mode not in ("RGB", "RGBA"):
            fixed = fixed.convert("RGB")
        fixed.save(webp_path, format="WebP", quality=QUALITY, method=4)
        new_size = webp_path.stat().st_size

    return ("reencoded", {
        "source_ori": ori,
        "src_dims": (src_w, src_h),
        "old_webp_dims": old_dims,
        "new_webp_dims": (out_w, out_h),
        "old_kb": old_size // 1024,
        "new_kb": new_size // 1024,
    })


def main() -> None:
    text = POSTS_TS.read_text()
    hero_paths = sorted(set(re.findall(r"heroImage: '(/founder/[^']+)'", text)))

    stats = {"reencoded": 0, "no-source-jpg": 0}
    for rel in hero_paths:
        webp = PUBLIC_DIR / rel.lstrip("/")
        status, info = reencode_one(webp)
        stats[status] = stats.get(status, 0) + 1
        if status == "reencoded":
            rotated = "ROTATED" if info["source_ori"] != 1 else "upright"
            old_dims = info.get("old_webp_dims")
            new_dims = info.get("new_webp_dims")
            flipped = old_dims and new_dims and (old_dims[0] != new_dims[0] or old_dims[1] != new_dims[1])
            flip_mark = " *dims-flipped*" if flipped else ""
            print(
                f"[reencoded {rotated:>7}] ori={info['source_ori']} "
                f"{info.get('src_dims')} -> {info.get('new_webp_dims')}  "
                f"{info['old_kb']}KB -> {info['new_kb']}KB{flip_mark}  {webp.name}"
            )
        else:
            print(f"[{status}] {webp.name}")

    print(f"\n=== Summary: {stats} ===")


if __name__ == "__main__":
    main()
