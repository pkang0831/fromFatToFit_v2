"""
Generate test-case folders from raw photos.

Runs the existing edit_prep + cut_warp pipeline on each photo and saves
all intermediate masks/images into a structured folder suitable for the
evaluation harness.

Usage:
    python -m backend.app.tools.generate_test_cases \
        --images photo1.jpg photo2.jpg \
        --output-dir test_cases \
        --preset medium
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import logging
import sys
import time
from pathlib import Path

from PIL import Image, ImageOps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


def _encode_jpeg_b64(path: Path) -> str:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img) or img
    img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return base64.b64encode(buf.getvalue()).decode()


def _save_b64_png(b64: str, out: Path) -> None:
    raw = base64.b64decode(b64)
    Image.open(io.BytesIO(raw)).save(out, format="PNG")


def _save_b64_jpeg(b64: str, out: Path) -> None:
    raw = base64.b64decode(b64)
    Image.open(io.BytesIO(raw)).save(out, format="JPEG", quality=95)


async def _generate_one(
    image_path: Path,
    output_dir: Path,
    preset: str,
    intensity: float,
) -> None:
    from backend.app.services.edit_prep import prepare_cut_edit
    from backend.app.services.cut_warp import cut_warp_preview

    case_name = image_path.stem
    case_dir = output_dir / case_name
    case_dir.mkdir(parents=True, exist_ok=True)

    img_b64 = _encode_jpeg_b64(image_path)

    # Save original (with EXIF orientation baked in)
    orig = Image.open(image_path)
    orig = ImageOps.exif_transpose(orig) or orig
    orig.convert("RGB").save(
        case_dir / "original.jpg", format="JPEG", quality=95,
    )

    logger.info(f"[{case_name}] Running edit_prep...")
    t0 = time.monotonic()
    prep = await prepare_cut_edit(img_b64, intensity=intensity)
    prep_ms = round((time.monotonic() - t0) * 1000, 1)

    _save_b64_png(prep.protect_mask_b64, case_dir / "protect_mask.png")
    _save_b64_png(prep.edit_mask_b64, case_dir / "edit_mask.png")
    _save_b64_png(prep.weight_map_b64, case_dir / "weight_map.png")
    _save_b64_png(prep.feather_mask_b64, case_dir / "feather_mask.png")
    _save_b64_png(prep.combined_map_b64, case_dir / "combined_map.png")

    logger.info(f"[{case_name}] Running cut_warp (preset={preset})...")
    t0 = time.monotonic()
    warp = await cut_warp_preview(img_b64, preset=preset, intensity=intensity)
    warp_ms = round((time.monotonic() - t0) * 1000, 1)

    _save_b64_jpeg(warp.warped_image_b64, case_dir / "warped.jpg")
    _save_b64_png(warp.displacement_viz_b64, case_dir / "displacement_viz.png")

    metadata = {
        "source_image": str(image_path),
        "case_name": case_name,
        "preset": preset,
        "intensity": intensity,
        "image_size": [prep.width, prep.height],
        "prep_elapsed_ms": prep_ms,
        "warp_elapsed_ms": warp_ms,
        "prep_debug": prep.debug_info,
        "warp_debug": warp.debug_info,
    }
    (case_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8",
    )

    logger.info(
        f"[{case_name}] Done — prep={prep_ms}ms, warp={warp_ms}ms → {case_dir}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate test-case folders from raw photos",
    )
    parser.add_argument(
        "--images", nargs="+", required=True,
        help="Paths to JPEG/PNG photos",
    )
    parser.add_argument(
        "--output-dir", default="test_cases",
        help="Root directory for test case folders",
    )
    parser.add_argument(
        "--preset", default="medium",
        choices=["mild", "medium", "strong"],
    )
    parser.add_argument(
        "--intensity", type=float, default=0.5,
        help="Edit intensity [0.0, 1.0]",
    )

    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for path_str in args.images:
        p = Path(path_str)
        if not p.exists():
            logger.error(f"File not found: {p}")
            sys.exit(1)

    for path_str in args.images:
        asyncio.run(_generate_one(
            Path(path_str), out_dir, args.preset, args.intensity,
        ))

    logger.info(f"All test cases saved to {out_dir}")


if __name__ == "__main__":
    main()
