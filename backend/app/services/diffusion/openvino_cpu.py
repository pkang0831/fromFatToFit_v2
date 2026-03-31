"""
SD 1.5 Inpainting via OpenVINO — optional Intel CPU acceleration.

Uses ``optimum-intel`` + ``OVStableDiffusionInpaintPipeline`` for
2-4x speedup on Intel CPUs compared to plain PyTorch.

If ``optimum[openvino]`` is not installed this module raises a clear
error at load() time, never at import time.
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Optional

from PIL import Image

from .base import DiffusionBackend, RefineRequest, RefineResult
from .download import resolve_model_path, DownloadError
from .registry import MODELS
from . import prompts as P

logger = logging.getLogger(__name__)

_OPENVINO_AVAILABLE: Optional[bool] = None


def _check_openvino() -> bool:
    global _OPENVINO_AVAILABLE
    if _OPENVINO_AVAILABLE is not None:
        return _OPENVINO_AVAILABLE
    try:
        from optimum.intel import OVStableDiffusionInpaintPipeline  # noqa: F401
        _OPENVINO_AVAILABLE = True
    except ImportError:
        _OPENVINO_AVAILABLE = False
    return _OPENVINO_AVAILABLE


class SD15InpaintOpenVINO(DiffusionBackend):

    def __init__(
        self,
        *,
        hf_token: str = "",
        cache_dir: str = "",
        num_steps: int = 18,
    ):
        self._token = hf_token or None
        self._cache_dir = Path(cache_dir) if cache_dir else None
        self._num_steps = num_steps
        self._pipe = None
        self._load_time_ms: float = 0

    def load(self) -> None:
        if not _check_openvino():
            raise RuntimeError(
                "OpenVINO not available.  Install with:\n"
                "  pip install optimum[openvino]\n"
                "Or set BODY_DIFFUSION_BACKEND=sd15_inpaint_cpu "
                "to use plain PyTorch CPU."
            )

        from optimum.intel import OVStableDiffusionInpaintPipeline

        spec = MODELS["sd15_inpaint"]
        try:
            local_path = resolve_model_path(
                spec, token=self._token, cache_dir=self._cache_dir,
            )
        except DownloadError as exc:
            raise RuntimeError(str(exc)) from exc

        logger.info(f"Loading SD 1.5 Inpainting (OpenVINO) from {local_path}")
        t0 = time.monotonic()

        self._pipe = OVStableDiffusionInpaintPipeline.from_pretrained(
            local_path,
            export=True,
        )

        self._load_time_ms = round((time.monotonic() - t0) * 1000, 1)
        logger.info(f"SD 1.5 OpenVINO loaded in {self._load_time_ms}ms")

    def is_ready(self) -> bool:
        return self._pipe is not None

    def refine_seam(self, request: RefineRequest) -> RefineResult:
        return self._run(request, tag="seam")

    def refine_torso(self, request: RefineRequest) -> RefineResult:
        return self._run(request, tag="torso")

    def get_debug_info(self) -> dict:
        return {
            "backend": "sd15_inpaint_openvino",
            "model": MODELS["sd15_inpaint"].repo_id,
            "loaded": self.is_ready(),
            "device": "openvino-cpu",
            "openvino_available": _check_openvino(),
            "num_steps": self._num_steps,
            "load_time_ms": self._load_time_ms,
        }

    def unload(self) -> None:
        if self._pipe is not None:
            del self._pipe
            self._pipe = None
            logger.info("SD 1.5 OpenVINO unloaded")

    def _run(self, req: RefineRequest, tag: str) -> RefineResult:
        if not self.is_ready():
            raise RuntimeError("SD15InpaintOpenVINO not loaded — call load() first")

        w = req.width or req.init_image.width
        h = req.height or req.init_image.height
        w, h = (w // 8) * 8, (h // 8) * 8

        seed = req.seed if req.seed >= 0 else random.randint(0, 2**32 - 1)
        steps = req.num_steps or self._num_steps

        # OpenVINO pipeline uses numpy random, not torch Generator
        import numpy as np
        np.random.seed(seed)

        t0 = time.monotonic()
        out = self._pipe(
            prompt=req.prompt,
            negative_prompt=req.negative_prompt or None,
            image=req.init_image.resize((w, h), Image.LANCZOS),
            mask_image=req.mask_image.resize((w, h), Image.LANCZOS),
            width=w,
            height=h,
            guidance_scale=req.guidance_scale,
            strength=req.strength,
            num_inference_steps=steps,
        ).images[0]
        elapsed = round((time.monotonic() - t0) * 1000, 1)

        logger.info(f"OV-SD1.5 {tag}: {elapsed}ms, {w}x{h}, steps={steps}, seed={seed}")
        return RefineResult(
            image=out,
            seed_used=seed,
            elapsed_ms=elapsed,
            debug_info={"tag": tag, "steps": steps, "strength": req.strength},
        )
