import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.requests import Request


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_insert_user_profile_resilient_retries_with_legacy_safe_payload():
    from app.routers.auth import _insert_user_profile_resilient

    insert_chain = MagicMock()
    insert_chain.insert.return_value = insert_chain
    insert_chain.execute.side_effect = [Exception("column consent_terms_at does not exist"), MagicMock(data=[{"ok": True}])]

    supabase = MagicMock()
    supabase.table.return_value = insert_chain

    payload = {
        "user_id": "user-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "premium_status": False,
        "created_at": "2026-03-30T00:00:00Z",
        "onboarding_completed": False,
        "consent_terms_at": "2026-03-30T00:00:00Z",
        "consent_privacy_at": "2026-03-30T00:00:00Z",
        "consent_sensitive_data_at": "2026-03-30T00:00:00Z",
        "consent_age_verified_at": "2026-03-30T00:00:00Z",
        "consent_version": "2026-02-26",
    }

    _insert_user_profile_resilient(supabase, payload)

    assert insert_chain.insert.call_count == 2

    first_payload = insert_chain.insert.call_args_list[0].args[0]
    second_payload = insert_chain.insert.call_args_list[1].args[0]

    assert "consent_terms_at" in first_payload
    assert "consent_terms_at" not in second_payload
    assert "onboarding_completed" not in second_payload
    assert second_payload["user_id"] == "user-123"
    assert second_payload["email"] == "test@example.com"


def test_register_logs_register_completed_with_proof_share_attribution():
    from app.routers.auth import register
    from app.schemas.auth_schemas import UserRegister

    auth_client = MagicMock()
    auth_client.auth.sign_up.return_value = SimpleNamespace(
        user=SimpleNamespace(id="user-123", email="test@example.com"),
        session=SimpleNamespace(access_token="access", refresh_token="refresh", expires_in=3600),
    )

    db = MagicMock()
    share_chain = MagicMock()
    share_chain.select.return_value = share_chain
    share_chain.eq.return_value = share_chain
    share_chain.limit.return_value = share_chain
    share_chain.execute.side_effect = [
        MagicMock(data=[{"id": "share-1", "token": "share-token-123", "status": "active"}]),
        MagicMock(data=[{"id": "funnel-1"}]),
    ]
    db.table.return_value = share_chain

    with (
        patch("app.routers.auth.get_supabase_auth", return_value=auth_client),
        patch("app.routers.auth.get_supabase", return_value=db),
        patch("app.routers.auth._insert_user_profile_resilient"),
        patch("app.routers.auth.log_retention_event", AsyncMock()) as log_event,
    ):
        response = _run(register(
            Request({"type": "http", "method": "POST", "path": "/auth/register", "headers": []}),
            UserRegister(
                email="test@example.com",
                password="password123",
                full_name="Test User",
                gender="male",
                age=29,
                height_cm=180,
                consent_terms=True,
                consent_privacy=True,
                consent_sensitive_data=True,
                consent_age_verification=True,
                attribution_source="proof_share",
                attribution_token="share-token-123",
                attribution_session_id="sess-register-1",
            ),
        ))

    assert response.user.id == "user-123"
    log_event.assert_awaited_once()
    assert log_event.await_args.args[0] == "user-123"
    assert log_event.await_args.args[1] == "register_completed"
    assert log_event.await_args.args[3]["source"] == "proof_share"
    assert log_event.await_args.args[3]["share_token"] == "share-token-123"
    assert log_event.await_args.args[3]["session_id"] == "sess-register-1"


def test_register_drops_unverified_proof_share_attribution():
    from app.routers.auth import register
    from app.schemas.auth_schemas import UserRegister

    auth_client = MagicMock()
    auth_client.auth.sign_up.return_value = SimpleNamespace(
        user=SimpleNamespace(id="user-999", email="test@example.com"),
        session=SimpleNamespace(access_token="access", refresh_token="refresh", expires_in=3600),
    )

    db = MagicMock()
    share_chain = MagicMock()
    share_chain.select.return_value = share_chain
    share_chain.eq.return_value = share_chain
    share_chain.limit.return_value = share_chain
    share_chain.execute.return_value = MagicMock(data=[])
    db.table.return_value = share_chain

    with (
        patch("app.routers.auth.get_supabase_auth", return_value=auth_client),
        patch("app.routers.auth.get_supabase", return_value=db),
        patch("app.routers.auth._insert_user_profile_resilient"),
        patch("app.routers.auth.log_retention_event", AsyncMock()) as log_event,
    ):
        _run(register(
            Request({"type": "http", "method": "POST", "path": "/auth/register", "headers": []}),
            UserRegister(
                email="test@example.com",
                password="password123",
                full_name="Test User",
                gender="male",
                age=29,
                height_cm=180,
                consent_terms=True,
                consent_privacy=True,
                consent_sensitive_data=True,
                consent_age_verification=True,
                attribution_source="proof_share",
                attribution_token="forged-token",
                attribution_session_id="forged-session",
            ),
        ))

    assert log_event.await_args.args[3]["source"] is None
    assert log_event.await_args.args[3]["share_token"] is None
    assert log_event.await_args.args[3]["session_id"] is None


def test_test_login_bootstraps_user_when_sign_in_returns_no_session():
    from app.routers.auth import test_login
    from app.config import settings

    auth_client = MagicMock()
    user = SimpleNamespace(id="user-123", email="e2e@devenira.test")
    session = SimpleNamespace(access_token="access", refresh_token="refresh", expires_in=3600)
    auth_client.auth.sign_in_with_password.side_effect = [
        SimpleNamespace(user=None, session=None),
        SimpleNamespace(user=user, session=session),
    ]

    db = MagicMock()
    query = MagicMock()
    query.select.return_value = query
    query.eq.return_value = query
    query.limit.return_value = query
    query.execute.return_value = MagicMock(data=[])
    db.table.return_value = query

    with (
        patch.object(settings, "enable_test_login", True),
        patch.object(settings, "test_login_email", "e2e@devenira.test"),
        patch.object(settings, "test_login_password", "DeneviraE2E123!"),
        patch("app.routers.auth.get_supabase_auth", return_value=auth_client),
        patch("app.routers.auth.get_supabase", return_value=db),
        patch("app.routers.auth._insert_user_profile_resilient"),
        patch("app.routers.auth._build_token_response", return_value="ok") as build_response,
    ):
        result = _run(test_login())

    assert result == "ok"
    assert auth_client.auth.sign_in_with_password.call_count == 2
    auth_client.auth.admin.create_user.assert_called_once()
    build_response.assert_called_once()
