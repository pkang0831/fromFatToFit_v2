from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import datetime, timezone
from app.dependencies import get_current_user
from app.database import get_supabase, get_user_supabase
from app.config import settings
from app.services.progress_photo_storage import (
    build_progress_photo_url,
    delete_progress_image,
    upload_progress_image,
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/progress-photos", tags=["progress-photos"])


def _storage_kwargs(access_token: str | None) -> dict:
    return {"access_token": access_token} if access_token else {}


def _legacy_image_url(image_base64: str | None) -> str | None:
    if not image_base64:
        return None
    return f"data:image/jpeg;base64,{image_base64}"


def _serialize_progress_photo(
    row: dict,
    *,
    include_legacy_base64: bool = False,
    access_token: str | None = None,
) -> dict:
    serialized = dict(row)
    storage_key = serialized.get("storage_key")
    storage_bucket = serialized.get("storage_bucket") or settings.progress_photo_storage_bucket
    legacy_base64 = serialized.get("image_base64")

    if storage_key:
        serialized["image_url"] = build_progress_photo_url(
            storage_key,
            storage_bucket,
            access_token=access_token,
        )
        serialized.pop("image_base64", None)
    else:
        serialized["image_url"] = _legacy_image_url(legacy_base64)
        if not include_legacy_base64:
            serialized.pop("image_base64", None)

    return serialized


@router.post("")
async def upload_progress_photo(
    image_base64: str = Body(..., embed=True),
    notes: str = Body("", embed=True),
    weight_kg: float = Body(None, embed=True),
    body_fat_pct: float = Body(None, embed=True),
    current_user: dict = Depends(get_current_user),
):
    """Upload a progress photo with optional metadata."""
    user_id = current_user["id"]
    access_token = current_user.get("access_token")
    supabase = get_user_supabase(access_token) if access_token else get_supabase()
    try:
        storage = upload_progress_image(user_id, image_base64, **_storage_kwargs(access_token))
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Progress photo storage upload failed for %s", user_id, exc_info=True)
        raise HTTPException(status_code=503, detail="Progress photo storage is unavailable") from exc

    photo_data = {
        "user_id": user_id,
        "image_base64": None,
        "storage_bucket": storage["storage_bucket"],
        "storage_key": storage["storage_key"],
        "notes": notes,
        "weight_kg": weight_kg,
        "body_fat_pct": body_fat_pct,
        "taken_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        result = supabase.table("progress_photos").insert(photo_data).execute()
    except Exception:
        try:
            delete_progress_image(
                storage["storage_key"],
                storage["storage_bucket"],
                **_storage_kwargs(access_token),
            )
        except Exception:
            logger.warning("Failed to clean up uploaded progress photo after DB insert error", exc_info=True)
        raise

    if not result.data:
        try:
            delete_progress_image(
                storage["storage_key"],
                storage["storage_bucket"],
                **_storage_kwargs(access_token),
            )
        except Exception:
            logger.warning("Failed to clean up uploaded progress photo after empty DB insert result", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save photo")

    return _serialize_progress_photo(result.data[0], access_token=access_token)


@router.get("")
async def get_progress_photos(current_user: dict = Depends(get_current_user)):
    """Get all progress photos, newest first."""
    user_id = current_user["id"]
    access_token = current_user.get("access_token")
    supabase = get_user_supabase(access_token) if access_token else get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("id, notes, weight_kg, body_fat_pct, taken_at, created_at, storage_bucket, storage_key")
        .eq("user_id", user_id)
        .order("taken_at", desc=True)
        .execute()
    )

    return [_serialize_progress_photo(row, access_token=access_token) for row in (result.data or [])]


@router.get("/{photo_id}")
async def get_progress_photo(
    photo_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a single progress photo with image data."""
    user_id = current_user["id"]
    access_token = current_user.get("access_token")
    supabase = get_user_supabase(access_token) if access_token else get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("*")
        .eq("id", photo_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Photo not found")

    return _serialize_progress_photo(
        result.data[0],
        include_legacy_base64=True,
        access_token=access_token,
    )


@router.delete("/{photo_id}")
async def delete_progress_photo(
    photo_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a progress photo."""
    user_id = current_user["id"]
    access_token = current_user.get("access_token")
    supabase = get_user_supabase(access_token) if access_token else get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("id, storage_bucket, storage_key")
        .eq("id", photo_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo = result.data[0]
    try:
        supabase.table("proof_shares").delete().eq("progress_photo_id", photo_id).eq("user_id", user_id).execute()
    except Exception:
        logger.warning("Failed to revoke proof shares for deleted progress photo %s", photo_id, exc_info=True)
    if photo.get("storage_key"):
        delete_progress_image(
            photo["storage_key"],
            photo.get("storage_bucket") or settings.progress_photo_storage_bucket,
            **_storage_kwargs(access_token),
        )

    supabase.table("progress_photos").delete().eq("id", photo_id).eq("user_id", user_id).execute()

    return {"message": "Photo deleted"}


@router.get("/compare/{photo_id_1}/{photo_id_2}")
async def compare_photos(
    photo_id_1: str,
    photo_id_2: str,
    current_user: dict = Depends(get_current_user),
):
    """Get two photos for side-by-side comparison."""
    user_id = current_user["id"]
    access_token = current_user.get("access_token")
    supabase = get_user_supabase(access_token) if access_token else get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("*")
        .eq("user_id", user_id)
        .in_("id", [photo_id_1, photo_id_2])
        .execute()
    )

    if not result.data or len(result.data) < 2:
        raise HTTPException(status_code=404, detail="One or both photos not found")

    photos = sorted(result.data, key=lambda x: x["taken_at"])
    before = _serialize_progress_photo(
        photos[0],
        include_legacy_base64=True,
        access_token=access_token,
    )
    after = _serialize_progress_photo(
        photos[1],
        include_legacy_base64=True,
        access_token=access_token,
    )

    days_between = None
    try:
        before_taken = datetime.fromisoformat(photos[0]["taken_at"].replace("Z", "+00:00"))
        after_taken = datetime.fromisoformat(photos[1]["taken_at"].replace("Z", "+00:00"))
        days_between = (after_taken.date() - before_taken.date()).days
    except Exception:
        logger.warning("Unable to compute days_between for progress compare", exc_info=True)

    weight_change = None
    if photos[0].get("weight_kg") is not None and photos[1].get("weight_kg") is not None:
        weight_change = photos[1]["weight_kg"] - photos[0]["weight_kg"]

    bf_change = None
    if photos[0].get("body_fat_pct") is not None and photos[1].get("body_fat_pct") is not None:
        bf_change = photos[1]["body_fat_pct"] - photos[0]["body_fat_pct"]

    return {
        "before": before,
        "after": after,
        "days_between": days_between,
        "weight_change": weight_change,
        "bf_change": bf_change,
    }
