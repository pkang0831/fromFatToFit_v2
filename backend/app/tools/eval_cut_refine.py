"""
Offline evaluation / regression harness for the CUT refinement pipeline.

Evaluates three stages per test case:
  A. warp only
  B. warp + seam repair (pass 1)
  C. warp + seam repair + torso refine (pass 1 + 2)

Saves all intermediates, computes safety and edit metrics, and produces
an HTML comparison report.

Usage:
    python -m backend.app.tools.eval_cut_refine \
        --input-dir test_cases \
        --output-dir eval_runs/run_001 \
        --preset medium \
        --seed 42

Prerequisites:
    1. Test cases generated via generate_test_cases.py
    2. SD 1.5 inpainting model downloaded:
       python -m backend.app.tools.download_models download --profile sd15_only
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
# § 1  Image I/O helpers
# ═════════════════════════════════════════════════════════════════════════════

def _load_rgb(path: Path) -> np.ndarray:
    """Load RGB image with EXIF orientation applied.

    Prefers a lossless .png sidecar when available so that metrics are
    not polluted by JPEG re-encoding artefacts.
    """
    png_path = path.with_suffix(".png")
    load_path = png_path if png_path.exists() else path
    img = Image.open(load_path)
    img = ImageOps.exif_transpose(img) or img
    return np.array(img.convert("RGB"))


def _load_mask(path: Path, w: int, h: int) -> np.ndarray:
    """Load a grayscale mask, resize to (w, h), return bool array."""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img) or img
    img = img.convert("L").resize((w, h), Image.NEAREST)
    return np.array(img) > 128


def _load_float_map(path: Path, w: int, h: int) -> np.ndarray:
    img = Image.open(path)
    img = ImageOps.exif_transpose(img) or img
    img = img.convert("L").resize((w, h), Image.BILINEAR)
    return np.array(img).astype(np.float32) / 255.0


def _save_rgb(arr: np.ndarray, path: Path) -> None:
    """Save as lossless PNG (for metrics) and JPEG (for viewing)."""
    pil = Image.fromarray(arr)
    pil.save(path.with_suffix(".png"), format="PNG")
    pil.save(path.with_suffix(".jpg"), format="JPEG", quality=95)


def _save_mask(arr: np.ndarray, path: Path) -> None:
    if arr.dtype == bool:
        arr = arr.astype(np.uint8) * 255
    Image.fromarray(arr, mode="L").save(path, format="PNG")


def _encode_mask_b64(arr: np.ndarray) -> str:
    if arr.dtype == bool:
        arr = arr.astype(np.uint8) * 255
    buf = io.BytesIO()
    Image.fromarray(arr, mode="L").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ═════════════════════════════════════════════════════════════════════════════
# § 2  Metrics computation
# ═════════════════════════════════════════════════════════════════════════════

def compute_safety_metrics(
    original: np.ndarray,
    result: np.ndarray,
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
) -> dict:
    """Measure how much the result changed in regions that should be untouched.

    Lower values = safer.
    """
    diff = np.abs(original.astype(np.float32) - result.astype(np.float32))
    pixel_diff = diff.mean(axis=2)

    outside = ~edit_mask
    outside_px = int(outside.sum())
    outside_mae = float(pixel_diff[outside].mean()) if outside_px > 0 else 0.0
    outside_max = float(pixel_diff[outside].max()) if outside_px > 0 else 0.0
    outside_changed = int((pixel_diff[outside] > 3.0).sum())
    outside_changed_ratio = outside_changed / max(1, outside_px)

    protect_px = int(protect_mask.sum())
    protect_mae = float(pixel_diff[protect_mask].mean()) if protect_px > 0 else 0.0
    protect_max = float(pixel_diff[protect_mask].max()) if protect_px > 0 else 0.0
    protect_changed = int((pixel_diff[protect_mask] > 2.0).sum())
    protect_changed_ratio = protect_changed / max(1, protect_px)

    return {
        "outside_edit_mae": round(outside_mae, 3),
        "outside_edit_max": round(outside_max, 3),
        "outside_edit_changed_px": outside_changed,
        "outside_edit_changed_ratio": round(outside_changed_ratio, 6),
        "protect_mae": round(protect_mae, 3),
        "protect_max": round(protect_max, 3),
        "protect_changed_px": protect_changed,
        "protect_changed_ratio": round(protect_changed_ratio, 6),
    }


def compute_edit_metrics(
    warped: np.ndarray,
    result: np.ndarray,
    edit_mask: np.ndarray,
    seam_mask: np.ndarray,
    torso_mask: np.ndarray,
) -> dict:
    """Measure the magnitude and character of edits within allowed regions."""
    diff = np.abs(warped.astype(np.float32) - result.astype(np.float32))
    pixel_diff = diff.mean(axis=2)

    edit_px = int(edit_mask.sum())
    edit_mae = float(pixel_diff[edit_mask].mean()) if edit_px > 0 else 0.0

    seam_bool = seam_mask > 0
    seam_px = int(seam_bool.sum())
    seam_mae = float(pixel_diff[seam_bool].mean()) if seam_px > 0 else 0.0

    torso_bool = torso_mask > 0
    torso_px = int(torso_bool.sum())
    torso_mae = float(pixel_diff[torso_bool].mean()) if torso_px > 0 else 0.0

    edit_vals = pixel_diff[edit_mask]
    if len(edit_vals) > 0:
        p50 = float(np.percentile(edit_vals, 50))
        p90 = float(np.percentile(edit_vals, 90))
        p99 = float(np.percentile(edit_vals, 99))
    else:
        p50 = p90 = p99 = 0.0

    return {
        "edit_region_mae": round(edit_mae, 3),
        "edit_region_p50": round(p50, 3),
        "edit_region_p90": round(p90, 3),
        "edit_region_p99": round(p99, 3),
        "seam_band_mae": round(seam_mae, 3),
        "seam_band_px": seam_px,
        "torso_interior_mae": round(torso_mae, 3),
        "torso_interior_px": torso_px,
    }


# ═════════════════════════════════════════════════════════════════════════════
# § 2.5  Pass-2 regression metrics + debug overlays
# ═════════════════════════════════════════════════════════════════════════════

def _compute_lower_belly_regression(
    after_seam: np.ndarray,
    final: np.ndarray,
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    seam_mask: np.ndarray,
    warped: np.ndarray,
    out_dir: Path,
) -> dict:
    """Detect pass2 re-inflating the lower belly.

    Compares after_seam (pass1 output) vs final (pass2 output) in the
    lower-belly center zone — the region most vulnerable to SD inpainting
    reverting the warped-flatter silhouette back to a rounder average.
    """
    from backend.app.services.cut_refine import _build_lower_belly_center_mask

    h, w = edit_mask.shape
    lb_mask = _build_lower_belly_center_mask(edit_mask, protect_mask, seam_mask)
    lb_px = int(lb_mask.sum())

    result: dict = {"lower_belly_center_px": lb_px}

    if lb_px < 100:
        result.update({
            "lower_belly_mae": 0.0,
            "lower_belly_p90": 0.0,
            "lower_belly_brightness_shift": 0.0,
            "lower_belly_regression": False,
        })
        return result

    diff_lb = np.abs(
        final.astype(np.float32) - after_seam.astype(np.float32),
    ).mean(axis=2)

    lb_mae = float(diff_lb[lb_mask].mean())
    lb_p90 = float(np.percentile(diff_lb[lb_mask], 90))

    # Signed brightness shift: positive = pass2 made it brighter (rounder
    # bellies tend to have more highlight due to curvature).
    final_lum = final.astype(np.float32).mean(axis=2)
    seam_lum = after_seam.astype(np.float32).mean(axis=2)
    brightness_shift = float((final_lum[lb_mask] - seam_lum[lb_mask]).mean())

    from backend.app.services.cut_refine import PASS2_LOWER_BELLY_REJECT_MAE
    regression = lb_mae > PASS2_LOWER_BELLY_REJECT_MAE

    result.update({
        "lower_belly_mae": round(lb_mae, 3),
        "lower_belly_p90": round(lb_p90, 3),
        "lower_belly_brightness_shift": round(brightness_shift, 3),
        "lower_belly_regression": regression,
    })

    # Debug overlay: lower-belly region highlighted
    _save_lower_belly_overlay(
        warped, lb_mask, out_dir / "10_lower_belly_region.png",
    )

    return result


def _compute_lean_signal(
    original: np.ndarray,
    warped: np.ndarray,
    final: np.ndarray,
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    seam_mask: np.ndarray,
    case_meta: dict,
) -> dict:
    """Perceptual lean-signal metrics.

    Measures whether the final result reads visibly leaner than the original:
    - waist width reduction from warp metadata (geometry measured at warp time)
    - upper-ab texture definition gain (warped → final, Laplacian variance)
    - oblique texture definition gain (warped → final, Laplacian variance)
    """
    from backend.app.services.cut_refine import _PROTECT_BUFFER_PX

    h, w = edit_mask.shape
    result: dict = {}

    # ── Waist width reduction from warp metadata ──────────────────────────
    warp_debug = case_meta.get("warp_debug", {})
    warp_waist = warp_debug.get("waist_metrics", {}).get("scanlines", [])

    waist_reductions = []
    for scan in warp_waist:
        frac = scan.get("frac", 0)
        pct = scan.get("reduction_pct", 0)
        label = f"waist_{int(frac*100)}"
        result[f"{label}_reduction_pct"] = pct
        result[f"{label}_orig_px"] = scan.get("width_before", 0)
        result[f"{label}_final_px"] = scan.get("width_after", 0)
        waist_reductions.append(pct)

    if not waist_reductions:
        result["waist_50_reduction_pct"] = 0.0
        result["waist_65_reduction_pct"] = 0.0
        result["waist_80_reduction_pct"] = 0.0

    # ── Texture definition gain (warped → final via Laplacian variance) ───
    #    Compares warped (pre-pass2) vs final (post-pass2) to measure
    #    how much definition pass2 added in each zone.
    warped_gray = cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY).astype(np.float32)
    final_gray = cv2.cvtColor(final, cv2.COLOR_RGB2GRAY).astype(np.float32)
    warped_lap = cv2.Laplacian(warped_gray, cv2.CV_32F, ksize=3)
    final_lap = cv2.Laplacian(final_gray, cv2.CV_32F, ksize=3)

    candidate = edit_mask.copy()
    buf_k = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (_PROTECT_BUFFER_PX, _PROTECT_BUFFER_PX),
    )
    protect_buf = cv2.dilate(
        protect_mask.astype(np.uint8), buf_k, iterations=1,
    ) > 0
    candidate &= ~protect_buf

    rows_active = np.where(candidate.any(axis=1))[0]
    if len(rows_active) >= 20:
        top_y = int(rows_active.min())
        bot_y = int(rows_active.max())
        span = bot_y - top_y

        # Upper-ab zone: 25-50% of span, center 60% width
        upper_ab = np.zeros((h, w), dtype=bool)
        ua_top = top_y + int(span * 0.25)
        ua_bot = top_y + int(span * 0.50)
        for y in range(ua_top, min(ua_bot, h)):
            row_cols = np.where(candidate[y])[0]
            if len(row_cols) < 4:
                continue
            rl, rr = int(row_cols.min()), int(row_cols.max())
            rw = rr - rl
            margin = int(rw * 0.20)
            upper_ab[y, rl + margin:rr - margin + 1] = True
        upper_ab &= candidate

        # Oblique zone: 30-75% of span, outer 30% on each side
        oblique = np.zeros((h, w), dtype=bool)
        ob_top = top_y + int(span * 0.30)
        ob_bot = top_y + int(span * 0.75)
        for y in range(ob_top, min(ob_bot, h)):
            row_cols = np.where(candidate[y])[0]
            if len(row_cols) < 8:
                continue
            rl, rr = int(row_cols.min()), int(row_cols.max())
            rw = rr - rl
            inner_margin = int(rw * 0.30)
            left_band = candidate[y].copy()
            left_band[rl + inner_margin:] = False
            right_band = candidate[y].copy()
            right_band[:rr - inner_margin] = False
            oblique[y] = left_band | right_band
        oblique &= candidate

        def _variance_gain(zone_mask: np.ndarray) -> tuple[float, float, float]:
            px = int(zone_mask.sum())
            if px < 100:
                return 0.0, 0.0, 0.0
            w_var = float(np.var(warped_lap[zone_mask]))
            f_var = float(np.var(final_lap[zone_mask]))
            gain = (f_var - w_var) / max(1.0, w_var) * 100
            return round(w_var, 1), round(f_var, 1), round(gain, 2)

        w_v, f_v, g = _variance_gain(upper_ab)
        result["upper_ab_tex_var_warped"] = w_v
        result["upper_ab_tex_var_final"] = f_v
        result["upper_ab_tex_gain_pct"] = g
        result["upper_ab_px"] = int(upper_ab.sum())

        w_v, f_v, g = _variance_gain(oblique)
        result["oblique_tex_var_warped"] = w_v
        result["oblique_tex_var_final"] = f_v
        result["oblique_tex_gain_pct"] = g
        result["oblique_px"] = int(oblique.sum())
    else:
        for prefix in ("upper_ab", "oblique"):
            result[f"{prefix}_tex_var_warped"] = 0.0
            result[f"{prefix}_tex_var_final"] = 0.0
            result[f"{prefix}_tex_gain_pct"] = 0.0
            result[f"{prefix}_px"] = 0

    # ── Lean-signal summary ───────────────────────────────────────────────
    avg_waist = sum(waist_reductions) / max(1, len(waist_reductions)) if waist_reductions else 0.0
    ua_gain = result.get("upper_ab_tex_gain_pct", 0)
    ob_gain = result.get("oblique_tex_gain_pct", 0)

    lean_score = avg_waist * 0.6 + max(0, ua_gain) * 0.003 + max(0, ob_gain) * 0.002
    result["lean_score"] = round(lean_score, 2)
    result["avg_waist_reduction_pct"] = round(avg_waist, 2)

    return result


def _compute_pass2_regression(
    torso_mask: np.ndarray,
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    seam_mask: np.ndarray,
    weight_map: np.ndarray,
    after_seam: np.ndarray,
    final: np.ndarray,
    original_pil: Image.Image,
    roi_info: dict | None,
    out_dir: Path,
    warped: np.ndarray,
) -> dict:
    """Comprehensive pass-2 regression metrics + visual debug artifacts."""
    from backend.app.services.cut_refine import (
        _PROTECT_BUFFER_PX, _SHOULDER_SUPPRESS_FRAC, _MIN_TORSO_CORE_PX,
    )

    h, w = edit_mask.shape
    torso_bool = torso_mask > 0
    torso_px = int(torso_bool.sum())
    edit_px = int(edit_mask.sum())

    reg: dict = {
        "pass2_mask_area_px": torso_px,
        "pass2_mask_area_ratio_vs_edit": round(torso_px / max(1, edit_px), 4),
    }

    if roi_info:
        reg["pass2_roi_w"] = roi_info.get("roi_w", 0)
        reg["pass2_roi_h"] = roi_info.get("roi_h", 0)
    else:
        reg["pass2_roi_w"] = 0
        reg["pass2_roi_h"] = 0

    # Protect-mask overlap
    protect_overlap = int((torso_bool & protect_mask).sum())
    reg["protect_overlap_px"] = protect_overlap
    reg["protect_overlap_ratio"] = round(protect_overlap / max(1, torso_px), 6)

    # ── Fashn label overlap (shoulder + arm) ──────────────────────────────
    shoulder_mask = np.zeros((h, w), dtype=bool)
    arm_mask = np.zeros((h, w), dtype=bool)
    fashn_ok = False
    try:
        from backend.app.services.fashn_human_parser import (
            run_fashn_parsing, detect_pose, _remap_to_seg_classes,
        )
        fashn_map = run_fashn_parsing(original_pil)
        img_bgr = cv2.cvtColor(np.array(original_pil), cv2.COLOR_RGB2BGR)
        landmarks = detect_pose(img_bgr)
        img_w, img_h = original_pil.size
        label_map = _remap_to_seg_classes(fashn_map, landmarks, img_w, img_h)

        shoulder_mask = (label_map == 4) | (label_map == 5)
        arm_mask = (fashn_map == 12)
        fashn_ok = True
    except Exception as exc:
        logger.warning(f"Fashn overlap computation skipped: {exc}")

    shoulder_overlap = int((torso_bool & shoulder_mask).sum())
    arm_overlap = int((torso_bool & arm_mask).sum())
    reg["shoulder_overlap_px"] = shoulder_overlap
    reg["shoulder_overlap_ratio"] = round(shoulder_overlap / max(1, torso_px), 6)
    reg["arm_overlap_px"] = arm_overlap
    reg["arm_overlap_ratio"] = round(arm_overlap / max(1, torso_px), 6)
    reg["fashn_overlap_available"] = fashn_ok

    # ── MAE(final vs pass1) inside torso mask ─────────────────────────────
    if torso_px > 0:
        diff_p2 = np.abs(
            final.astype(np.float32) - after_seam.astype(np.float32),
        ).mean(axis=2)
        reg["mae_final_vs_pass1_in_torso"] = round(float(diff_p2[torso_bool].mean()), 3)
        reg["mae_final_vs_pass1_p90_in_torso"] = round(
            float(np.percentile(diff_p2[torso_bool], 90)), 3,
        )
    else:
        reg["mae_final_vs_pass1_in_torso"] = 0.0
        reg["mae_final_vs_pass1_p90_in_torso"] = 0.0

    # ── MAE(final vs pass1) outside edit region ───────────────────────────
    outside = ~edit_mask
    if outside.any():
        diff_out = np.abs(
            final.astype(np.float32) - after_seam.astype(np.float32),
        ).mean(axis=2)
        reg["mae_final_vs_pass1_outside_edit"] = round(
            float(diff_out[outside].mean()), 3,
        )
    else:
        reg["mae_final_vs_pass1_outside_edit"] = 0.0

    # ── Fallback-to-full-candidate detection ──────────────────────────────
    candidate = edit_mask.copy()
    buf_k = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (_PROTECT_BUFFER_PX, _PROTECT_BUFFER_PX),
    )
    protect_buf = cv2.dilate(
        protect_mask.astype(np.uint8), buf_k, iterations=1,
    ) > 0
    candidate &= ~protect_buf
    if np.any(seam_mask > 0):
        seam_dil = cv2.dilate(
            (seam_mask > 0).astype(np.uint8) * 255,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
            iterations=1,
        ) > 0
        candidate &= ~seam_dil
    rows_active = np.where(candidate.any(axis=1))[0]
    if len(rows_active) >= 10:
        top_y, bot_y = int(rows_active.min()), int(rows_active.max())
        span = bot_y - top_y
        if span >= 20:
            suppress_y = top_y + int(span * _SHOULDER_SUPPRESS_FRAC)
            candidate[:suppress_y, :] = False
    candidate_px = int(candidate.sum())
    reg["candidate_mask_px"] = candidate_px
    if candidate_px > 0:
        coverage = torso_px / candidate_px
        reg["fallback_triggered"] = coverage > 0.95
        reg["core_vs_candidate_ratio"] = round(coverage, 4)
    else:
        reg["fallback_triggered"] = False
        reg["core_vs_candidate_ratio"] = 0.0

    # ── Lower-belly regression ────────────────────────────────────────────
    lb_reg = _compute_lower_belly_regression(
        after_seam, final, edit_mask, protect_mask, seam_mask, warped, out_dir,
    )
    reg.update(lb_reg)

    # ── Debug overlays ────────────────────────────────────────────────────
    _save_mask_overlay(warped, torso_mask, out_dir / "08_pass2_mask_overlay.png")
    _save_overlap_debug(
        warped, torso_mask, shoulder_mask, arm_mask, protect_mask,
        out_dir / "09_pass2_overlap_debug.png",
    )
    _save_mask_zone_debug(
        warped, torso_mask, edit_mask, protect_mask, seam_mask,
        out_dir / "11_mask_zone_debug.png",
    )

    return reg


def _save_mask_overlay(
    image: np.ndarray,
    mask: np.ndarray,
    path: Path,
) -> None:
    """Save image with semi-transparent red mask overlay + contour."""
    h, w = image.shape[:2]
    scale = min(1.0, 1600 / max(w, h))
    new_w, new_h = int(w * scale), int(h * scale)
    vis = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA).copy()
    m = cv2.resize(
        (mask > 0).astype(np.uint8), (new_w, new_h),
        interpolation=cv2.INTER_NEAREST,
    ) > 0

    vis[m, 0] = np.clip(vis[m, 0].astype(int) + 80, 0, 255).astype(np.uint8)
    vis[m, 1] = (vis[m, 1] * 0.6).astype(np.uint8)
    vis[m, 2] = (vis[m, 2] * 0.6).astype(np.uint8)

    contours, _ = cv2.findContours(
        m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )
    cv2.drawContours(vis, contours, -1, (255, 60, 60), 2)
    Image.fromarray(vis).save(path, format="PNG")


def _save_overlap_debug(
    image: np.ndarray,
    torso_mask: np.ndarray,
    shoulder_mask: np.ndarray,
    arm_mask: np.ndarray,
    protect_mask: np.ndarray,
    path: Path,
) -> None:
    """Labeled overlap visualization.

    Green  = torso mask (no overlap)
    Yellow = torso overlapping shoulders
    Blue   = torso overlapping arms
    Red    = torso overlapping protect
    """
    h, w = image.shape[:2]
    scale = min(1.0, 1600 / max(w, h))
    new_w, new_h = int(w * scale), int(h * scale)
    vis = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA).copy()

    def _rs(m: np.ndarray) -> np.ndarray:
        return cv2.resize(
            m.astype(np.uint8), (new_w, new_h),
            interpolation=cv2.INTER_NEAREST,
        ) > 0

    t = _rs(torso_mask > 0)
    s = _rs(shoulder_mask)
    a = _rs(arm_mask)
    p = _rs(protect_mask)

    clean = t & ~s & ~a & ~p
    vis[clean, 1] = np.clip(vis[clean, 1].astype(int) + 100, 0, 255).astype(np.uint8)

    ov_s = t & s
    vis[ov_s, 0] = 255; vis[ov_s, 1] = 255; vis[ov_s, 2] = 0
    ov_a = t & a
    vis[ov_a, 0] = 0; vis[ov_a, 1] = 100; vis[ov_a, 2] = 255
    ov_p = t & p
    vis[ov_p, 0] = 255; vis[ov_p, 1] = 0; vis[ov_p, 2] = 0

    Image.fromarray(vis).save(path, format="PNG")


def _save_lower_belly_overlay(
    image: np.ndarray,
    lb_mask: np.ndarray,
    path: Path,
) -> None:
    """Lower-belly center region highlighted in orange."""
    h, w = image.shape[:2]
    scale = min(1.0, 1600 / max(w, h))
    new_w, new_h = int(w * scale), int(h * scale)
    vis = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA).copy()
    m = cv2.resize(
        lb_mask.astype(np.uint8), (new_w, new_h),
        interpolation=cv2.INTER_NEAREST,
    ) > 0

    vis[m, 0] = np.clip(vis[m, 0].astype(int) + 100, 0, 255).astype(np.uint8)
    vis[m, 1] = np.clip(vis[m, 1].astype(int) + 40, 0, 255).astype(np.uint8)
    vis[m, 2] = (vis[m, 2] * 0.4).astype(np.uint8)

    contours, _ = cv2.findContours(
        m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE,
    )
    cv2.drawContours(vis, contours, -1, (255, 140, 0), 2)
    Image.fromarray(vis).save(path, format="PNG")


def _save_mask_zone_debug(
    image: np.ndarray,
    torso_mask: np.ndarray,
    edit_mask: np.ndarray,
    protect_mask: np.ndarray,
    seam_mask: np.ndarray,
    path: Path,
) -> None:
    """Zone visualization showing included vs excluded regions.

    Green  = included upper-ab / oblique (pass2 mask)
    Red    = excluded lower-belly center
    Cyan   = navel exclusion area
    Yellow = seam band (pass1)
    """
    from backend.app.services.cut_refine import _build_lower_belly_center_mask

    h, w = image.shape[:2]
    scale = min(1.0, 1600 / max(w, h))
    new_w, new_h = int(w * scale), int(h * scale)
    vis = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA).copy()

    def _rs(m: np.ndarray) -> np.ndarray:
        return cv2.resize(
            m.astype(np.uint8), (new_w, new_h),
            interpolation=cv2.INTER_NEAREST,
        ) > 0

    t = _rs(torso_mask > 0)
    lb = _rs(_build_lower_belly_center_mask(edit_mask, protect_mask, seam_mask))
    sm = _rs(seam_mask > 0)

    # Green = pass2 mask
    vis[t, 1] = np.clip(vis[t, 1].astype(int) + 80, 0, 255).astype(np.uint8)

    # Red = lower-belly center (excluded)
    vis[lb & ~t, 0] = np.clip(vis[lb & ~t, 0].astype(int) + 100, 0, 255).astype(np.uint8)
    vis[lb & ~t, 1] = (vis[lb & ~t, 1] * 0.5).astype(np.uint8)
    vis[lb & ~t, 2] = (vis[lb & ~t, 2] * 0.5).astype(np.uint8)

    # Yellow = seam band
    vis[sm, 0] = np.clip(vis[sm, 0].astype(int) + 60, 0, 255).astype(np.uint8)
    vis[sm, 1] = np.clip(vis[sm, 1].astype(int) + 60, 0, 255).astype(np.uint8)

    Image.fromarray(vis).save(path, format="PNG")


# ═════════════════════════════════════════════════════════════════════════════
# § 3  Comparison grid
# ═════════════════════════════════════════════════════════════════════════════

def _make_comparison_grid(
    images: list[tuple[str, np.ndarray]],
    target_h: int = 600,
) -> Image.Image:
    """Create a labeled side-by-side comparison strip."""
    panels: list[Image.Image] = []
    for label, arr in images:
        pil = Image.fromarray(arr)
        scale = target_h / pil.height
        new_w = int(pil.width * scale)
        pil = pil.resize((new_w, target_h), Image.LANCZOS)

        bar_h = 28
        canvas = Image.new("RGB", (new_w, target_h + bar_h), (30, 30, 30))
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except OSError:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((new_w - tw) // 2, 4), label, fill=(255, 255, 255), font=font)
        canvas.paste(pil, (0, bar_h))
        panels.append(canvas)

    total_w = sum(p.width for p in panels) + 4 * (len(panels) - 1)
    grid_h = max(p.height for p in panels)
    grid = Image.new("RGB", (total_w, grid_h), (20, 20, 20))
    x = 0
    for p in panels:
        grid.paste(p, (x, 0))
        x += p.width + 4

    return grid


# ═════════════════════════════════════════════════════════════════════════════
# § 4  Single-case evaluation
# ═════════════════════════════════════════════════════════════════════════════

def _evaluate_case(
    case_dir: Path,
    out_dir: Path,
    preset: str,
    seed: int,
    backend,
    roi_max: int,
) -> dict:
    """Evaluate one test case through all three stages."""
    from backend.app.services.cut_refine import (
        _build_seam_mask,
        _build_torso_interior_mask,
        _PASS2_MIN_TARGET_W,
        _PASS2_MIN_TARGET_H,
        REFINE_PRESETS,
    )
    from backend.app.services.diffusion.base import RefineRequest
    from backend.app.services.diffusion.roi import (
        compute_roi, crop_to_roi, crop_mask_to_roi, composite_roi,
    )
    from backend.app.services.diffusion import prompts as P

    case_name = case_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"[{case_name}] Evaluating...")

    params = REFINE_PRESETS.get(preset, REFINE_PRESETS["medium"])

    # ── Load inputs ──────────────────────────────────────────────────────
    original = _load_rgb(case_dir / "original.jpg")
    warped = _load_rgb(case_dir / "warped.jpg")
    h, w = warped.shape[:2]

    edit_mask = _load_mask(case_dir / "edit_mask.png", w, h)
    protect_mask = _load_mask(case_dir / "protect_mask.png", w, h)
    weight_map = _load_float_map(case_dir / "weight_map.png", w, h)

    meta_path = case_dir / "metadata.json"
    case_meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

    # ── Save inputs ──────────────────────────────────────────────────────
    _save_rgb(original, out_dir / "01_original.jpg")
    _save_rgb(warped, out_dir / "02_warped.jpg")

    # ── Build pass masks ─────────────────────────────────────────────────
    seam_mask = _build_seam_mask(edit_mask, protect_mask)
    torso_mask, torso_strength = _build_torso_interior_mask(
        edit_mask, protect_mask, weight_map, seam_mask=seam_mask,
    )
    torso_mask_px = int((torso_mask > 0).sum())

    _save_mask(seam_mask, out_dir / "03_seam_mask.png")
    _save_mask(torso_mask, out_dir / "04_torso_refine_mask.png")
    logger.info(
        f"[{case_name}] torso_mask={torso_mask_px}px, "
        f"seam_mask={int((seam_mask > 0).sum())}px"
    )

    timings = {}

    # ── Stage A: warp only ───────────────────────────────────────────────
    safety_warp = compute_safety_metrics(original, warped, edit_mask, protect_mask)

    # ── Stage B: warp + pass 1 seam repair ───────────────────────────────
    after_seam = warped.copy()
    seam_settings = {}

    if np.any(seam_mask > 0):
        roi_seam = compute_roi(seam_mask, max_side=roi_max)
        roi_img = crop_to_roi(after_seam, roi_seam)
        roi_mask = crop_mask_to_roi(seam_mask, roi_seam)

        req = RefineRequest(
            init_image=roi_img,
            mask_image=roi_mask,
            prompt=P.SEAM_PROMPT,
            negative_prompt=P.SEAM_NEGATIVE,
            strength=params["seam_strength"],
            guidance_scale=params["seam_guidance"],
            num_steps=params["seam_steps"],
            seed=seed,
            width=roi_seam.target_w,
            height=roi_seam.target_h,
        )
        seam_settings = {
            "prompt": P.SEAM_PROMPT,
            "negative_prompt": P.SEAM_NEGATIVE,
            "strength": params["seam_strength"],
            "guidance_scale": params["seam_guidance"],
            "steps": params["seam_steps"],
            "seed": seed,
            "roi_w": roi_seam.target_w,
            "roi_h": roi_seam.target_h,
            "roi_crop": [roi_seam.x0, roi_seam.y0, roi_seam.x1, roi_seam.y1],
        }

        t0 = time.monotonic()
        seam_result = backend.refine_seam(req)
        timings["pass1_seam_ms"] = round((time.monotonic() - t0) * 1000, 1)

        after_seam = composite_roi(
            after_seam, seam_result.image, seam_mask > 0, roi_seam, feather_px=8,
        )
        seed = seam_result.seed_used
        logger.info(f"[{case_name}] Pass 1 seam: {timings['pass1_seam_ms']}ms")
    else:
        timings["pass1_seam_ms"] = 0
        logger.info(f"[{case_name}] Pass 1 skipped (no seam pixels)")

    _save_rgb(after_seam, out_dir / "05_pass1_seam_repair.jpg")

    # ── Stage C: + pass 2 torso refine ───────────────────────────────────
    final = after_seam.copy()
    torso_settings = {}

    if np.any(torso_mask > 0):
        roi_torso = compute_roi(
            torso_mask, max_side=roi_max,
            min_target_w=_PASS2_MIN_TARGET_W,
            min_target_h=_PASS2_MIN_TARGET_H,
        )
        roi_img = crop_to_roi(final, roi_torso)
        roi_mask = crop_mask_to_roi(torso_mask, roi_torso)

        req = RefineRequest(
            init_image=roi_img,
            mask_image=roi_mask,
            prompt=P.get_torso_prompt(5.0, preset),
            negative_prompt=P.get_torso_negative(5.0, preset),
            strength=params["torso_strength"],
            guidance_scale=params["torso_guidance"],
            num_steps=params["torso_steps"],
            seed=seed,
            width=roi_torso.target_w,
            height=roi_torso.target_h,
        )
        torso_settings = {
            "prompt": P.get_torso_prompt(5.0, preset),
            "negative_prompt": P.get_torso_negative(5.0, preset),
            "strength": params["torso_strength"],
            "guidance_scale": params["torso_guidance"],
            "steps": params["torso_steps"],
            "seed": seed,
            "roi_w": roi_torso.target_w,
            "roi_h": roi_torso.target_h,
            "roi_crop": [roi_torso.x0, roi_torso.y0, roi_torso.x1, roi_torso.y1],
            "mask_px": torso_mask_px,
        }

        t0 = time.monotonic()
        torso_result = backend.refine_torso(req)
        timings["pass2_torso_ms"] = round((time.monotonic() - t0) * 1000, 1)

        final = composite_roi(
            final, torso_result.image, torso_mask > 0, roi_torso,
            feather_px=14,
            strength_map=torso_strength,
        )
        logger.info(
            f"[{case_name}] Pass 2 torso: {timings['pass2_torso_ms']}ms, "
            f"mask={torso_mask_px}px, roi={roi_torso.target_w}x{roi_torso.target_h}"
        )
    else:
        timings["pass2_torso_ms"] = 0
        logger.info(f"[{case_name}] Pass 2 skipped (no torso pixels)")

    _save_rgb(final, out_dir / "06_final_refined.jpg")
    timings["total_ms"] = timings["pass1_seam_ms"] + timings["pass2_torso_ms"]

    # ── Metrics ──────────────────────────────────────────────────────────
    safety_seam = compute_safety_metrics(original, after_seam, edit_mask, protect_mask)
    safety_final = compute_safety_metrics(original, final, edit_mask, protect_mask)

    edit_seam_vs_warp = compute_edit_metrics(
        warped, after_seam, edit_mask, seam_mask, torso_mask,
    )
    edit_final_vs_warp = compute_edit_metrics(
        warped, final, edit_mask, seam_mask, torso_mask,
    )

    # ── Pass-2 regression metrics + debug overlays ────────────────────────
    original_pil = Image.open(
        (case_dir / "original.png") if (case_dir / "original.png").exists()
        else (case_dir / "original.jpg")
    )
    original_pil = ImageOps.exif_transpose(original_pil) or original_pil
    original_pil = original_pil.convert("RGB")

    pass2_reg = _compute_pass2_regression(
        torso_mask=torso_mask,
        edit_mask=edit_mask,
        protect_mask=protect_mask,
        seam_mask=seam_mask,
        weight_map=weight_map,
        after_seam=after_seam,
        final=final,
        original_pil=original_pil,
        roi_info=torso_settings if torso_settings else None,
        out_dir=out_dir,
        warped=warped,
    )
    logger.info(
        f"[{case_name}] pass2 regression: "
        f"mask={pass2_reg['pass2_mask_area_px']}px "
        f"({pass2_reg['pass2_mask_area_ratio_vs_edit']:.2%} of edit), "
        f"roi={pass2_reg['pass2_roi_w']}x{pass2_reg['pass2_roi_h']}, "
        f"shoulder_overlap={pass2_reg['shoulder_overlap_px']}, "
        f"arm_overlap={pass2_reg['arm_overlap_px']}, "
        f"mae_torso={pass2_reg['mae_final_vs_pass1_in_torso']}, "
        f"lb_mae={pass2_reg.get('lower_belly_mae', 0):.2f}, "
        f"lb_regression={pass2_reg.get('lower_belly_regression', False)}, "
        f"fallback={pass2_reg['fallback_triggered']}"
    )

    # ── Lean-signal metrics ─────────────────────────────────────────────
    lean_sig = _compute_lean_signal(
        original, warped, final,
        edit_mask, protect_mask, seam_mask,
        case_meta,
    )
    logger.info(
        f"[{case_name}] lean signal: "
        f"waist_avg={lean_sig.get('avg_waist_reduction_pct', 0):.1f}%, "
        f"ua_gain={lean_sig.get('upper_ab_tex_gain_pct', 0):.1f}%, "
        f"ob_gain={lean_sig.get('oblique_tex_gain_pct', 0):.1f}%, "
        f"score={lean_sig.get('lean_score', 0):.2f}"
    )

    # ── Comparison grid ──────────────────────────────────────────────────
    grid = _make_comparison_grid([
        ("Original", original),
        ("Warp only", warped),
        ("+ Seam repair", after_seam),
        ("+ Torso refine", final),
    ])
    grid.save(out_dir / "07_comparison_grid.jpg", quality=92)

    # ── Persist metrics + settings ───────────────────────────────────────
    case_metrics = {
        "case_name": case_name,
        "image_size": [w, h],
        "preset": preset,
        "timings": timings,
        "mask_areas": {
            "seam_mask_px": int((seam_mask > 0).sum()),
            "torso_mask_px": torso_mask_px,
            "edit_mask_px": int(edit_mask.sum()),
        },
        "pass2_regression": pass2_reg,
        "lean_signal": lean_sig,
        "safety": {
            "warp_only": safety_warp,
            "warp_plus_seam": safety_seam,
            "final": safety_final,
        },
        "edit": {
            "seam_vs_warp": edit_seam_vs_warp,
            "final_vs_warp": edit_final_vs_warp,
        },
        "backend": backend.get_debug_info(),
    }
    (out_dir / "metrics.json").write_text(
        json.dumps(case_metrics, indent=2), encoding="utf-8",
    )

    settings_log = {
        "case_name": case_name,
        "preset": preset,
        "pass1_seam": seam_settings,
        "pass2_torso": torso_settings,
        "input_metadata": case_meta,
    }
    (out_dir / "settings.json").write_text(
        json.dumps(settings_log, indent=2), encoding="utf-8",
    )

    logger.info(
        f"[{case_name}] Done — total={timings['total_ms']}ms, "
        f"protect_leak={safety_final['protect_mae']:.3f}"
    )
    return case_metrics


# ═════════════════════════════════════════════════════════════════════════════
# § 5  HTML report generator
# ═════════════════════════════════════════════════════════════════════════════

def _generate_html_report(
    run_dir: Path,
    all_metrics: list[dict],
    run_meta: dict,
) -> Path:
    cases_html = []
    for m in all_metrics:
        name = m["case_name"]
        case_dir = name
        if "error" in m:
            cases_html.append(f'<div class="case"><h2>{name} — ERROR</h2></div>')
            continue
        t = m["timings"]
        sf = m["safety"]["final"]
        ef = m["edit"]["final_vs_warp"]
        ma = m.get("mask_areas", {})
        p2 = m.get("pass2_regression", {})
        ls = m.get("lean_signal", {})

        def _cls(ok: bool) -> str:
            return "ok" if ok else "warn"

        cases_html.append(f"""
    <div class="case">
      <h2>{name}</h2>

      <h3>Stage outputs</h3>
      <div class="grid-row">
        <img src="{case_dir}/01_original.png" alt="original" />
        <img src="{case_dir}/02_warped.png" alt="warped" />
        <img src="{case_dir}/05_pass1_seam_repair.png" alt="seam" />
        <img src="{case_dir}/06_final_refined.png" alt="final" />
      </div>
      <div class="grid-row">
        <img src="{case_dir}/07_comparison_grid.jpg" alt="grid"
             style="max-width:100%;" />
      </div>

      <h3>Pass-2 debug overlays</h3>
      <div class="grid-row">
        <img src="{case_dir}/04_torso_refine_mask.png" alt="torso mask" />
        <img src="{case_dir}/08_pass2_mask_overlay.png" alt="mask overlay" />
        <img src="{case_dir}/09_pass2_overlap_debug.png" alt="overlap debug" />
      </div>
      <div class="grid-row">
        <img src="{case_dir}/10_lower_belly_region.png" alt="lower belly" />
        <img src="{case_dir}/11_mask_zone_debug.png" alt="zone debug" />
      </div>

      <h3>Lower-belly regression</h3>
      <table>
        <tr><th>Check</th><th>Value</th><th>Status</th></tr>
        <tr><td>Lower-belly center px</td>
            <td>{p2.get('lower_belly_center_px', '?')}</td>
            <td>—</td></tr>
        <tr><td>Lower-belly MAE (pass2 vs pass1)</td>
            <td>{p2.get('lower_belly_mae', '?')}
                (p90: {p2.get('lower_belly_p90', '?')})</td>
            <td class="{_cls(not p2.get('lower_belly_regression', False))}">
                {"REGRESSION" if p2.get('lower_belly_regression', False) else "OK"}</td></tr>
        <tr><td>Brightness shift</td>
            <td>{p2.get('lower_belly_brightness_shift', '?')}</td>
            <td class="{_cls(abs(p2.get('lower_belly_brightness_shift', 0)) < 5.0)}">
                {"HIGH" if abs(p2.get('lower_belly_brightness_shift', 0)) >= 5.0 else "OK"}</td></tr>
      </table>

      <h3>Lean signal</h3>
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Waist reduction @50%</td><td>{ls.get('waist_50_reduction_pct','?')}%</td></tr>
        <tr><td>Waist reduction @65%</td><td>{ls.get('waist_65_reduction_pct','?')}%</td></tr>
        <tr><td>Waist reduction @80%</td><td>{ls.get('waist_80_reduction_pct','?')}%</td></tr>
        <tr><td>Avg waist reduction</td><td>{ls.get('avg_waist_reduction_pct','?')}%</td></tr>
        <tr><td>Upper-ab texture gain</td><td>{ls.get('upper_ab_tex_gain_pct','?')}%</td></tr>
        <tr><td>Oblique texture gain</td><td>{ls.get('oblique_tex_gain_pct','?')}%</td></tr>
        <tr><td>Lean score</td>
            <td class="{_cls(ls.get('lean_score',0) >= 2.0)}">
            <strong>{ls.get('lean_score','?')}</strong></td></tr>
      </table>

      <h3>Pass-2 regression</h3>
      <table>
        <tr><th>Check</th><th>Value</th><th>Status</th></tr>
        <tr><td>Torso mask area</td>
            <td>{p2.get('pass2_mask_area_px','?')} px
                ({p2.get('pass2_mask_area_ratio_vs_edit',0):.1%} of edit)</td>
            <td class="{_cls(p2.get('pass2_mask_area_px',0) > 5000)}">
                {"GOOD" if p2.get('pass2_mask_area_px',0) > 5000 else "TOO SMALL"}</td></tr>
        <tr><td>ROI target dims</td>
            <td>{p2.get('pass2_roi_w','?')} x {p2.get('pass2_roi_h','?')}</td>
            <td class="{_cls(p2.get('pass2_roi_w',0) >= 192 and p2.get('pass2_roi_h',0) >= 192)}">
                {"GOOD" if min(p2.get('pass2_roi_w',0), p2.get('pass2_roi_h',0)) >= 192 else "THIN"}</td></tr>
        <tr><td>Shoulder overlap</td>
            <td>{p2.get('shoulder_overlap_px','?')} px
                ({p2.get('shoulder_overlap_ratio',0):.3%})</td>
            <td class="{_cls(p2.get('shoulder_overlap_ratio',0) < 0.01)}">
                {"CLEAN" if p2.get('shoulder_overlap_ratio',0) < 0.01 else "LEAK"}</td></tr>
        <tr><td>Arm overlap</td>
            <td>{p2.get('arm_overlap_px','?')} px
                ({p2.get('arm_overlap_ratio',0):.3%})</td>
            <td class="{_cls(p2.get('arm_overlap_ratio',0) < 0.01)}">
                {"CLEAN" if p2.get('arm_overlap_ratio',0) < 0.01 else "LEAK"}</td></tr>
        <tr><td>Protect overlap</td>
            <td>{p2.get('protect_overlap_px','?')} px</td>
            <td class="{_cls(p2.get('protect_overlap_px',0) == 0)}">
                {"CLEAN" if p2.get('protect_overlap_px',0) == 0 else "VIOLATION"}</td></tr>
        <tr><td>MAE final-vs-pass1 (torso)</td>
            <td>{p2.get('mae_final_vs_pass1_in_torso','?')}
                (p90: {p2.get('mae_final_vs_pass1_p90_in_torso','?')})</td>
            <td class="{_cls(p2.get('mae_final_vs_pass1_in_torso',0) > 0.5)}">
                {"ACTIVE" if p2.get('mae_final_vs_pass1_in_torso',0) > 0.5 else "INACTIVE"}</td></tr>
        <tr><td>MAE final-vs-pass1 (outside edit)</td>
            <td>{p2.get('mae_final_vs_pass1_outside_edit','?')}</td>
            <td class="{_cls(p2.get('mae_final_vs_pass1_outside_edit',0) < 0.5)}">
                {"STABLE" if p2.get('mae_final_vs_pass1_outside_edit',0) < 0.5 else "LEAK"}</td></tr>
        <tr><td>Fallback to candidate</td>
            <td>core/candidate = {p2.get('core_vs_candidate_ratio','?')}</td>
            <td class="{_cls(not p2.get('fallback_triggered', False))}">
                {"FALLBACK" if p2.get('fallback_triggered', False) else "CORE OK"}</td></tr>
      </table>

      <h3>Safety &amp; edit metrics</h3>
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Pass 1 (seam)</td><td>{t['pass1_seam_ms']}ms</td></tr>
        <tr><td>Pass 2 (torso)</td><td>{t['pass2_torso_ms']}ms</td></tr>
        <tr><td>Total</td><td>{t['total_ms']}ms</td></tr>
        <tr><td>Protect leak MAE</td>
            <td class="{'warn' if sf['protect_mae'] > 1.0 else 'ok'}">
            {sf['protect_mae']}</td></tr>
        <tr><td>Protect changed ratio</td>
            <td class="{'warn' if sf['protect_changed_ratio'] > 0.001 else 'ok'}">
            {sf['protect_changed_ratio']:.6f}</td></tr>
        <tr><td>Outside-edit MAE</td><td>{sf['outside_edit_mae']}</td></tr>
        <tr><td>Edit region MAE</td><td>{ef['edit_region_mae']}</td></tr>
        <tr><td>Seam band MAE</td><td>{ef['seam_band_mae']}</td></tr>
        <tr><td>Torso interior MAE</td><td>{ef['torso_interior_mae']}</td></tr>
        <tr><td>Edit P90</td><td>{ef['edit_region_p90']}</td></tr>
        <tr><td>Torso mask px</td><td>{ma.get('torso_mask_px', 'n/a')}</td></tr>
        <tr><td>Seam mask px</td><td>{ma.get('seam_mask_px', 'n/a')}</td></tr>
      </table>
      <details><summary>Full metrics JSON</summary>
        <pre>{json.dumps(m, indent=2)}</pre>
      </details>
    </div>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>CUT Refine Evaluation — {run_meta.get('run_id', '')}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #111; color: #ddd; margin: 20px; }}
  h1 {{ color: #fff; border-bottom: 1px solid #444; padding-bottom: 8px; }}
  h2 {{ color: #adf; margin-top: 32px; }}
  .case {{ margin-bottom: 48px; }}
  .grid-row {{ display: flex; gap: 6px; flex-wrap: wrap; margin: 12px 0; }}
  .grid-row img {{ max-height: 320px; border: 1px solid #333; border-radius: 4px; }}
  table {{ border-collapse: collapse; margin: 12px 0; }}
  th, td {{ border: 1px solid #444; padding: 6px 14px; text-align: left; }}
  th {{ background: #222; }}
  .ok {{ color: #6f6; }}
  .warn {{ color: #f66; font-weight: bold; }}
  details {{ margin: 8px 0; }}
  pre {{ background: #1a1a1a; padding: 12px; border-radius: 4px;
         overflow-x: auto; font-size: 12px; max-height: 400px; }}
  .summary {{ background: #1a1a1a; padding: 16px; border-radius: 8px;
              margin: 16px 0; }}
</style>
</head>
<body>
<h1>CUT Refine Evaluation</h1>
<div class="summary">
  <strong>Run:</strong> {run_meta.get('run_id', '')} &nbsp;|&nbsp;
  <strong>Backend:</strong> {run_meta.get('backend', '')} &nbsp;|&nbsp;
  <strong>Preset:</strong> {run_meta.get('preset', '')} &nbsp;|&nbsp;
  <strong>Seed:</strong> {run_meta.get('seed', '')} &nbsp;|&nbsp;
  <strong>Cases:</strong> {len(all_metrics)} &nbsp;|&nbsp;
  <strong>Date:</strong> {run_meta.get('timestamp', '')}
</div>

{''.join(cases_html)}

</body>
</html>"""

    report_path = run_dir / "report.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path


# ═════════════════════════════════════════════════════════════════════════════
# § 6  Batch runner
# ═════════════════════════════════════════════════════════════════════════════

def _find_cases(input_dir: Path) -> list[Path]:
    """Find valid test case directories (must contain warped.jpg or warped.png)."""
    cases = []
    for d in sorted(input_dir.iterdir()):
        if d.is_dir() and (
            (d / "warped.jpg").exists() or (d / "warped.png").exists()
        ):
            cases.append(d)
    return cases


def _print_regression_summary(all_metrics: list[dict]) -> None:
    """Print a concise pass/fail regression summary to stdout."""
    sep = "=" * 72
    print(f"\n{sep}")
    print("  PASS-2 REGRESSION SUMMARY")
    print(sep)

    for m in all_metrics:
        name = m.get("case_name", "?")
        if "error" in m:
            print(f"\n  [{name}]  *** ERROR — skipped ***")
            continue

        p2 = m.get("pass2_regression", {})
        sf = m.get("safety", {}).get("final", {})

        mask_px = p2.get("pass2_mask_area_px", 0)
        mask_ratio = p2.get("pass2_mask_area_ratio_vs_edit", 0)
        roi_w = p2.get("pass2_roi_w", 0)
        roi_h = p2.get("pass2_roi_h", 0)
        sho = p2.get("shoulder_overlap_ratio", 0)
        arm = p2.get("arm_overlap_ratio", 0)
        pro = p2.get("protect_overlap_px", 0)
        mae_t = p2.get("mae_final_vs_pass1_in_torso", 0)
        mae_t90 = p2.get("mae_final_vs_pass1_p90_in_torso", 0)
        mae_out = p2.get("mae_final_vs_pass1_outside_edit", 0)
        fb = p2.get("fallback_triggered", False)
        core_r = p2.get("core_vs_candidate_ratio", 0)
        lb_mae = p2.get("lower_belly_mae", 0)
        lb_p90 = p2.get("lower_belly_p90", 0)
        lb_bri = p2.get("lower_belly_brightness_shift", 0)
        lb_reg = p2.get("lower_belly_regression", False)

        def _tag(ok: bool) -> str:
            return "PASS" if ok else "FAIL"

        checks = [
            (f"mask area         {mask_px:>8} px ({mask_ratio:.1%} of edit)",
             _tag(mask_px > 5000)),
            (f"ROI target        {roi_w}x{roi_h}",
             _tag(min(roi_w, roi_h) >= 192)),
            (f"shoulder overlap  {sho:.3%}",
             _tag(sho < 0.01)),
            (f"arm overlap       {arm:.3%}",
             _tag(arm < 0.01)),
            (f"protect overlap   {pro} px",
             _tag(pro == 0)),
            (f"torso MAE (f-p1)  {mae_t:.2f}  (p90={mae_t90:.2f})",
             _tag(mae_t > 0.5)),
            (f"outside MAE (f-p1){mae_out:.2f}",
             _tag(mae_out < 0.5)),
            (f"fallback          {'YES' if fb else 'no'}  (core/cand={core_r:.2f})",
             _tag(not fb)),
            (f"protect leak MAE  {sf.get('protect_mae', 0):.3f}",
             _tag(sf.get("protect_mae", 99) < 2.0)),
            (f"lower-belly MAE   {lb_mae:.2f}  (p90={lb_p90:.2f})  bri={lb_bri:+.1f}",
             _tag(not lb_reg)),
        ]

        all_pass = all(tag == "PASS" for _, tag in checks)
        status = "ALL PASS" if all_pass else "HAS FAILURES"
        print(f"\n  [{name}]  {status}")
        for desc, tag in checks:
            marker = "  [x]" if tag == "PASS" else "  [ ]"
            print(f"    {marker} {tag:4s}  {desc}")

        # Lean signal summary
        ls = m.get("lean_signal", {})
        if ls:
            print(f"\n    LEAN SIGNAL:")
            waist_keys = sorted([k for k in ls if k.startswith("waist_") and k.endswith("_reduction_pct")])
            waist_parts = [f"{k.replace('_reduction_pct','').replace('waist_','@')}%={ls[k]:.1f}%"
                           for k in waist_keys]
            print(f"      waist: {', '.join(waist_parts)}  "
                  f"avg={ls.get('avg_waist_reduction_pct',0):.1f}%")
            print(f"      upper-ab tex gain={ls.get('upper_ab_tex_gain_pct',0):.1f}%  "
                  f"oblique tex gain={ls.get('oblique_tex_gain_pct',0):.1f}%")
            print(f"      lean score = {ls.get('lean_score',0):.2f}")

    print(f"\n{sep}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the CUT refinement pipeline on test cases",
    )
    parser.add_argument(
        "--input-dir", required=True,
        help="Directory containing test case folders",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory for evaluation outputs",
    )
    parser.add_argument(
        "--preset", default="medium",
        choices=["mild", "medium", "strong"],
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--backend", default="sd15_inpaint_cpu",
        choices=["sd15_inpaint_cpu", "sd2_inpaint_cpu"],
    )
    parser.add_argument(
        "--roi-max", type=int, default=0,
        help="Override ROI max side (0 = use config default)",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cases = _find_cases(input_dir)
    if not cases:
        logger.error(f"No test cases found in {input_dir}")
        sys.exit(1)

    logger.info(f"Found {len(cases)} test case(s) in {input_dir}")

    # Load backend
    from backend.app.services.diffusion.loader import get_backend
    from backend.app.config import settings

    roi_max = args.roi_max or settings.diffusion_roi_max_px
    backend = get_backend(args.backend, force_new=True)

    logger.info(f"Loading backend: {args.backend}")
    t_load = time.monotonic()
    backend.load()
    load_ms = round((time.monotonic() - t_load) * 1000, 1)
    logger.info(f"Backend loaded in {load_ms}ms")

    run_id = output_dir.name
    run_meta = {
        "run_id": run_id,
        "timestamp": datetime.now().isoformat(),
        "backend": args.backend,
        "preset": args.preset,
        "seed": args.seed,
        "roi_max_px": roi_max,
        "num_cases": len(cases),
        "backend_info": backend.get_debug_info(),
        "model_load_ms": load_ms,
    }

    all_metrics: list[dict] = []
    total_t0 = time.monotonic()

    for case_dir in cases:
        case_out = output_dir / case_dir.name
        try:
            m = _evaluate_case(
                case_dir, case_out, args.preset, args.seed, backend, roi_max,
            )
            all_metrics.append(m)
        except Exception:
            logger.exception(f"[{case_dir.name}] FAILED")
            all_metrics.append({
                "case_name": case_dir.name,
                "error": True,
            })

    total_elapsed = round(time.monotonic() - total_t0, 1)
    run_meta["total_elapsed_s"] = total_elapsed

    summary = {
        "run": run_meta,
        "cases": all_metrics,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8",
    )

    report_path = _generate_html_report(output_dir, all_metrics, run_meta)

    backend.unload()

    _print_regression_summary(all_metrics)

    logger.info(f"Evaluation complete: {len(all_metrics)} cases in {total_elapsed}s")
    logger.info(f"Report: {report_path}")
    logger.info(f"Summary: {output_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
