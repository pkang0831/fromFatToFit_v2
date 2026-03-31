"""Validate body photos: segmentation-based framing + frontal pose heuristics.

Framing uses the **person mask** from Fashn, not a single ``foreground / full image``
ratio (that breaks on wide backgrounds / high resolution). We combine:

- **bbox_area_ratio**: axis-aligned box around the mask vs image area — “how big is the subject in frame”.
- **mask_fill_ratio**: mask pixels / bbox area — “how solid is the silhouette” (rejects speckle noise).
- **body_area_ratio** (API): still ``foreground_pixels / image`` for debugging / clients.

Supports ``upper_body`` (waist-up / mirror-style) vs ``full_body`` stricter framing.
"""

from __future__ import annotations

import base64
import io
import logging
import re
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np
from PIL import Image

from .body_image_utils import lm_visible, load_and_normalize_image
from .segmenter_interface import SegmentationResult

logger = logging.getLogger(__name__)

# ── Tunable thresholds ───────────────────────────────────────────────────────
# Framing pass: (bbox_area_ratio >= MIN_BBOX_*) AND (
#     mask_fill_ratio >= MIN_MASK_FILL_* OR body_area_ratio >= MIN_FG_FALLBACK_* )

MIN_BBOX_AREA_RATIO_FULL = 0.18
MIN_MASK_FILL_RATIO_FULL = 0.30
MIN_FG_FALLBACK_RATIO_FULL = 0.12

MIN_BBOX_AREA_RATIO_UPPER = 0.22
MIN_MASK_FILL_RATIO_UPPER = 0.34
MIN_FG_FALLBACK_RATIO_UPPER = 0.14

# Nose horizontal offset vs shoulder line, normalized by shoulder width in [0,1] space
MAX_NOSE_OFFSET_VS_SHOULDER = 0.38

# Max |y_left - y_right| for shoulders (normalized 0–1)
MAX_SHOULDER_Y_DIFF = 0.07

# Min shoulder width (normalized) so tiny/failed detections don't pass as "frontal"
MIN_SHOULDER_WIDTH_NORM = 0.08

# MediaPipe z: one shoulder much closer to camera than the other ⇒ side / oblique
MAX_SHOULDER_Z_DIFF = 0.14

# Profile: left vs right eye visibility strongly asymmetric (one eye occluded on side face)
EYE_VIS_ASYM_THRESHOLD = 0.52
EYE_VIS_MIN_FOR_ASYM_CHECK = 0.28

# Hips appear much narrower than shoulders in 2D ⇒ common in side view
MIN_HIP_WIDTH_TO_SHOULDER_RATIO = 0.38

# ── Shirtless / lighting thresholds ───────────────────────────────────────────

# Minimum skin-to-(skin+clothing) ratio in the upper-body ROI to count as shirtless.
# 0.50 = at least half the upper body must be bare skin (fashn label 16).
MIN_SHIRTLESS_RATIO = 0.50

# Body-region mean brightness (HSV V channel, 0–255).
# Below this the photo is considered too dark for reliable analysis.
MIN_BODY_BRIGHTNESS = 60


def strip_data_uri_prefix(image_base64: str) -> str:
    s = image_base64.strip()
    if s.startswith("data:"):
        m = re.search(r"base64,(.+)", s, re.DOTALL)
        if m:
            return m.group(1).strip()
    return s


@dataclass
class BodyPhotoQualityResult:
    ok: bool
    body_area_ratio: float
    bbox_area_ratio: float
    mask_fill_ratio: float
    is_front_facing: bool
    pose_detected: bool
    is_shirtless: bool
    brightness: float
    failure_codes: list[str]
    messages: list[str]
    width: int
    height: int
    framing: str
    min_body_area_ratio: float
    min_mask_fill_ratio: float
    foreground_component_count: int = 1
    multiple_subjects_detected: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "body_area_ratio": round(self.body_area_ratio, 4),
            "bbox_area_ratio": round(self.bbox_area_ratio, 4),
            "mask_fill_ratio": round(self.mask_fill_ratio, 4),
            "is_front_facing": self.is_front_facing,
            "pose_detected": self.pose_detected,
            "is_shirtless": self.is_shirtless,
            "brightness": round(self.brightness, 1),
            "failure_codes": list(self.failure_codes),
            "messages": list(self.messages),
            "width": self.width,
            "height": self.height,
            "framing": self.framing,
            "min_body_area_ratio": round(self.min_body_area_ratio, 4),
            "min_mask_fill_ratio": round(self.min_mask_fill_ratio, 4),
        }


def _foreground_mask_from_result(result: SegmentationResult) -> np.ndarray:
    raw = base64.b64decode(result.foreground_mask_b64)
    mask = np.array(Image.open(io.BytesIO(raw)).convert("L"))
    return mask > 127


def _metrics_from_fg_mask(mask: np.ndarray, w: int, h: int) -> tuple[float, float, float]:
    """Return (body_area_ratio, bbox_area_ratio, mask_fill_ratio)."""
    total = float(w * h)
    if total <= 0:
        return 0.0, 0.0, 0.0
    fp = float(np.count_nonzero(mask))
    if fp <= 0:
        return 0.0, 0.0, 0.0
    ys, xs = np.where(mask)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bbox_area = float((x1 - x0 + 1) * (y1 - y0 + 1))
    fg_ratio = fp / total
    bbox_ratio = bbox_area / total
    fill = fp / bbox_area if bbox_area > 0 else 0.0
    return fg_ratio, bbox_ratio, fill


def _body_area_ratio_from_result(result: SegmentationResult) -> float:
    """Foreground / image — prefers decoded mask; falls back to debug_info for tests."""
    w, h = result.width, result.height
    total = float(w * h)
    if total <= 0:
        return 0.0
    if result.foreground_mask_b64:
        mask = _foreground_mask_from_result(result)
        if np.any(mask):
            fg, _, _ = _metrics_from_fg_mask(mask, w, h)
            return fg
    dbg = result.debug_info or {}
    fp = dbg.get("foreground_pixels")
    if fp is not None:
        return float(fp) / total
    return 0.0


def _lm_from_tuple(t: tuple) -> Any:
    x, y, vis = t[0], t[1], t[2]
    z = float(t[3]) if len(t) > 3 else 0.0
    return type("_L", (), {"x": x, "y": y, "visibility": vis, "z": z})()


def _landmarks_from_pose_summary(pose_summary: dict | None):
    """Rebuild landmarks from segmenter ``pose_summary`` (nose, eyes, shoulders, hips + z)."""
    if not pose_summary:
        return None
    lms: list = [None] * 33
    for idx, key in (
        (0, "nose"),
        (2, "left_eye"),
        (5, "right_eye"),
        (11, "left_shoulder"),
        (12, "right_shoulder"),
        (23, "left_hip"),
        (24, "right_hip"),
    ):
        t = pose_summary.get(key)
        if not t or len(t) < 3:
            if idx in (0, 11, 12):
                return None
            continue
        lms[idx] = _lm_from_tuple(t)
    if lms[0] is None or lms[11] is None or lms[12] is None:
        return None
    return lms


def evaluate_frontal_pose(landmarks) -> tuple[bool, list[str]]:
    """Heuristic frontal check: nose vs shoulders, depth (z), eyes, hip line."""
    if landmarks is None:
        return False, ["pose_not_detected"]

    reasons: list[str] = []

    if not (
        lm_visible(landmarks, 0)
        and lm_visible(landmarks, 11)
        and lm_visible(landmarks, 12)
    ):
        return False, ["pose_not_detected"]

    nose = landmarks[0]
    ls = landmarks[11]
    rs = landmarks[12]

    shoulder_w = abs(ls.x - rs.x)
    if shoulder_w < MIN_SHOULDER_WIDTH_NORM:
        reasons.append("shoulders_too_narrow")
        return False, reasons

    z_ls = float(getattr(ls, "z", 0.0))
    z_rs = float(getattr(rs, "z", 0.0))
    if abs(z_ls - z_rs) > MAX_SHOULDER_Z_DIFF:
        reasons.append("shoulders_turned")

    mid_sx = (ls.x + rs.x) * 0.5
    nose_offset = abs(nose.x - mid_sx) / shoulder_w
    if nose_offset > MAX_NOSE_OFFSET_VS_SHOULDER:
        reasons.append("not_frontal")

    le = landmarks[2]
    re = landmarks[5]
    if le is not None and re is not None and le.visibility > EYE_VIS_MIN_FOR_ASYM_CHECK and re.visibility > EYE_VIS_MIN_FOR_ASYM_CHECK:
        if abs(le.visibility - re.visibility) > EYE_VIS_ASYM_THRESHOLD:
            if min(le.visibility, re.visibility) < 0.48:
                reasons.append("profile_pose")

    lh = landmarks[23]
    rh = landmarks[24]
    if (
        lh is not None
        and rh is not None
        and lm_visible(landmarks, 23)
        and lm_visible(landmarks, 24)
    ):
        hip_w = abs(lh.x - rh.x)
        if hip_w < shoulder_w * MIN_HIP_WIDTH_TO_SHOULDER_RATIO:
            reasons.append("hips_too_narrow")

    y_diff = abs(ls.y - rs.y)
    if y_diff > MAX_SHOULDER_Y_DIFF:
        reasons.append("shoulders_not_level")

    ok = len(reasons) == 0
    return ok, reasons if not ok else []


def _check_lighting(pil_img: Image.Image, fg_mask: np.ndarray) -> tuple[bool, float]:
    """Check body-region brightness via HSV V-channel.

    Returns (passes, mean_brightness) where mean_brightness is 0–255.
    Only pixels inside the foreground mask are considered so backgrounds
    don't skew the measurement.
    """
    if not np.any(fg_mask):
        return False, 0.0
    hsv = np.array(pil_img.convert("HSV"))
    v_channel = hsv[:, :, 2]
    body_v = v_channel[fg_mask]
    mean_brightness = float(body_v.mean())
    return mean_brightness >= MIN_BODY_BRIGHTNESS, mean_brightness


def _foreground_component_stats(mask: np.ndarray) -> tuple[int, bool]:
    if not np.any(mask):
        return 0, False

    binary = mask.astype(np.uint8)
    component_count, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    if component_count <= 1:
        return 0, False

    areas = [int(stats[idx, cv2.CC_STAT_AREA]) for idx in range(1, component_count)]
    if not areas:
        return 0, False

    areas.sort(reverse=True)
    total_foreground = sum(areas)
    largest = areas[0]
    significant_threshold = max(int(total_foreground * 0.05), int(largest * 0.2), 1500)
    significant_components = [area for area in areas if area >= significant_threshold]

    return len(significant_components), len(significant_components) > 1


def _thresholds_for_framing(framing: str) -> tuple[float, float, float]:
    """min_bbox_area_ratio, min_mask_fill_ratio, min_fg_fallback_ratio."""
    if framing == "full_body":
        return (
            MIN_BBOX_AREA_RATIO_FULL,
            MIN_MASK_FILL_RATIO_FULL,
            MIN_FG_FALLBACK_RATIO_FULL,
        )
    return (
        MIN_BBOX_AREA_RATIO_UPPER,
        MIN_MASK_FILL_RATIO_UPPER,
        MIN_FG_FALLBACK_RATIO_UPPER,
    )


def _framing_passes(framing: str, fg_ratio: float, bbox_ratio: float, fill: float) -> bool:
    min_bbox, min_fill, min_fg_fb = _thresholds_for_framing(framing)
    if bbox_ratio < min_bbox:
        return False
    return fill >= min_fill or fg_ratio >= min_fg_fb


def _messages_for_failures(
    codes: list[str],
    *,
    framing: str,
) -> list[str]:
    msgs: list[str] = []
    if "body_too_small" in codes:
        if framing == "upper_body":
            msgs.append(
                "Your upper body should fill more of the frame — move closer or zoom in so you’re "
                "clearly visible (match the sample framing)."
            )
        else:
            msgs.append(
                "Your body should fill more of the frame — move closer or zoom in so you’re the main subject, "
                "not a small figure with lots of empty background."
            )
    if "pose_not_detected" in codes:
        if framing == "upper_body":
            msgs.append(
                "Face and shoulders should be clearly visible, like the sample photo. "
                "Stand in front of the camera."
            )
        else:
            msgs.append(
                "Could not detect a clear standing pose. Face the camera with your full body visible."
            )
    if any(
        c in codes
        for c in (
            "not_frontal",
            "profile_pose",
            "shoulders_turned",
            "hips_too_narrow",
        )
    ):
        msgs.append(
            "Use a straight-on, front-facing photo — not side profile or back view. "
            "Face the camera with your shoulders square."
        )
    if "shoulders_not_level" in codes:
        msgs.append("Keep shoulders level and stand straight.")
    if "shoulders_too_narrow" in codes:
        msgs.append("Move back so your upper body is clearly visible.")
    if "wearing_top" in codes:
        msgs.append(
            "For accurate body analysis, please remove your shirt and upload "
            "a shirtless photo with your upper body clearly visible."
        )
    if "too_dark" in codes:
        msgs.append(
            "The photo is too dark — use better lighting so your body is "
            "clearly visible. Natural or bright indoor light works best."
        )
    return msgs


async def analyze_body_photo_quality(
    image_base64: str,
    framing: str = "upper_body",
) -> BodyPhotoQualityResult:
    """
    Run human segmentation + pose checks.

    ``framing``: ``upper_body`` (default, waist-up friendly) or ``full_body`` (stricter).

    Raises ValueError on invalid image data.
    """
    if framing not in ("upper_body", "full_body"):
        framing = "upper_body"
    min_bbox, min_fill, _ = _thresholds_for_framing(framing)

    logger.warning(
        "analyze_body_photo_quality: start framing=%s min_bbox=%.2f min_fill=%.2f",
        framing,
        min_bbox,
        min_fill,
    )

    b64 = strip_data_uri_prefix(image_base64)
    pil_img = load_and_normalize_image(b64)
    img_w, img_h = pil_img.size

    from .fashn_human_parser import FashnHumanParserSegmenter

    segmenter = FashnHumanParserSegmenter()
    seg_result = await segmenter.segment(b64)

    fg_mask = _foreground_mask_from_result(seg_result)
    body_area_ratio, bbox_area_ratio, mask_fill_ratio = _metrics_from_fg_mask(
        fg_mask, img_w, img_h
    )
    foreground_component_count, multiple_subjects_detected = _foreground_component_stats(fg_mask)

    # Lighting check (body-region HSV brightness)
    lighting_ok, brightness = _check_lighting(pil_img, fg_mask)

    logger.warning(
        "analyze_body_photo_quality: fg=%.3f bbox=%.3f fill=%.3f brightness=%.1f",
        body_area_ratio,
        bbox_area_ratio,
        mask_fill_ratio,
        brightness,
    )

    dbg = seg_result.debug_info or {}
    pose_summary = dbg.get("pose_summary")
    landmarks = _landmarks_from_pose_summary(pose_summary)
    pose_detected = bool(dbg.get("pose_detected"))

    is_front, pose_reasons = evaluate_frontal_pose(landmarks)

    # Shirtless check — only meaningful when pose was detected (landmarks
    # define the ROI). When pose is missing, shirtless_ratio defaults to 0
    # which would false-positive; skip the check and let pose_not_detected
    # surface instead.
    shirtless_ratio = float(dbg.get("shirtless_ratio", -1.0))
    can_check_shirtless = pose_detected and shirtless_ratio >= 0.0
    is_shirtless = shirtless_ratio >= MIN_SHIRTLESS_RATIO if can_check_shirtless else True

    logger.warning(
        "analyze_body_photo_quality: shirtless_ratio=%.3f is_shirtless=%s can_check=%s",
        shirtless_ratio,
        is_shirtless,
        can_check_shirtless,
    )

    framing_ok = _framing_passes(framing, body_area_ratio, bbox_area_ratio, mask_fill_ratio)

    failure_codes: list[str] = []
    if not framing_ok:
        failure_codes.append("body_too_small")
    for code in pose_reasons:
        if code not in failure_codes:
            failure_codes.append(code)
    if can_check_shirtless and not is_shirtless:
        failure_codes.append("wearing_top")
    if not lighting_ok:
        failure_codes.append("too_dark")

    messages = _messages_for_failures(
        failure_codes,
        framing=framing,
    )
    ok = framing_ok and is_front and pose_detected and is_shirtless and lighting_ok

    if ok:
        messages = ["Photo meets all quality guidelines."]

    return BodyPhotoQualityResult(
        ok=ok,
        body_area_ratio=body_area_ratio,
        bbox_area_ratio=bbox_area_ratio,
        mask_fill_ratio=mask_fill_ratio,
        is_front_facing=is_front,
        pose_detected=pose_detected,
        is_shirtless=is_shirtless,
        brightness=brightness,
        failure_codes=failure_codes,
        messages=messages,
        width=img_w,
        height=img_h,
        framing=framing,
        min_body_area_ratio=min_bbox,
        min_mask_fill_ratio=min_fill,
        foreground_component_count=foreground_component_count,
        multiple_subjects_detected=multiple_subjects_detected,
    )
