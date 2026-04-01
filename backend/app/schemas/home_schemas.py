from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


PromptState = Literal["first_scan", "too_early", "ready", "overdue"]
EntryState = Literal[
    "plan_setup",
    "challenge_checkin",
    "first_scan",
    "weekly_scan",
    "progress_proof",
    "review_progress",
]
RetentionEventName = Literal[
    "scan_success",
    "reengagement_session",
    "history_viewed",
    "notification_sent",
    "notification_opened",
    "progress_proof_started",
    "progress_proof_completed",
    "progress_compare_viewed",
    "progress_checkin_started",
    "progress_checkin_completed",
    "progress_checkin_failed",
    "share_created",
    "share_viewed",
    "share_revoked",
    "referred_try_started",
    "register_completed",
    "purchase_completed",
]


class HomeTransformationSummary(BaseModel):
    id: str
    date: datetime
    result_summary: str
    image_url: Optional[str] = None


class HomeGoalSummary(BaseModel):
    has_saved_plan: bool
    plan_updated_at: Optional[datetime] = None
    current_bf: Optional[float] = None
    target_bf: Optional[float] = None
    goal_image_url: Optional[str] = None
    gap: Optional[float] = None
    selected_tier_calories: Optional[int] = None


class HomeScanSummary(BaseModel):
    scan_count: int
    last_scan_date: Optional[str] = None
    prompt_state: PromptState
    latest_transformation: Optional[HomeTransformationSummary] = None
    next_check_in_label: str


class HomeChallengeSummary(BaseModel):
    is_active: bool
    checked_in_today: bool
    day_index: Optional[int] = None


class HomeProgressSummary(BaseModel):
    photo_count: int
    latest_photo_date: Optional[str] = None
    compare_ready: bool


class HomePrimaryCta(BaseModel):
    state: EntryState
    href: str
    label: str
    title: str
    description: str


class HomeSummaryResponse(BaseModel):
    entry_state: EntryState
    goal_summary: HomeGoalSummary
    scan_summary: HomeScanSummary
    challenge_summary: HomeChallengeSummary
    progress_summary: HomeProgressSummary
    primary_cta: HomePrimaryCta


class RetentionEventRequest(BaseModel):
    event_name: RetentionEventName
    surface: str = Field(..., min_length=1, max_length=100)
    properties: Dict[str, Any] = Field(default_factory=dict)
