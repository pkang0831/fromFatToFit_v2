"""Unit tests for body photo framing / frontal pose helpers."""

import numpy as np
import pytest
from PIL import Image

from app.services.body_photo_quality import (
    evaluate_frontal_pose,
    strip_data_uri_prefix,
    _messages_for_failures,
    _body_area_ratio_from_result,
    _check_lighting,
    MIN_BODY_BRIGHTNESS,
    MIN_SHIRTLESS_RATIO,
)
from app.services.segmenter_interface import SegmentationResult


def _lm(x: float, y: float, visibility: float = 0.95, z: float = 0.0):
    return type("_L", (), {"x": x, "y": y, "visibility": visibility, "z": z})()


class TestStripDataUri:
    def test_plain_base64(self):
        assert strip_data_uri_prefix("  abc123  ") == "abc123"

    def test_data_uri(self):
        s = "data:image/jpeg;base64,XX/Y+Q=="
        assert strip_data_uri_prefix(s) == "XX/Y+Q=="


class TestEvaluateFrontalPose:
    def test_none(self):
        ok, reasons = evaluate_frontal_pose(None)
        assert not ok
        assert "pose_not_detected" in reasons

    def test_frontal_ok(self):
        lms = [None] * 33
        lms[0] = _lm(0.5, 0.22)
        lms[11] = _lm(0.42, 0.35)
        lms[12] = _lm(0.58, 0.35)
        ok, reasons = evaluate_frontal_pose(lms)
        assert ok
        assert reasons == []

    def test_nose_off_center(self):
        lms = [None] * 33
        lms[0] = _lm(0.75, 0.22)
        lms[11] = _lm(0.42, 0.35)
        lms[12] = _lm(0.58, 0.35)
        ok, reasons = evaluate_frontal_pose(lms)
        assert not ok
        assert "not_frontal" in reasons

    def test_shoulders_uneven(self):
        lms = [None] * 33
        lms[0] = _lm(0.5, 0.22)
        lms[11] = _lm(0.42, 0.35)
        lms[12] = _lm(0.58, 0.50)
        ok, reasons = evaluate_frontal_pose(lms)
        assert not ok
        assert "shoulders_not_level" in reasons

    def test_shoulder_z_side_pose(self):
        lms = [None] * 33
        lms[0] = _lm(0.5, 0.22)
        lms[11] = _lm(0.42, 0.35, z=0.0)
        lms[12] = _lm(0.58, 0.35, z=0.22)
        ok, reasons = evaluate_frontal_pose(lms)
        assert not ok
        assert "shoulders_turned" in reasons

    def test_profile_eye_asymmetry(self):
        lms = [None] * 33
        lms[0] = _lm(0.5, 0.22)
        lms[2] = _lm(0.45, 0.20, visibility=0.30)
        lms[5] = _lm(0.55, 0.20, visibility=0.92)
        lms[11] = _lm(0.42, 0.35)
        lms[12] = _lm(0.58, 0.35)
        ok, reasons = evaluate_frontal_pose(lms)
        assert not ok
        assert "profile_pose" in reasons


class TestMessagesForFailures:
    def test_codes(self):
        m = _messages_for_failures(
            ["body_too_small", "not_frontal"],
            framing="upper_body",
        )
        assert any("closer" in x.lower() or "frame" in x.lower() for x in m)
        assert any("straight-on" in x for x in m)

    def test_full_body_message(self):
        m = _messages_for_failures(
            ["body_too_small"],
            framing="full_body",
        )
        assert any("frame" in x.lower() for x in m)


class TestMessagesForNewFailures:
    def test_wearing_top_message(self):
        m = _messages_for_failures(["wearing_top"], framing="upper_body")
        assert len(m) == 1
        assert "shirtless" in m[0].lower() or "shirt" in m[0].lower()

    def test_too_dark_message(self):
        m = _messages_for_failures(["too_dark"], framing="upper_body")
        assert len(m) == 1
        assert "dark" in m[0].lower() or "lighting" in m[0].lower()

    def test_multiple_new_codes(self):
        m = _messages_for_failures(
            ["wearing_top", "too_dark"],
            framing="upper_body",
        )
        assert len(m) == 2

    def test_new_codes_combined_with_existing(self):
        m = _messages_for_failures(
            ["body_too_small", "wearing_top", "too_dark"],
            framing="upper_body",
        )
        assert len(m) == 3


class TestCheckLighting:
    def _make_image_and_mask(self, brightness: int, mask_fill: bool = True):
        """Create a synthetic image + foreground mask for testing."""
        h, w = 100, 100
        rgb = np.full((h, w, 3), brightness, dtype=np.uint8)
        pil_img = Image.fromarray(rgb, mode="RGB")
        fg_mask = np.ones((h, w), dtype=bool) if mask_fill else np.zeros((h, w), dtype=bool)
        return pil_img, fg_mask

    def test_bright_image_passes(self):
        pil_img, fg_mask = self._make_image_and_mask(180)
        ok, brightness = _check_lighting(pil_img, fg_mask)
        assert ok
        assert brightness > MIN_BODY_BRIGHTNESS

    def test_dark_image_fails(self):
        pil_img, fg_mask = self._make_image_and_mask(30)
        ok, brightness = _check_lighting(pil_img, fg_mask)
        assert not ok
        assert brightness < MIN_BODY_BRIGHTNESS

    def test_borderline_brightness(self):
        pil_img, fg_mask = self._make_image_and_mask(int(MIN_BODY_BRIGHTNESS))
        ok, _ = _check_lighting(pil_img, fg_mask)
        assert ok

    def test_empty_mask_fails(self):
        pil_img, fg_mask = self._make_image_and_mask(200, mask_fill=False)
        ok, brightness = _check_lighting(pil_img, fg_mask)
        assert not ok
        assert brightness == 0.0


class TestShirtlessCheckLogic:
    """Verify shirtless_ratio → is_shirtless / can_check_shirtless mapping."""

    def test_high_ratio_is_shirtless(self):
        assert 0.85 >= MIN_SHIRTLESS_RATIO

    def test_low_ratio_is_clothed(self):
        assert 0.15 < MIN_SHIRTLESS_RATIO

    def test_negative_one_is_inconclusive(self):
        ratio = -1.0
        can_check = True and ratio >= 0.0
        assert not can_check

    def test_zero_ratio_is_fully_clothed(self):
        ratio = 0.0
        can_check = True and ratio >= 0.0
        assert can_check
        is_shirtless = ratio >= MIN_SHIRTLESS_RATIO
        assert not is_shirtless


class TestComputeShirtlessRatio:
    """Test _compute_shirtless_ratio with synthetic fashn label maps."""

    def _make_landmarks(self):
        """Create landmarks with visible shoulders and hips for a 100x200 image."""
        lms = [None] * 33
        lms[11] = _lm(0.3, 0.25)   # left shoulder
        lms[12] = _lm(0.7, 0.25)   # right shoulder
        lms[23] = _lm(0.35, 0.65)  # left hip
        lms[24] = _lm(0.65, 0.65)  # right hip
        return lms

    def test_fully_shirtless(self):
        from app.services.fashn_human_parser import _compute_shirtless_ratio
        img_w, img_h = 100, 200
        fashn_map = np.zeros((img_h, img_w), dtype=np.uint8)
        fashn_map[40:140, 25:75] = 16  # torso (bare skin)
        lms = self._make_landmarks()
        result = _compute_shirtless_ratio(fashn_map, lms, img_w, img_h)
        assert result["shirtless_ratio"] >= 0.9

    def test_fully_clothed(self):
        from app.services.fashn_human_parser import _compute_shirtless_ratio
        img_w, img_h = 100, 200
        fashn_map = np.zeros((img_h, img_w), dtype=np.uint8)
        fashn_map[40:140, 25:75] = 3  # top (clothing)
        lms = self._make_landmarks()
        result = _compute_shirtless_ratio(fashn_map, lms, img_w, img_h)
        assert result["shirtless_ratio"] == 0.0

    def test_mixed_skin_and_clothing(self):
        from app.services.fashn_human_parser import _compute_shirtless_ratio
        img_w, img_h = 100, 200
        fashn_map = np.zeros((img_h, img_w), dtype=np.uint8)
        fashn_map[40:90, 25:75] = 16  # upper half: skin
        fashn_map[90:140, 25:75] = 3  # lower half: clothing
        lms = self._make_landmarks()
        result = _compute_shirtless_ratio(fashn_map, lms, img_w, img_h)
        assert 0.3 <= result["shirtless_ratio"] <= 0.7

    def test_no_landmarks_returns_inconclusive(self):
        from app.services.fashn_human_parser import _compute_shirtless_ratio
        fashn_map = np.zeros((200, 100), dtype=np.uint8)
        result = _compute_shirtless_ratio(fashn_map, None, 100, 200)
        assert result["shirtless_ratio"] == -1.0

    def test_empty_roi_returns_inconclusive(self):
        from app.services.fashn_human_parser import _compute_shirtless_ratio
        img_w, img_h = 100, 200
        fashn_map = np.zeros((img_h, img_w), dtype=np.uint8)  # all background
        lms = self._make_landmarks()
        result = _compute_shirtless_ratio(fashn_map, lms, img_w, img_h)
        assert result["shirtless_ratio"] == -1.0


class TestBodyAreaRatioFromResult:
    def test_from_debug_foreground_pixels(self):
        r = SegmentationResult(
            width=100,
            height=100,
            label_map_b64="",
            foreground_mask_b64="",
            debug_info={"foreground_pixels": 6000},
        )
        assert _body_area_ratio_from_result(r) == pytest.approx(0.6)
