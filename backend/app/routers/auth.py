from fastapi import APIRouter, HTTPException, status, Depends
import logging
from datetime import datetime
from ..schemas.auth_schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PasswordReset, PasswordUpdate
)
from ..schemas.body_schemas import UserProfileUpdate
from ..database import get_supabase
from ..middleware.auth_middleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        supabase = get_supabase()
        
        # Create user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "full_name": user_data.full_name
                }
            }
        })
        
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        user = auth_response.user
        session = auth_response.session
        
        # Create user profile
        profile_data = {
            "user_id": user.id,
            "email": user.email,
            "full_name": user_data.full_name,
            "ethnicity": user_data.ethnicity,
            "gender": user_data.gender,
            "age": user_data.age,
            "height_cm": user_data.height_cm,
            "premium_status": False,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("user_profiles").insert(profile_data).execute()
        
        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user_data.full_name,
                height_cm=user_data.height_cm,
                weight_kg=None,
                age=user_data.age,
                gender=user_data.gender,
                ethnicity=user_data.ethnicity,
                activity_level=None,
                calorie_goal=None,
                premium_status=False,
                created_at=datetime.utcnow()
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login with email and password"""
    try:
        supabase = get_supabase()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user = auth_response.user
        session = auth_response.session
        
        # Get user profile
        profile_result = supabase.table("user_profiles").select("*").eq("user_id", user.id).execute()
        profile = profile_result.data[0] if profile_result.data else {}
        
        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            token_type="bearer",
            expires_in=session.expires_in or 3600,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=profile.get("full_name"),
                height_cm=profile.get("height_cm"),
                weight_kg=profile.get("weight_kg"),
                age=profile.get("age"),
                gender=profile.get("gender"),
                ethnicity=profile.get("ethnicity"),
                activity_level=profile.get("activity_level"),
                calorie_goal=profile.get("calorie_goal"),
                premium_status=profile.get("premium_status", False),
                created_at=datetime.fromisoformat(profile.get("created_at", datetime.utcnow().isoformat()))
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user"""
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=current_user.get("full_name"),
            height_cm=current_user.get("height_cm"),
            weight_kg=current_user.get("weight_kg"),
            age=current_user.get("age"),
            gender=current_user.get("gender"),
            ethnicity=current_user.get("ethnicity"),
            activity_level=current_user.get("activity_level"),
            calorie_goal=current_user.get("calorie_goal"),
            premium_status=current_user.get("premium_status", False),
            created_at=datetime.fromisoformat(current_user.get("created_at", datetime.utcnow().isoformat()))
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile"
        )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        supabase = get_supabase()
        
        # Prepare update data (only include fields that were provided)
        update_data = {
            k: v for k, v in profile_update.model_dump().items()
            if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update profile
        supabase.table("user_profiles").update(update_data).eq("user_id", current_user["id"]).execute()
        
        # Get updated profile
        result = supabase.table("user_profiles").select("*").eq("user_id", current_user["id"]).execute()
        profile = result.data[0] if result.data else {}
        
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=profile.get("full_name"),
            height_cm=profile.get("height_cm"),
            weight_kg=profile.get("weight_kg"),
            age=profile.get("age"),
            gender=profile.get("gender"),
            ethnicity=profile.get("ethnicity"),
            activity_level=profile.get("activity_level"),
            calorie_goal=profile.get("calorie_goal"),
            premium_status=profile.get("premium_status", False),
            created_at=datetime.fromisoformat(profile.get("created_at", datetime.utcnow().isoformat()))
        )
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Request password reset email"""
    try:
        supabase = get_supabase()
        supabase.auth.reset_password_email(reset_data.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}
