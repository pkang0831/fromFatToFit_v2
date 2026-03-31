import asyncio
from unittest.mock import MagicMock, patch


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


def _mock_chain(execute_results):
    chain = MagicMock()
    chain.select.return_value = chain
    chain.insert.return_value = chain
    chain.delete.return_value = chain
    chain.eq.return_value = chain
    chain.order.return_value = chain
    chain.in_.return_value = chain
    chain.execute.side_effect = execute_results
    return chain


def _user():
    return {"id": "user-123"}


def test_upload_progress_photo_persists_storage_metadata_only():
    from app.routers.progress_photos import upload_progress_photo

    inserted_row = {
        "id": "photo-1",
        "user_id": "user-123",
        "image_base64": None,
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-1.jpg",
        "notes": "Week 1",
        "weight_kg": 81.2,
        "body_fat_pct": 19.4,
        "taken_at": "2026-03-30T12:00:00+00:00",
        "created_at": "2026-03-30T12:00:00+00:00",
    }
    chain = _mock_chain([_result([inserted_row])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with (
        patch("app.routers.progress_photos.get_supabase", return_value=supabase),
        patch(
            "app.routers.progress_photos.upload_progress_image",
            return_value={
                "storage_bucket": "progress-photos-private",
                "storage_key": "user-123/photo-1.jpg",
            },
        ),
        patch(
            "app.routers.progress_photos.build_progress_photo_url",
            return_value="https://signed.example/photo-1",
        ),
    ):
        result = _run(
            upload_progress_photo(
                image_base64="ZmFrZQ==",
                notes="Week 1",
                weight_kg=81.2,
                body_fat_pct=19.4,
                current_user=_user(),
            )
        )

    insert_payload = chain.insert.call_args.args[0]
    assert insert_payload["image_base64"] is None
    assert insert_payload["storage_key"] == "user-123/photo-1.jpg"
    assert result["image_url"] == "https://signed.example/photo-1"


def test_list_progress_photos_returns_signed_urls_for_storage_rows():
    from app.routers.progress_photos import get_progress_photos

    row = {
        "id": "photo-1",
        "notes": "Week 1",
        "weight_kg": 81.2,
        "body_fat_pct": 19.4,
        "taken_at": "2026-03-30T12:00:00+00:00",
        "created_at": "2026-03-30T12:00:00+00:00",
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-1.jpg",
    }
    chain = _mock_chain([_result([row])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with (
        patch("app.routers.progress_photos.get_supabase", return_value=supabase),
        patch(
            "app.routers.progress_photos.build_progress_photo_url",
            return_value="https://signed.example/photo-1",
        ),
    ):
        result = _run(get_progress_photos(current_user=_user()))

    assert result[0]["image_url"] == "https://signed.example/photo-1"
    assert "image_base64" not in result[0]


def test_get_progress_photo_returns_signed_url_for_storage_rows():
    from app.routers.progress_photos import get_progress_photo

    row = {
        "id": "photo-1",
        "user_id": "user-123",
        "image_base64": None,
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-1.jpg",
        "notes": "Week 1",
        "weight_kg": 81.2,
        "body_fat_pct": 19.4,
        "taken_at": "2026-03-30T12:00:00+00:00",
        "created_at": "2026-03-30T12:00:00+00:00",
    }
    chain = _mock_chain([_result([row])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with (
        patch("app.routers.progress_photos.get_supabase", return_value=supabase),
        patch(
            "app.routers.progress_photos.build_progress_photo_url",
            return_value="https://signed.example/photo-1",
        ),
    ):
        result = _run(get_progress_photo("photo-1", current_user=_user()))

    assert result["image_url"] == "https://signed.example/photo-1"
    assert result.get("image_base64") is None


def test_compare_progress_photos_returns_ordered_signed_urls_and_metrics():
    from app.routers.progress_photos import compare_photos

    older = {
        "id": "photo-1",
        "user_id": "user-123",
        "image_base64": None,
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-1.jpg",
        "notes": "Week 1",
        "weight_kg": 82.0,
        "body_fat_pct": 20.0,
        "taken_at": "2026-03-01T12:00:00+00:00",
        "created_at": "2026-03-01T12:00:00+00:00",
    }
    newer = {
        "id": "photo-2",
        "user_id": "user-123",
        "image_base64": None,
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-2.jpg",
        "notes": "Week 5",
        "weight_kg": 79.5,
        "body_fat_pct": 17.5,
        "taken_at": "2026-03-29T12:00:00+00:00",
        "created_at": "2026-03-29T12:00:00+00:00",
    }
    chain = _mock_chain([_result([newer, older])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with (
        patch("app.routers.progress_photos.get_supabase", return_value=supabase),
        patch(
            "app.routers.progress_photos.build_progress_photo_url",
            side_effect=[
                "https://signed.example/photo-1",
                "https://signed.example/photo-2",
            ],
        ),
    ):
        result = _run(compare_photos("photo-1", "photo-2", current_user=_user()))

    assert result["before"]["id"] == "photo-1"
    assert result["before"]["image_url"] == "https://signed.example/photo-1"
    assert result["after"]["image_url"] == "https://signed.example/photo-2"
    assert result["days_between"] == 28
    assert result["weight_change"] == -2.5
    assert result["bf_change"] == -2.5


def test_delete_progress_photo_removes_storage_then_row():
    from app.routers.progress_photos import delete_progress_photo

    existing = {
        "id": "photo-1",
        "storage_bucket": "progress-photos-private",
        "storage_key": "user-123/photo-1.jpg",
    }
    chain = _mock_chain([_result([existing]), _result([])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with (
        patch("app.routers.progress_photos.get_supabase", return_value=supabase),
        patch("app.routers.progress_photos.delete_progress_image") as delete_storage,
    ):
        result = _run(delete_progress_photo("photo-1", current_user=_user()))

    delete_storage.assert_called_once_with("user-123/photo-1.jpg", "progress-photos-private")
    assert chain.delete.called
    assert result == {"message": "Photo deleted"}


def test_get_progress_photo_legacy_row_returns_data_url_fallback():
    from app.routers.progress_photos import get_progress_photo

    row = {
        "id": "legacy-photo",
        "user_id": "user-123",
        "image_base64": "bGVnYWN5",
        "storage_bucket": None,
        "storage_key": None,
        "notes": "Legacy",
        "weight_kg": None,
        "body_fat_pct": None,
        "taken_at": "2026-03-30T12:00:00+00:00",
        "created_at": "2026-03-30T12:00:00+00:00",
    }
    chain = _mock_chain([_result([row])])
    supabase = MagicMock()
    supabase.table.return_value = chain

    with patch("app.routers.progress_photos.get_supabase", return_value=supabase):
        result = _run(get_progress_photo("legacy-photo", current_user=_user()))

    assert result["image_url"] == "data:image/jpeg;base64,bGVnYWN5"
    assert result["image_base64"] == "bGVnYWN5"
