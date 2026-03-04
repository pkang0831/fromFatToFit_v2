"""Rate limiting for API endpoints using slowapi."""
from slowapi import Limiter
from slowapi.util import get_remote_address


def _get_identifier(request):
    return get_remote_address(request)


limiter = Limiter(key_func=_get_identifier)
