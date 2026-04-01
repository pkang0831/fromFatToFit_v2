import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class _Result:
    def __init__(self, data):
        self.data = data


class _FakeTable:
    def __init__(self, supabase, name):
        self.supabase = supabase
        self.name = name
        self._reset()

    def _reset(self):
        self.filters = []
        self._limit = None
        self._order_key = None
        self._order_desc = False
        self._op = "select"
        self._payload = None

    def select(self, *_args, **_kwargs):
        self._op = "select"
        return self

    def insert(self, payload):
        self._op = "insert"
        self._payload = dict(payload)
        return self

    def update(self, payload):
        self._op = "update"
        self._payload = dict(payload)
        return self

    def delete(self):
        self._op = "delete"
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def order(self, key, desc=False):
        self._order_key = key
        self._order_desc = desc
        return self

    def limit(self, value):
        self._limit = value
        return self

    def execute(self):
        rows = self.supabase.tables.setdefault(self.name, [])
        matched = [row for row in rows if all(check(row) for check in self.filters)]

        if self._op == "insert":
            row = dict(self._payload)
            row.setdefault("id", f"{self.name}-{len(rows) + 1}")
            rows.append(row)
            self._reset()
            return _Result([dict(row)])

        if self._op == "update":
            updated = []
            for row in rows:
                if all(check(row) for check in self.filters):
                    row.update(self._payload)
                    updated.append(dict(row))
            self._reset()
            return _Result(updated)

        if self._op == "delete":
            remaining = []
            deleted = []
            for row in rows:
                if all(check(row) for check in self.filters):
                    deleted.append(dict(row))
                else:
                    remaining.append(row)
            self.supabase.tables[self.name] = remaining
            self._reset()
            return _Result(deleted)

        if self._order_key:
            matched.sort(key=lambda row: row.get(self._order_key) or "", reverse=self._order_desc)
        if self._limit is not None:
            matched = matched[:self._limit]
        self._reset()
        return _Result([dict(row) for row in matched])


class _FakeSupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _FakeTable(self, name)


class _FakeHttpxResponse:
    def __init__(self, content=b"image-bytes", media_type="image/png"):
        self.content = content
        self.status_code = 200
        self.headers = {"content-type": media_type}


class _FakeAsyncClient:
    def __init__(self, response):
        self.response = response
        self.requested_url = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        self.requested_url = url
        return self.response


def _base_tables():
    return {
        "user_profiles": [{
            "user_id": "user-1",
            "target_body_fat_percentage": 14.0,
        }],
        "body_scans": [{
            "user_id": "user-1",
            "scan_type": "bodyfat",
            "created_at": "2026-03-30T12:00:00+00:00",
            "result_data": {"body_fat_percentage": 18.4},
        }],
        "progress_photos": [{
            "id": "photo-1",
            "user_id": "user-1",
            "taken_at": "2026-03-31T12:00:00+00:00",
            "weight_kg": 81.2,
            "body_fat_pct": 18.1,
            "storage_bucket": "progress-photos-private",
            "storage_key": "user-1/photo-1.jpg",
            "image_base64": None,
        }],
        "proof_shares": [],
    }


def test_create_and_revoke_proof_share_flow():
    from app.routers.proof_shares import create_proof_share, list_proof_shares, revoke_proof_share
    from app.schemas.proof_share_schemas import CreateProofShareRequest

    supabase = _FakeSupabase(_base_tables())
    log_event = AsyncMock()

    with (
        patch("app.routers.proof_shares.get_supabase", return_value=supabase),
        patch("app.routers.proof_shares.log_retention_event", log_event),
        patch("app.routers.proof_shares.token_urlsafe", return_value="token-123"),
    ):
        created = _run(create_proof_share(
            CreateProofShareRequest(
                progress_photo_id="photo-1",
                week_marker=4,
                session_id="sess-share-1",
                source="weekly_reminder",
                reentry_state="weekly_scan",
                surface_state="progress_proof",
                reminder_event_id="rem-1",
            ),
            {"id": "user-1"},
        ))
        shares = _run(list_proof_shares(current_user={"id": "user-1"}))
        revoked = _run(revoke_proof_share("proof_shares-1", {"id": "user-1"}))

    assert created.token == "token-123"
    assert created.public_url.endswith("/proof/token-123")
    assert created.image_url.endswith("/api/proof-shares/public/token-123/image")
    assert len(shares) == 1
    assert shares[0].status == "active"
    assert revoked == {"message": "Share revoked"}
    assert supabase.tables["proof_shares"][0]["status"] == "revoked"
    assert log_event.await_count == 2
    assert log_event.await_args_list[0].args[1] == "share_created"
    assert log_event.await_args_list[0].args[3]["session_id"] == "sess-share-1"
    assert log_event.await_args_list[0].args[3]["source"] == "weekly_reminder"
    assert log_event.await_args_list[0].args[3]["reentry_state"] == "weekly_scan"
    assert log_event.await_args_list[0].args[3]["surface_state"] == "progress_proof"
    assert log_event.await_args_list[0].args[3]["reminder_event_id"] == "rem-1"
    assert log_event.await_args_list[1].args[1] == "share_revoked"


def test_public_share_view_returns_proxy_image_and_logs_view():
    from app.routers.proof_shares import get_public_proof_share

    tables = _base_tables()
    tables["proof_shares"] = [{
        "id": "share-1",
        "user_id": "user-1",
        "progress_photo_id": "photo-1",
        "token": "public-token",
        "week_marker": 5,
        "status": "active",
        "created_at": "2026-03-31T12:00:00+00:00",
        "revoked_at": None,
        "current_bf_snapshot": 18.4,
        "target_bf_snapshot": 14.0,
        "goal_gap_snapshot": 4.4,
        "shared_photo_taken_at": "2026-03-31T12:00:00+00:00",
        "shared_photo_weight_kg": 81.2,
        "shared_photo_body_fat_pct": 18.1,
    }]
    supabase = _FakeSupabase(tables)
    log_event = AsyncMock()

    with (
        patch("app.routers.proof_shares.get_supabase", return_value=supabase),
        patch("app.routers.proof_shares.log_retention_event", log_event),
    ):
        result = _run(get_public_proof_share("public-token", session_id="anon-session-1"))

    assert result.token == "public-token"
    assert result.image_url.endswith("/api/proof-shares/public/public-token/image")
    assert "signed.example" not in result.image_url
    assert result.referred_try_url.endswith("/api/proof-shares/public/public-token/try")
    assert log_event.await_count == 1
    assert log_event.await_args.args[0] is None
    assert log_event.await_args.args[1] == "share_viewed"
    assert log_event.await_args.args[3]["session_id"] == "anon-session-1"
    assert log_event.await_args.args[3]["source"] == "proof_share"
    assert log_event.await_args.args[3]["share_token"] == "public-token"


def test_revoked_token_denies_anonymous_access():
    from app.routers.proof_shares import get_public_proof_share

    tables = _base_tables()
    tables["proof_shares"] = [{
        "id": "share-1",
        "user_id": "user-1",
        "progress_photo_id": "photo-1",
        "token": "revoked-token",
        "status": "revoked",
        "created_at": "2026-03-31T12:00:00+00:00",
        "revoked_at": "2026-03-31T13:00:00+00:00",
    }]
    supabase = _FakeSupabase(tables)

    with patch("app.routers.proof_shares.get_supabase", return_value=supabase):
        try:
            _run(get_public_proof_share("revoked-token"))
            assert False, "expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 404


def test_deleted_asset_denies_public_share_access():
    from app.routers.proof_shares import get_public_proof_share

    tables = _base_tables()
    tables["progress_photos"] = []
    tables["proof_shares"] = [{
        "id": "share-1",
        "user_id": "user-1",
        "progress_photo_id": "photo-1",
        "token": "missing-asset",
        "status": "active",
        "created_at": "2026-03-31T12:00:00+00:00",
        "revoked_at": None,
    }]
    supabase = _FakeSupabase(tables)

    with patch("app.routers.proof_shares.get_supabase", return_value=supabase):
        try:
            _run(get_public_proof_share("missing-asset"))
            assert False, "expected HTTPException"
        except HTTPException as exc:
            assert exc.status_code == 404


def test_public_image_proxy_hides_private_signed_url():
    from app.routers.proof_shares import get_public_proof_share_image

    tables = _base_tables()
    tables["proof_shares"] = [{
        "id": "share-1",
        "user_id": "user-1",
        "progress_photo_id": "photo-1",
        "token": "image-token",
        "status": "active",
        "created_at": "2026-03-31T12:00:00+00:00",
        "revoked_at": None,
    }]
    supabase = _FakeSupabase(tables)
    fake_client = _FakeAsyncClient(_FakeHttpxResponse())

    with (
        patch("app.routers.proof_shares.get_supabase", return_value=supabase),
        patch("app.routers.proof_shares.build_progress_photo_url", return_value="https://signed.example/private-photo"),
        patch("app.routers.proof_shares.httpx.AsyncClient", return_value=fake_client),
    ):
        response = _run(get_public_proof_share_image("image-token"))

    assert response.media_type == "image/png"
    assert response.body == b"image-bytes"
    assert fake_client.requested_url == "https://signed.example/private-photo"


def test_referred_try_redirect_logs_event():
    from app.routers.proof_shares import start_referred_try

    tables = _base_tables()
    tables["proof_shares"] = [{
        "id": "share-1",
        "user_id": "user-1",
        "progress_photo_id": "photo-1",
        "token": "try-token",
        "status": "active",
        "created_at": "2026-03-31T12:00:00+00:00",
        "revoked_at": None,
    }]
    supabase = _FakeSupabase(tables)
    log_event = AsyncMock()

    with (
        patch("app.routers.proof_shares.get_supabase", return_value=supabase),
        patch("app.routers.proof_shares.log_retention_event", log_event),
    ):
        response = _run(start_referred_try("try-token", session_id="anon-session-2"))

    assert response.status_code == 307
    assert response.headers["location"].endswith("/try?source=proof_share&share_token=try-token&session_id=anon-session-2")
    assert log_event.await_args.args[0] is None
    assert log_event.await_args.args[1] == "referred_try_started"
    assert log_event.await_args.args[3]["session_id"] == "anon-session-2"
    assert log_event.await_args.args[3]["source"] == "proof_share"
    assert log_event.await_args.args[3]["share_token"] == "try-token"
