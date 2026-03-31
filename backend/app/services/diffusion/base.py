"""
Abstract diffusion backend interface for CPU inpainting.

Every backend (SD1.5 CPU, SD2 CPU, OpenVINO) implements this contract.
The two-pass refinement pipeline depends only on this interface.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image


@dataclass
class RefineRequest:
    """Inputs for one diffusion inpainting pass."""
    init_image: Image.Image       # RGB PIL image (ROI-cropped)
    mask_image: Image.Image       # L-mode PIL mask  (white = inpaint)
    prompt: str = ""
    negative_prompt: str = ""
    strength: float = 0.55
    guidance_scale: float = 7.5
    num_steps: int = 18
    seed: int = -1
    width: Optional[int] = None   # target width  (multiple of 8)
    height: Optional[int] = None  # target height (multiple of 8)


@dataclass
class RefineResult:
    """Output of one diffusion inpainting pass."""
    image: Image.Image            # RGB PIL image at ROI resolution
    seed_used: int = -1
    elapsed_ms: float = 0.0
    debug_info: dict = field(default_factory=dict)


class DiffusionBackend(abc.ABC):
    """Abstract base for all CPU inpainting backends."""

    @abc.abstractmethod
    def load(self) -> None:
        """Download (if needed) and load the pipeline into memory."""
        ...

    @abc.abstractmethod
    def is_ready(self) -> bool:
        ...

    @abc.abstractmethod
    def refine_seam(self, request: RefineRequest) -> RefineResult:
        """Pass 1: repair narrow warp-seam artifacts."""
        ...

    @abc.abstractmethod
    def refine_torso(self, request: RefineRequest) -> RefineResult:
        """Pass 2: interior torso texture refinement."""
        ...

    @abc.abstractmethod
    def get_debug_info(self) -> dict:
        ...

    def unload(self) -> None:
        """Release memory.  Optional override."""
        pass
