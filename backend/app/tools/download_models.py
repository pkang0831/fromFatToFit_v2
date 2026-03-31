"""
CLI tool for downloading, verifying, and warming up CPU diffusion models.

Usage:
    python -m backend.app.tools.download_models download --profile sd15_only
    python -m backend.app.tools.download_models download --profile all
    python -m backend.app.tools.download_models verify
    python -m backend.app.tools.download_models warmup [--backend sd15_inpaint_cpu]
    python -m backend.app.tools.download_models test-refine --image path/to/photo.jpg
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


def cmd_download(args: argparse.Namespace) -> None:
    from backend.app.services.diffusion.download import download_profile, DownloadError
    from backend.app.config import settings

    token = args.token or settings.hf_token or None
    cache_dir = Path(args.cache_dir) if args.cache_dir else (
        Path(settings.hf_cache_dir) if settings.hf_cache_dir else None
    )

    logger.info(f"Download profile: {args.profile}")
    try:
        results = download_profile(args.profile, token=token, cache_dir=cache_dir)
    except (DownloadError, ValueError) as exc:
        logger.error(str(exc))
        sys.exit(1)

    for r in results:
        logger.info(f"  {r.key}: → {r.local_path} (~{r.size_gb} GB)")
    logger.info(f"Done — {len(results)} model(s) ready.")


def cmd_verify(args: argparse.Namespace) -> None:
    from backend.app.services.diffusion.download import verify_all_models
    from backend.app.config import settings

    cache_dir = Path(args.cache_dir) if args.cache_dir else (
        Path(settings.hf_cache_dir) if settings.hf_cache_dir else None
    )

    results = verify_all_models(cache_dir=cache_dir)
    for r in results:
        icon = "OK" if r["status"] == "cached" else "MISSING"
        logger.info(f"  [{icon}]  {r['key']}: {r['status']}  {r.get('local_path', '')}")

    all_ok = all(r["status"] == "cached" for r in results)
    sys.exit(0 if all_ok else 1)


def cmd_warmup(args: argparse.Namespace) -> None:
    from backend.app.services.diffusion.loader import get_backend
    from backend.app.config import settings

    key = args.backend or settings.body_diffusion_backend
    logger.info(f"Warming up: {key}")

    t0 = time.monotonic()
    try:
        backend = get_backend(key, force_new=True)
        backend.load()
    except Exception as exc:
        logger.error(f"Warmup failed: {exc}")
        sys.exit(1)

    elapsed = round(time.monotonic() - t0, 1)
    logger.info(f"Backend '{key}' ready in {elapsed}s")
    logger.info(json.dumps(backend.get_debug_info(), indent=2))

    backend.unload()
    logger.info("Unloaded.  Warmup complete.")


def cmd_test_refine(args: argparse.Namespace) -> None:
    """Quick smoke test: load an image, build dummy masks, run one refine pass."""
    import asyncio
    import base64
    from PIL import Image
    import io
    import numpy as np

    image_path = Path(args.image)
    if not image_path.exists():
        logger.error(f"Image not found: {image_path}")
        sys.exit(1)

    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    logger.info(f"Test image: {image_path} ({w}x{h})")

    # Encode image
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92)
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    # Build a simple centered rectangle as edit_mask (middle 50% of image)
    edit = np.zeros((h, w), dtype=np.uint8)
    y0, y1 = h // 4, 3 * h // 4
    x0, x1 = w // 4, 3 * w // 4
    edit[y0:y1, x0:x1] = 255

    # Protect = everything outside the edit rectangle
    protect = 255 - edit

    # Weight map: simple gradient within edit zone
    weight = np.zeros((h, w), dtype=np.uint8)
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        weight[y, x0:x1] = int(t * 200)

    # Feather mask: all ones inside edit zone
    feather = np.zeros((h, w), dtype=np.uint8)
    feather[y0:y1, x0:x1] = 255

    def encode_mask(arr):
        buf = io.BytesIO()
        Image.fromarray(arr, mode="L").save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    from backend.app.services.cut_refine import cut_refine

    result = asyncio.run(cut_refine(
        warped_image_b64=img_b64,
        edit_mask_b64=encode_mask(edit),
        protect_mask_b64=encode_mask(protect),
        weight_map_b64=encode_mask(weight),
        feather_mask_b64=encode_mask(feather),
        preset=args.preset,
        seed=42,
    ))

    # Save result
    out_path = image_path.parent / f"{image_path.stem}_refined.jpg"
    raw = base64.b64decode(result.refined_image_b64)
    Image.open(io.BytesIO(raw)).save(out_path, quality=92)

    logger.info(f"Refined image saved: {out_path}")
    logger.info(f"Debug: {json.dumps(result.debug_info, indent=2)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage CPU diffusion models for body-cut refinement",
    )
    sub = parser.add_subparsers(dest="command")

    dl = sub.add_parser("download", help="Download models by profile")
    dl.add_argument(
        "--profile", required=True,
        choices=["sd15_only", "sd2_only", "all"],
    )
    dl.add_argument("--token", default="")
    dl.add_argument("--cache-dir", default="")

    vf = sub.add_parser("verify", help="Verify cached models")
    vf.add_argument("--cache-dir", default="")

    wu = sub.add_parser("warmup", help="Load backend into memory, then unload")
    wu.add_argument(
        "--backend", default="",
        choices=["sd15_inpaint_cpu", "sd2_inpaint_cpu", "sd15_inpaint_openvino", ""],
    )

    tr = sub.add_parser("test-refine", help="Run one refinement on a test image")
    tr.add_argument("--image", required=True, help="Path to a JPEG/PNG photo")
    tr.add_argument("--preset", default="medium", choices=["mild", "medium", "strong"])

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    {
        "download": cmd_download,
        "verify": cmd_verify,
        "warmup": cmd_warmup,
        "test-refine": cmd_test_refine,
    }[args.command](args)


if __name__ == "__main__":
    main()
