from supabase import create_client, Client, ClientOptions
from .config import settings

# supabase-py mutates the client's PostgREST auth headers when auth
# operations (sign_in, get_user, etc.) are called.  We keep ONE singleton
# exclusively for auth endpoints (login / register) — those need a warm
# GoTrue client.  All data (PostgREST) calls use fresh per-request
# clients so state from one request never leaks into another.

_auth_client: Client | None = None


def _ensure_settings():
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")


def get_supabase_auth() -> Client:
    """Singleton used ONLY for GoTrue auth operations (sign_in, sign_up, get_user).
    Do NOT use this client for PostgREST table queries — its auth headers
    get mutated by GoTrue calls."""
    global _auth_client
    if _auth_client is None:
        _ensure_settings()
        _auth_client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _auth_client


def get_supabase() -> Client:
    """Fresh Supabase client for PostgREST data operations (service key).
    Returns a new instance each time to prevent auth state pollution."""
    _ensure_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase_admin() -> Client:
    """Alias for get_supabase()."""
    return get_supabase()


def get_user_supabase(access_token: str) -> Client:
    """Fresh client scoped to a user's JWT (satisfies RLS)."""
    _ensure_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
        options=ClientOptions(
            headers={"Authorization": f"Bearer {access_token}"},
        ),
    )
