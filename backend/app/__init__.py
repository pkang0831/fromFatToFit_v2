# Backend application package

import os as _os

if _os.environ.get("ENVIRONMENT", "development").lower() == "development":
    # Disable SSL verification for local dev behind corporate proxy/VPN.
    # This patches httpx globally so Supabase and other SDK clients also skip verify.
    # Has no effect in production (ENVIRONMENT != "development").
    try:
        import ssl as _ssl
        import httpx as _httpx

        _ssl._create_default_https_context = _ssl._create_unverified_context

        _orig_client = _httpx.Client.__init__
        _orig_async = _httpx.AsyncClient.__init__

        def _client_no_verify(self, *a, **kw):
            kw["verify"] = False
            _orig_client(self, *a, **kw)

        def _async_no_verify(self, *a, **kw):
            kw["verify"] = False
            _orig_async(self, *a, **kw)

        _httpx.Client.__init__ = _client_no_verify  # type: ignore
        _httpx.AsyncClient.__init__ = _async_no_verify  # type: ignore
    except ImportError:
        pass
