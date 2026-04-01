import base64
import logging
from datetime import datetime, timezone
from secrets import token_urlsafe
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, Response

from app.dependencies import get_current_user
from ..database import get_supabase
from ..schemas.proof_share_schemas import (
    CreateProofShareRequest,
    ProofShareResponse,
    PublicProofShareResponse,
)
from ..services.progress_photo_storage import build_progress_photo_url
from ..services.retention_event_service import log_retention_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/proof-shares", tags=["proof-shares"])


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _public_share_url(token: str) -> str:
    from ..config import settings

    return f"{settings.public_app_url.rstrip('/')}/proof/{token}"


def _public_share_image_url(token: str) -> str:
    from ..config import settings

    return f"{settings.public_api_url.rstrip('/')}/proof-shares/public/{token}/image"


def _public_share_try_url(token: str) -> str:
    from ..config import settings

    return f"{settings.public_api_url.rstrip('/')}/proof-shares/public/{token}/try"


def _goal_snapshot_for_user(supabase: Any, user_id: str) -> dict[str, float | None]:
    current_bf = None
    target_bf = None

    profile_result = (
        supabase.table("user_profiles")
        .select("target_body_fat_percentage")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if profile_result.data:
        target_bf = _to_float(profile_result.data[0].get("target_body_fat_percentage"))

    scans_result = (
        supabase.table("body_scans")
        .select("scan_type, result_data, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )
    for scan in scans_result.data or []:
        if scan.get("scan_type") not in {"bodyfat", "percentile"}:
            continue
        result_data = scan.get("result_data") or {}
        bf = _to_float(result_data.get("body_fat_percentage"))
        if bf is not None:
            current_bf = bf

    gap = None
    if current_bf is not None and target_bf is not None:
        gap = round(current_bf - target_bf, 1)

    return {
        "current_bf_snapshot": current_bf,
        "target_bf_snapshot": target_bf,
        "goal_gap_snapshot": gap,
    }


def _serialize_share(row: dict[str, Any]) -> ProofShareResponse:
    status_value = "revoked" if row.get("revoked_at") or row.get("status") == "revoked" else "active"
    return ProofShareResponse(
        id=row["id"],
        token=row["token"],
        progress_photo_id=row["progress_photo_id"],
        week_marker=row.get("week_marker"),
        status=status_value,
        created_at=row["created_at"],
        revoked_at=row.get("revoked_at"),
        public_url=_public_share_url(row["token"]),
        image_url=_public_share_image_url(row["token"]),
        referred_try_url=_public_share_try_url(row["token"]),
        goal_summary={
            "current_bf": _to_float(row.get("current_bf_snapshot")),
            "target_bf": _to_float(row.get("target_bf_snapshot")),
            "gap": _to_float(row.get("goal_gap_snapshot")),
        },
        photo_summary={
            "progress_photo_id": row["progress_photo_id"],
            "taken_at": row.get("shared_photo_taken_at"),
            "weight_kg": _to_float(row.get("shared_photo_weight_kg")),
            "body_fat_pct": _to_float(row.get("shared_photo_body_fat_pct")),
        },
    )


def _load_share_for_owner(supabase: Any, user_id: str, share_id: str) -> dict[str, Any]:
    result = (
        supabase.table("proof_shares")
        .select("*")
        .eq("id", share_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Share not found")
    return dict(result.data[0])


def _load_public_share_context(supabase: Any, token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    share_result = (
        supabase.table("proof_shares")
        .select("*")
        .eq("token", token)
        .limit(1)
        .execute()
    )
    if not share_result.data:
        raise HTTPException(status_code=404, detail="Share not found")

    share = dict(share_result.data[0])
    if share.get("status") != "active" or share.get("revoked_at"):
        raise HTTPException(status_code=404, detail="Share not found")

    photo_result = (
        supabase.table("progress_photos")
        .select("id, taken_at, weight_kg, body_fat_pct, storage_bucket, storage_key, image_base64")
        .eq("id", share["progress_photo_id"])
        .limit(1)
        .execute()
    )
    if not photo_result.data:
        raise HTTPException(status_code=404, detail="Share not found")

    return share, dict(photo_result.data[0])


@router.post("", response_model=ProofShareResponse)
async def create_proof_share(
    body: CreateProofShareRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    supabase = get_supabase()

    photo_result = (
        supabase.table("progress_photos")
        .select("id, taken_at, weight_kg, body_fat_pct")
        .eq("id", body.progress_photo_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not photo_result.data:
        raise HTTPException(status_code=404, detail="Progress photo not found")

    existing = (
        supabase.table("proof_shares")
        .select("*")
        .eq("user_id", user_id)
        .eq("progress_photo_id", body.progress_photo_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if existing.data:
        return _serialize_share(dict(existing.data[0]))

    photo = dict(photo_result.data[0])
    snapshot = _goal_snapshot_for_user(supabase, user_id)
    now = datetime.now(timezone.utc).isoformat()
    share_row = {
        "user_id": user_id,
        "progress_photo_id": body.progress_photo_id,
        "token": token_urlsafe(18),
        "week_marker": body.week_marker,
        "status": "active",
        "created_at": now,
        "revoked_at": None,
        "current_bf_snapshot": snapshot["current_bf_snapshot"],
        "target_bf_snapshot": snapshot["target_bf_snapshot"],
        "goal_gap_snapshot": snapshot["goal_gap_snapshot"],
        "shared_photo_taken_at": photo.get("taken_at"),
        "shared_photo_weight_kg": photo.get("weight_kg"),
        "shared_photo_body_fat_pct": photo.get("body_fat_pct"),
    }

    result = supabase.table("proof_shares").insert(share_row).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create share")

    share = dict(result.data[0])
    await log_retention_event(
        user_id,
        "share_created",
        "progress_page",
        {
            "share_id": share["id"],
            "share_token": share["token"],
            "progress_photo_id": share["progress_photo_id"],
            "week_marker": share.get("week_marker"),
            "source": body.source or "proof_share",
            "reentry_state": body.reentry_state,
            "surface_state": body.surface_state,
            "reminder_event_id": body.reminder_event_id,
            "session_id": body.session_id,
        },
    )
    return _serialize_share(share)


@router.get("", response_model=list[ProofShareResponse])
async def list_proof_shares(
    progress_photo_id: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    supabase = get_supabase()
    query = (
        supabase.table("proof_shares")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
    )
    if progress_photo_id:
        query = query.eq("progress_photo_id", progress_photo_id)
    result = query.execute()
    return [_serialize_share(dict(row)) for row in (result.data or [])]


@router.delete("/{share_id}")
async def revoke_proof_share(
    share_id: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    supabase = get_supabase()
    share = _load_share_for_owner(supabase, user_id, share_id)

    if share.get("status") == "revoked" or share.get("revoked_at"):
        return {"message": "Share revoked"}

    revoked_at = datetime.now(timezone.utc).isoformat()
    result = (
        supabase.table("proof_shares")
        .update({"status": "revoked", "revoked_at": revoked_at})
        .eq("id", share_id)
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to revoke share")

    await log_retention_event(
        user_id,
        "share_revoked",
        "progress_page",
        {
            "share_id": share_id,
            "share_token": share.get("token"),
            "progress_photo_id": share.get("progress_photo_id"),
            "source": "proof_share",
        },
    )
    return {"message": "Share revoked"}


@router.get("/public/{token}", response_model=PublicProofShareResponse)
async def get_public_proof_share(token: str, session_id: str | None = None):
    supabase = get_supabase()
    share, _photo = _load_public_share_context(supabase, token)

    await log_retention_event(
        None,
        "share_viewed",
        "proof_share_public",
        {
            "owner_user_id": share["user_id"],
            "source": "proof_share",
            "session_id": session_id,
            "share_id": share["id"],
            "share_token": share["token"],
            "progress_photo_id": share["progress_photo_id"],
            "week_marker": share.get("week_marker"),
        },
    )

    serialized = _serialize_share(share)
    return PublicProofShareResponse(
        token=serialized.token,
        public_url=serialized.public_url,
        image_url=serialized.image_url,
        referred_try_url=serialized.referred_try_url,
        week_marker=serialized.week_marker,
        goal_summary=serialized.goal_summary,
        photo_summary=serialized.photo_summary,
    )


@router.get("/public/{token}/image")
async def get_public_proof_share_image(token: str):
    supabase = get_supabase()
    _share, photo = _load_public_share_context(supabase, token)

    if photo.get("storage_key"):
        signed_url = build_progress_photo_url(
            photo["storage_key"],
            photo.get("storage_bucket"),
        )
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(signed_url)
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="Failed to load shared image")

        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "image/jpeg"),
            headers={"Cache-Control": "no-store"},
        )

    legacy_base64 = photo.get("image_base64")
    if legacy_base64:
        return Response(
            content=base64.b64decode(legacy_base64),
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )

    raise HTTPException(status_code=404, detail="Share not found")


@router.get("/public/{token}/try")
async def start_referred_try(token: str, session_id: str | None = None):
    supabase = get_supabase()
    share, _photo = _load_public_share_context(supabase, token)

    await log_retention_event(
        None,
        "referred_try_started",
        "proof_share_public",
        {
            "owner_user_id": share["user_id"],
            "source": "proof_share",
            "session_id": session_id,
            "share_id": share["id"],
            "share_token": share["token"],
            "progress_photo_id": share["progress_photo_id"],
        },
    )

    from ..config import settings

    redirect_url = f"{settings.public_app_url.rstrip('/')}/try?source=proof_share&share_token={token}"
    if session_id:
        redirect_url = f"{redirect_url}&session_id={session_id}"
    return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
