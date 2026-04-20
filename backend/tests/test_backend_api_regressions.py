import asyncio
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.food_schemas import FoodLogCreate
from app.schemas.payment_schemas import VerifyPurchaseRequest


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class _Result:
    def __init__(self, data):
        self.data = data


class _FoodTable:
    def __init__(self, rows):
        self.rows = rows
        self._reset()

    def _reset(self):
        self._mode = "select"
        self._filters = []
        self._payload = None

    def select(self, *_args, **_kwargs):
        self._mode = "select"
        return self

    def update(self, payload):
        self._mode = "update"
        self._payload = dict(payload)
        return self

    def eq(self, key, value):
        self._filters.append((key, value))
        return self

    def execute(self):
        rows = [
            row for row in self.rows
            if all(row.get(key) == value for key, value in self._filters)
        ]
        if self._mode == "update":
            for row in rows:
                row.update(self._payload)
            data = [dict(row) for row in rows]
        else:
            data = [dict(row) for row in rows]
        self._reset()
        return _Result(data)


class _FoodSupabase:
    def __init__(self):
        self.food_logs = [{
            "id": "log-1",
            "user_id": "user-1",
            "date": "2026-04-18",
            "food_name": "Oats",
            "calories": 200,
            "protein": 8,
            "carbs": 30,
            "fat": 4,
            "serving_size": "1 bowl",
            "meal_type": "breakfast",
            "source": "manual",
            "image_url": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }]

    def table(self, name):
        if name != "food_logs":
            raise AssertionError(f"Unexpected table access: {name}")
        return _FoodTable(self.food_logs)


class _UsageTable:
    def __init__(self, rows):
        self.rows = rows

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def execute(self):
        return _Result([dict(row) for row in self.rows])


class _UsageSupabase:
    def __init__(self, usage_rows=None):
        self.usage_rows = usage_rows or []

    def table(self, name):
        if name != "usage_limits":
            raise AssertionError(f"Unexpected table access: {name}")
        return _UsageTable(self.usage_rows)


class _AnalyticsTable:
    def __init__(self, rows):
        self.rows = [dict(row) for row in rows]
        self._filters = []

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self._filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def gte(self, key, value):
        self._filters.append(lambda row, k=key.strip('"'), v=value: row.get(k) >= v)
        return self

    def lte(self, key, value):
        self._filters.append(lambda row, k=key.strip('"'), v=value: row.get(k) <= v)
        return self

    def order(self, *_args, **_kwargs):
        return self

    def execute(self):
        data = [
            dict(row)
            for row in self.rows
            if all(check(row) for check in self._filters)
        ]
        return _Result(data)


class _AnalyticsSupabase:
    def __init__(self, *, daily_summaries=None, food_logs=None, calorie_goal=2100):
        self.daily_summaries = daily_summaries or []
        self.food_logs = food_logs or []
        self.user_profiles = [{"user_id": "user-1", "calorie_goal": calorie_goal}]

    def table(self, name):
        if name == "daily_summaries":
            return _AnalyticsTable(self.daily_summaries)
        if name == "food_logs":
            return _AnalyticsTable(self.food_logs)
        if name == "user_profiles":
            return _AnalyticsTable(self.user_profiles)
        raise AssertionError(f"Unexpected table access: {name}")


class _AnalyticsTable:
    def __init__(self, rows, *, fail_on_execute: bool = False):
        self.rows = rows
        self.fail_on_execute = fail_on_execute
        self._reset()

    def _reset(self):
        self._filters = []
        self._order_key = None
        self._order_desc = False

    @staticmethod
    def _normalize_key(key):
        return key.strip('"') if isinstance(key, str) else key

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self._filters.append(("eq", self._normalize_key(key), value))
        return self

    def gte(self, key, value):
        self._filters.append(("gte", self._normalize_key(key), value))
        return self

    def lte(self, key, value):
        self._filters.append(("lte", self._normalize_key(key), value))
        return self

    def order(self, key, desc=False):
        self._order_key = self._normalize_key(key)
        self._order_desc = desc
        return self

    def execute(self):
        if self.fail_on_execute:
            raise Exception("daily_summaries unavailable")

        def _matches(row):
            for op, key, value in self._filters:
                row_value = row.get(key)
                if op == "eq" and row_value != value:
                    return False
                if op == "gte" and row_value < value:
                    return False
                if op == "lte" and row_value > value:
                    return False
            return True

        rows = [dict(row) for row in self.rows if _matches(row)]
        if self._order_key:
            rows.sort(key=lambda row: row.get(self._order_key) or "", reverse=self._order_desc)
        self._reset()
        return _Result(rows)


class _AnalyticsSupabase:
    def __init__(self, *, daily_summaries=None, food_logs=None, failing_tables=None, calorie_goal=2100):
        self.daily_summaries = daily_summaries or []
        self.food_logs = food_logs or []
        self.user_profiles = [{"user_id": "user-1", "calorie_goal": calorie_goal}]
        self.failing_tables = set(failing_tables or [])

    def table(self, name):
        if name == "daily_summaries":
            return _AnalyticsTable(
                self.daily_summaries,
                fail_on_execute=name in self.failing_tables,
            )
        if name == "food_logs":
            return _AnalyticsTable(
                self.food_logs,
                fail_on_execute=name in self.failing_tables,
            )
        if name == "user_profiles":
            return _AnalyticsTable(
                self.user_profiles,
                fail_on_execute=name in self.failing_tables,
            )
        raise AssertionError(f"Unexpected table access: {name}")


def test_calorie_balance_trend_handles_partial_profile_defaults():
    from app.services.analytics import get_calorie_balance_trend

    profile = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "weight_kg": None,
        "height_cm": None,
        "age": None,
        "gender": None,
        "activity_level": None,
        "calorie_goal": None,
    }

    with (
        patch("app.services.analytics.get_food_trend_data", new=AsyncMock(return_value=[])),
        patch("app.services.analytics.get_workout_trend_data", new=AsyncMock(return_value=[])),
    ):
        result = _run(get_calorie_balance_trend("user-1", days=7, profile=profile))

    assert result["summary"]["tdee"] > 0
    assert result["summary"]["avg_deficit"] >= 0


def test_get_food_trend_data_falls_back_to_food_logs_when_daily_summaries_fail():
    from app.services.analytics import get_food_trend_data

    today = date.today()
    start_date = today - timedelta(days=2)
    supabase = _AnalyticsSupabase(
        food_logs=[
            {
                "user_id": "user-1",
                "date": start_date.isoformat(),
                "calories": 410,
                "protein": 21,
                "carbs": 45,
                "fat": 12,
            },
            {
                "user_id": "user-1",
                "date": today.isoformat(),
                "calories": 620,
                "protein": 39,
                "carbs": 58,
                "fat": 19,
            },
        ],
        failing_tables={"daily_summaries"},
    )

    with patch("app.services.analytics.get_supabase", return_value=supabase):
        trend = _run(get_food_trend_data("user-1", days=3, calorie_goal_override=1800))

    assert len(trend) == 3
    assert trend[0]["date"] == start_date.isoformat()
    assert trend[0]["calories"] == 410
    assert trend[0]["protein"] == 21
    assert trend[1]["calories"] == 0
    assert trend[2]["date"] == today.isoformat()
    assert trend[2]["fat"] == 19
    assert all(point["goal"] == 1800 for point in trend)


def test_get_food_trend_data_repairs_missing_and_degraded_summary_days_from_food_logs():
    from app.services.analytics import get_food_trend_data

    today = date.today()
    day_one = today - timedelta(days=2)
    day_two = today - timedelta(days=1)
    supabase = _AnalyticsSupabase(
        daily_summaries=[
            {
                "user_id": "user-1",
                "date": day_one.isoformat(),
                "total_calories": 500,
                "total_protein": 25,
                "total_carbs": 50,
                "total_fat": 10,
            },
            {
                "user_id": "user-1",
                "date": day_two.isoformat(),
                "total_calories": None,
                "total_protein": None,
                "total_carbs": None,
                "total_fat": None,
            },
        ],
        food_logs=[
            {
                "user_id": "user-1",
                "date": day_two.isoformat(),
                "calories": 640,
                "protein": 33,
                "carbs": 77,
                "fat": 18,
            },
            {
                "user_id": "user-1",
                "date": today.isoformat(),
                "calories": 720,
                "protein": 41,
                "carbs": 80,
                "fat": 24,
            },
        ],
    )

    with patch("app.services.analytics.get_supabase", return_value=supabase):
        trend = _run(get_food_trend_data("user-1", days=3, calorie_goal_override=2000))

    assert [point["date"] for point in trend] == [
        day_one.isoformat(),
        day_two.isoformat(),
        today.isoformat(),
    ]
    assert trend[0]["calories"] == 500
    assert trend[0]["protein"] == 25
    assert trend[1]["calories"] == 640
    assert trend[1]["carbs"] == 77
    assert trend[2]["calories"] == 720
    assert trend[2]["protein"] == 41
    assert all(point["goal"] == 2000 for point in trend)


def test_weekly_checkin_latest_returns_503_when_storage_not_provisioned():
    from app.routers.weekly_checkins import get_latest_weekly_checkin

    with patch(
        "app.routers.weekly_checkins._load_previous_checkin",
        new=AsyncMock(side_effect=Exception('relation "weekly_checkins" does not exist')),
    ):
        with pytest.raises(HTTPException) as exc:
            _run(get_latest_weekly_checkin(current_user={"id": "user-1"}))

    assert exc.value.status_code == 503


def test_update_food_log_recalculates_original_and_new_dates():
    from app.routers.food import update_food_log

    supabase = _FoodSupabase()
    recalc = AsyncMock()

    with (
        patch("app.routers.food.get_supabase", return_value=supabase),
        patch("app.routers.food.calculate_daily_summary", new=recalc),
        patch("app.routers.food.invalidate_calorie_balance_cache"),
    ):
        response = _run(
            update_food_log(
                "log-1",
                FoodLogCreate(
                    food_name="Oats",
                    calories=220,
                    protein=9,
                    carbs=32,
                    fat=4,
                    serving_size="1 bowl",
                    meal_type="breakfast",
                    date=date(2026, 4, 19),
                ),
                current_user={"id": "user-1"},
            )
        )

    assert response.date == date(2026, 4, 19)
    recalculated_dates = [call.args[1] for call in recalc.await_args_list]
    assert date(2026, 4, 18) in recalculated_dates
    assert date(2026, 4, 19) in recalculated_dates


def test_verify_purchase_transient_failure_returns_502_without_downgrade_write():
    from app.routers.payments import verify_purchase

    with (
        patch(
            "app.routers.payments.verify_revenuecat_purchase",
            new=AsyncMock(return_value={"status": "verification_error", "is_valid": False}),
        ),
        patch("app.routers.payments._upsert_external_subscription", new=AsyncMock()) as upsert_subscription,
    ):
        with pytest.raises(HTTPException) as exc:
            _run(
                verify_purchase(
                    VerifyPurchaseRequest(receipt_token="receipt", platform="ios"),
                    current_user={"id": "user-1"},
                )
            )

    assert exc.value.status_code == 502
    upsert_subscription.assert_not_awaited()


def test_usage_limits_endpoint_shape_uses_first_month_boosts():
    from app.services.usage_limiter import get_all_usage_limits

    with (
        patch("app.services.usage_limiter.get_supabase", return_value=_UsageSupabase()),
        patch("app.services.usage_limiter._is_first_month", new=AsyncMock(return_value=True)),
    ):
        result = _run(get_all_usage_limits("user-1", is_premium=False))

    assert result["food_scan"]["limit"] == 10
    assert result["body_fat_scan"]["limit"] == 3
    assert result["percentile_scan"]["limit"] == 3


def test_food_trend_data_falls_back_to_food_logs_when_daily_summaries_are_missing():
    from app.services.analytics import get_food_trend_data

    today = date.today().isoformat()
    supabase = _AnalyticsSupabase(
        daily_summaries=[],
        food_logs=[
            {
                "user_id": "user-1",
                "date": today,
                "calories": 520,
                "protein": 35,
                "carbs": 40,
                "fat": 18,
            }
        ],
    )

    with patch("app.services.analytics.get_supabase", return_value=supabase):
        trend = _run(get_food_trend_data("user-1", days=1))

    assert trend == [
        {
            "date": today,
            "calories": 520.0,
            "protein": 35.0,
            "carbs": 40.0,
            "fat": 18.0,
            "goal": 2100,
        }
    ]


def test_food_trend_data_prefers_food_log_rollup_when_daily_summaries_are_partial():
    from app.services.analytics import get_food_trend_data

    today = date.today().isoformat()
    supabase = _AnalyticsSupabase(
        daily_summaries=[
            {
                "user_id": "user-1",
                "date": today,
                "total_calories": 120,
                "total_protein": 10,
                "total_carbs": 15,
                "total_fat": 3,
            }
        ],
        food_logs=[
            {
                "user_id": "user-1",
                "date": today,
                "calories": 700,
                "protein": 50,
                "carbs": 60,
                "fat": 22,
            }
        ],
    )

    with patch("app.services.analytics.get_supabase", return_value=supabase):
        trend = _run(get_food_trend_data("user-1", days=2))

    today_row = next(item for item in trend if item["date"] == today)
    assert today_row["calories"] == 700.0
    assert today_row["protein"] == 50.0
    assert today_row["carbs"] == 60.0
    assert today_row["fat"] == 22.0
