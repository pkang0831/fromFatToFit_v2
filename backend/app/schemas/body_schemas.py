from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime

ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]


class MuscleGainsInput(BaseModel):
    arms: float = 0
    chest: float = 0
    back: float = 0
    shoulders: float = 0
    legs: float = 0
    core: float = 0


class BodyScanRequest(BaseModel):
    image_base64: str
    scan_type: Optional[str] = Field(
        default=None,
        description="Optional client hint: bodyfat, percentile, transformation, or enhancement",
    )
    source: Optional[str] = None
    session_id: Optional[str] = None
    reminder_event_id: Optional[str] = None
    reentry_state: Optional[str] = None
    surface_state: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    height_cm: Optional[float] = None
    target_bf_reduction: Optional[float] = Field(None, description="Deprecated — use target_bf instead")
    target_bf: Optional[float] = Field(None, description="Target body fat percentage")
    enhancement_level: Optional[str] = Field(None, description="subtle, natural, or studio")
    muscle_gains: Optional[MuscleGainsInput] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    ownership_confirmed: bool = Field(
        default=False,
        description="Uploader confirms this is their own photo or that they have permission to upload it",
    )


class BodyFatEstimateResponse(BaseModel):
    body_fat_percentage: float
    confidence: str = Field(description="low, medium, high")
    recommendations: List[str]
    scan_id: str
    usage_remaining: int


class PercentileData(BaseModel):
    percentile: float = Field(..., ge=0, le=100)
    rank_text: str = Field(description="e.g., 'top 15%'")
    comparison_group: str
    body_fat_percentage: float


class PercentileResponse(BaseModel):
    percentile_data: PercentileData
    distribution_data: Dict[str, Any] = Field(description="Data for bell curve visualization")
    scan_id: str
    usage_remaining: int


class TransformationResponse(BaseModel):
    original_image_url: str = ""
    transformed_image_url: str
    current_bf: Optional[float] = None
    target_bf: Optional[float] = None
    direction: Optional[str] = None
    muscle_gain_estimate: Optional[str] = None
    estimated_timeline_weeks: int = 0
    recommendations: List[str] = []
    progress_frames: Optional[List[str]] = None
    scan_id: Optional[str] = None


class EnhancementResponse(BaseModel):
    original_image_url: str
    enhanced_image_url: str
    enhancement_level: str
    scan_id: Optional[str] = None


class SegmentRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo (no data: prefix)")
    click_x: float = Field(..., ge=0.0, le=1.0, description="Normalized x coordinate of click (0=left, 1=right)")
    click_y: float = Field(..., ge=0.0, le=1.0, description="Normalized y coordinate of click (0=top, 1=bottom)")


class SegmentResponse(BaseModel):
    mask_base64: str = Field(..., description="Base64 PNG mask (white=selected, black=background)")
    body_part_guess: str = Field(..., description="AI guess of the body part: shoulders, chest, abs, arms, etc.")
    mask_area_pct: float = Field(..., description="Percentage of image covered by mask")


class RegionTransformRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo")
    mask_base64: str = Field(..., description="Base64 PNG mask from segmentation (possibly user-refined)")
    body_part: str = Field(..., description="Body part label: shoulders, chest, abs, arms, back, thighs, legs")
    goal: str = Field(..., description="Transformation goal: bigger, leaner, more_defined, slimmer")
    gender: str = Field(default="male", description="male or female")
    intensity: str = Field(default="moderate", description="subtle, moderate, or dramatic")
    ownership_confirmed: bool = Field(
        default=False,
        description="Uploader confirms this is their own photo or that they have permission to upload it",
    )


class RegionTransformResponse(BaseModel):
    transformed_image_url: str = Field(..., description="Data URI of the composited result")
    body_part: str
    goal: str
    direction: str = Field(..., description="fat_loss, muscle_gain, or definition")


class BodyScanHistoryItem(BaseModel):
    id: str
    scan_type: str
    date: datetime
    result_summary: str
    image_url: Optional[str]


class ScanHistoryPoint(BaseModel):
    date: str
    bf: float


class GapToGoalResponse(BaseModel):
    current_bf: Optional[float] = None
    target_bf: Optional[float] = None
    goal_image_url: Optional[str] = None
    gap: Optional[float] = None
    scan_count: int = 0
    last_scan_date: Optional[str] = None
    scan_history: List[ScanHistoryPoint] = []


class SaveGoalRequest(BaseModel):
    goal_image_url: str
    target_bf: float


# ── Auto-segmentation ───────────────────────────────────────────────────────

class AutoSegmentRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo (no data: prefix)")


class SegClassInfo(BaseModel):
    id: int
    key: str
    label: str


class CandidateSegmentInfo(BaseModel):
    segment_id: int
    assigned_class: int = Field(..., description="Class ID 0-7 (0 = rejected/unassigned)")
    score: float = Field(..., description="Assignment confidence ∈ [0, 1]")
    bbox: List[int] = Field(..., description="[x0, y0, x1, y1] in image pixels")
    area: int = Field(..., description="Pixel count of the mask")
    centroid: List[float] = Field(..., description="[cx, cy] normalized ∈ [0,1]²")
    mask_rle: str = Field(..., description="COCO-style run-length encoding")
    rejection_reason: Optional[str] = Field(None, description="None = accepted")


class AutoSegmentResponse(BaseModel):
    width: int = Field(..., description="Original image width in pixels")
    height: int = Field(..., description="Original image height in pixels")
    label_map_base64: str = Field(
        ...,
        description=(
            "Grayscale PNG at original resolution. "
            "Pixel value = class ID (0=background, 1-7=body parts). "
            "left/right = person's anatomical left/right."
        ),
    )
    foreground_mask_base64: str = Field(
        "",
        description="Binary PNG — white = union of accepted person masks",
    )
    editable_region_base64: str = Field(
        "",
        description="Binary PNG — white = dilated foreground (safe edit zone)",
    )
    classes: List[SegClassInfo]
    candidate_segments: List[CandidateSegmentInfo] = Field(
        default_factory=list,
        description="All SAM2 proposals with scoring metadata for click-to-reassign",
    )
    debug_info: Optional[Dict[str, Any]] = None


# ── CUT edit preparation ────────────────────────────────────────────────────

class CutEditPrepRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo (no data: prefix)")
    intensity: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Global edit strength multiplier (0 = minimal, 1 = maximum)",
    )
    user_protect_mask_base64: Optional[str] = Field(
        None,
        description="Optional user-drawn protection mask (base64 PNG, white = protect)",
    )


class CutEditPrepResponse(BaseModel):
    width: int = Field(..., description="Original image width in pixels")
    height: int = Field(..., description="Original image height in pixels")
    protect_mask_base64: str = Field(
        ..., description="Binary PNG — white = protected (never edit)",
    )
    edit_mask_base64: str = Field(
        ..., description="Binary PNG — white = editable region",
    )
    weight_map_base64: str = Field(
        ..., description="Grayscale PNG — 0=no edit, 255=max edit intensity",
    )
    feather_mask_base64: str = Field(
        ..., description="Grayscale PNG — soft boundary falloff (0=edge, 255=deep inside)",
    )
    combined_map_base64: str = Field(
        ..., description="Grayscale PNG — weight_map * feather_mask, ready for warp/diffusion",
    )
    debug_info: Optional[Dict[str, Any]] = None


# ── CUT warp preview ────────────────────────────────────────────────────────

class CutWarpPreviewRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo (no data: prefix)")
    preset: str = Field(
        default="medium",
        description="Warp intensity preset: mild, medium, or strong",
    )
    intensity: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description="Edit-prep weight map intensity (0 = minimal, 1 = maximum)",
    )


class CutWarpPreviewResponse(BaseModel):
    width: int
    height: int
    warped_image_base64: str = Field(
        ..., description="JPEG base64 — the warped preview image",
    )
    displacement_viz_base64: str = Field(
        ..., description="PNG base64 — displacement field debug visualization (R=dx, G=dy, B=magnitude)",
    )
    debug_info: Optional[Dict[str, Any]] = None


class GuestScanRequest(BaseModel):
    image_base64: str
    gender: str = Field(..., description="male or female")
    age: int = Field(..., ge=18, le=100)
    ownership_confirmed: bool = Field(
        default=False,
        description="Uploader confirms this is their own photo or that they have permission to upload it",
    )
    adult_confirmed: bool = Field(
        default=False,
        description="Uploader confirms the pictured subject is 18 or older",
    )
    framing: Literal["upper_body", "full_body"] = Field(
        default="upper_body",
        description="Must match the framing used in /guest/validate-photo for this image",
    )


class BodyPhotoQualityRequest(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded body photo (optional data: URI prefix)")
    framing: Literal["upper_body", "full_body"] = Field(
        default="upper_body",
        description="upper_body: waist-up / mirror selfie; full_body: stricter full-body framing",
    )


class BodyPhotoQualityResponse(BaseModel):
    ok: bool
    body_area_ratio: float
    bbox_area_ratio: float = 0.0
    mask_fill_ratio: float = 0.0
    is_front_facing: bool
    pose_detected: bool
    is_shirtless: bool = True
    brightness: float = 0.0
    failure_codes: List[str] = Field(default_factory=list)
    messages: List[str] = Field(default_factory=list)
    width: int = 0
    height: int = 0
    framing: str = "upper_body"
    min_body_area_ratio: float = 0.38
    min_mask_fill_ratio: float = 0.34


class GuestScanResponse(BaseModel):
    body_fat_percentage: float = Field(description="Approximate BF% estimate. Create an account for richer trend tracking and more context.")
    confidence: str
    category: str
    insight: str
    body_fat_range_low: float = Field(default=0, description="Lower bound of estimated BF% range")
    body_fat_range_high: float = Field(default=0, description="Upper bound of estimated BF% range")


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    target_weight_kg: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    activity_level: Optional[ActivityLevel] = None
    calorie_goal: Optional[float] = None
    onboarding_completed: Optional[bool] = None
    consent_terms_at: Optional[str] = None
    consent_privacy_at: Optional[str] = None
    consent_sensitive_data_at: Optional[str] = None
    consent_age_verified_at: Optional[str] = None
    consent_version: Optional[str] = None


# ── Transformation Journey response models ──────────────────────────────────

class StageDescriptorResponse(BaseModel):
    face: str
    waist: str
    abdomen: str
    chest: str
    arms: str
    shoulders: str
    legs: str
    overall: str


class StageNutritionSnapshotResponse(BaseModel):
    daily_calories: int
    protein_g: int


class TransformationStageResponse(BaseModel):
    stage_number: int
    label: str
    week: int
    bf_pct: float
    weight_kg: Optional[float] = None
    lean_mass_delta_kg: float = 0
    fat_mass_delta_kg: float = 0
    body_state: StageDescriptorResponse
    image_url: Optional[str] = None
    warnings: List[str] = []
    stage_nutrition: Optional[StageNutritionSnapshotResponse] = None
    stage_exercises: List[str] = []


class NutritionPlanResponse(BaseModel):
    daily_calories: int
    protein_g: int
    carbs_g_min: int
    carbs_g_max: int
    fat_g_min: int
    fat_g_max: int
    meal_structure: List[str]
    weekly_adjustment: str
    checkin_cadence: str
    stage_notes: Dict[str, str]
    assumptions: List[str]
    disclaimer: str


class WorkoutPlanResponse(BaseModel):
    split_type: str
    sessions_per_week: int
    exercises: List[Dict[str, Any]]
    sets_reps_guidance: str
    progression_scheme: str
    cardio_guidance: str
    recovery_notes: str
    deload_protocol: str
    stage_adjustments: Dict[str, str]


class TransformationJourneyResponse(BaseModel):
    mode: str
    current_bf: float
    target_bf: float
    target_bf_clamped: Optional[float] = None
    total_weeks: int
    stages: List[TransformationStageResponse]
    nutrition: NutritionPlanResponse
    workout: WorkoutPlanResponse
    warnings: List[str] = []
    disclaimer: str
    scan_id: Optional[str] = None
