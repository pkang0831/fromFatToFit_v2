from supabase import create_client, Client
from .config import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_key)
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_key)


def get_supabase() -> Client:
    """Get Supabase client instance"""
    return supabase


def get_user_supabase(access_token: str) -> Client:
    """Get Supabase client with user's access token for RLS"""
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
        options={"headers": {"Authorization": f"Bearer {access_token}"}}
    )
