import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


async def log_retention_event(
    user_id: str,
    event_name: str,
    surface: str,
    properties: dict[str, Any] | None = None,
) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "event_name": event_name,
        "surface": surface,
        "properties": properties or {},
    }
    logger.info("retention_event=%s", json.dumps(event, sort_keys=True, default=str))
