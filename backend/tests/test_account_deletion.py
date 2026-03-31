import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _result(data):
    mock = MagicMock()
    mock.data = data
    return mock


def _progress_chain(data):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.execute.return_value = _result(data)
    return chain


def test_delete_user_account_cleans_progress_photo_storage_and_deletes_auth_user():
    from app.services.account_deletion import delete_user_account

    progress_chain = _progress_chain([
        {"storage_bucket": "progress-photos-private", "storage_key": "user-1/photo-1.jpg"},
        {"storage_bucket": None, "storage_key": "user-1/photo-2.jpg"},
        {"storage_bucket": "progress-photos-private", "storage_key": None},
    ])

    storage_bucket = MagicMock()
    auth_admin = MagicMock()
    supabase = MagicMock()
    supabase.table.side_effect = lambda table_name: {
        "progress_photos": progress_chain,
    }[table_name]
    supabase.storage.from_.return_value = storage_bucket
    supabase.auth.admin = auth_admin

    with (
        patch("app.services.account_deletion.get_supabase", return_value=supabase),
        patch(
            "app.services.account_deletion.get_subscription_diagnostics",
            AsyncMock(return_value={"deletion_blocked": False}),
        ),
    ):
        result = _run(delete_user_account({"id": "user-1", "premium_status": False}))

    assert storage_bucket.remove.call_count == 1
    storage_bucket.remove.assert_called_once_with(["user-1/photo-1.jpg", "user-1/photo-2.jpg"])
    auth_admin.delete_user.assert_called_once_with("user-1", should_soft_delete=False)
    assert "Stored progress photo files" in result["deleted_immediately"][2]


def test_delete_user_account_blocks_when_subscription_row_is_active():
    from app.services.account_deletion import delete_user_account

    progress_chain = _progress_chain([])

    storage_bucket = MagicMock()
    auth_admin = MagicMock()
    supabase = MagicMock()
    supabase.table.side_effect = lambda table_name: {
        "progress_photos": progress_chain,
    }[table_name]
    supabase.storage.from_.return_value = storage_bucket
    supabase.auth.admin = auth_admin

    with (
        patch("app.services.account_deletion.get_supabase", return_value=supabase),
        patch(
            "app.services.account_deletion.get_subscription_diagnostics",
            AsyncMock(return_value={
                "deletion_blocked": True,
                "deletion_block_reason": "active_billing_requires_cancellation",
            }),
        ),
    ):
        with pytest.raises(Exception) as exc_info:
            _run(delete_user_account({"id": "user-1", "premium_status": False}))

    assert getattr(exc_info.value, "status_code", None) == 409
    auth_admin.delete_user.assert_not_called()
    storage_bucket.remove.assert_not_called()

def test_delete_user_account_blocks_when_billing_state_is_mismatched():
    from app.services.account_deletion import delete_user_account

    progress_chain = _progress_chain([])

    supabase = MagicMock()
    supabase.table.side_effect = lambda table_name: {
        "progress_photos": progress_chain,
    }[table_name]

    with (
        patch("app.services.account_deletion.get_supabase", return_value=supabase),
        patch(
            "app.services.account_deletion.get_subscription_diagnostics",
            AsyncMock(return_value={
                "deletion_blocked": True,
                "deletion_block_reason": "billing_state_mismatch_requires_reconciliation",
            }),
        ),
    ):
        with pytest.raises(Exception) as exc_info:
            _run(delete_user_account({"id": "user-1", "premium_status": False}))

    assert getattr(exc_info.value, "status_code", None) == 409
    assert "Manage billing first" in str(getattr(exc_info.value, "detail", ""))


def test_delete_user_account_stops_if_storage_cleanup_fails():
    from app.services.account_deletion import delete_user_account

    progress_chain = _progress_chain([
        {"storage_bucket": "progress-photos-private", "storage_key": "user-1/photo-1.jpg"},
    ])

    storage_bucket = MagicMock()
    storage_bucket.remove.side_effect = RuntimeError("storage down")
    auth_admin = MagicMock()
    supabase = MagicMock()
    supabase.table.side_effect = lambda table_name: {
        "progress_photos": progress_chain,
    }[table_name]
    supabase.storage.from_.return_value = storage_bucket
    supabase.auth.admin = auth_admin

    with (
        patch("app.services.account_deletion.get_supabase", return_value=supabase),
        patch(
            "app.services.account_deletion.get_subscription_diagnostics",
            AsyncMock(return_value={"deletion_blocked": False}),
        ),
    ):
        with pytest.raises(Exception) as exc_info:
            _run(delete_user_account({"id": "user-1", "premium_status": False}))

    assert getattr(exc_info.value, "status_code", None) == 500
    auth_admin.delete_user.assert_not_called()
