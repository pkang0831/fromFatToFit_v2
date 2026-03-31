from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


ProofShareStatus = Literal["active", "revoked"]


class CreateProofShareRequest(BaseModel):
    progress_photo_id: str = Field(..., min_length=1)
    week_marker: Optional[int] = Field(default=None, ge=1, le=52)


class ProofShareGoalSummary(BaseModel):
    current_bf: Optional[float] = None
    target_bf: Optional[float] = None
    gap: Optional[float] = None


class ProofSharePhotoSummary(BaseModel):
    progress_photo_id: str
    taken_at: Optional[datetime] = None
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None


class ProofShareResponse(BaseModel):
    id: str
    token: str
    progress_photo_id: str
    week_marker: Optional[int] = None
    status: ProofShareStatus
    created_at: datetime
    revoked_at: Optional[datetime] = None
    public_url: str
    image_url: str
    referred_try_url: str
    goal_summary: ProofShareGoalSummary
    photo_summary: ProofSharePhotoSummary


class PublicProofShareResponse(BaseModel):
    token: str
    public_url: str
    image_url: str
    referred_try_url: str
    week_marker: Optional[int] = None
    goal_summary: ProofShareGoalSummary
    photo_summary: ProofSharePhotoSummary
