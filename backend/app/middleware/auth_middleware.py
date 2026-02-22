from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import logging
from ..database import get_supabase

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get current authenticated user from JWT token
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User data from Supabase
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>"
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
        
        # Verify token with Supabase
        supabase = get_supabase()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_response.user
        
        # Get extended user profile
        profile_result = supabase.table("user_profiles").select("*").eq("user_id", user.id).execute()
        
        if profile_result.data:
            profile = profile_result.data[0]
            # Merge user data with profile (use user_id from profile, not profile's primary key id)
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
                "age": profile.get("age"),
                "gender": profile.get("gender"),
                "ethnicity": profile.get("ethnicity"),
                "activity_level": profile.get("activity_level"),
                "stripe_customer_id": profile.get("stripe_customer_id"),
                "onboarding_completed": profile.get("onboarding_completed", has_required),
            }
        else:
            # Auto-create profile for first-time users (including OAuth)
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
            supabase.table("user_profiles").insert(profile_data).execute()
            
            logger.info(f"Auto-created profile for user {user.id} (provider: {meta.get('iss', 'email')})")
            
            return {
                "id": user.id,
                "email": user.email,
                "access_token": token,
                "full_name": profile_data.get("full_name"),
                "premium_status": False,
                "height_cm": None,
                "weight_kg": None,
                "age": None,
                "gender": None,
                "ethnicity": None,
                "activity_level": None,
                "calorie_goal": None,
                "stripe_customer_id": None,
                "onboarding_completed": False,
            }
        
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
