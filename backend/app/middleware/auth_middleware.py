from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import logging
from supabase import create_client, ClientOptions
from ..config import settings

logger = logging.getLogger(__name__)


def _build_fallback_current_user(user, token: str):
    meta = user.user_metadata or {}
    return {
        "id": user.id,
        "email": user.email,
        "access_token": token,
        "full_name": meta.get("full_name") or meta.get("name") or meta.get("user_name"),
        "premium_status": False,
        "height_cm": None,
        "weight_kg": None,
        "target_weight_kg": None,
        "age": None,
        "gender": None,
        "ethnicity": None,
        "activity_level": None,
        "calorie_goal": None,
        "stripe_customer_id": None,
        "onboarding_completed": bool(meta.get("onboarding_completed", False)),
    }

def _make_auth_client():
    """Ephemeral client used only for auth.get_user() verification,
    so the singleton PostgREST auth state is never polluted."""
    return create_client(settings.supabase_url, settings.supabase_service_key)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get current authenticated user from JWT token.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        parts = authorization.split(None, 1)
        if len(parts) != 2:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if settings.test_login_stub_mode and token == settings.test_login_stub_access_token:
            return {
                "id": settings.test_login_stub_user_id,
                "email": settings.test_login_email,
                "access_token": token,
                "full_name": "Denevira E2E",
                "premium_status": True,
                "height_cm": 180,
                "weight_kg": 82,
                "target_weight_kg": None,
                "age": 30,
                "gender": "male",
                "ethnicity": None,
                "activity_level": "moderate",
                "calorie_goal": None,
                "stripe_customer_id": None,
                "onboarding_completed": True,
            }
        
        # Verify token with an ephemeral client to avoid mutating
        # the singleton's PostgREST auth headers.
        auth_client = _make_auth_client()
        user_response = auth_client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user

        # Use a per-request client with the user's JWT for all PostgREST
        # operations. This satisfies RLS policies (auth.uid() = user_id)
        # for SELECT, INSERT, and UPDATE.
        db = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
            options=ClientOptions(
                headers={"Authorization": f"Bearer {token}"},
            ),
        )
        
        try:
            profile_result = db.table("user_profiles").select("*").eq("user_id", user.id).execute()
        except Exception as profile_error:
            logger.warning(
                "Auth middleware profile lookup degraded for user %s: %s",
                user.id,
                profile_error,
            )
            return _build_fallback_current_user(user, token)
        
        if profile_result.data:
            profile = profile_result.data[0]
            has_required = all([
                profile.get("gender"),
                profile.get("age"),
                profile.get("height_cm"),
            ])
            return {
                "id": user.id,
                "email": user.email,
                "access_token": token,
                "premium_status": profile.get("premium_status", False),
                "calorie_goal": profile.get("calorie_goal"),
                "full_name": profile.get("full_name"),
                "height_cm": profile.get("height_cm"),
                "weight_kg": profile.get("weight_kg"),
                "target_weight_kg": profile.get("target_weight_kg"),
                "age": profile.get("age"),
                "gender": profile.get("gender"),
                "ethnicity": profile.get("ethnicity"),
                "activity_level": profile.get("activity_level"),
                "stripe_customer_id": profile.get("stripe_customer_id"),
                "onboarding_completed": profile.get("onboarding_completed", has_required),
            }
        else:
            from datetime import datetime
            meta = user.user_metadata or {}
            profile_data = {
                "user_id": user.id,
                "email": user.email,
                "full_name": meta.get("full_name") or meta.get("name") or meta.get("user_name"),
                "premium_status": False,
                "created_at": datetime.utcnow().isoformat()
            }
            profile_data = {k: v for k, v in profile_data.items() if v is not None}
            try:
                db.table("user_profiles").insert(profile_data).execute()
            except Exception as profile_insert_error:
                logger.warning(
                    "Auth middleware profile autoinsert degraded for user %s: %s",
                    user.id,
                    profile_insert_error,
                )
                return _build_fallback_current_user(user, token)
            
            logger.info(f"Auto-created profile for user {user.id} (provider: {meta.get('iss', 'email')})")
            
            return _build_fallback_current_user(user, token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in auth middleware: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """
    Optional authentication - returns None if no token provided
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
