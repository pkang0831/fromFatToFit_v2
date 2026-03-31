from unittest.mock import MagicMock, patch

import pytest


def _result(data):
    mock = MagicMock()
    mock.data = data
    return mock


def _select_chain(results):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.is_.return_value = chain
    chain.order.return_value = chain
    chain.limit.return_value = chain
    chain.execute.side_effect = results
    return chain


def _update_chain():
    chain = MagicMock()
    chain.update.return_value = chain
    chain.eq.return_value = chain
    chain.execute.return_value = _result([])
    return chain


def test_backfill_dry_run_reports_migrations_without_writes():
    from app.services.progress_photo_backfill import backfill_legacy_progress_photos

    legacy_rows = [
        {"id": "photo-1", "user_id": "user-1", "image_base64": "abc", "storage_key": None, "created_at": "2026-03-01T00:00:00Z"},
        {"id": "photo-2", "user_id": "user-1", "image_base64": "def", "storage_key": None, "created_at": "2026-03-02T00:00:00Z"},
    ]

    supabase = MagicMock()
    supabase.table.side_effect = [_select_chain([_result(legacy_rows), _result([])])]

    with patch("app.services.progress_photo_backfill.get_supabase", return_value=supabase):
        summary = backfill_legacy_progress_photos(dry_run=True, batch_size=10)

    assert summary["migrated"] == 2
    assert summary["failures"] == 0
    assert summary["migrated_ids"] == ["photo-1", "photo-2"]
    assert supabase.table.call_count == 1


def test_backfill_uploads_and_nulls_legacy_blob_by_default():
    from app.services.progress_photo_backfill import backfill_legacy_progress_photos

    legacy_rows = [
        {"id": "photo-1", "user_id": "user-1", "image_base64": "abc", "storage_key": None, "created_at": "2026-03-01T00:00:00Z"},
    ]
    select_chain = _select_chain([_result(legacy_rows), _result([])])
    update_chain = _update_chain()
    supabase = MagicMock()
    supabase.table.side_effect = [select_chain, update_chain, select_chain]

    with patch("app.services.progress_photo_backfill.get_supabase", return_value=supabase):
        summary = backfill_legacy_progress_photos(
            batch_size=10,
            upload_fn=lambda user_id, image_base64: {
                "storage_bucket": "progress-photos-private",
                "storage_key": f"{user_id}/photo-1.jpg",
            },
        )

    update_payload = update_chain.update.call_args.args[0]
    assert update_payload["storage_key"] == "user-1/photo-1.jpg"
    assert update_payload["storage_bucket"] == "progress-photos-private"
    assert update_payload["image_base64"] is None
    assert summary["migrated"] == 1
    assert summary["failures"] == 0


def test_backfill_can_keep_legacy_blob_when_requested():
    from app.services.progress_photo_backfill import backfill_legacy_progress_photos

    legacy_rows = [
        {"id": "photo-1", "user_id": "user-1", "image_base64": "abc", "storage_key": None, "created_at": "2026-03-01T00:00:00Z"},
    ]
    select_chain = _select_chain([_result(legacy_rows), _result([])])
    update_chain = _update_chain()
    supabase = MagicMock()
    supabase.table.side_effect = [select_chain, update_chain, select_chain]

    with patch("app.services.progress_photo_backfill.get_supabase", return_value=supabase):
        summary = backfill_legacy_progress_photos(
            batch_size=10,
            keep_legacy=True,
            upload_fn=lambda user_id, image_base64: {
                "storage_bucket": "progress-photos-private",
                "storage_key": f"{user_id}/photo-1.jpg",
            },
        )

    update_payload = update_chain.update.call_args.args[0]
    assert "image_base64" not in update_payload
    assert summary["migrated"] == 1


def test_backfill_tracks_failures_and_continues():
    from app.services.progress_photo_backfill import backfill_legacy_progress_photos

    legacy_rows = [
        {"id": "photo-1", "user_id": "user-1", "image_base64": "abc", "storage_key": None, "created_at": "2026-03-01T00:00:00Z"},
        {"id": "photo-2", "user_id": "user-2", "image_base64": "def", "storage_key": None, "created_at": "2026-03-02T00:00:00Z"},
    ]
    select_chain = _select_chain([_result(legacy_rows), _result([])])
    update_chain = _update_chain()
    supabase = MagicMock()
    supabase.table.side_effect = [select_chain, update_chain, update_chain, select_chain]

    def _upload(user_id, image_base64):
        if user_id == "user-1":
            raise RuntimeError("upload failed")
        return {
            "storage_bucket": "progress-photos-private",
            "storage_key": f"{user_id}/photo.jpg",
        }

    with patch("app.services.progress_photo_backfill.get_supabase", return_value=supabase):
        summary = backfill_legacy_progress_photos(batch_size=10, upload_fn=_upload)

    assert summary["migrated"] == 1
    assert summary["failures"] == 1
    assert summary["failed_ids"] == ["photo-1"]
    assert summary["migrated_ids"] == ["photo-2"]


def test_backfill_validates_arguments():
    from app.services.progress_photo_backfill import backfill_legacy_progress_photos

    with pytest.raises(ValueError):
        backfill_legacy_progress_photos(batch_size=0)

    with pytest.raises(ValueError):
        backfill_legacy_progress_photos(max_photos=0)
