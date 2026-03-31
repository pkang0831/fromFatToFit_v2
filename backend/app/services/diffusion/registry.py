"""
Model registry — single source of truth for model IDs, sizes, and profiles.

All models here are CPU-friendly (SD 1.5 / SD 2 class).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ModelSpec:
    key: str
    repo_id: str
    revision: Optional[str] = None
    is_gated: bool = False
    approx_size_gb: float = 0.0
    description: str = ""


MODELS: dict[str, ModelSpec] = {
    "sd15_inpaint": ModelSpec(
        key="sd15_inpaint",
        repo_id="sd-legacy/stable-diffusion-inpainting",
        is_gated=False,
        approx_size_gb=4.3,
        description="SD 1.5 Inpainting — primary CPU backbone (~512px native)",
    ),
    "sd2_inpaint": ModelSpec(
        key="sd2_inpaint",
        repo_id="stabilityai/stable-diffusion-2-inpainting",
        is_gated=False,
        approx_size_gb=5.2,
        description="SD 2 Inpainting — fallback CPU backbone (~512px native)",
    ),
}

DOWNLOAD_PROFILES: dict[str, list[str]] = {
    "sd15_only": ["sd15_inpaint"],
    "sd2_only": ["sd2_inpaint"],
    "all": ["sd15_inpaint", "sd2_inpaint"],
}

BACKEND_TO_MODEL: dict[str, str] = {
    "sd15_inpaint_cpu": "sd15_inpaint",
    "sd2_inpaint_cpu": "sd2_inpaint",
    "sd15_inpaint_openvino": "sd15_inpaint",
}
