import hashlib
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_request_cache: dict[str, tuple[float, int]] = {}
CACHE_TTL_SECONDS = 300

def get_idempotency_key(user_id: str, method: str, path: str, body_hash: str) -> str:
    return hashlib.sha256(f"{user_id}:{method}:{path}:{body_hash}".encode()).hexdigest()

def check_duplicate_request(user_id: str, method: str, path: str, body: Optional[bytes] = None) -> Optional[int]:
    """Returns cached status code if duplicate, None if new request."""
    if method not in ("POST", "PUT", "PATCH"):
        return None
    
    body_hash = hashlib.md5(body or b"").hexdigest()
    key = get_idempotency_key(user_id, method, path, body_hash)
    
    now = time.time()
    # Clean expired entries
    expired = [k for k, (ts, _) in _request_cache.items() if now - ts > CACHE_TTL_SECONDS]
    for k in expired:
        del _request_cache[k]
    
    if key in _request_cache:
        ts, status = _request_cache[key]
        if now - ts < CACHE_TTL_SECONDS:
            logger.warning(f"DUPLICATE_REQUEST | user={user_id} | {method} {path} | age={now-ts:.1f}s")
            return status
    
    return None

def record_request(user_id: str, method: str, path: str, body: Optional[bytes], status_code: int):
    body_hash = hashlib.md5(body or b"").hexdigest()
    key = get_idempotency_key(user_id, method, path, body_hash)
    _request_cache[key] = (time.time(), status_code)
