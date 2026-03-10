"""Lightweight telemetry for transformation journey requests.

Emits structured log lines (JSON-like) that can be grepped, piped to
a log aggregator, or read directly in staging.  No external dependencies.

Counters are in-process only (reset on restart) — suitable for
beta/staging observation, not production analytics.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger("journey.telemetry")

# ── In-process counters (beta observation only) ────────────────────────────

_counters = {
    "total_requests": 0,
    "success": 0,
    "partial_success": 0,
    "total_failure": 0,
    "below_threshold_failure": 0,
    "credits_charged": 0,
    "total_latency_ms": 0,
    "warnings_emitted": 0,
}

_mode_counts: dict[str, int] = {}


def get_counters() -> dict:
    return {**_counters, "by_mode": dict(_mode_counts)}


# ── Per-request record ─────────────────────────────────────────────────────

@dataclass
class JourneyRequestRecord:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    user_id: str = ""
    mode: str = ""
    stage_count: int = 0
    stages_requested: int = 0
    stages_succeeded: int = 0
    stages_failed: int = 0
    failed_stage_numbers: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    credits_charged: int = 0
    stage_latencies_ms: dict[int, float] = field(default_factory=dict)
    total_latency_ms: float = 0
    outcome: str = ""  # "success" | "partial" | "failure" | "error"
    error_detail: str = ""

    def to_log_dict(self) -> dict:
        return asdict(self)


def start_timer() -> float:
    return time.monotonic()


def elapsed_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 1)


def record_journey(rec: JourneyRequestRecord) -> None:
    """Emit the structured telemetry log line and update counters."""
    _counters["total_requests"] += 1

    if rec.outcome == "success":
        _counters["success"] += 1
    elif rec.outcome == "partial":
        _counters["partial_success"] += 1
    elif rec.outcome == "failure":
        _counters["total_failure"] += 1
    elif rec.outcome == "below_threshold":
        _counters["below_threshold_failure"] += 1

    _counters["credits_charged"] += rec.credits_charged
    _counters["total_latency_ms"] += rec.total_latency_ms
    _counters["warnings_emitted"] += len(rec.warnings)

    _mode_counts[rec.mode] = _mode_counts.get(rec.mode, 0) + 1

    logger.info("JOURNEY_TELEMETRY %s", rec.to_log_dict())
