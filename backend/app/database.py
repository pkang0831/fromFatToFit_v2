from supabase import create_client, Client, ClientOptions
from .config import settings

# NOTE: For user data queries, prefer get_user_supabase(token) which respects RLS.
# get_supabase() uses the service key and bypasses RLS — use only for admin operations
# or system-level queries (webhooks, scheduled jobs, etc.)

_supabase: Client | None = None
_supabase_admin: Client | None = None


def _init_client() -> Client:
    if not settings.supabase_url or not settings.supabase_service_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase() -> Client:
    """Get Supabase client instance (service key — bypasses RLS)."""
    global _supabase
    if _supabase is None:
        _supabase = _init_client()
    return _supabase


def get_supabase_admin() -> Client:
    """Get Supabase admin client instance."""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = _init_client()
    return _supabase_admin


def get_user_supabase(access_token: str) -> Client:
    """Create a Supabase client scoped to a specific user's JWT.
    This client respects RLS policies, so queries are automatically
    filtered to only return the user's own data.
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
        options=ClientOptions(
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": settings.supabase_anon_key,
            }
        ),
    )
