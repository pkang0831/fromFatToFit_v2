from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from fastapi import HTTPException, status

from ..database import get_supabase
from .body_photo_quality import BodyPhotoQualityResult

logger = logging.getLogger(__name__)


@dataclass
class BodyImageModerationDecision:
    allowed: bool
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def _block(
    code: str,
    message: str,
    *,
    route_name: str,
    source: str,
    user_id: str | None,
    details: dict[str, Any] | None = None,
) -> None:
    payload = {
        "error": "body_image_moderation",
        "code": code,
        "message": message,
        "messages": [message],
    }
    if details:
        payload["details"] = details

    logger.warning(
        "body_image_moderation blocked route=%s source=%s user_id=%s code=%s details=%s",
        route_name,
        source,
        user_id or "guest",
        code,
        details or {},
    )
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=payload,
    )


def _log_allow(
    *,
    route_name: str,
    source: str,
    user_id: str | None,
    details: dict[str, Any] | None = None,
) -> None:
    logger.info(
        "body_image_moderation allowed route=%s source=%s user_id=%s details=%s",
        route_name,
        source,
        user_id or "guest",
        details or {},
    )


def _get_user_moderation_profile(user_id: str) -> dict[str, Any]:
    supabase = get_supabase()
    result = (
        supabase.table("user_profiles")
        .select(
            "user_id, age, consent_terms_at, consent_privacy_at, "
            "consent_sensitive_data_at, consent_age_verified_at"
        )
        .eq("user_id", user_id)
        .execute()
    )
    rows = result.data or []
    return rows[0] if rows else {"user_id": user_id}


async def enforce_body_image_moderation(
    *,
    route_name: str,
    source: str,
    quality_result: BodyPhotoQualityResult,
    user_id: str | None = None,
    ownership_confirmed: bool = False,
    adult_confirmed: bool = False,
    stated_age: int | None = None,
) -> BodyImageModerationDecision:
    details = {
        "ownership_confirmed": ownership_confirmed,
        "adult_confirmed": adult_confirmed,
        "stated_age": stated_age,
        "foreground_component_count": quality_result.foreground_component_count,
        "multiple_subjects_detected": quality_result.multiple_subjects_detected,
    }

    if quality_result.multiple_subjects_detected:
        _block(
            "multiple_people_detected",
            (
                "Upload one clear photo of a single adult subject only. "
                "We do not send ambiguous or multi-person body photos to AI vendors."
            ),
            route_name=route_name,
            source=source,
            user_id=user_id,
            details=details,
        )

    if source == "guest":
        if stated_age is None or stated_age < 18 or not adult_confirmed:
            _block(
                "adult_confirmation_required",
                "Guest body scans require an 18+ confirmation before analysis.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details=details,
            )
        if not ownership_confirmed:
            _block(
                "ownership_confirmation_required",
                "Confirm that this is your own photo before requesting analysis.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details=details,
            )
    else:
        if not user_id:
            _block(
                "missing_user_context",
                "Could not verify the account attached to this upload.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details=details,
            )

        profile = _get_user_moderation_profile(user_id)
        required_consent_fields = (
            "consent_terms_at",
            "consent_privacy_at",
            "consent_sensitive_data_at",
            "consent_age_verified_at",
        )
        missing_consents = [field for field in required_consent_fields if not profile.get(field)]
        if missing_consents:
            _block(
                "sensitive_data_consent_required",
                "Sensitive-image consent is missing on this account. Complete consent before uploading body photos.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details={**details, "missing_consents": missing_consents},
            )

        profile_age = profile.get("age")
        if profile_age is not None and int(profile_age) < 18:
            _block(
                "adult_account_required",
                "Accounts marked under 18 cannot upload body images for AI analysis.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details={**details, "profile_age": profile_age},
            )

        if not ownership_confirmed:
            _block(
                "ownership_confirmation_required",
                "Confirm that this is your own photo before sending it for AI analysis.",
                route_name=route_name,
                source=source,
                user_id=user_id,
                details=details,
            )

    decision = BodyImageModerationDecision(
        allowed=True,
        code="allowed",
        message="Upload passed first-party moderation checks.",
        details=details,
    )
    _log_allow(
        route_name=route_name,
        source=source,
        user_id=user_id,
        details=decision.details,
    )
    return decision
