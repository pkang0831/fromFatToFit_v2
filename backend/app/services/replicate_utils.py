"""
Shared utilities for Replicate API calls.

Uses urllib for portable HTTP without external binary dependencies.
Falls back to curl subprocess when available (corporate proxy workaround).
"""

import asyncio
import base64
import io
import json
import logging
import os
import shutil
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

_HAS_CURL = shutil.which("curl") is not None


def curl_json(method: str, url: str, api_key: str, json_body: dict | None = None) -> dict:
    """Make an API call, preferring urllib with curl fallback."""
    if _HAS_CURL:
        return _curl_json_subprocess(method, url, api_key, json_body)
    return _urllib_json(method, url, api_key, json_body)


def _urllib_json(method: str, url: str, api_key: str, json_body: dict | None = None) -> dict:
    """Make an API call via urllib (no external dependencies)."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Devenira/1.0 (Python urllib)",
        "Accept": "application/json",
    }
    data = json.dumps(json_body).encode() if json_body is not None else None
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        raise RuntimeError(f"HTTP {e.code} from {url}: {body}") from e


def _curl_json_subprocess(method: str, url: str, api_key: str, json_body: dict | None = None) -> dict:
    """Make an API call via curl subprocess (corporate proxy workaround)."""
    import subprocess
    import tempfile

    cmd = [
        "curl", "-s",
        "-X", method,
        url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
    ]

    tmp_file = None
    if json_body is not None:
        tmp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(json_body, tmp_file)
        tmp_file.close()
        cmd.extend(["-d", f"@{tmp_file.name}"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(f"curl failed (exit {result.returncode}): {result.stderr[:300]}")
        return json.loads(result.stdout)
    finally:
        if tmp_file is not None:
            os.unlink(tmp_file.name)


def curl_download(url: str, dest_path: str) -> None:
    """Download a file via urllib, with curl fallback."""
    if _HAS_CURL:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "-o", dest_path, url],
            capture_output=True, timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"curl download failed: {result.stderr[:200]}")
        return

    req = urllib.request.Request(url, headers={"User-Agent": "Devenira/1.0 (Python urllib)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        with open(dest_path, "wb") as f:
            f.write(resp.read())


async def poll_prediction(poll_url: str, api_key: str, max_polls: int = 90, interval: float = 2.0) -> dict:
    """
    Poll a Replicate prediction until completion.

    Returns the final prediction dict with status 'succeeded'.
    Raises RuntimeError on failure/timeout.
    """
    loop = asyncio.get_event_loop()

    for _ in range(max_polls):
        await asyncio.sleep(interval)
        data = await loop.run_in_executor(None, curl_json, "GET", poll_url, api_key, None)
        status = data.get("status")

        if status == "succeeded":
            return data
        elif status in ("failed", "canceled"):
            raise RuntimeError(f"Prediction {status}: {data.get('error')}")

    raise RuntimeError(f"Prediction timed out after {max_polls * interval:.0f}s")


def image_to_data_uri(image_base64: str, fmt: str = "jpeg") -> str:
    """Convert raw base64 string to a data URI."""
    return f"data:image/{fmt};base64,{image_base64}"


def download_to_base64(url: str) -> str:
    """Download a URL and return its content as base64."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        curl_download(url, tmp_path)
        with open(tmp_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    finally:
        os.unlink(tmp_path)


def get_replicate_api_key() -> str:
    """Get the Replicate API key from settings, raising if missing."""
    from ..config import settings
    api_key = getattr(settings, "replicate_api_key", None)
    if not api_key:
        raise RuntimeError("REPLICATE_API_KEY is not configured")
    return api_key
