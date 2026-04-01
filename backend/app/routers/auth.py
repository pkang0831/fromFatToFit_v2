from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
from datetime import datetime, timezone
from ..schemas.auth_schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PasswordReset, PasswordUpdate, AccountDeletionResponse
)
from ..schemas.body_schemas import UserProfileUpdate
from supabase import create_client, ClientOptions
from ..database import get_supabase, get_supabase_auth
from ..middleware.auth_middleware import get_current_user
from ..config import settings
from ..rate_limit import limiter
from ..services.account_deletion import delete_user_account
from ..services.retention_event_service import log_retention_event

logger = logging.getLogger(__name__)
router = APIRouter()

_LEGACY_USER_PROFILE_COLUMNS = {
    "user_id",
    "email",
    "full_name",
    "height_cm",
    "weight_kg",
    "age",
    "gender",
    "ethnicity",
    "activity_level",
    "calorie_goal",
    "premium_status",
    "stripe_customer_id",
    "created_at",
    "updated_at",
}


def _insert_user_profile_resilient(supabase, profile_data: dict) -> None:
    try:
        supabase.table("user_profiles").insert(profile_data).execute()
        return
    except Exception as full_insert_error:
        logger.warning(
            "user_profiles insert failed with extended columns; retrying with legacy-safe payload: %s",
            full_insert_error,
        )

    legacy_payload = {
        key: value
        for key, value in profile_data.items()
        if key in _LEGACY_USER_PROFILE_COLUMNS
    }
    supabase.table("user_profiles").insert(legacy_payload).execute()


def _sanitize_registration_attribution(db, user_data: UserRegister) -> tuple[str | None, str | None, str | None]:
    source = (user_data.attribution_source or "").strip() or None
    token = (user_data.attribution_token or "").strip() or None
    session_id = (user_data.attribution_session_id or "").strip() or None

    if source != "proof_share" or not token or not session_id:
        return None, None, None

    share_result = (
        db.table("proof_shares")
        .select("id, token, status")
        .eq("token", token)
        .eq("status", "active")
        .limit(1)
        .execute()
    )
    if not share_result.data:
        return None, None, None

    continuity_result = (
        db.table("funnel_events")
        .select("id")
        .eq("event_name", "referred_try_started")
        .eq("share_token", token)
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    if not continuity_result.data:
        return None, None, None

    return source, token, session_id


def _build_token_response(user, session, profile: dict) -> TokenResponse:
    has_required = all([profile.get("gender"), profile.get("age"), profile.get("height_cm")])
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
            target_weight_kg=profile.get("target_weight_kg"),
            age=profile.get("age"),
            gender=profile.get("gender"),
            ethnicity=profile.get("ethnicity"),
            activity_level=profile.get("activity_level"),
            calorie_goal=profile.get("calorie_goal"),
            premium_status=profile.get("premium_status", False),
            onboarding_completed=profile.get("onboarding_completed", has_required),
            created_at=datetime.fromisoformat(profile.get("created_at", datetime.utcnow().isoformat()))
        )
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, user_data: UserRegister):
    """Register a new user"""
    try:
        if not all([user_data.consent_terms, user_data.consent_privacy,
                     user_data.consent_sensitive_data, user_data.consent_age_verification]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All consent agreements must be accepted to create an account"
            )

        if user_data.age is not None and user_data.age < 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must be at least 18 years old to use this service"
            )

        supabase = get_supabase_auth()
        
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
        
        if not session:
            return {"message": "Check your email for confirmation link", "user": {"id": str(user.id), "email": user.email}}
        
        # Create user profile
        has_required = all([user_data.gender, user_data.age, user_data.height_cm])
        consent_timestamp = datetime.now(timezone.utc).isoformat()
        profile_data = {
            "user_id": user.id,
            "email": user.email,
            "full_name": user_data.full_name,
            "ethnicity": user_data.ethnicity,
            "gender": user_data.gender,
            "age": user_data.age,
            "height_cm": user_data.height_cm,
            "weight_kg": user_data.weight_kg,
            "activity_level": user_data.activity_level,
            "premium_status": False,
            "onboarding_completed": has_required,
            "created_at": consent_timestamp,
            "consent_terms_at": consent_timestamp,
            "consent_privacy_at": consent_timestamp,
            "consent_sensitive_data_at": consent_timestamp,
            "consent_age_verified_at": consent_timestamp,
            "consent_version": "2026-02-26",
        }
        db = get_supabase()
        _insert_user_profile_resilient(db, profile_data)
        attribution_source, attribution_token, attribution_session_id = _sanitize_registration_attribution(db, user_data)

        await log_retention_event(
            str(user.id),
            "register_completed",
            "auth_register",
            {
                "source": attribution_source,
                "share_token": attribution_token,
                "session_id": attribution_session_id,
            },
        )

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
                weight_kg=user_data.weight_kg,
                target_weight_kg=None,
                age=user_data.age,
                gender=user_data.gender,
                ethnicity=user_data.ethnicity,
                activity_level=user_data.activity_level,
                calorie_goal=None,
                premium_status=False,
                onboarding_completed=has_required,
                created_at=datetime.now(timezone.utc)
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        message = str(e)
        auth_validation_markers = (
            "password should contain at least one character",
            "user already registered",
            "invalid email",
            "signup is disabled",
        )
        if any(marker in message.lower() for marker in auth_validation_markers):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    """Login with email and password"""
    try:
        supabase = get_supabase_auth()
        
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
        
        # Get user profile — use a per-request client with the user's JWT
        # so the singleton's PostgREST state isn't polluted by sign_in above.
        db = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
            options=ClientOptions(
                headers={"Authorization": f"Bearer {session.access_token}"},
            ),
        )
        profile_result = db.table("user_profiles").select("*").eq("user_id", user.id).execute()
        profile = profile_result.data[0] if profile_result.data else {}
        
        return _build_token_response(user, session, profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.post("/test-login", response_model=TokenResponse)
async def test_login():
    """Explicitly opt-in auth bootstrap for Playwright and local QA."""
    if not settings.enable_test_login:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    try:
        auth_client = get_supabase_auth()
        email = settings.test_login_email.strip().lower()
        password = settings.test_login_password
        db = get_supabase()

        def _sign_in():
            return auth_client.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })

        def _bootstrap_user():
            logger.info("Test login user missing; creating dev-only bootstrap account")
            try:
                auth_client.auth.admin.create_user({
                    "email": email,
                    "password": password,
                    "email_confirm": True,
                    "user_metadata": {"full_name": "Denevira E2E"},
                })
            except Exception as bootstrap_error:
                message = str(bootstrap_error).lower()
                if "already" not in message and "exists" not in message and "registered" not in message:
                    raise

        try:
            auth_response = _sign_in()
        except Exception:
            _bootstrap_user()
            auth_response = _sign_in()

        if not auth_response.user or not auth_response.session:
            _bootstrap_user()
            auth_response = _sign_in()

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Test login bootstrap failed",
            )

        user = auth_response.user
        session = auth_response.session
        now = datetime.now(timezone.utc).isoformat()

        existing = db.table("user_profiles").select("*").eq("user_id", user.id).limit(1).execute()
        if existing.data:
            profile = existing.data[0]
            update_data = {
                "email": user.email,
                "full_name": profile.get("full_name") or "Denevira E2E",
                "gender": profile.get("gender") or "male",
                "age": profile.get("age") or 30,
                "height_cm": profile.get("height_cm") or 180,
                "weight_kg": profile.get("weight_kg") or 82,
                "activity_level": profile.get("activity_level") or "moderate",
                "onboarding_completed": True,
                "updated_at": now,
            }
            db.table("user_profiles").update(update_data).eq("user_id", user.id).execute()
            profile = {**profile, **update_data}
        else:
            profile = {
                "user_id": user.id,
                "email": user.email,
                "full_name": "Denevira E2E",
                "gender": "male",
                "age": 30,
                "height_cm": 180,
                "weight_kg": 82,
                "activity_level": "moderate",
                "premium_status": False,
                "onboarding_completed": True,
                "created_at": now,
            }
            _insert_user_profile_resilient(db, profile)

        return _build_token_response(user, session, profile)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test login bootstrap failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Test login bootstrap failed",
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user"""
    try:
        supabase = get_supabase_auth()
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
            target_weight_kg=current_user.get("target_weight_kg"),
            age=current_user.get("age"),
            gender=current_user.get("gender"),
            ethnicity=current_user.get("ethnicity"),
            activity_level=current_user.get("activity_level"),
            calorie_goal=current_user.get("calorie_goal"),
            premium_status=current_user.get("premium_status", False),
            onboarding_completed=current_user.get("onboarding_completed", False),
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
        db = create_client(
            settings.supabase_url,
            settings.supabase_service_key,
            options=ClientOptions(
                headers={"Authorization": f"Bearer {current_user['access_token']}"},
            ),
        )
        
        # Prepare update data (only include fields that were provided)
        update_data = {
            k: v for k, v in profile_update.model_dump().items()
            if v is not None
        }
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update profile
        db.table("user_profiles").update(update_data).eq("user_id", current_user["id"]).execute()
        
        # Get updated profile
        result = db.table("user_profiles").select("*").eq("user_id", current_user["id"]).execute()
        profile = result.data[0] if result.data else {}
        
        has_required = all([profile.get("gender"), profile.get("age"), profile.get("height_cm")])
        return UserResponse(
            id=current_user["id"],
            email=current_user["email"],
            full_name=profile.get("full_name"),
            height_cm=profile.get("height_cm"),
            weight_kg=profile.get("weight_kg"),
            target_weight_kg=profile.get("target_weight_kg"),
            age=profile.get("age"),
            gender=profile.get("gender"),
            ethnicity=profile.get("ethnicity"),
            activity_level=profile.get("activity_level"),
            calorie_goal=profile.get("calorie_goal"),
            premium_status=profile.get("premium_status", False),
            onboarding_completed=profile.get("onboarding_completed", has_required),
            created_at=datetime.fromisoformat(profile.get("created_at", datetime.utcnow().isoformat()))
        )
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(request: Request, reset_data: PasswordReset):
    """Request password reset email"""
    try:
        supabase = get_supabase_auth()
        supabase.auth.reset_password_email(reset_data.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a reset link has been sent"}


@router.delete("/account", response_model=AccountDeletionResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """Delete the current user's app account and linked data."""
    return await delete_user_account(current_user)
