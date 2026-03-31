"""
Hugging Face download / cache manager.

Handles authentication, resumable downloads, cache verification,
and clear error reporting.
"""

from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .registry import MODELS, DOWNLOAD_PROFILES, ModelSpec

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when a model download fails for a recoverable reason."""


@dataclass
class DownloadResult:
    key: str
    repo_id: str
    local_path: str
    already_cached: bool
    size_gb: float


def _resolve_cache_dir(override: str = "") -> Path:
    if override:
        return Path(override)
    return Path(
        os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")
    ) / "hub"


def _resolve_token(override: str = "") -> Optional[str]:
    token = (
        override
        or os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    )
    return token if token else None


def _check_disk_space(cache_dir: Path, required_gb: float) -> None:
    try:
        target = cache_dir if cache_dir.exists() else cache_dir.parent
        usage = shutil.disk_usage(target)
        free_gb = usage.free / (1024 ** 3)
        if free_gb < required_gb * 1.15:
            raise DownloadError(
                f"Insufficient disk space: {free_gb:.1f} GB free, "
                f"need ~{required_gb:.1f} GB (+15 % headroom).  "
                f"Free space or set HF_CACHE_DIR to a larger volume."
            )
    except OSError:
        pass


# ── Public API ───────────────────────────────────────────────────────────────

def download_model(
    spec: ModelSpec,
    *,
    token: Optional[str] = None,
    cache_dir: Optional[Path] = None,
    force: bool = False,
) -> DownloadResult:
    """Download a single model via ``huggingface_hub.snapshot_download``.

    Skips already-cached files, supports resume, returns the local path.
    """
    from huggingface_hub import snapshot_download
    from huggingface_hub.utils import (
        GatedRepoError,
        RepositoryNotFoundError,
        HfHubHTTPError,
    )

    resolved_token = token or _resolve_token()
    resolved_cache = cache_dir or _resolve_cache_dir()
    resolved_cache.mkdir(parents=True, exist_ok=True)

    if spec.is_gated and not resolved_token:
        raise DownloadError(
            f"Model '{spec.repo_id}' is gated — set HF_TOKEN in .env.  "
            f"Also accept the license at https://huggingface.co/{spec.repo_id}"
        )

    _check_disk_space(resolved_cache, spec.approx_size_gb)

    logger.info(
        f"Downloading {spec.key} ({spec.repo_id}, ~{spec.approx_size_gb} GB) "
        f"→ {resolved_cache}"
    )

    kwargs: dict = dict(
        repo_id=spec.repo_id,
        cache_dir=str(resolved_cache),
        token=resolved_token,
        resume_download=True,
    )
    if spec.revision:
        kwargs["revision"] = spec.revision

    try:
        local_dir = snapshot_download(**kwargs)
    except GatedRepoError:
        raise DownloadError(
            f"Gated-access denied for '{spec.repo_id}'.  "
            f"Accept the license at https://huggingface.co/{spec.repo_id} "
            f"and verify HF_TOKEN has read access."
        )
    except RepositoryNotFoundError:
        raise DownloadError(f"Repo '{spec.repo_id}' not found on HF Hub.")
    except HfHubHTTPError as exc:
        raise DownloadError(f"HF Hub HTTP error for '{spec.repo_id}': {exc}")
    except Exception as exc:
        raise DownloadError(f"Download failed for '{spec.repo_id}': {exc}")

    logger.info(f"Ready: {spec.key} → {local_dir}")
    return DownloadResult(
        key=spec.key,
        repo_id=spec.repo_id,
        local_path=local_dir,
        already_cached=False,
        size_gb=spec.approx_size_gb,
    )


def download_profile(
    profile: str,
    *,
    token: Optional[str] = None,
    cache_dir: Optional[Path] = None,
) -> list[DownloadResult]:
    keys = DOWNLOAD_PROFILES.get(profile)
    if keys is None:
        raise ValueError(
            f"Unknown profile '{profile}'.  "
            f"Available: {', '.join(DOWNLOAD_PROFILES)}"
        )
    return [
        download_model(MODELS[k], token=token, cache_dir=cache_dir)
        for k in keys
    ]


def resolve_model_path(
    spec: ModelSpec,
    *,
    token: Optional[str] = None,
    cache_dir: Optional[Path] = None,
) -> str:
    """Return the local cache path.  Never hits the network."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.utils import LocalEntryNotFoundError

    resolved_cache = cache_dir or _resolve_cache_dir()
    kwargs: dict = dict(
        repo_id=spec.repo_id,
        cache_dir=str(resolved_cache),
        local_files_only=True,
    )
    if spec.revision:
        kwargs["revision"] = spec.revision
    try:
        return snapshot_download(**kwargs)
    except (LocalEntryNotFoundError, FileNotFoundError, OSError):
        raise DownloadError(
            f"Model '{spec.repo_id}' not cached.  "
            f"Run: python -m backend.app.tools.download_models download "
            f"--profile {spec.key.replace('_inpaint', '')}_only"
        )


def verify_model(spec: ModelSpec, *, cache_dir: Optional[Path] = None) -> dict:
    try:
        lp = resolve_model_path(spec, cache_dir=cache_dir)
        return {
            "key": spec.key,
            "repo_id": spec.repo_id,
            "status": "cached",
            "local_path": lp,
        }
    except DownloadError:
        return {
            "key": spec.key,
            "repo_id": spec.repo_id,
            "status": "not_cached",
            "local_path": None,
        }


def verify_all_models(cache_dir: Optional[Path] = None) -> list[dict]:
    return [verify_model(s, cache_dir=cache_dir) for s in MODELS.values()]
