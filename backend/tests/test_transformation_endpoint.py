"""Integration-level tests for POST /body/transformation.

Mocks: body fat estimate, photo-quality gate, RealVis journey generation, credits, Supabase.
Aligned with the current multi-stage ``generate_realvis_journey`` flow.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.body_schemas import BodyScanRequest


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _make_request(**overrides):
    defaults = dict(
        image_base64="fake_b64_data",
        scan_type="transformation",
        gender="male",
        age=30,
        target_bf=12.0,
    )
    defaults.update(overrides)
    return BodyScanRequest(**defaults)


_PATCHES = {
    "bf": "app.routers.body.estimate_body_fat_with_fallback",
    "quality": "app.routers.body._require_safe_body_photo",
    "gen": "app.services.realvis_service.generate_realvis_journey",
    "credits": "app.routers.body.deduct_credits",
    "premium": "app.routers.body.check_premium_status",
    "balance": "app.routers.body.get_credit_balance",
    "supabase": "app.routers.body.get_supabase",
}


def _standard_mocks():
    mock_exec_result = MagicMock()
    mock_exec_result.data = [{"id": "scan-123"}]

    mock_chain = MagicMock()
    mock_chain.execute.return_value = mock_exec_result
    mock_chain.insert.return_value = mock_chain
    mock_chain.update.return_value = mock_chain
    mock_chain.eq.return_value = mock_chain

    mock_supabase_client = MagicMock()
    mock_supabase_client.table.return_value = mock_chain

    mock_get_supabase = MagicMock(return_value=mock_supabase_client)

    return {
        "bf": AsyncMock(return_value={"body_fat_percentage": 22.0, "confidence": "medium"}),
        "quality": AsyncMock(return_value=True),
        "gen": AsyncMock(
            return_value=[
                {"stage_number": 1, "image_data_uri": "data:image/jpeg;base64,stage1", "latency_ms": 100},
                {"stage_number": 2, "image_data_uri": "data:image/jpeg;base64,stage2", "latency_ms": 110},
                {"stage_number": 3, "image_data_uri": "data:image/jpeg;base64,stage3", "latency_ms": 115},
                {"stage_number": 4, "image_data_uri": "data:image/jpeg;base64,finalstage", "latency_ms": 120},
            ]
        ),
        "credits": AsyncMock(return_value={"success": True, "total": 70}),
        "premium": AsyncMock(return_value=False),
        "balance": AsyncMock(return_value={"total_credits": 100}),
        "supabase": mock_get_supabase,
    }


def _call(scan_request=None, mock_overrides=None):
    from app.routers.body import generate_transformation_journey

    fn = getattr(generate_transformation_journey, "__wrapped__", generate_transformation_journey)

    mocks = _standard_mocks()
    if mock_overrides:
        mocks.update(mock_overrides)

    user = {"id": "user-abc"}
    req = MagicMock()

    with (
        patch(_PATCHES["bf"], mocks["bf"]),
        patch(_PATCHES["quality"], mocks["quality"]),
        patch(_PATCHES["gen"], mocks["gen"]),
        patch(_PATCHES["credits"], mocks["credits"]),
        patch(_PATCHES["premium"], mocks["premium"]),
        patch(_PATCHES["balance"], mocks["balance"]),
        patch(_PATCHES["supabase"], mocks["supabase"]),
    ):
        result = _run(
            fn(
                request=req,
                scan_request=scan_request or _make_request(),
                current_user=user,
            )
        )

    return result, mocks


# ── Happy path ──────────────────────────────────────────────────────────────


class TestHappyPath:
    def test_returns_journey_response_shape(self):
        result, _ = _call()
        assert result.mode == "cut"
        assert len(result.stages) == 5
        assert result.nutrition is not None
        assert result.workout is not None
        assert result.disclaimer

    def test_credits_deducted_once(self):
        _, mocks = _call()
        mocks["credits"].assert_called_once()

    def test_generated_stages_have_images(self):
        result, _ = _call()
        urls = [s.image_url for s in result.stages if s.image_url]
        assert len(urls) == 4
        assert "finalstage" in urls[-1]

    def test_scan_id_present(self):
        result, _ = _call()
        assert result.scan_id == "scan-123"

    def test_realvis_called_once(self):
        _, mocks = _call()
        mocks["gen"].assert_called_once()


# ── Billing / errors ─────────────────────────────────────────────────────────


class TestBillingSafety:
    def test_realvis_failure_no_credits(self):
        from fastapi import HTTPException

        mocks = _standard_mocks()
        mocks["gen"] = AsyncMock(side_effect=RuntimeError("realvis down"))

        with (
            patch(_PATCHES["bf"], mocks["bf"]),
            patch(_PATCHES["quality"], mocks["quality"]),
            patch(_PATCHES["gen"], mocks["gen"]),
            patch(_PATCHES["credits"], mocks["credits"]),
            patch(_PATCHES["premium"], mocks["premium"]),
            patch(_PATCHES["balance"], mocks["balance"]),
            patch(_PATCHES["supabase"], mocks["supabase"]),
        ):
            from app.routers.body import generate_transformation_journey

            fn = getattr(generate_transformation_journey, "__wrapped__", generate_transformation_journey)
            user = {"id": "user-abc"}
            req = MagicMock()
            with pytest.raises(HTTPException) as exc_info:
                _run(fn(request=req, scan_request=_make_request(), current_user=user))
        assert exc_info.value.status_code == 500
        mocks["credits"].assert_not_called()

    def test_insufficient_credits_returns_402(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(mock_overrides={"balance": AsyncMock(return_value={"total_credits": 5})})
        assert exc_info.value.status_code == 402


# ── Input validation ────────────────────────────────────────────────────────


class TestInputValidation:
    def test_missing_gender_returns_400(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(scan_request=_make_request(gender=None))
        assert exc_info.value.status_code == 400

    def test_missing_target_bf_returns_400(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(scan_request=_make_request(target_bf=None))
        assert exc_info.value.status_code == 400


# ── Response content ────────────────────────────────────────────────────────


class TestResponseContent:
    def test_warnings_from_clamped_bf(self):
        result, _ = _call(scan_request=_make_request(target_bf=3.0))
        assert any("clamped" in w.lower() or "below" in w.lower() for w in result.warnings)

    def test_nutrition_and_workout_present(self):
        result, _ = _call()
        assert result.nutrition.daily_calories > 0
        assert result.workout.sessions_per_week > 0

    def test_disclaimer_present(self):
        result, _ = _call()
        assert "not" in result.disclaimer.lower()
