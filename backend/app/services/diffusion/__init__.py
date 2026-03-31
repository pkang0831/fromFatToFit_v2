"""
CPU-only local diffusion backends for body-cut refinement.

Provides modular backend abstraction over:
  - SD 1.5 Inpainting on CPU  (primary)
  - SD 2 Inpainting on CPU    (fallback)
  - SD 1.5 via OpenVINO       (optional Intel CPU acceleration)

Usage:
    from backend.app.services.diffusion import get_backend
    backend = get_backend()
    backend.load()
    result = backend.refine_torso(...)
"""

from .base import DiffusionBackend, RefineRequest, RefineResult
from .loader import get_backend

__all__ = [
    "DiffusionBackend",
    "RefineRequest",
    "RefineResult",
    "get_backend",
]
