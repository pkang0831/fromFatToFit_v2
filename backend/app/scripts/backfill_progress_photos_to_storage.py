"""
One-time migration script: move legacy progress_photos.image_base64 blobs into
private Supabase Storage and persist only storage metadata in the table.

Usage:
    cd backend && python -m app.scripts.backfill_progress_photos_to_storage --dry-run
    cd backend && python -m app.scripts.backfill_progress_photos_to_storage --batch-size 50
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from ..services.progress_photo_backfill import backfill_legacy_progress_photos


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backfill legacy progress photos into private storage")
    parser.add_argument("--batch-size", type=int, default=25, help="Number of legacy rows to migrate per batch")
    parser.add_argument("--max-photos", type=int, default=None, help="Optional cap on number of photos to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Report what would migrate without writing changes")
    parser.add_argument(
        "--keep-legacy",
        action="store_true",
        help="Keep image_base64 after storage upload instead of nulling it out",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = backfill_legacy_progress_photos(
        batch_size=args.batch_size,
        max_photos=args.max_photos,
        keep_legacy=args.keep_legacy,
        dry_run=args.dry_run,
    )

    logger.info("Backfill summary: %s", json.dumps(summary, indent=2))
    return 0 if summary["failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
