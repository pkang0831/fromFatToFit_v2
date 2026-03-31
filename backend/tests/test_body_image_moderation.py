import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.body_schemas import BodyScanRequest, GuestScanRequest, RegionTransformRequest
from app.services.body_image_moderation import enforce_body_image_moderation
from app.services.body_photo_quality import BodyPhotoQualityResult


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _quality_result(*, multiple_subjects_detected: bool = False) -> BodyPhotoQualityResult:
    return BodyPhotoQualityResult(
        ok=True,
        body_area_ratio=0.32,
        bbox_area_ratio=0.41,
        mask_fill_ratio=0.77,
        is_front_facing=True,
        pose_detected=True,
        is_shirtless=True,
        brightness=120.0,
        failure_codes=[],
        messages=["ok"],
        width=1200,
        height=1600,
        framing="upper_body",
        min_body_area_ratio=0.22,
        min_mask_fill_ratio=0.34,
        foreground_component_count=2 if multiple_subjects_detected else 1,
        multiple_subjects_detected=multiple_subjects_detected,
    )


class TestModerationService:
    def test_guest_blocks_without_adult_confirmation(self):
        with pytest.raises(HTTPException) as exc_info:
            _run(
                enforce_body_image_moderation(
                    route_name="guest_body_scan",
                    source="guest",
                    quality_result=_quality_result(),
                    ownership_confirmed=True,
                    adult_confirmed=False,
                    stated_age=18,
                )
            )

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["code"] == "adult_confirmation_required"

    def test_authenticated_blocks_missing_sensitive_consent(self):
        with patch(
            "app.services.body_image_moderation._get_user_moderation_profile",
            return_value={
                "user_id": "user-1",
                "age": 28,
                "consent_terms_at": "2026-03-01T00:00:00+00:00",
                "consent_privacy_at": None,
                "consent_sensitive_data_at": None,
                "consent_age_verified_at": "2026-03-01T00:00:00+00:00",
            },
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    enforce_body_image_moderation(
                        route_name="transformation",
                        source="authenticated",
                        quality_result=_quality_result(),
                        user_id="user-1",
                        ownership_confirmed=True,
                    )
                )

        assert exc_info.value.status_code == 422
        assert exc_info.value.detail["code"] == "sensitive_data_consent_required"

    def test_authenticated_allows_consented_single_subject_upload(self):
        with patch(
            "app.services.body_image_moderation._get_user_moderation_profile",
            return_value={
                "user_id": "user-1",
                "age": 28,
                "consent_terms_at": "2026-03-01T00:00:00+00:00",
                "consent_privacy_at": "2026-03-01T00:00:00+00:00",
                "consent_sensitive_data_at": "2026-03-01T00:00:00+00:00",
                "consent_age_verified_at": "2026-03-01T00:00:00+00:00",
            },
        ):
            decision = _run(
                enforce_body_image_moderation(
                    route_name="transformation",
                    source="authenticated",
                    quality_result=_quality_result(),
                    user_id="user-1",
                    ownership_confirmed=True,
                )
            )

        assert decision.allowed is True
        assert decision.code == "allowed"


class TestBlockedUploadsNeverReachVendor:
    def test_guest_body_scan_blocked_before_vendor_upload(self):
        from app.routers.guest import guest_body_scan

        fn = getattr(guest_body_scan, "__wrapped__", guest_body_scan)
        vendor = AsyncMock()

        with (
            patch(
                "app.routers.guest._require_safe_body_photo",
                AsyncMock(side_effect=HTTPException(status_code=422, detail={"code": "ownership_confirmation_required"})),
            ),
            patch("app.routers.guest.estimate_body_fat_with_fallback", vendor),
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    fn(
                        request=MagicMock(),
                        scan_request=GuestScanRequest(
                            image_base64="ZmFrZQ==",
                            gender="male",
                            age=25,
                            ownership_confirmed=False,
                            adult_confirmed=True,
                        ),
                    )
                )

        assert exc_info.value.status_code == 422
        vendor.assert_not_called()

    def test_guest_body_scan_safe_upload_reaches_vendor(self):
        from app.routers.guest import guest_body_scan

        fn = getattr(guest_body_scan, "__wrapped__", guest_body_scan)
        vendor = AsyncMock(return_value={"body_fat_percentage": 18.4, "confidence": "high"})

        with (
            patch("app.routers.guest._require_safe_body_photo", AsyncMock(return_value=_quality_result())),
            patch("app.routers.guest.estimate_body_fat_with_fallback", vendor),
        ):
            result = _run(
                fn(
                    request=MagicMock(),
                    scan_request=GuestScanRequest(
                        image_base64="ZmFrZQ==",
                        gender="male",
                        age=25,
                        ownership_confirmed=True,
                        adult_confirmed=True,
                    ),
                )
            )

        assert result.body_fat_percentage == 18.4
        vendor.assert_awaited_once()

    def test_estimate_bodyfat_blocked_before_vendor_upload(self):
        from app.routers.body import estimate_bodyfat

        fn = getattr(estimate_bodyfat, "__wrapped__", estimate_bodyfat)
        vendor = AsyncMock()

        with (
            patch(
                "app.routers.body._require_safe_body_photo",
                AsyncMock(side_effect=HTTPException(status_code=422, detail={"code": "multiple_people_detected"})),
            ),
            patch("app.routers.body.estimate_body_fat_with_fallback", vendor),
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    fn(
                        request=MagicMock(),
                        scan_request=BodyScanRequest(
                            image_base64="ZmFrZQ==",
                            scan_type="bodyfat",
                            gender="male",
                            age=30,
                            ownership_confirmed=True,
                        ),
                        current_user={"id": "user-1"},
                    )
                )

        assert exc_info.value.status_code == 422
        vendor.assert_not_called()

    def test_transformation_blocked_before_vendor_upload(self):
        from app.routers.body import generate_transformation_journey

        fn = getattr(generate_transformation_journey, "__wrapped__", generate_transformation_journey)
        bf_vendor = AsyncMock()
        realvis_vendor = AsyncMock()

        with (
            patch(
                "app.routers.body._require_safe_body_photo",
                AsyncMock(side_effect=HTTPException(status_code=422, detail={"code": "multiple_people_detected"})),
            ),
            patch("app.routers.body.estimate_body_fat_with_fallback", bf_vendor),
            patch("app.services.realvis_service.generate_realvis_journey", realvis_vendor),
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    fn(
                        request=MagicMock(),
                        scan_request=BodyScanRequest(
                            image_base64="ZmFrZQ==",
                            scan_type="transformation",
                            gender="male",
                            age=30,
                            target_bf=12.0,
                            ownership_confirmed=True,
                        ),
                        current_user={"id": "user-1"},
                    )
                )

        assert exc_info.value.status_code == 422
        bf_vendor.assert_not_called()
        realvis_vendor.assert_not_called()

    def test_enhancement_blocked_before_openai_upload(self):
        from app.routers.body import generate_body_enhancement

        fn = getattr(generate_body_enhancement, "__wrapped__", generate_body_enhancement)
        vendor = AsyncMock()

        with (
            patch(
                "app.routers.body._require_safe_body_photo",
                AsyncMock(side_effect=HTTPException(status_code=422, detail={"code": "ownership_confirmation_required"})),
            ),
            patch("app.routers.body.openai_service.generate_body_enhancement", vendor),
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    fn(
                        request=MagicMock(),
                        scan_request=BodyScanRequest(
                            image_base64="ZmFrZQ==",
                            scan_type="enhancement",
                            gender="male",
                            age=30,
                            enhancement_level="natural",
                            ownership_confirmed=False,
                        ),
                        current_user={"id": "user-1", "age": 30},
                    )
                )

        assert exc_info.value.status_code == 422
        vendor.assert_not_called()

    def test_region_transform_blocked_before_replicate_upload(self):
        from app.routers.body import transform_body_region

        fn = getattr(transform_body_region, "__wrapped__", transform_body_region)
        vendor = AsyncMock()

        with (
            patch(
                "app.routers.body._require_safe_body_photo",
                AsyncMock(side_effect=HTTPException(status_code=422, detail={"code": "ownership_confirmation_required"})),
            ),
            patch("app.routers.body.replicate_service.controlnet_transform_region", vendor),
        ):
            with pytest.raises(HTTPException) as exc_info:
                _run(
                    fn(
                        request=MagicMock(),
                        transform_request=RegionTransformRequest(
                            image_base64="ZmFrZQ==",
                            mask_base64="ZmFrZV9tYXNr",
                            body_part="abs",
                            goal="leaner",
                            gender="male",
                            intensity="moderate",
                            ownership_confirmed=False,
                        ),
                        current_user={"id": "user-1", "age": 30},
                    )
                )

        assert exc_info.value.status_code == 422
        vendor.assert_not_called()
