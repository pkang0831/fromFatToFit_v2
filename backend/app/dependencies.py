from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
from supabase import Client

from app.middleware.auth_middleware import get_current_user, get_current_user_optional


async def get_user_db(request: Request) -> Client:
    """Get a user-scoped Supabase client from the request's auth token.
    This client uses the anon key + user JWT, so RLS policies apply automatically.
    """
    from app.database import get_user_supabase

    authorization = request.headers.get("Authorization", "")
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid auth token",
        )

    return get_user_supabase(parts[1])
