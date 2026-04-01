import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi import HTTPException


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_get_current_user_returns_fallback_when_profile_lookup_fails():
    from app.middleware.auth_middleware import get_current_user

    auth_client = MagicMock()
    auth_client.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(
            id="user-123",
            email="e2e@devenira.test",
            user_metadata={"full_name": "Denevira E2E", "onboarding_completed": True},
        )
    )

    db_client = MagicMock()
    query = MagicMock()
    query.select.return_value = query
    query.eq.return_value = query
    query.execute.side_effect = Exception("profiles unavailable")
    db_client.table.return_value = query

    with patch("app.middleware.auth_middleware.create_client", side_effect=[auth_client, db_client]):
        current_user = _run(get_current_user("Bearer token-123"))

    assert current_user["id"] == "user-123"
    assert current_user["email"] == "e2e@devenira.test"
    assert current_user["access_token"] == "token-123"
    assert current_user["full_name"] == "Denevira E2E"
    assert current_user["onboarding_completed"] is True


def test_get_current_user_rejects_missing_authorization_header():
    from app.middleware.auth_middleware import get_current_user

    try:
        _run(get_current_user(None))
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Missing authorization header"
    else:
        raise AssertionError("Expected HTTPException for missing authorization header")
