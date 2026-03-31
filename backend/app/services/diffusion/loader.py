"""
Backend factory — instantiates the configured CPU diffusion backend.

Selection is driven by ``BODY_DIFFUSION_BACKEND`` env var.
Auto-detects OpenVINO availability when the openvino backend is requested
and falls back to plain CPU if unavailable.
"""

from __future__ import annotations

import logging
from typing import Optional

from .base import DiffusionBackend

logger = logging.getLogger(__name__)

_CACHE: dict[str, DiffusionBackend] = {}


def get_backend(
    backend_key: Optional[str] = None,
    *,
    force_new: bool = False,
) -> DiffusionBackend:
    """Return a DiffusionBackend instance (cached per key)."""
    from ...config import settings

    key = backend_key or settings.body_diffusion_backend

    if not force_new and key in _CACHE:
        return _CACHE[key]

    backend = _create(key, settings)
    _CACHE[key] = backend
    return backend


def _create(key: str, settings) -> DiffusionBackend:
    common = dict(
        hf_token=settings.hf_token,
        cache_dir=settings.hf_cache_dir,
        num_steps=settings.diffusion_num_steps,
    )

    if key == "sd15_inpaint_cpu":
        from .sd15_cpu import SD15InpaintCPU
        return SD15InpaintCPU(local_model_path=settings.sd15_local_model_path, **common)

    if key == "sd2_inpaint_cpu":
        from .sd2_cpu import SD2InpaintCPU
        return SD2InpaintCPU(**common)

    if key == "sd15_inpaint_openvino":
        from .openvino_cpu import SD15InpaintOpenVINO, _check_openvino
        if not _check_openvino():
            logger.warning(
                "OpenVINO requested but not installed — "
                "falling back to sd15_inpaint_cpu"
            )
            from .sd15_cpu import SD15InpaintCPU
            return SD15InpaintCPU(**common)
        return SD15InpaintOpenVINO(**common)

    raise ValueError(
        f"Unknown backend '{key}'.  "
        f"Set BODY_DIFFUSION_BACKEND to one of: "
        f"sd15_inpaint_cpu, sd2_inpaint_cpu, sd15_inpaint_openvino"
    )
