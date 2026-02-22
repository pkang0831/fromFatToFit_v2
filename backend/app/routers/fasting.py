from fastapi import APIRouter, Depends, HTTPException, Body
from datetime import datetime, timezone, timedelta
from app.dependencies import get_current_user
from app.database import get_supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/fasting", tags=["fasting"])

PRESETS = {
    "16:8": {"fast_hours": 16, "eat_hours": 8},
    "18:6": {"fast_hours": 18, "eat_hours": 6},
    "20:4": {"fast_hours": 20, "eat_hours": 4},
    "14:10": {"fast_hours": 14, "eat_hours": 10},
    "5:2": {"fast_hours": 0, "eat_hours": 0, "description": "Eat normally 5 days, restrict 2 days"},
    "omad": {"fast_hours": 23, "eat_hours": 1},
}


@router.get("/presets")
async def get_presets():
    return PRESETS


@router.get("/current")
async def get_current_fast(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    supabase = get_supabase()

    result = supabase.table("fasting_sessions").select("*").eq(
        "user_id", user_id
    ).is_("ended_at", "null").order("started_at", desc=True).limit(1).execute()

    if not result.data:
        return {"active": False, "session": None}

    session = result.data[0]
    started = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    elapsed_hours = (now - started).total_seconds() / 3600
    target_hours = session.get("target_hours", 16)
    progress = min(elapsed_hours / target_hours * 100, 100) if target_hours > 0 else 0

    return {
        "active": True,
        "session": {
            **session,
            "elapsed_hours": round(elapsed_hours, 2),
            "remaining_hours": max(0, round(target_hours - elapsed_hours, 2)),
            "progress_percent": round(progress, 1),
            "completed": elapsed_hours >= target_hours,
        }
    }


@router.post("/start")
async def start_fast(
    protocol: str = Body("16:8", embed=True),
    target_hours: float = Body(None, embed=True),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    supabase = get_supabase()

    active = supabase.table("fasting_sessions").select("id").eq(
        "user_id", user_id
    ).is_("ended_at", "null").execute()

    if active.data:
        raise HTTPException(status_code=400, detail="You already have an active fast. End it first.")

    preset = PRESETS.get(protocol, {})
    hours = target_hours or preset.get("fast_hours", 16)

    session_data = {
        "user_id": user_id,
        "protocol": protocol,
        "target_hours": hours,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    result = supabase.table("fasting_sessions").insert(session_data).execute()

    return {"message": f"Started {protocol} fast ({hours}h)", "session": result.data[0] if result.data else session_data}


@router.post("/end")
async def end_fast(
    current_user: dict = Depends(get_current_user),
    notes: str = Body("", embed=True),
):
    user_id = current_user["id"]
    supabase = get_supabase()

    active = supabase.table("fasting_sessions").select("*").eq(
        "user_id", user_id
    ).is_("ended_at", "null").order("started_at", desc=True).limit(1).execute()

    if not active.data:
        raise HTTPException(status_code=400, detail="No active fast to end.")

    session = active.data[0]
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
    actual_hours = (now - started).total_seconds() / 3600
    completed = actual_hours >= session.get("target_hours", 0)

    update_data = {
        "ended_at": now.isoformat(),
        "actual_hours": round(actual_hours, 2),
        "completed": completed,
        "notes": notes,
    }

    supabase.table("fasting_sessions").update(update_data).eq("id", session["id"]).execute()

    return {
        "message": f"Fast ended after {round(actual_hours, 1)}h" + (" - Goal reached!" if completed else ""),
        "actual_hours": round(actual_hours, 2),
        "completed": completed,
    }


@router.get("/history")
async def get_fasting_history(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["id"]
    supabase = get_supabase()

    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    result = supabase.table("fasting_sessions").select("*").eq(
        "user_id", user_id
    ).gte("started_at", since).order("started_at", desc=True).execute()

    sessions = result.data or []
    completed_count = sum(1 for s in sessions if s.get("completed"))

    return {
        "sessions": sessions,
        "total": len(sessions),
        "completed": completed_count,
        "completion_rate": round(completed_count / len(sessions) * 100, 1) if sessions else 0,
    }
