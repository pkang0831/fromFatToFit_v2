import logging
from collections.abc import Callable
from typing import Any

from ..config import settings
from ..database import get_supabase
from .progress_photo_storage import upload_progress_image

logger = logging.getLogger(__name__)


def _fetch_legacy_batch(supabase: Any, batch_size: int) -> list[dict[str, Any]]:
    result = (
        supabase.table("progress_photos")
        .select("id, user_id, image_base64, storage_bucket, storage_key, created_at")
        .is_("storage_key", "null")
        .order("created_at")
        .limit(batch_size)
        .execute()
    )

    rows = result.data or []
    return [row for row in rows if row.get("image_base64")]


def backfill_legacy_progress_photos(
    *,
    batch_size: int = 25,
    max_photos: int | None = None,
    keep_legacy: bool = False,
    dry_run: bool = False,
    upload_fn: Callable[[str, str], dict[str, str]] = upload_progress_image,
) -> dict[str, Any]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    if max_photos is not None and max_photos <= 0:
        raise ValueError("max_photos must be positive when provided")

    supabase = get_supabase()
    scanned = 0
    migrated = 0
    failures = 0
    skipped = 0
    migrated_ids: list[str] = []
    failed_ids: list[str] = []

    while True:
        remaining = None if max_photos is None else max(max_photos - migrated, 0)
        if remaining == 0:
            break

        current_batch_size = batch_size if remaining is None else min(batch_size, remaining)
        rows = _fetch_legacy_batch(supabase, current_batch_size)
        if not rows:
            break

        scanned += len(rows)

        for row in rows:
            photo_id = row["id"]
            user_id = row["user_id"]

            if row.get("storage_key"):
                skipped += 1
                continue

            if dry_run:
                migrated += 1
                migrated_ids.append(photo_id)
                logger.info("[dry-run] would migrate progress photo %s", photo_id)
                continue

            try:
                storage = upload_fn(user_id, row["image_base64"])
                update_payload = {
                    "storage_bucket": storage.get("storage_bucket") or settings.progress_photo_storage_bucket,
                    "storage_key": storage["storage_key"],
                }
                if not keep_legacy:
                    update_payload["image_base64"] = None

                supabase.table("progress_photos").update(update_payload).eq("id", photo_id).execute()
                migrated += 1
                migrated_ids.append(photo_id)
                logger.info("Migrated progress photo %s to storage key %s", photo_id, storage["storage_key"])
            except Exception as exc:
                failures += 1
                failed_ids.append(photo_id)
                logger.exception("Failed to backfill progress photo %s: %s", photo_id, exc)

        if len(rows) < current_batch_size:
            break

    return {
        "scanned": scanned,
        "migrated": migrated,
        "skipped": skipped,
        "failures": failures,
        "dry_run": dry_run,
        "keep_legacy": keep_legacy,
        "migrated_ids": migrated_ids,
        "failed_ids": failed_ids,
    }
