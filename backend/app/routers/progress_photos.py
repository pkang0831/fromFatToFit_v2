from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import datetime, timezone
from app.dependencies import get_current_user
from app.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/progress-photos", tags=["progress-photos"])


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
    supabase = get_supabase()

    photo_data = {
        "user_id": user_id,
        "image_base64": image_base64,
        "notes": notes,
        "weight_kg": weight_kg,
        "body_fat_pct": body_fat_pct,
        "taken_at": datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("progress_photos").insert(photo_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save photo")

    return result.data[0]


@router.get("")
async def get_progress_photos(current_user: dict = Depends(get_current_user)):
    """Get all progress photos, newest first."""
    user_id = current_user["id"]
    supabase = get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("id, notes, weight_kg, body_fat_pct, taken_at, created_at")
        .eq("user_id", user_id)
        .order("taken_at", desc=True)
        .execute()
    )

    return result.data or []


@router.get("/{photo_id}")
async def get_progress_photo(
    photo_id: str, current_user: dict = Depends(get_current_user)
):
    """Get a single progress photo with image data."""
    user_id = current_user["id"]
    supabase = get_supabase()

    result = (
        supabase.table("progress_photos")
        .select("*")
        .eq("id", photo_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Photo not found")

    return result.data[0]


@router.delete("/{photo_id}")
async def delete_progress_photo(
    photo_id: str, current_user: dict = Depends(get_current_user)
):
    """Delete a progress photo."""
    user_id = current_user["id"]
    supabase = get_supabase()

    supabase.table("progress_photos").delete().eq("id", photo_id).eq(
        "user_id", user_id
    ).execute()

    return {"message": "Photo deleted"}


@router.get("/compare/{photo_id_1}/{photo_id_2}")
async def compare_photos(
    photo_id_1: str,
    photo_id_2: str,
    current_user: dict = Depends(get_current_user),
):
    """Get two photos for side-by-side comparison."""
    user_id = current_user["id"]
    supabase = get_supabase()

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

    return {
        "before": photos[0],
        "after": photos[1],
        "days_between": None,
        "weight_change": None,
        "bf_change": None,
    }
