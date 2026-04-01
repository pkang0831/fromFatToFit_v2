import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.requests import Request


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
        self._operation = "select"
        self._payload = None

    def select(self, *_args, **_kwargs):
        self._operation = "select"
        return self

    def insert(self, payload):
        self._operation = "insert"
        self._payload = payload
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def contains(self, key, value):
        self.filters.append(
            lambda row, k=key, v=value: all((row.get(k) or {}).get(inner_key) == inner_value for inner_key, inner_value in v.items())
        )
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

        if self._operation == "insert":
            records = self._payload if isinstance(self._payload, list) else [self._payload]
            inserted = []
            for record in records:
                row = dict(record)
                row.setdefault("id", f"{self.name}-{len(rows) + 1}")
                rows.append(row)
                inserted.append(dict(row))
            self._reset()
            return _Result(inserted)

        matched = [dict(row) for row in rows if all(check(row) for check in self.filters)]
        if self._order_key:
            matched.sort(key=lambda row: row.get(self._order_key) or "", reverse=self._order_desc)
        if self._limit is not None:
            matched = matched[:self._limit]
        self._reset()
        return _Result(matched)


class _FakeSupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _FakeTable(self, name)


def test_log_retention_event_persists_append_only_funnel_row():
    from app.services.retention_event_service import log_retention_event

    supabase = _FakeSupabase({"funnel_events": []})

    with patch("app.services.retention_event_service.get_supabase", return_value=supabase):
        event = _run(log_retention_event(
            None,
            "share_viewed",
            "proof_share_public",
            {
                "source": "proof_share",
                "share_token": "share-token-1",
                "session_id": "sess-proof-1",
                "entry_state": "review_progress",
            },
        ))

    assert event["source"] == "proof_share"
    assert event["share_token"] == "share-token-1"
    assert event["session_id"] == "sess-proof-1"
    assert len(supabase.tables["funnel_events"]) == 1
    row = supabase.tables["funnel_events"][0]
    assert row["user_id"] is None
    assert row["event_name"] == "share_viewed"
    assert row["surface"] == "proof_share_public"
    assert row["source"] == "proof_share"
    assert row["session_id"] == "sess-proof-1"
    assert row["share_token"] == "share-token-1"
    assert row["entry_state"] == "review_progress"


def test_funnel_summary_endpoints_read_expected_views():
    from app.routers.retention_analytics import (
        get_daily_funnel_snapshot,
        get_entry_state_performance,
        get_reminder_open_to_proof,
        get_share_view_to_register,
        get_weekly_cohort_by_source,
    )

    supabase = _FakeSupabase({
        "analytics_daily_funnel_snapshot": [{"snapshot_date": "2026-03-31", "scan_success_count": 3}],
        "analytics_weekly_cohort_by_source": [{"cohort_week": "2026-03-30", "source": "weekly_reminder", "scan_successes": 2}],
        "analytics_entry_state_performance": [{"entry_state": "progress_proof", "source": "weekly_reminder", "reengagement_sessions": 4}],
        "analytics_reminder_open_to_proof": [{"opened_date": "2026-03-31", "reminder_opens": 2, "proof_uploads_after_open": 1}],
        "analytics_share_view_to_try_to_register": [{"share_token": "share-token-1", "share_views": 5, "try_starts": 2, "register_completions": 1}],
    })

    fake_settings = type("Settings", (), {"is_production": False, "analytics_admin_emails_list": []})()

    with (
        patch("app.services.retention_event_service.get_supabase", return_value=supabase),
        patch("app.routers.retention_analytics.settings", fake_settings),
    ):
        assert _run(get_daily_funnel_snapshot({"id": "user-1"}))[0]["scan_success_count"] == 3
        assert _run(get_weekly_cohort_by_source({"id": "user-1"}))[0]["source"] == "weekly_reminder"
        assert _run(get_entry_state_performance({"id": "user-1"}))[0]["entry_state"] == "progress_proof"
        assert _run(get_reminder_open_to_proof({"id": "user-1"}))[0]["proof_uploads_after_open"] == 1
        share_row = _run(get_share_view_to_register({"id": "user-1"}))[0]

    assert share_row["register_completions"] == 1
    assert "share_token" not in share_row
    assert share_row["share_token_preview"] == "share-...en-1"


def test_capture_retention_event_rejects_server_truth_events_from_clients():
    from fastapi import HTTPException
    from app.routers.retention_analytics import capture_retention_event
    from app.schemas.home_schemas import RetentionEventRequest

    request = RetentionEventRequest(
        event_name="purchase_completed",
        surface="progress_page",
        properties={},
    )

    try:
        _run(capture_retention_event(request, {"id": "user-1", "email": "user@example.com"}))
    except HTTPException as exc:
        assert exc.status_code == 403
        assert "server-side" in exc.detail
    else:
        raise AssertionError("Expected capture_retention_event to reject server-truth event names")


def test_funnel_views_require_admin_access_in_production():
    from fastapi import HTTPException
    from app.routers.retention_analytics import get_daily_funnel_snapshot

    fake_settings = type("Settings", (), {"is_production": True, "analytics_admin_emails_list": ["ops@devenira.com"]})()

    with patch("app.routers.retention_analytics.settings", fake_settings):
        try:
            _run(get_daily_funnel_snapshot({"id": "user-1", "email": "member@example.com"}))
        except HTTPException as exc:
            assert exc.status_code == 403
        else:
            raise AssertionError("Expected analytics endpoint to reject non-admin user in production")


def test_log_retention_event_dedupes_on_dedupe_key():
    from app.services.retention_event_service import log_retention_event

    supabase = _FakeSupabase({"funnel_events": []})

    with patch("app.services.retention_event_service.get_supabase", return_value=supabase):
        _run(log_retention_event(
            "user-1",
            "purchase_completed",
            "revenuecat_verification",
            {"dedupe_key": "purchase:user-1:sub-1"},
        ))
        _run(log_retention_event(
            "user-1",
            "purchase_completed",
            "revenuecat_verification",
            {"dedupe_key": "purchase:user-1:sub-1"},
        ))

    assert len(supabase.tables["funnel_events"]) == 1


def test_calculate_body_percentile_logs_scan_success_with_weekly_reminder_context():
    from app.routers.body import calculate_body_percentile
    from app.schemas.body_schemas import BodyScanRequest

    supabase = _FakeSupabase({"body_scans": []})
    log_event = AsyncMock()

    with (
        patch("app.routers.body._require_safe_body_photo", AsyncMock()),
        patch("app.routers.body.check_premium_status", AsyncMock(return_value=False)),
        patch("app.routers.body.check_usage_limit", AsyncMock(return_value={"remaining": 1})),
        patch("app.routers.body.estimate_body_fat_with_fallback", AsyncMock(return_value={"body_fat_percentage": 18.2, "confidence": "high"})),
        patch("app.routers.body.calculate_percentile", return_value={
            "percentile": 72.0,
            "rank_text": "top 28%",
            "comparison_group": "men 25-34",
            "distribution_data": {"mean": 20.0},
        }),
        patch("app.routers.body.get_supabase", return_value=supabase),
        patch("app.routers.body.increment_usage", AsyncMock()),
        patch("app.routers.body.log_retention_event", log_event),
    ):
        response = _run(calculate_body_percentile(
            Request({"type": "http", "method": "POST", "path": "/body/percentile", "headers": []}),
            BodyScanRequest(
                image_base64="abc",
                scan_type="percentile",
                gender="male",
                age=29,
                ethnicity="asian",
                source="weekly_reminder",
                session_id="sess-body-1",
                ownership_confirmed=True,
            ),
            {"id": "user-1"},
        ))

    assert response.percentile_data.body_fat_percentage == 18.2
    assert len(supabase.tables["body_scans"]) == 1
    log_event.assert_awaited_once()
    assert log_event.await_args.args[1] == "scan_success"
    assert log_event.await_args.args[3]["source"] == "weekly_reminder"
    assert log_event.await_args.args[3]["session_id"] == "sess-body-1"
    assert log_event.await_args.args[3]["entry_state"] == "weekly_scan"


def test_proof_loop_analytics_sql_defines_required_views_and_attribution_filters():
    sql = (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "sql"
        / "ADD_PROOF_LOOP_ANALYTICS.sql"
    ).read_text()

    assert "CREATE TABLE IF NOT EXISTS funnel_events" in sql
    assert "CREATE OR REPLACE VIEW analytics_daily_funnel_snapshot AS" in sql
    assert "CREATE OR REPLACE VIEW analytics_weekly_cohort_by_source AS" in sql
    assert "CREATE OR REPLACE VIEW analytics_entry_state_performance AS" in sql
    assert "CREATE OR REPLACE VIEW analytics_reminder_open_to_proof AS" in sql
    assert "CREATE OR REPLACE VIEW analytics_share_view_to_try_to_register AS" in sql
    assert "event_name = 'notification_opened'" in sql
    assert "source = 'weekly_reminder'" in sql
    assert "event_name = 'share_viewed'" in sql
    assert "event_name = 'referred_try_started'" in sql
    assert "event_name = 'register_completed'" in sql
