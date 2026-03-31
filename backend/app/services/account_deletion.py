import logging
from collections import defaultdict
from typing import Any

from fastapi import HTTPException, status

from ..config import settings
from ..database import get_supabase
from .payment_service import get_subscription_diagnostics

logger = logging.getLogger(__name__)

ACCOUNT_DATA_DELETED_IMMEDIATELY = [
    "Your Supabase authentication account",
    "Profile and onboarding data stored in user_profiles",
    "Stored progress photo files in the private progress-photos-private bucket and their progress_photos rows",
    "Body scan history, saved goal plans, challenge data, streak data, and usage/credit records tied to your user_id",
    "Food logs, workout logs, weight logs, fasting sessions, daily summaries, notification preferences, push subscriptions, and AI coach chat rows tied to your user_id",
]

ACCOUNT_DATA_RETAINED_OUTSIDE_APP = [
    "Stripe, RevenueCat, Apple, or Google may keep billing and transaction records under their own legal and operational policies",
    "Third-party AI providers may keep submitted inputs under their own retention policies; this delete flow does not delete provider-side copies",
    "Operational logs outside user tables may retain limited metadata for security and debugging",
]

ACCOUNT_DELETION_BLOCKERS = [
    "Active paid subscriptions must be canceled before account deletion because this flow does not cancel billing with Stripe or app stores",
]

def build_account_deletion_summary() -> dict[str, Any]:
    return {
        "message": "Your Denevira account and app data were deleted.",
        "deleted_immediately": list(ACCOUNT_DATA_DELETED_IMMEDIATELY),
        "retained_outside_app": list(ACCOUNT_DATA_RETAINED_OUTSIDE_APP),
        "blocking_requirements": list(ACCOUNT_DELETION_BLOCKERS),
    }
def _delete_progress_photo_objects(supabase: Any, user_id: str) -> None:
    result = (
        supabase.table("progress_photos")
        .select("storage_bucket, storage_key")
        .eq("user_id", user_id)
        .execute()
    )
    rows = result.data or []

    storage_paths_by_bucket: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        storage_key = row.get("storage_key")
        if not storage_key:
            continue
        bucket = row.get("storage_bucket") or settings.progress_photo_storage_bucket
        storage_paths_by_bucket[bucket].append(storage_key)

    for bucket_name, paths in storage_paths_by_bucket.items():
        if not paths:
            continue
        logger.info("Deleting %s progress photo objects from bucket %s for user %s", len(paths), bucket_name, user_id)
        supabase.storage.from_(bucket_name).remove(paths)


async def delete_user_account(current_user: dict) -> dict[str, Any]:
    user_id = current_user["id"]
    supabase = get_supabase()

    diagnostics = await get_subscription_diagnostics(user_id)
    if diagnostics.get("deletion_blocked"):
        detail = (
            "We could not confirm that billing is fully canceled. "
            "Use Manage billing first, then try account deletion again."
            if diagnostics.get("deletion_block_reason") == "billing_state_mismatch_requires_reconciliation"
            else (
                "Cancel or resolve your current subscription billing before deleting your account. "
                "This delete flow does not cancel Stripe or app-store billing."
            )
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    try:
        _delete_progress_photo_objects(supabase, user_id)
        supabase.auth.admin.delete_user(user_id, should_soft_delete=False)
        logger.info("Deleted account for user %s", user_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete account for user %s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        ) from exc

    return build_account_deletion_summary()
