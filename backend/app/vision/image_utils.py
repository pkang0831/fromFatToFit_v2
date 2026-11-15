"""Lightweight image + pose helpers (no torch/transformers).

Shared by ``body_photo_quality`` and ``fashn_human_parser`` so tests and
framing logic can import without optional ML dependencies.
"""

from __future__ import annotations

import base64
import io

from PIL import Image, ImageOps


def load_and_normalize_image(image_base64: str) -> Image.Image:
    """Decode base64 → PIL Image with EXIF orientation applied."""
    raw = base64.b64decode(image_base64)
    pil_img = Image.open(io.BytesIO(raw))
    pil_img = ImageOps.exif_transpose(pil_img) or pil_img
    return pil_img.convert("RGB")


def lm_visible(landmarks, idx: int) -> bool:
    """Check if a landmark is visible (visibility > 0.3)."""
    return landmarks[idx].visibility > 0.3
