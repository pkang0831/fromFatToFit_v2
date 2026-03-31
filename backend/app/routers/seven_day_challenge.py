"""7-day commitment loop: check-ins, identity nudges, AI vs logged Week 1 hint."""

from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
import logging

from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user
from ..rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()


class StartChallengeBody(BaseModel):
    ai_weeks_snapshot: Optional[int] = Field(None, ge=1, le=520)
    ai_current_bf: Optional[float] = Field(None, ge=3, le=60)
    ai_target_bf: Optional[float] = Field(None, ge=3, le=60)


class CheckinBody(BaseModel):
    weight_kg: Optional[float] = Field(None, gt=0, le=400)
    body_fat_pct: Optional[float] = Field(None, ge=3, le=60)


def _identity_message(day_index: int) -> str:
    if day_index <= 1:
        return "Day 1: You crossed the line from browsing to starting."
    if day_index <= 3:
        return "Day 3: Consistency beats intensity — you're showing up."
    if day_index <= 6:
        return "The gap between you and the goal is shrinking because you keep returning."
    return "Day 7: Week one is data. You're not 'trying' anymore — you're in motion."


def _week_one_compare(ai_weeks: Optional[int], ai_cur: Optional[float], ai_tgt: Optional[float], checkins: list) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ai_weekly_bf_delta_pct": None,
        "logged_points": len(checkins),
        "message": "Check in a few times this week to unlock AI vs your numbers.",
    }
    if ai_weeks and ai_cur is not None and ai_tgt is not None and ai_weeks > 0:
        delta = (ai_tgt - ai_cur) / ai_weeks
        out["ai_weekly_bf_delta_pct"] = round(delta, 3)
        out["message"] = (
            f"AI linear pace: about {delta:+.2f}% body fat per week over {ai_weeks} weeks. "
            "Your real curve is what you log — beat or chase that line."
        )
    bfs = [c.get("body_fat_pct") for c in checkins if c.get("body_fat_pct") is not None]
    if len(bfs) >= 2:
        actual = float(bfs[-1]) - float(bfs[0])
        out["actual_bf_delta_first_to_last_pct"] = round(actual, 2)
        out["message"] = (
            f"Week 1 logged change: {actual:+.2f}% BF vs start of week. "
            + (out.get("message") or "")
        )
    return out


@router.post("/seven-day/start")
@limiter.limit("10/minute")
async def start_seven_day_challenge(
    body: StartChallengeBody,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    supabase = get_supabase()
    try:
        supabase.table("seven_day_challenges").update({"status": "ended"}).eq(
            "user_id", user_id
        ).eq("status", "active").execute()

        row = {
            "user_id": user_id,
            "status": "active",
            "ai_weeks_snapshot": body.ai_weeks_snapshot,
            "ai_current_bf": body.ai_current_bf,
            "ai_target_bf": body.ai_target_bf,
        }
        row = {k: v for k, v in row.items() if v is not None}
        ins = supabase.table("seven_day_challenges").insert(row).execute()
        if not ins.data:
            raise HTTPException(status_code=500, detail="failed to start challenge")
        return {"challenge": ins.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"start challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to start challenge")


@router.get("/seven-day")
@limiter.limit("60/minute")
async def get_seven_day_challenge(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    supabase = get_supabase()
    try:
        ch = (
            supabase.table("seven_day_challenges")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not ch.data:
            return {"challenge": None, "checkins": [], "day_index": 0, "identity_message": None, "week_one_compare": None}

        challenge = ch.data[0]
        cid = challenge["id"]
        started = challenge["started_at"]
        if isinstance(started, str):
            started_s = started.split("T")[0]
            start_d = date.fromisoformat(started_s)
        else:
            start_d = datetime.fromisoformat(str(started)).date()

        today = date.today()
        raw_day = (today - start_d).days + 1
        day_index = max(1, min(raw_day, 7))

        checkins = (
            supabase.table("seven_day_checkins")
            .select("calendar_date, weight_kg, body_fat_pct, checked_at")
            .eq("challenge_id", cid)
            .order("calendar_date")
            .execute()
        )
        ci_list = checkins.data or []

        if raw_day > 7 and challenge["status"] == "active":
            supabase.table("seven_day_challenges").update({"status": "completed"}).eq(
                "id", cid
            ).execute()
            challenge["status"] = "completed"

        wk = _week_one_compare(
            challenge.get("ai_weeks_snapshot"),
            challenge.get("ai_current_bf"),
            challenge.get("ai_target_bf"),
            ci_list,
        )

        return {
            "challenge": challenge,
            "checkins": ci_list,
            "day_index": day_index,
            "identity_message": _identity_message(day_index),
            "week_one_compare": wk,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get challenge: {e}")
        raise HTTPException(status_code=500, detail="Failed to load challenge")


@router.post("/seven-day/checkin")
@limiter.limit("30/minute")
async def checkin_seven_day(
    body: CheckinBody,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    today = date.today()
    supabase = get_supabase()
    try:
        ch = (
            supabase.table("seven_day_challenges")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        if not ch.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active challenge — start one from your transformation result.",
            )
        challenge = ch.data[0]
        cid = challenge["id"]
        started = challenge["started_at"]
        if isinstance(started, str):
            start_d = date.fromisoformat(started.split("T")[0])
        else:
            start_d = datetime.fromisoformat(str(started)).date()
        if (today - start_d).days + 1 > 7:
            supabase.table("seven_day_challenges").update({"status": "completed"}).eq(
                "id", cid
            ).execute()
            raise HTTPException(status_code=400, detail="This 7-day window has ended. Start a new one.")

        existing = (
            supabase.table("seven_day_checkins")
            .select("id")
            .eq("challenge_id", cid)
            .eq("calendar_date", today.isoformat())
            .execute()
        )
        if existing.data:
            return {"ok": True, "duplicate": True, "message": "Already checked in today."}

        supabase.table("seven_day_checkins").insert(
            {
                "challenge_id": cid,
                "calendar_date": today.isoformat(),
                "weight_kg": body.weight_kg,
                "body_fat_pct": body.body_fat_pct,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

        return {"ok": True, "duplicate": False, "message": "Checked in."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"checkin: {e}")
        raise HTTPException(status_code=500, detail="Check-in failed")
