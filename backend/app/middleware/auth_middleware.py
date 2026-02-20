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
        scheme, token = authorization.split()
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
            return {
                "id": user.id,  # Use auth user ID, not profile table ID
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
                "stripe_customer_id": profile.get("stripe_customer_id")
            }
        else:
            # Create profile if it doesn't exist
            from datetime import datetime
            profile_data = {
                "user_id": user.id,
                "email": user.email,
                "premium_status": False,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.table("user_profiles").insert(profile_data).execute()
            
            return {
                "id": user.id,
                "email": user.email,
                "access_token": token,
                **profile_data
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
