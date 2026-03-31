#!/usr/bin/env python3
"""
Run Fashn human-parser on a local image and save overlay + stats.

Usage (from ``backend/``)::

    PYTHONPATH=. python -m app.tools.visualize_fashn_segmentation ../sample_image.jpg

Output: ``backend/tmp/fashn_preview/<stem>_segmentation_preview.png`` and ``_legend.txt``.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

_CLASS_COLORS_RGBA = [
    (0, 0, 0, 0),
    (255, 180, 160, 200),
    (120, 200, 255, 180),
    (80, 160, 255, 180),
    (255, 220, 100, 160),
    (255, 200, 80, 160),
    (180, 255, 140, 160),
    (140, 255, 180, 160),
]


def _colorize_labels(label_u8: np.ndarray) -> Image.Image:
    h, w = label_u8.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    for cid in range(8):
        sel = label_u8 == cid
        if not np.any(sel):
            continue
        rgba[sel] = _CLASS_COLORS_RGBA[cid]
    return Image.fromarray(rgba, mode="RGBA")


async def _run(image_path: Path, out_dir: Path) -> None:
    from app.services.fashn_human_parser import FashnHumanParserSegmenter
    from app.services.segmenter_interface import SEG_CLASSES

    raw = image_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")

    seg = FashnHumanParserSegmenter()
    result = await seg.segment(b64)

    buf = io.BytesIO(base64.b64decode(result.label_map_b64))
    label_map = np.array(Image.open(buf).convert("L"), dtype=np.uint8)

    fg_buf = io.BytesIO(base64.b64decode(result.foreground_mask_b64))
    fg_mask = np.array(Image.open(fg_buf).convert("L")) > 127

    w, h = result.width, result.height
    total = float(w * h)
    fg_ratio = float(fg_mask.sum()) / total if total else 0.0

    dbg = result.debug_info or {}
    lines = [
        f"image: {image_path} ({w}x{h})",
        f"foreground_pixels (label>0): {dbg.get('foreground_pixels', int(fg_mask.sum()))}",
        f"foreground_ratio: {fg_ratio:.4f}",
        f"fashn_unique_labels: {dbg.get('fashn_unique_labels')}",
        f"assigned_classes: {dbg.get('assigned_classes')}",
        f"pose_detected: {dbg.get('pose_detected')}",
        f"elapsed_ms: {dbg.get('elapsed_ms')}",
        "",
        "SEG_CLASSES:",
    ]
    for c in SEG_CLASSES:
        lines.append(f"  {c['id']}: {c['key']} — {c['label']}")

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem

    legend_path = out_dir / f"{stem}_legend.txt"
    legend_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    orig = Image.open(io.BytesIO(raw)).convert("RGB")
    orig = ImageOps.exif_transpose(orig) or orig
    if orig.size != (w, h):
        orig = orig.resize((w, h), Image.Resampling.BICUBIC)

    label_rgba = _colorize_labels(label_map)
    overlay = Image.alpha_composite(orig.convert("RGBA"), label_rgba)

    gray = Image.new("RGB", (w, h), (40, 40, 45))
    label_only = Image.alpha_composite(gray.convert("RGBA"), label_rgba).convert("RGB")

    fg_rgba = np.zeros((h, w, 4), dtype=np.uint8)
    fg_rgba[fg_mask] = (255, 80, 80, 140)
    fg_overlay = Image.alpha_composite(orig.convert("RGBA"), Image.fromarray(fg_rgba, mode="RGBA")).convert(
        "RGB"
    )

    combined = Image.new("RGB", (w * 3 + 40, h + 40), (15, 15, 20))
    combined.paste(orig, (10, 30))
    combined.paste(label_only, (w + 20, 30))
    combined.paste(overlay, (2 * w + 30, 30))

    try:
        dr = ImageDraw.Draw(combined)
        font = ImageFont.load_default()
        for i, txt in enumerate(["Original", "8-class map", "Overlay"]):
            dr.text((10 + i * (w + 10), 8), txt, fill=(220, 220, 230), font=font)
    except Exception:
        pass

    out_png = out_dir / f"{stem}_segmentation_preview.png"
    combined.save(out_png, format="PNG", optimize=True)

    fg_small = out_dir / f"{stem}_foreground_mask.png"
    Image.fromarray((fg_mask.astype(np.uint8) * 255), mode="L").save(fg_small)

    print("\n".join(lines))
    print(f"\nSaved: {out_png}")
    print(f"Saved: {legend_path}")
    print(f"Saved: {fg_small}")


def main() -> None:
    p = argparse.ArgumentParser(description="Visualize Fashn segmentation on a local image.")
    p.add_argument(
        "image",
        type=Path,
        nargs="?",
        default=Path(__file__).resolve().parents[3] / "sample_image.jpg",
        help="Path to JPEG/PNG",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=_BACKEND / "tmp" / "fashn_preview",
        help="Output directory",
    )
    args = p.parse_args()

    if not args.image.is_file():
        print(f"File not found: {args.image.resolve()}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(_run(args.image, args.out))


if __name__ == "__main__":
    main()
