"""
SD 2 Inpainting on CPU — fallback backend.

Uses ``StableDiffusionInpaintPipeline`` with the SD2 community
inpainting checkpoint.  Same interface as SD15InpaintCPU.
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Optional

import torch
from PIL import Image

from .base import DiffusionBackend, RefineRequest, RefineResult
from .download import resolve_model_path, DownloadError
from .registry import MODELS
from . import prompts as P

logger = logging.getLogger(__name__)


class SD2InpaintCPU(DiffusionBackend):

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
        from diffusers import StableDiffusionInpaintPipeline

        spec = MODELS["sd2_inpaint"]
        try:
            local_path = resolve_model_path(
                spec, token=self._token, cache_dir=self._cache_dir,
            )
        except DownloadError as exc:
            raise RuntimeError(str(exc)) from exc

        logger.info(f"Loading SD 2 Inpainting (CPU/fp32) from {local_path}")
        t0 = time.monotonic()

        self._pipe = StableDiffusionInpaintPipeline.from_pretrained(
            local_path,
            torch_dtype=torch.float32,
            safety_checker=None,
            requires_safety_checker=False,
        )
        self._pipe.to("cpu")
        self._pipe.set_progress_bar_config(disable=True)

        self._load_time_ms = round((time.monotonic() - t0) * 1000, 1)
        logger.info(f"SD 2 Inpainting loaded in {self._load_time_ms}ms")

    def is_ready(self) -> bool:
        return self._pipe is not None

    def refine_seam(self, request: RefineRequest) -> RefineResult:
        return self._run(request, tag="seam")

    def refine_torso(self, request: RefineRequest) -> RefineResult:
        return self._run(request, tag="torso")

    def get_debug_info(self) -> dict:
        return {
            "backend": "sd2_inpaint_cpu",
            "model": MODELS["sd2_inpaint"].repo_id,
            "loaded": self.is_ready(),
            "device": "cpu",
            "dtype": "float32",
            "num_steps": self._num_steps,
            "load_time_ms": self._load_time_ms,
        }

    def unload(self) -> None:
        if self._pipe is not None:
            del self._pipe
            self._pipe = None
            logger.info("SD 2 Inpainting unloaded")

    def _run(self, req: RefineRequest, tag: str) -> RefineResult:
        if not self.is_ready():
            raise RuntimeError("SD2InpaintCPU not loaded — call load() first")

        w = req.width or req.init_image.width
        h = req.height or req.init_image.height
        w, h = (w // 8) * 8, (h // 8) * 8

        seed = req.seed if req.seed >= 0 else random.randint(0, 2**32 - 1)
        gen = torch.Generator(device="cpu").manual_seed(seed)
        steps = req.num_steps or self._num_steps

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
            generator=gen,
        ).images[0]
        elapsed = round((time.monotonic() - t0) * 1000, 1)

        logger.info(f"SD2 {tag}: {elapsed}ms, {w}x{h}, steps={steps}, seed={seed}")
        return RefineResult(
            image=out,
            seed_used=seed,
            elapsed_ms=elapsed,
            debug_info={"tag": tag, "steps": steps, "strength": req.strength},
        )
