from fastapi import HTTPException, status

def is_openai_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "openai_api_key" in message
        or ("api key" in message and "openai" in message)
        or "api_key" in message
        or ("openai" in message and ("unauthorized" in message or "connection" in message or "timeout" in message))
    )


def is_hf_or_body_model_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "hugging face",
            "huggingface",
            "hf_token",
            "snapshot_download",
            "fashn-human-parser",
            "could not download",
            "localentrynotfounderror",
        )
    )


def is_stripe_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "stripe" in message
        or "api.stripe.com" in message
        or "ssl certificate" in message
    )


def is_admin_auth_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "requires a valid bearer token" in message
        or "auth/v1/admin/users" in message
    )


def is_proof_share_storage_unavailable(exc: Exception) -> bool:
    message = str(exc).lower()
    return (
        "proof_shares" in message
        and ("row-level security" in message or "does not exist" in message or "relation" in message)
    )


def ai_service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def payment_service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def body_model_service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def admin_service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


def proof_share_service_unavailable(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
