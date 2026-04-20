import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.weekly_checkin_schemas import (
    BodyObservation,
    EstimatedBodyFatRange,
    GoalWeighting,
    ImageQualityObservation,
    RegionNotes,
    VisualObservations,
    WeeklyCheckinCreateRequest,
)
from app.services.weekly_checkin_scoring import compute_derived_scores


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _iso_now():
    return datetime.now(timezone.utc).isoformat()


class _Result:
    def __init__(self, data):
        self.data = data


class _FakeTable:
    def __init__(self, supabase, name):
        self.supabase = supabase
        self.name = name
        self._reset()

    def _reset(self):
        self.filters = []
        self._limit = None
        self._order_key = None
        self._order_desc = False
        self._operation = "select"
        self._payload = None

    def select(self, *_args, **_kwargs):
        self._operation = "select"
        return self

    def insert(self, payload):
        self._operation = "insert"
        self._payload = dict(payload)
        return self

    def delete(self):
        self._operation = "delete"
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def order(self, key, desc=False):
        self._order_key = key
        self._order_desc = desc
        return self

    def limit(self, value):
        self._limit = value
        return self

    def execute(self):
        rows = self.supabase.tables.setdefault(self.name, [])

        if self._operation == "insert":
            row = dict(self._payload)
            row.setdefault("id", f"{self.name}-{len(rows) + 1}")
            row.setdefault("created_at", _iso_now())
            row.setdefault("taken_at", row.get("taken_at") or _iso_now())
            rows.append(row)
            self._reset()
            return _Result([dict(row)])

        if self._operation == "delete":
            to_delete = [
                row for row in rows
                if all(check(row) for check in self.filters)
            ]
            self.supabase.tables[self.name] = [
                row for row in rows
                if not all(check(row) for check in self.filters)
            ]
            self._reset()
            return _Result([dict(row) for row in to_delete])

        result = [
            dict(row)
            for row in rows
            if all(check(row) for check in self.filters)
        ]
        if self._order_key:
            result.sort(key=lambda row: row.get(self._order_key) or "", reverse=self._order_desc)
        if self._limit is not None:
            result = result[:self._limit]
        self._reset()
        return _Result(result)


class _FakeSupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _FakeTable(self, name)


def _observation(
    *,
    abdomen_softness: float,
    lower_abdomen_protrusion: float,
    ab_definition: float,
    chest_definition: float,
    arm_definition: float,
    shoulder_roundness: float,
    v_taper_visibility: float,
    overall_visual_leanness: float,
    comparison_confidence: float = 0.82,
) -> BodyObservation:
    return BodyObservation(
        image_quality=ImageQualityObservation(
            frontal_pose=0.92,
            body_visibility=0.95,
            lighting_consistency=0.82,
            pose_consistency=0.84,
            comparison_confidence=comparison_confidence,
            quality_flags=["none"],
        ),
        observations=VisualObservations(
            abdomen_softness=abdomen_softness,
            lower_abdomen_protrusion=lower_abdomen_protrusion,
            ab_definition=ab_definition,
            chest_definition=chest_definition,
            arm_definition=arm_definition,
            shoulder_roundness=shoulder_roundness,
            v_taper_visibility=v_taper_visibility,
            overall_visual_leanness=overall_visual_leanness,
        ),
        estimated_ranges=EstimatedBodyFatRange(
            body_fat_percent_min=15,
            body_fat_percent_max=19,
            body_fat_confidence=0.6,
        ),
        qualitative_summary=[
            "Midsection appears slightly tighter.",
            "Arm definition is stable.",
        ],
        region_notes=RegionNotes(
            abdomen="Waistline appears tighter.",
            chest="Chest is slightly more defined.",
            arms="Arms look stable.",
            shoulders="Shoulders are unchanged.",
        ),
    )


def test_analyze_weekly_checkin_saves_first_report():
    from app.routers.weekly_checkins import analyze_weekly_checkin
    handler = getattr(analyze_weekly_checkin, "__wrapped__", analyze_weekly_checkin)

    supabase = _FakeSupabase(
        {
            "user_profiles": [{"user_id": "user-1", "target_body_fat_percentage": 12.0}],
            "saved_goal_plans": [],
            "progress_photos": [],
            "weekly_checkins": [],
        }
    )
    observation = _observation(
        abdomen_softness=6.2,
        lower_abdomen_protrusion=5.8,
        ab_definition=3.8,
        chest_definition=5.4,
        arm_definition=6.0,
        shoulder_roundness=5.9,
        v_taper_visibility=5.1,
        overall_visual_leanness=4.9,
    )

    check_usage_limit = AsyncMock(return_value={"remaining": 1})

    with (
        patch("app.routers.weekly_checkins.get_supabase", return_value=supabase),
        patch("app.routers.weekly_checkins.check_premium_status", new=AsyncMock(return_value=False)),
        patch("app.routers.weekly_checkins.check_usage_limit", new=check_usage_limit),
        patch("app.routers.weekly_checkins.increment_usage", new=AsyncMock()) as increment_usage,
        patch("app.routers.weekly_checkins._ensure_safe_weekly_photo", new=AsyncMock()),
        patch("app.routers.weekly_checkins.analyze_weekly_checkin_image", new=AsyncMock(return_value=observation)),
        patch(
            "app.routers.weekly_checkins.upload_progress_image",
            return_value={"storage_bucket": "progress-photos-private", "storage_key": "user-1/checkin.jpg"},
        ),
        ):
            response = _run(
                handler(
                    request=None,
                    body=WeeklyCheckinCreateRequest(image_base64="ZmFrZQ==", ownership_confirmed=True),
                    current_user={"id": "user-1"},
                )
            )

    assert response.is_first_checkin is True
    assert response.weekly_status == "stable"
    assert response.progress_photo_id.startswith("progress_photos-")
    assert len(supabase.tables["progress_photos"]) == 1
    assert len(supabase.tables["weekly_checkins"]) == 1
    check_usage_limit.assert_awaited_once_with("user-1", "body_fat_scan", False)
    increment_usage.assert_awaited_once_with("user-1", "body_fat_scan")


def test_analyze_weekly_checkin_compares_against_previous_report():
    from app.routers.weekly_checkins import analyze_weekly_checkin
    handler = getattr(analyze_weekly_checkin, "__wrapped__", analyze_weekly_checkin)

    previous_observation = _observation(
        abdomen_softness=6.6,
        lower_abdomen_protrusion=6.1,
        ab_definition=3.1,
        chest_definition=5.0,
        arm_definition=5.7,
        shoulder_roundness=5.6,
        v_taper_visibility=4.8,
        overall_visual_leanness=4.6,
        comparison_confidence=0.8,
    )
    previous_scores = compute_derived_scores(previous_observation, goal=GoalWeighting())

    supabase = _FakeSupabase(
        {
            "user_profiles": [{"user_id": "user-1", "target_body_fat_percentage": 12.0}],
            "saved_goal_plans": [],
            "progress_photos": [],
            "weekly_checkins": [
                {
                    "id": "weekly-1",
                    "user_id": "user-1",
                    "progress_photo_id": "photo-1",
                    "analysis_version": "v1",
                    "created_at": _iso_now(),
                    "taken_at": _iso_now(),
                    "image_quality": previous_observation.image_quality.model_dump(),
                    "observations": previous_observation.observations.model_dump(),
                    "estimated_ranges": previous_observation.estimated_ranges.model_dump(),
                    "qualitative_summary": previous_observation.qualitative_summary,
                    "region_notes": previous_observation.region_notes.model_dump(),
                    "derived_scores": previous_scores.model_dump(),
                    "delta_from_previous": None,
                    "comparison_confidence": 0.8,
                    "weekly_status": "stable",
                    "is_first_checkin": True,
                    "regional_visualization": [],
                    "hologram_visualization": {
                        "glow_intensity": 0.5,
                        "body_clarity": 0.5,
                        "pedestal_progress": 0.5,
                    },
                }
            ],
        }
    )
    current_observation = _observation(
        abdomen_softness=5.8,
        lower_abdomen_protrusion=5.4,
        ab_definition=4.0,
        chest_definition=5.4,
        arm_definition=6.1,
        shoulder_roundness=5.9,
        v_taper_visibility=5.2,
        overall_visual_leanness=5.3,
        comparison_confidence=0.82,
    )
    check_usage_limit = AsyncMock()

    with (
        patch("app.routers.weekly_checkins.get_supabase", return_value=supabase),
        patch("app.routers.weekly_checkins.check_premium_status", new=AsyncMock(return_value=True)),
        patch("app.routers.weekly_checkins.check_usage_limit", new=check_usage_limit),
        patch("app.routers.weekly_checkins.increment_usage", new=AsyncMock()) as increment_usage,
        patch("app.routers.weekly_checkins._ensure_safe_weekly_photo", new=AsyncMock()),
        patch("app.routers.weekly_checkins.analyze_weekly_checkin_image", new=AsyncMock(return_value=current_observation)),
        patch(
            "app.routers.weekly_checkins.upload_progress_image",
            return_value={"storage_bucket": "progress-photos-private", "storage_key": "user-1/checkin-2.jpg"},
        ),
        ):
            response = _run(
                handler(
                    request=None,
                    body=WeeklyCheckinCreateRequest(image_base64="ZmFrZQ==", ownership_confirmed=True),
                    current_user={"id": "user-1"},
                )
            )

    assert response.is_first_checkin is False
    assert response.previous_checkin_id == "weekly-1"
    assert response.delta_from_previous is not None
    assert response.delta_from_previous.goal_proximity_score > 0
    assert response.weekly_status == "improved"
    check_usage_limit.assert_not_awaited()
    increment_usage.assert_not_awaited()


def test_analyze_weekly_checkin_blocks_free_users_when_limit_is_exhausted():
    from app.routers.weekly_checkins import analyze_weekly_checkin
    from app.services.usage_limiter import UsageLimitExceeded

    handler = getattr(analyze_weekly_checkin, "__wrapped__", analyze_weekly_checkin)
    supabase = _FakeSupabase(
        {
            "user_profiles": [{"user_id": "user-1", "target_body_fat_percentage": 12.0}],
            "saved_goal_plans": [],
            "progress_photos": [],
            "weekly_checkins": [],
        }
    )
    check_usage_limit = AsyncMock(side_effect=UsageLimitExceeded("body_fat_scan exhausted"))

    with (
        patch("app.routers.weekly_checkins.get_supabase", return_value=supabase),
        patch("app.routers.weekly_checkins.check_premium_status", new=AsyncMock(return_value=False)),
        patch("app.routers.weekly_checkins.check_usage_limit", new=check_usage_limit),
        patch("app.routers.weekly_checkins.increment_usage", new=AsyncMock()) as increment_usage,
        patch("app.routers.weekly_checkins._ensure_safe_weekly_photo", new=AsyncMock()) as ensure_safe_photo,
        patch("app.routers.weekly_checkins.upload_progress_image") as upload_progress_image,
    ):
        with pytest.raises(HTTPException) as exc:
            _run(
                handler(
                    request=None,
                    body=WeeklyCheckinCreateRequest(image_base64="ZmFrZQ==", ownership_confirmed=True),
                    current_user={"id": "user-1"},
                )
            )

    assert exc.value.status_code == 402
    assert "Weekly check-in free limit reached" in exc.value.detail
    check_usage_limit.assert_awaited_once_with("user-1", "body_fat_scan", False)
    ensure_safe_photo.assert_not_awaited()
    upload_progress_image.assert_not_called()
    increment_usage.assert_not_awaited()
    assert supabase.tables["progress_photos"] == []
    assert supabase.tables["weekly_checkins"] == []
