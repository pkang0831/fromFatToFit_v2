"""Integration-level tests for POST /body/transformation.

All external dependencies (AI estimation, Replicate, Supabase, credits)
are mocked.  These tests verify the router's orchestration logic:
response shape, billing safety, and error handling.

The slowapi rate limiter is bypassed by patching the limiter to skip
validation of the request object.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.body_schemas import BodyScanRequest, MuscleGainsInput


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


def _fake_stage_images(stage_numbers):
    return [
        {"stage_number": n, "image_data_uri": f"data:image/jpeg;base64,stage{n}"}
        for n in stage_numbers
    ]


_PATCHES = {
    "bf": "app.routers.body.estimate_body_fat_with_fallback",
    "journey": "app.routers.body.replicate_service.generate_journey_images",
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
        "journey": AsyncMock(return_value=_fake_stage_images([1, 2, 3, 4])),
        "credits": AsyncMock(return_value={"success": True, "total": 70}),
        "premium": AsyncMock(return_value=False),
        "balance": AsyncMock(return_value={"total_credits": 100}),
        "supabase": mock_get_supabase,
    }


def _call(scan_request=None, mock_overrides=None):
    """Call the handler function directly, bypassing rate-limiter decorator.

    We import the module, grab the actual wrapped function, and call it
    with mocked dependencies. The ``__wrapped__`` attribute is set by
    slowapi on decorated async functions.
    """
    from app.routers.body import generate_transformation_journey

    fn = getattr(generate_transformation_journey, "__wrapped__", generate_transformation_journey)

    mocks = _standard_mocks()
    if mock_overrides:
        mocks.update(mock_overrides)

    user = {"id": "user-abc"}
    req = MagicMock()

    with (
        patch(_PATCHES["bf"], mocks["bf"]),
        patch(_PATCHES["journey"], mocks["journey"]),
        patch(_PATCHES["credits"], mocks["credits"]),
        patch(_PATCHES["premium"], mocks["premium"]),
        patch(_PATCHES["balance"], mocks["balance"]),
        patch(_PATCHES["supabase"], mocks["supabase"]),
    ):
        result = _run(fn(
            request=req,
            scan_request=scan_request or _make_request(),
            current_user=user,
        ))

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

    def test_stages_include_images(self):
        result, _ = _call()
        images = [s.image_url for s in result.stages if s.image_url]
        assert len(images) == 4

    def test_scan_id_present(self):
        result, _ = _call()
        assert result.scan_id == "scan-123"


# ── Billing safety ──────────────────────────────────────────────────────────


class TestBillingSafety:
    def test_total_failure_no_credits_charged(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(mock_overrides={"journey": AsyncMock(return_value=[])})
        assert exc_info.value.status_code == 500
        assert "No credits were charged" in exc_info.value.detail

    def test_one_stage_below_threshold(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(mock_overrides={"journey": AsyncMock(return_value=_fake_stage_images([2]))})
        assert exc_info.value.status_code == 500
        assert "No credits were charged" in exc_info.value.detail

    def test_two_stages_below_threshold(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _call(mock_overrides={"journey": AsyncMock(return_value=_fake_stage_images([1, 3]))})
        assert exc_info.value.status_code == 500

    def test_three_stages_charges_with_warning(self):
        result, mocks = _call(mock_overrides={
            "journey": AsyncMock(return_value=_fake_stage_images([1, 2, 3])),
        })
        mocks["credits"].assert_called_once()
        assert any("failed to generate" in w for w in result.warnings)

    def test_four_stages_no_warning(self):
        result, mocks = _call()
        mocks["credits"].assert_called_once()
        assert not any("failed to generate" in w for w in result.warnings)

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
