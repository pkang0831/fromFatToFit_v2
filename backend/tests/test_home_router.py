import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch


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
        self._payload = dict(payload)
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def in_(self, key, values):
        accepted = set(values)
        self.filters.append(lambda row, k=key, allowed=accepted: row.get(k) in allowed)
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
            row = dict(self._payload)
            row.setdefault("id", f"{self.name}-{len(rows) + 1}")
            rows.append(row)
            self._reset()
            return _Result([dict(row)])

        rows = [
            dict(row)
            for row in self.supabase.tables.get(self.name, [])
            if all(check(row) for check in self.filters)
        ]
        if self._order_key:
            rows.sort(key=lambda row: row.get(self._order_key) or "", reverse=self._order_desc)
        if self._limit is not None:
            rows = rows[:self._limit]
        self._reset()
        return _Result(rows)


class _FakeSupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _FakeTable(self, name)


def _iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def test_home_summary_defaults_to_plan_setup_for_empty_user():
    from app.routers.home import get_home_summary

    supabase = _FakeSupabase({
        "user_profiles": [{"user_id": "user-1", "target_body_fat_percentage": None, "goal_image_url": None}],
        "saved_goal_plans": [],
        "body_scans": [],
        "progress_photos": [],
        "seven_day_challenges": [],
        "seven_day_checkins": [],
    })

    with patch("app.routers.home.get_supabase", return_value=supabase):
        summary = _run(get_home_summary({"id": "user-1"}))

    assert summary.entry_state == "plan_setup"
    assert summary.primary_cta.href == "/goal-planner"
    assert summary.goal_summary.has_saved_plan is False
    assert summary.scan_summary.scan_count == 0
    assert summary.progress_summary.photo_count == 0


def test_home_summary_surfaces_weekly_scan_and_progress_context():
    from app.routers.home import get_home_summary

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-1",
            "target_body_fat_percentage": 14.0,
            "goal_image_url": "https://cdn.test/goal.jpg",
        }],
        "saved_goal_plans": [{
            "user_id": "user-1",
            "updated_at": _iso_days_ago(2),
            "plan_data": {
                "selectedTier": 1,
                "tierData": {"tiers": [{"daily_calories": 2300}, {"daily_calories": 2100}]},
                "goals": {"targetBf": 14},
            },
        }],
        "body_scans": [
            {
                "user_id": "user-1",
                "scan_type": "bodyfat",
                "created_at": _iso_days_ago(8),
                "result_data": {"body_fat_percentage": 19.5},
            },
            {
                "user_id": "user-1",
                "id": "scan-transform-1",
                "scan_type": "transformation",
                "created_at": _iso_days_ago(3),
                "result_data": {"target_bf_reduction": 5},
                "image_url": "https://cdn.test/transformation.jpg",
            },
        ],
        "progress_photos": [
            {"user_id": "user-1", "taken_at": _iso_days_ago(1)},
            {"user_id": "user-1", "taken_at": _iso_days_ago(10)},
        ],
        "seven_day_challenges": [],
        "seven_day_checkins": [],
    })

    with patch("app.routers.home.get_supabase", return_value=supabase):
        summary = _run(get_home_summary({"id": "user-1"}))

    assert summary.entry_state == "weekly_scan"
    assert summary.goal_summary.gap == 5.5
    assert summary.goal_summary.selected_tier_calories == 2100
    assert summary.scan_summary.prompt_state == "ready"
    assert summary.scan_summary.latest_transformation is not None
    assert summary.scan_summary.latest_transformation.id == "scan-transform-1"
    assert summary.progress_summary.photo_count == 2
    assert summary.progress_summary.compare_ready is True


def test_home_summary_progress_proof_cta_routes_to_upload_focus():
    from app.routers.home import get_home_summary

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-1",
            "target_body_fat_percentage": 14.0,
            "goal_image_url": "https://cdn.test/goal.jpg",
        }],
        "saved_goal_plans": [{
            "user_id": "user-1",
            "updated_at": _iso_days_ago(2),
            "plan_data": {"goals": {"targetBf": 14}},
        }],
        "body_scans": [
            {
                "user_id": "user-1",
                "scan_type": "bodyfat",
                "created_at": _iso_days_ago(2),
                "result_data": {"body_fat_percentage": 19.5},
            },
        ],
        "progress_photos": [],
        "seven_day_challenges": [],
        "seven_day_checkins": [],
    })

    with patch("app.routers.home.get_supabase", return_value=supabase):
        summary = _run(get_home_summary({"id": "user-1"}))

    assert summary.entry_state == "progress_proof"
    assert summary.primary_cta.href == "/progress?tab=photos&focus=upload&from=home_progress_proof"


def test_home_summary_review_progress_cta_routes_to_compare_focus():
    from app.routers.home import get_home_summary

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-1",
            "target_body_fat_percentage": 14.0,
            "goal_image_url": "https://cdn.test/goal.jpg",
        }],
        "saved_goal_plans": [{
            "user_id": "user-1",
            "updated_at": _iso_days_ago(2),
            "plan_data": {"goals": {"targetBf": 14}},
        }],
        "body_scans": [
            {
                "user_id": "user-1",
                "scan_type": "bodyfat",
                "created_at": _iso_days_ago(2),
                "result_data": {"body_fat_percentage": 19.5},
            },
        ],
        "progress_photos": [
            {"user_id": "user-1", "taken_at": _iso_days_ago(1)},
            {"user_id": "user-1", "taken_at": _iso_days_ago(10)},
        ],
        "seven_day_challenges": [],
        "seven_day_checkins": [],
    })

    with patch("app.routers.home.get_supabase", return_value=supabase):
        summary = _run(get_home_summary({"id": "user-1"}))

    assert summary.entry_state == "review_progress"
    assert summary.primary_cta.href == "/progress?tab=photos&focus=compare&from=home_review_progress"


def test_retention_event_sink_logs_authenticated_events():
    from app.routers.retention_analytics import capture_retention_event
    from app.schemas.home_schemas import RetentionEventRequest

    supabase = _FakeSupabase({"funnel_events": []})

    with patch("app.services.retention_event_service.get_supabase", return_value=supabase):
        result = _run(capture_retention_event(
            RetentionEventRequest(
                event_name="history_viewed",
                surface="progress_page",
                properties={"target": "progress_proof", "source": "weekly_reminder", "session_id": "sess-home-1"},
            ),
            {"id": "user-1"},
        ))

    assert result == {"status": "ok"}
    assert len(supabase.tables["funnel_events"]) == 1
    row = supabase.tables["funnel_events"][0]
    assert row["user_id"] == "user-1"
    assert row["event_name"] == "history_viewed"
    assert row["source"] == "weekly_reminder"
    assert row["session_id"] == "sess-home-1"
