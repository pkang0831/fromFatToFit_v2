from types import SimpleNamespace
from unittest.mock import MagicMock


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
