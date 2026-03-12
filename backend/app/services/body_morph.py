"""
Landmark-based body morphing between original and AI-generated final images.

Uses MediaPipe PoseLandmarker (Tasks API) for body landmark detection,
Delaunay triangulation for mesh correspondence, and per-triangle affine
warping with cross-dissolve to produce natural intermediate frames.
"""

import base64
import io
import logging
import os
import urllib.request
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

logger = logging.getLogger(__name__)

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task"
MODEL_PATH = "/tmp/pose_landmarker_heavy.task"

_landmarker: Optional[vision.PoseLandmarker] = None


def _get_landmarker() -> vision.PoseLandmarker:
    global _landmarker
    if _landmarker is None:
        if not os.path.exists(MODEL_PATH):
            logger.info("Downloading pose_landmarker_heavy model...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

        options = vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=MODEL_PATH),
            num_poses=1,
        )
        _landmarker = vision.PoseLandmarker.create_from_options(options)
    return _landmarker


def _detect_landmarks(image: np.ndarray) -> Optional[list[tuple[int, int]]]:
    """Detect 33 MediaPipe Pose landmarks. Returns pixel coords or None."""
    h, w = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = _get_landmarker().detect(mp_image)

    if not result.pose_landmarks or len(result.pose_landmarks) == 0:
        return None

    landmarks = result.pose_landmarks[0]
    pts = []
    low_vis_count = 0
    for lm in landmarks:
        if lm.visibility < 0.3:
            low_vis_count += 1
        px = max(0, min(w - 1, int(lm.x * w)))
        py = max(0, min(h - 1, int(lm.y * h)))
        pts.append((px, py))

    if low_vis_count > 10:
        return None

    return pts


def _add_boundary_points(
    pts: list[tuple[int, int]], w: int, h: int,
) -> list[tuple[int, int]]:
    """Add 8 boundary points (corners + edge midpoints) for full coverage."""
    boundary = [
        (0, 0), (w // 2, 0), (w - 1, 0),
        (0, h // 2), (w - 1, h // 2),
        (0, h - 1), (w // 2, h - 1), (w - 1, h - 1),
    ]
    return pts + boundary


def _get_delaunay_indices(
    points: list[tuple[int, int]], w: int, h: int,
) -> list[tuple[int, int, int]]:
    """Compute Delaunay triangulation indices for a set of points."""
    rect = (0, 0, w, h)
    subdiv = cv2.Subdiv2D(rect)

    for p in points:
        px = max(0, min(w - 1, p[0]))
        py = max(0, min(h - 1, p[1]))
        subdiv.insert((float(px), float(py)))

    tri_list = subdiv.getTriangleList()
    indices = []
    pt_arr = np.array(points, dtype=np.float32)

    for t in tri_list:
        p1 = (t[0], t[1])
        p2 = (t[2], t[3])
        p3 = (t[4], t[5])

        if not all(
            0 <= p[0] < w and 0 <= p[1] < h for p in [p1, p2, p3]
        ):
            continue

        tri_pts = np.array([p1, p2, p3], dtype=np.float32)
        idx = []
        for tp in tri_pts:
            dists = np.sum((pt_arr - tp) ** 2, axis=1)
            idx.append(int(np.argmin(dists)))

        if len(set(idx)) == 3:
            indices.append(tuple(idx))

    return indices


def _warp_triangle(
    img: np.ndarray,
    src_tri: np.ndarray,
    dst_tri: np.ndarray,
    output: np.ndarray,
):
    """Warp a single triangle from img into output."""
    sr = cv2.boundingRect(np.float32([src_tri]))
    dr = cv2.boundingRect(np.float32([dst_tri]))

    src_cropped = np.float32([
        (src_tri[i][0] - sr[0], src_tri[i][1] - sr[1]) for i in range(3)
    ])
    dst_cropped = np.float32([
        (dst_tri[i][0] - dr[0], dst_tri[i][1] - dr[1]) for i in range(3)
    ])

    sx, sy, sw, sh = sr
    sx, sy = max(0, sx), max(0, sy)
    sw = min(sw, img.shape[1] - sx)
    sh = min(sh, img.shape[0] - sy)
    if sw <= 0 or sh <= 0:
        return

    img_crop = img[sy : sy + sh, sx : sx + sw]

    warp_mat = cv2.getAffineTransform(src_cropped, dst_cropped)
    dw, dh = dr[2], dr[3]
    if dw <= 0 or dh <= 0:
        return

    warped = cv2.warpAffine(
        img_crop, warp_mat, (dw, dh),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101,
    )

    mask = np.zeros((dh, dw, 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(dst_cropped), (1.0, 1.0, 1.0), 16)

    dx, dy = max(0, dr[0]), max(0, dr[1])
    ew = min(dw, output.shape[1] - dx)
    eh = min(dh, output.shape[0] - dy)
    if ew <= 0 or eh <= 0:
        return

    roi = output[dy : dy + eh, dx : dx + ew]
    warped_roi = warped[:eh, :ew]
    mask_roi = mask[:eh, :ew]

    roi[:] = roi * (1 - mask_roi) + warped_roi * mask_roi


def morph_images(orig_b64: str, final_b64: str, alpha: float) -> str:
    """Morph between original and final images using landmark-based warping.

    alpha=0 → original, alpha=1 → final.
    Falls back to original image if landmark detection fails.
    Returns base64-encoded JPEG.
    """
    orig_bytes = base64.b64decode(orig_b64)
    final_bytes = base64.b64decode(final_b64)

    orig_img = cv2.imdecode(np.frombuffer(orig_bytes, np.uint8), cv2.IMREAD_COLOR)
    final_img = cv2.imdecode(np.frombuffer(final_bytes, np.uint8), cv2.IMREAD_COLOR)

    if final_img.shape[:2] != orig_img.shape[:2]:
        final_img = cv2.resize(
            final_img, (orig_img.shape[1], orig_img.shape[0]),
            interpolation=cv2.INTER_LANCZOS4,
        )

    h, w = orig_img.shape[:2]

    orig_landmarks = _detect_landmarks(orig_img)
    final_landmarks = _detect_landmarks(final_img)

    if orig_landmarks is None or final_landmarks is None:
        logger.warning("Landmark detection failed, returning original image")
        _, buf = cv2.imencode(".jpg", orig_img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return base64.b64encode(buf.tobytes()).decode()

    if len(orig_landmarks) != len(final_landmarks):
        logger.warning("Landmark count mismatch, returning original image")
        _, buf = cv2.imencode(".jpg", orig_img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return base64.b64encode(buf.tobytes()).decode()

    orig_pts = _add_boundary_points(orig_landmarks, w, h)
    final_pts = _add_boundary_points(final_landmarks, w, h)

    mid_pts = []
    for (ox, oy), (fx, fy) in zip(orig_pts, final_pts):
        mx = int((1 - alpha) * ox + alpha * fx)
        my = int((1 - alpha) * oy + alpha * fy)
        mx = max(0, min(w - 1, mx))
        my = max(0, min(h - 1, my))
        mid_pts.append((mx, my))

    tri_indices = _get_delaunay_indices(mid_pts, w, h)

    warped_orig = np.zeros_like(orig_img, dtype=np.float32)
    warped_final = np.zeros_like(final_img, dtype=np.float32)

    for i1, i2, i3 in tri_indices:
        src_tri_o = np.float32([orig_pts[i1], orig_pts[i2], orig_pts[i3]])
        src_tri_f = np.float32([final_pts[i1], final_pts[i2], final_pts[i3]])
        dst_tri = np.float32([mid_pts[i1], mid_pts[i2], mid_pts[i3]])

        _warp_triangle(orig_img.astype(np.float32), src_tri_o, dst_tri, warped_orig)
        _warp_triangle(final_img.astype(np.float32), src_tri_f, dst_tri, warped_final)

    result = ((1 - alpha) * warped_orig + alpha * warped_final).astype(np.uint8)

    _, buf = cv2.imencode(".jpg", result, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return base64.b64encode(buf.tobytes()).decode()
