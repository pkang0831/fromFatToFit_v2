from supabase import create_client, Client, ClientOptions
from .config import settings

# NOTE: For user data queries, prefer get_user_supabase(token) which respects RLS.
# get_supabase() uses the service key and bypasses RLS — use only for admin operations
# or system-level queries (webhooks, scheduled jobs, etc.)

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase() -> Client:
    """Get Supabase client instance (service key — bypasses RLS)."""
    return supabase


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
