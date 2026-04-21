from __future__ import annotations

import json
import os
import hashlib
import asyncio
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests


BASE_URL = os.getenv("DEVENIRA_API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT_DEFAULT = 30
TIMEOUT_HEAVY = 120
TIMEOUT_GENERATION = 300
INCLUDE_GUEST_HEAVY = os.getenv("DEVENIRA_SWEEP_INCLUDE_GUEST_HEAVY", "false").lower() in {"1", "true", "yes", "on"}
NOW = datetime.now(UTC)
TODAY = NOW.date()
TODAY_STR = TODAY.isoformat()
WEEK_AGO_STR = (TODAY - timedelta(days=7)).isoformat()
TEMP_EMAIL = f"api-sweep-{int(NOW.timestamp())}@example.com"
TEMP_PASSWORD = "TestPass123!"

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO7Z4d8AAAAASUVORK5CYII="
)
VIDEO_BASE64 = "bm90LWEtcmVhbC12aWRlby1idXQtYmFzZTY0"
FAKE_UUID = "00000000-0000-0000-0000-000000000000"


def _load_base64_fixture(env_name: str, fallback_path: Path | None = None, fallback_base64: str = PNG_BASE64) -> str:
    path_value = os.getenv(env_name, "").strip()
    candidate = Path(path_value) if path_value else fallback_path
    if candidate and candidate.exists():
        import base64

        return base64.b64encode(candidate.read_bytes()).decode()
    return fallback_base64


BODY_IMAGE_BASE64 = _load_base64_fixture(
    "DEVENIRA_TEST_BODY_IMAGE_PATH",
    Path(__file__).resolve().parents[1] / "sample_image.jpg",
)
FOOD_IMAGE_BASE64 = _load_base64_fixture(
    "DEVENIRA_TEST_FOOD_IMAGE_PATH",
    None,
    PNG_BASE64,
)


@dataclass
class SweepContext:
    stable_token: str | None = None
    stable_headers: dict[str, str] | None = None
    stable_user_id: str | None = None
    temp_token: str | None = None
    temp_headers: dict[str, str] | None = None
    temp_user_id: str | None = None
    food_log_id: str | None = None
    workout_log_id: str | None = None
    weight_log_id: str | None = None
    progress_photo_ids: list[str] | None = None
    proof_share_id: str | None = None
    proof_share_token: str | None = None
    food_db_item_id: str | None = None
    food_db_total_foods: int = 0

    def __post_init__(self) -> None:
        if self.progress_photo_ids is None:
            self.progress_photo_ids = []


class ApiSweep:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.context = SweepContext()
        self.results: list[dict[str, Any]] = []
        self.attempted_templates: set[tuple[str, str]] = set()
        self.openapi_routes = self._load_openapi_routes()

    def _load_openapi_routes(self) -> list[tuple[str, str]]:
        response = requests.get(f"{self.base_url}/openapi.json", timeout=TIMEOUT_DEFAULT)
        response.raise_for_status()
        obj = response.json()
        routes: list[tuple[str, str]] = []
        for path, operations in obj.get("paths", {}).items():
            for method in operations:
                routes.append((method.upper(), path))
        return sorted(routes)

    def _body_excerpt(self, response: requests.Response) -> str:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                text = json.dumps(response.json(), ensure_ascii=False)
            except Exception:
                text = response.text
        elif content_type.startswith("image/"):
            text = f"<binary {content_type} {len(response.content)} bytes>"
        else:
            text = response.text
        return text[:4000]

    def call(
        self,
        *,
        name: str,
        method: str,
        path_template: str,
        path: str | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        expected_statuses: set[int] | None = None,
        timeout: int = TIMEOUT_DEFAULT,
        allow_redirects: bool = True,
        note: str | None = None,
    ) -> requests.Response | None:
        resolved_path = path or path_template
        url = f"{self.base_url}{resolved_path}"
        method = method.upper()
        self.attempted_templates.add((method, path_template))
        record: dict[str, Any] = {
            "name": name,
            "method": method,
            "path": path_template,
            "resolved_path": resolved_path,
            "url": url,
            "params": params,
            "request_json": json_body,
            "expected_statuses": sorted(expected_statuses) if expected_statuses else None,
            "note": note,
        }
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_body,
                data=data,
                timeout=timeout,
                allow_redirects=allow_redirects,
            )
            record.update(
                {
                    "status": response.status_code,
                    "ok": (
                        response.status_code in expected_statuses
                        if expected_statuses is not None
                        else response.status_code < 400
                    ),
                    "response_content_type": response.headers.get("content-type"),
                    "location": response.headers.get("location"),
                    "body": self._body_excerpt(response),
                }
            )
            self.results.append(record)
            return response
        except Exception as exc:  # noqa: BLE001
            record.update(
                {
                    "status": 0,
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            self.results.append(record)
            return None

    def skip(
        self,
        *,
        name: str,
        method: str,
        path_template: str,
        note: str,
    ) -> None:
        self.attempted_templates.add((method.upper(), path_template))
        self.results.append(
            {
                "name": name,
                "method": method.upper(),
                "path": path_template,
                "resolved_path": None,
                "url": None,
                "status": None,
                "ok": False,
                "skipped": True,
                "note": note,
            }
        )

    def prepare_auth(self) -> None:
        register_payload = {
            "email": TEMP_EMAIL,
            "password": TEMP_PASSWORD,
            "full_name": "API Sweep Temp",
            "gender": "male",
            "age": 30,
            "height_cm": 180,
            "weight_kg": 82,
            "ethnicity": "asian",
            "activity_level": "moderate",
            "consent_terms": True,
            "consent_privacy": True,
            "consent_sensitive_data": True,
            "consent_age_verification": True,
        }
        register_response = self.call(
            name="auth_register",
            method="POST",
            path_template="/api/auth/register",
            json_body=register_payload,
            expected_statuses={200, 201, 400},
            note="Temp account for destructive auth verification",
        )
        if register_response is not None:
            try:
                payload = register_response.json()
            except Exception:
                payload = {}
            access_token = payload.get("access_token")
            if access_token:
                self.context.temp_token = access_token
                self.context.temp_headers = {"Authorization": f"Bearer {access_token}"}

        login_response = self.call(
            name="auth_login_temp",
            method="POST",
            path_template="/api/auth/login",
            json_body={"email": TEMP_EMAIL, "password": TEMP_PASSWORD},
            expected_statuses={200, 401},
            note="Temp account login after register",
        )
        if login_response is not None and login_response.status_code == 200:
            login_payload = login_response.json()
            access_token = login_payload.get("access_token")
            if access_token:
                self.context.temp_token = access_token
                self.context.temp_headers = {"Authorization": f"Bearer {access_token}"}
                self.context.temp_user_id = (login_payload.get("user") or {}).get("id")

        test_login_response = self.call(
            name="auth_test_login",
            method="POST",
            path_template="/api/auth/test-login",
            json_body={"email": "e2e@devenira.test"},
            expected_statuses={200},
            note="Stable seeded account for auth-required endpoint sweep",
        )
        if test_login_response is None or test_login_response.status_code != 200:
            raise RuntimeError("Stable test login failed; cannot continue auth-required API sweep")

        stable_token = test_login_response.json()["access_token"]
        self.context.stable_token = stable_token
        self.context.stable_headers = {"Authorization": f"Bearer {stable_token}"}
        self.context.stable_user_id = (test_login_response.json().get("user") or {}).get("id")
        self._prepare_qa_state()

    def _prepare_qa_state(self) -> None:
        try:
            from app.database import get_supabase
            from app.services.usage_limiter import add_credits, ensure_credit_record
        except Exception:
            return

        supabase = get_supabase()

        if self.context.temp_user_id:
            asyncio.run(ensure_credit_record(self.context.temp_user_id, is_premium=False))
            asyncio.run(add_credits(self.context.temp_user_id, 250, credit_type="bonus"))

            for feature in ("body_fat_scan", "percentile_scan"):
                try:
                    supabase.table("usage_limits").delete().eq("user_id", self.context.temp_user_id).eq("feature_type", feature).execute()
                except Exception:
                    pass

            for table_name in ("weekly_checkins", "progress_photos"):
                try:
                    supabase.table(table_name).delete().eq("user_id", self.context.temp_user_id).execute()
                except Exception:
                    pass

        guest_fp = hashlib.sha256(
            f"127.0.0.1|{self.session.headers.get('User-Agent', '')}|".encode()
        ).hexdigest()
        try:
            supabase.table("guest_scan_usage").delete().eq("fingerprint_hash", guest_fp).execute()
        except Exception:
            pass

    def run(self) -> dict[str, Any]:
        self.prepare_auth()
        h = self.context.stable_headers or {}
        temp_h = self.context.temp_headers or {}

        # Root and assets
        self.call(name="root", method="GET", path_template="/", expected_statuses={200})
        self.call(name="health", method="GET", path_template="/health", expected_statuses={200})
        self.call(name="assets_model", method="GET", path_template="/api/assets/human-body-model", expected_statuses={200})
        self.call(name="assets_preview", method="GET", path_template="/api/assets/human-body-preview", expected_statuses={200})

        # Auth
        self.call(name="auth_me", method="GET", path_template="/api/auth/me", headers=h, expected_statuses={200})
        self.call(
            name="auth_profile_put",
            method="PUT",
            path_template="/api/auth/profile",
            headers=h,
            json_body={"full_name": "Denevira E2E QA", "height_cm": 181, "weight_kg": 81, "activity_level": "moderate"},
            expected_statuses={200},
        )
        self.call(
            name="auth_reset_password",
            method="POST",
            path_template="/api/auth/reset-password",
            json_body={"email": TEMP_EMAIL},
            expected_statuses={200},
        )

        # Analytics + home/dashboard
        self.call(
            name="analytics_retention",
            method="POST",
            path_template="/api/analytics/retention",
            headers=h,
            json_body={"event_name": "progress_proof_started", "surface": "api_sweep", "properties": {"source": "manual_http_sweep"}},
            expected_statuses={200},
        )
        self.call(name="analytics_daily_snapshot", method="GET", path_template="/api/analytics/funnel/daily-snapshot", headers=h, expected_statuses={200})
        self.call(name="analytics_weekly_cohort", method="GET", path_template="/api/analytics/funnel/weekly-cohort-by-source", headers=h, expected_statuses={200})
        self.call(name="analytics_entry_state", method="GET", path_template="/api/analytics/funnel/entry-state-performance", headers=h, expected_statuses={200})
        self.call(name="analytics_reminder_open_to_proof", method="GET", path_template="/api/analytics/funnel/reminder-open-to-proof", headers=h, expected_statuses={200})
        self.call(name="analytics_share_view_to_register", method="GET", path_template="/api/analytics/funnel/share-view-to-register", headers=h, expected_statuses={200})
        self.call(name="home_summary", method="GET", path_template="/api/home/summary", headers=h, expected_statuses={200})
        self.call(name="dashboard", method="GET", path_template="/api/dashboard", headers=h, expected_statuses={200})
        self.call(name="dashboard_quick_stats", method="GET", path_template="/api/dashboard/quick-stats", headers=h, expected_statuses={200})
        self.call(name="dashboard_calorie_balance", method="GET", path_template="/api/dashboard/calorie-balance-trend", headers=h, expected_statuses={200})

        # Payments
        self.call(name="payments_credits", method="GET", path_template="/api/payments/credits", headers=h, expected_statuses={200})
        self.call(name="payments_subscription", method="GET", path_template="/api/payments/subscription", headers=h, expected_statuses={200})
        self.call(name="payments_subscription_diagnostics", method="GET", path_template="/api/payments/subscription-diagnostics", headers=h, expected_statuses={200})
        self.call(name="payments_usage_limits", method="GET", path_template="/api/payments/usage-limits", headers=h, expected_statuses={200})
        self.call(
            name="payments_billing_portal",
            method="POST",
            path_template="/api/payments/billing-portal",
            headers=h,
            json_body={"return_url": "https://devenira.com/profile"},
            expected_statuses={200, 400},
            note="400 is acceptable when account has no Stripe customer",
        )
        self.call(
            name="payments_create_checkout",
            method="POST",
            path_template="/api/payments/create-checkout-session",
            headers=h,
            json_body={
                "price_id": os.getenv("DEVENIRA_TEST_PRICE_ID", "price_1TGuQACIAtieotxAy7HsfRhq"),
                "success_url": "https://devenira.com/profile?checkout=success",
                "cancel_url": "https://devenira.com/profile?checkout=cancelled",
            },
            timeout=TIMEOUT_HEAVY,
            expected_statuses={200, 400},
            note="400 is acceptable when the configured Stripe price is unavailable in this environment",
        )
        self.call(
            name="payments_buy_credits",
            method="POST",
            path_template="/api/payments/buy-credits",
            headers=h,
            json_body={
                "pack_size": 100,
                "success_url": "https://devenira.com/profile?credits=success",
                "cancel_url": "https://devenira.com/profile?credits=cancelled",
            },
            timeout=TIMEOUT_HEAVY,
        )
        self.call(
            name="payments_verify_purchase",
            method="POST",
            path_template="/api/payments/verify-purchase",
            headers=h,
            json_body={"receipt_token": "bogus-receipt", "platform": "android", "app_user_id": "api-sweep"},
            timeout=TIMEOUT_HEAVY,
            expected_statuses={200, 400, 502},
            note="Negative-path verification with bogus receipt; 502 is acceptable when verifier is unavailable",
        )
        self.call(
            name="payments_webhook_invalid",
            method="POST",
            path_template="/api/payments/webhook",
            headers={"stripe-signature": "invalid"},
            data="{}",
            expected_statuses={400},
            note="Negative-path verification for invalid Stripe signature",
        )

        # Notifications
        self.call(name="notifications_preferences_get", method="GET", path_template="/api/notifications/preferences", headers=h, expected_statuses={200})
        self.call(
            name="notifications_preferences_put",
            method="PUT",
            path_template="/api/notifications/preferences",
            headers=h,
            json_body={"weekly_proof_reminders_enabled": True, "timezone": "America/Toronto"},
            expected_statuses={200},
        )
        self.call(name="notifications_reminder_status", method="GET", path_template="/api/notifications/reminder-status", headers=h, expected_statuses={200})
        self.call(
            name="notifications_push_subscribe",
            method="POST",
            path_template="/api/notifications/push/subscribe",
            headers=h,
            json_body={"endpoint": "ExponentPushToken[api-sweep]", "device": "android", "app_version": "qa"},
            expected_statuses={200},
        )
        self.call(
            name="notifications_push_unsubscribe",
            method="POST",
            path_template="/api/notifications/push/unsubscribe",
            headers=h,
            json_body={"endpoint": "ExponentPushToken[api-sweep]"},
            expected_statuses={200},
        )
        self.call(
            name="notifications_reminder_open_fake",
            method="GET",
            path_template="/api/notifications/reminders/open/{reminder_event_id}",
            path=f"/api/notifications/reminders/open/{FAKE_UUID}",
            expected_statuses={404},
        )
        self.call(
            name="notifications_unsubscribe_get_fake",
            method="GET",
            path_template="/api/notifications/reminders/unsubscribe/{reminder_event_id}",
            path=f"/api/notifications/reminders/unsubscribe/{FAKE_UUID}",
            expected_statuses={404},
        )
        self.call(
            name="notifications_unsubscribe_post_fake",
            method="POST",
            path_template="/api/notifications/reminders/unsubscribe/{reminder_event_id}",
            path=f"/api/notifications/reminders/unsubscribe/{FAKE_UUID}",
            expected_statuses={404},
        )
        self.call(
            name="notifications_resend_webhook_invalid",
            method="POST",
            path_template="/api/notifications/webhooks/resend",
            data="{}",
            expected_statuses={400},
            note="Negative-path verification for invalid Resend webhook payload",
        )

        # Challenge / streaks / fasting
        self.call(name="challenge_get", method="GET", path_template="/api/challenge/seven-day", headers=h, expected_statuses={200})
        self.call(
            name="challenge_start",
            method="POST",
            path_template="/api/challenge/seven-day/start",
            headers=h,
            json_body={"ai_weeks_snapshot": 6, "ai_current_bf": 20.5, "ai_target_bf": 15.0},
            expected_statuses={200},
        )
        self.call(
            name="challenge_checkin",
            method="POST",
            path_template="/api/challenge/seven-day/checkin",
            headers=h,
            json_body={"weight_kg": 80.5, "body_fat_pct": 19.9},
            expected_statuses={200},
        )
        self.call(name="streaks_get", method="GET", path_template="/api/streaks", headers=h, expected_statuses={200})
        self.call(name="streaks_checkin", method="POST", path_template="/api/streaks/check-in", headers=h, expected_statuses={200})
        self.call(name="fasting_presets", method="GET", path_template="/api/fasting/presets", headers=h, expected_statuses={200})
        self.call(name="fasting_current_before", method="GET", path_template="/api/fasting/current", headers=h, expected_statuses={200})
        self.call(
            name="fasting_start",
            method="POST",
            path_template="/api/fasting/start",
            headers=h,
            json_body={"protocol": "16:8", "target_hours": 16},
            expected_statuses={200, 400},
            note="400 is acceptable if an active fast already exists",
        )
        self.call(name="fasting_current_after_start", method="GET", path_template="/api/fasting/current", headers=h, expected_statuses={200})
        self.call(
            name="fasting_end",
            method="POST",
            path_template="/api/fasting/end",
            headers=h,
            json_body={"notes": "Ended during API sweep"},
            expected_statuses={200, 400},
            note="400 is acceptable when there is no active fast to end",
        )
        self.call(name="fasting_history", method="GET", path_template="/api/fasting/history", headers=h, expected_statuses={200})

        # Food database
        search_response = self.call(
            name="food_db_search",
            method="GET",
            path_template="/api/food-database/search",
            params={"q": "apple", "limit": 5},
            expected_statuses={200},
        )
        if search_response is not None and search_response.status_code == 200:
            try:
                payload = search_response.json()
            except Exception:
                payload = {}
            items = payload.get("results") if isinstance(payload, dict) else payload
            if not isinstance(items, list):
                items = []
            if items:
                self.context.food_db_item_id = str(items[0].get("id") or items[0].get("food_id") or items[0].get("fdc_id"))
        self.call(name="food_db_categories", method="GET", path_template="/api/food-database/categories", expected_statuses={200})
        stats_response = self.call(name="food_db_stats", method="GET", path_template="/api/food-database/stats/overview", expected_statuses={200})
        if stats_response is not None and stats_response.status_code == 200:
            try:
                self.context.food_db_total_foods = int(stats_response.json().get("total_foods") or 0)
            except Exception:
                self.context.food_db_total_foods = 0
        if self.context.food_db_item_id:
            self.call(
                name="food_db_get_item",
                method="GET",
                path_template="/api/food-database/{food_id}",
                path=f"/api/food-database/{self.context.food_db_item_id}",
                expected_statuses={200},
            )
        else:
            self.skip(
                name="food_db_get_item",
                method="GET",
                path_template="/api/food-database/{food_id}",
                note="Search returned no food id to verify detail endpoint",
            )
        if self.context.food_db_item_id:
            self.call(
                name="food_db_calculate",
                method="POST",
                path_template="/api/food-database/calculate",
                params={"food_id": self.context.food_db_item_id, "amount_grams": 100},
                expected_statuses={200},
            )
        else:
            self.skip(
                name="food_db_calculate",
                method="POST",
                path_template="/api/food-database/calculate",
                note=(
                    "Food database is empty in this environment"
                    if self.context.food_db_total_foods == 0
                    else "Search returned no food id to verify nutrition calculation"
                ),
            )

        # Food decision
        self.call(name="food_decision_prefs_get", method="GET", path_template="/api/food-decision/preferences", headers=h, expected_statuses={200})
        self.call(
            name="food_decision_prefs_put",
            method="PUT",
            path_template="/api/food-decision/preferences",
            headers=h,
            json_body={"favorite_foods": ["salmon", "rice"], "prefer_high_protein": True},
            expected_statuses={200},
        )
        self.call(
            name="food_decision_recommend",
            method="POST",
            path_template="/api/food-decision/recommend",
            headers=h,
            json_body={"meal_type": "lunch", "target_date": TODAY_STR},
            timeout=TIMEOUT_HEAVY,
        )
        self.call(
            name="food_decision_should_i_eat",
            method="POST",
            path_template="/api/food-decision/should-i-eat",
            headers=h,
            json_body={"image_base64": FOOD_IMAGE_BASE64},
            timeout=TIMEOUT_HEAVY,
            expected_statuses={200, 422},
            note="422 is acceptable when the provided sample is not recognized as a valid food photo",
        )

        # Food logs
        food_create_response = self.call(
            name="food_log_create",
            method="POST",
            path_template="/api/food/log",
            headers=h,
            json_body={
                "date": TODAY_STR,
                "meal_type": "lunch",
                "food_name": "API Sweep Chicken Bowl",
                "calories": 650,
                "protein": 45,
                "carbs": 55,
                "fat": 20,
                "serving_size": "1 bowl",
                "source": "manual",
            },
            expected_statuses={201},
        )
        if food_create_response is not None and food_create_response.status_code == 201:
            try:
                self.context.food_log_id = food_create_response.json()["id"]
            except Exception:
                pass
        self.call(name="food_daily", method="GET", path_template="/api/food/daily/{target_date}", path=f"/api/food/daily/{TODAY_STR}", headers=h, expected_statuses={200})
        self.call(name="food_trends", method="GET", path_template="/api/food/trends", headers=h, expected_statuses={200})
        self.call(name="food_recent", method="GET", path_template="/api/food/recent", headers=h, expected_statuses={200})
        if self.context.food_log_id:
            self.call(
                name="food_log_update",
                method="PUT",
                path_template="/api/food/log/{log_id}",
                path=f"/api/food/log/{self.context.food_log_id}",
                headers=h,
                json_body={
                    "date": TODAY_STR,
                    "meal_type": "lunch",
                    "food_name": "API Sweep Chicken Bowl Updated",
                    "calories": 620,
                    "protein": 46,
                    "carbs": 48,
                    "fat": 18,
                    "serving_size": "1 bowl",
                    "source": "manual",
                },
                expected_statuses={200},
            )
        else:
            self.skip(name="food_log_update", method="PUT", path_template="/api/food/log/{log_id}", note="Food log create did not return an id")
        self.call(
            name="food_log_natural",
            method="POST",
            path_template="/api/food/log-natural",
            headers=h,
            json_body={"text": "I ate grilled chicken with rice and broccoli", "meal_type": "dinner", "date": TODAY_STR},
            timeout=TIMEOUT_HEAVY,
        )
        self.call(
            name="food_analyze_photo",
            method="POST",
            path_template="/api/food/analyze-photo",
            headers=h,
            json_body={"image_base64": FOOD_IMAGE_BASE64},
            timeout=TIMEOUT_HEAVY,
            expected_statuses={200, 422},
            note="422 is acceptable when the provided sample is not recognized as a valid food photo",
        )

        # Goal planner
        self.call(
            name="goalplan_tiers",
            method="POST",
            path_template="/api/goal-plan/tiers",
            headers=h,
            json_body={
                "current_weight_kg": 82,
                "current_bf_pct": 20,
                "target_bf_pct": 15,
                "gender": "male",
                "age": 30,
                "height_cm": 180,
                "activity_level": "moderate",
            },
            expected_statuses={200},
        )
        self.call(name="goalplan_macros", method="POST", path_template="/api/goal-plan/macros", headers=h, json_body={"daily_calories": 2200, "weight_kg": 82}, expected_statuses={200})
        goalplan_foods_response = self.call(name="goalplan_foods", method="POST", path_template="/api/goal-plan/foods", headers=h, json_body={"protein_g": 180, "carb_g": 180, "fat_g": 70, "priority": "balanced", "limit": 5}, expected_statuses={200})
        goalplan_food_ids: list[str] = []
        if goalplan_foods_response is not None and goalplan_foods_response.status_code == 200:
            try:
                foods_payload = goalplan_foods_response.json().get("foods") or []
            except Exception:
                foods_payload = []
            for item in foods_payload[:3]:
                food_id = item.get("id")
                if food_id:
                    goalplan_food_ids.append(str(food_id))
        if len(goalplan_food_ids) >= 2:
            ingredients = [
                {"food_id": goalplan_food_ids[0], "amount_g": 180},
                {"food_id": goalplan_food_ids[1], "amount_g": 150},
            ]
            if len(goalplan_food_ids) >= 3:
                ingredients.append({"food_id": goalplan_food_ids[2], "amount_g": 120})
            self.call(
                name="goalplan_dishes",
                method="POST",
                path_template="/api/goal-plan/dishes",
                headers=h,
                json_body={"ingredients": ingredients, "target_calories": 650},
                expected_statuses={200},
            )
        else:
            self.skip(
                name="goalplan_dishes",
                method="POST",
                path_template="/api/goal-plan/dishes",
                note="Goal-plan food suggestions returned no valid food ids to compose dishes",
            )
        self.call(name="goalplan_meals", method="POST", path_template="/api/goal-plan/recommend-meals", headers=h, json_body={"daily_calories": 2200, "protein_g": 180, "carb_g": 180, "fat_g": 70, "meals_per_day": 4}, expected_statuses={200})
        self.call(name="goalplan_exercise", method="POST", path_template="/api/goal-plan/exercise", headers=h, json_body={"mode": "cut", "gender": "male", "experience": "intermediate", "sessions_per_week": 4}, expected_statuses={200})
        self.call(name="goalplan_cardio", method="POST", path_template="/api/goal-plan/cardio", headers=h, json_body={"weight_kg": 82, "gender": "male", "height_cm": 180, "age": 30, "target_calories": 300}, expected_statuses={200})
        self.call(name="goalplan_saved_get", method="GET", path_template="/api/goal-plan/saved-plan", headers=h, expected_statuses={200, 404})
        self.call(name="goalplan_saved_post", method="POST", path_template="/api/goal-plan/saved-plan", headers=h, json_body={"plan": {"target": "lean", "calories": 2200}}, expected_statuses={200})

        # Guest / body / beauty / fashion / chat
        if INCLUDE_GUEST_HEAVY:
            self.call(name="guest_validate_photo", method="POST", path_template="/api/guest/validate-photo", json_body={"image_base64": BODY_IMAGE_BASE64, "framing": "upper_body"}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
            self.call(name="guest_body_scan", method="POST", path_template="/api/guest/body-scan", json_body={"image_base64": BODY_IMAGE_BASE64, "gender": "male", "age": 30, "ownership_confirmed": True, "adult_confirmed": True, "framing": "upper_body"}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable for low-quality samples")
        else:
            self.skip(
                name="guest_validate_photo",
                method="POST",
                path_template="/api/guest/validate-photo",
                note="Skipped in default sweep; heavy guest model cold-start is verified separately with DEVENIRA_SWEEP_INCLUDE_GUEST_HEAVY=true",
            )
            self.skip(
                name="guest_body_scan",
                method="POST",
                path_template="/api/guest/body-scan",
                note="Skipped in default sweep; heavy guest model cold-start is verified separately with DEVENIRA_SWEEP_INCLUDE_GUEST_HEAVY=true",
            )

        body_h = temp_h or h
        self.call(name="body_validate_photo", method="POST", path_template="/api/body/validate-photo", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "framing": "upper_body"}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_gap_to_goal", method="GET", path_template="/api/body/gap-to-goal", headers=body_h, expected_statuses={200})
        self.call(name="body_scans_history", method="GET", path_template="/api/body/scans/history", headers=body_h, expected_statuses={200})
        self.call(name="body_save_goal", method="PATCH", path_template="/api/body/save-goal", headers=body_h, json_body={"goal_image_url": "https://devenira.com/goal.jpg", "target_bf": 15}, expected_statuses={200})
        self.call(name="body_auto_segment", method="POST", path_template="/api/body/auto-segment", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_prepare_cut_edit", method="POST", path_template="/api/body/prepare-cut-edit", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "intensity": 0.5}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_cut_warp_preview", method="POST", path_template="/api/body/cut-warp-preview", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "preset": "tighten", "intensity": 0.4}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_segment", method="POST", path_template="/api/body/segment", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "click_x": 0.5, "click_y": 0.5}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_estimate_bodyfat", method="POST", path_template="/api/body/estimate-bodyfat", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "scan_type": "bodyfat", "ownership_confirmed": True, "gender": "male", "age": 30, "height_cm": 180, "weight_kg": 82, "activity_level": "moderate"}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_percentile", method="POST", path_template="/api/body/percentile", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "scan_type": "percentile", "ownership_confirmed": True, "gender": "male", "age": 30, "ethnicity": "asian", "height_cm": 180, "weight_kg": 82, "activity_level": "moderate"}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_transformation", method="POST", path_template="/api/body/transformation", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "scan_type": "transformation", "ownership_confirmed": True, "gender": "male", "age": 30, "height_cm": 180, "weight_kg": 82, "activity_level": "moderate", "target_bf": 15}, timeout=TIMEOUT_GENERATION, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_enhancement", method="POST", path_template="/api/body/enhancement", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "scan_type": "enhancement", "ownership_confirmed": True, "gender": "male", "age": 30, "height_cm": 180, "weight_kg": 82, "activity_level": "moderate"}, timeout=TIMEOUT_GENERATION, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="body_transform_region", method="POST", path_template="/api/body/transform-region", headers=body_h, json_body={"image_base64": BODY_IMAGE_BASE64, "mask_base64": BODY_IMAGE_BASE64, "body_part": "waist", "goal": "leaner", "gender": "male", "intensity": "medium", "ownership_confirmed": True}, timeout=TIMEOUT_GENERATION, expected_statuses={200, 422, 429}, note="422 is acceptable for sample quality failures; 429 is acceptable when the external image provider is temporarily rate limited")
        self.call(name="beauty_analyze", method="POST", path_template="/api/beauty/analyze", headers=body_h, json_body={"image_base64": PNG_BASE64, "gender": "male", "generate_images": False}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable for invalid/non-face sample input")
        self.call(name="fashion_recommend", method="POST", path_template="/api/fashion/recommend", headers=body_h, json_body={"season": "spring", "gender": "male", "height_cm": 180, "weight_kg": 82, "body_notes": "athletic", "generate_images": False}, timeout=TIMEOUT_GENERATION, expected_statuses={200})
        self.call(name="chat_status", method="GET", path_template="/api/chat/status", headers=h, expected_statuses={200})
        self.call(name="chat_history_get", method="GET", path_template="/api/chat/history", headers=h, expected_statuses={200})
        self.call(name="chat_message", method="POST", path_template="/api/chat/message", headers=h, json_body={"message": "Give me one concise fat-loss tip."}, timeout=TIMEOUT_HEAVY)

        # Weight
        self.call(name="weight_goals_patch", method="PATCH", path_template="/api/weight/goals", headers=h, json_body={"target_weight_kg": 76, "target_body_fat_percentage": 15}, expected_statuses={200})
        weight_create = self.call(name="weight_log_post", method="POST", path_template="/api/weight/log", headers=h, json_body={"date": TODAY_STR, "weight_kg": 80.2, "body_fat_percentage": 19.8, "notes": "API sweep log"}, expected_statuses={201, 200})
        if weight_create is not None and weight_create.status_code in {200, 201}:
            try:
                self.context.weight_log_id = weight_create.json()["id"]
            except Exception:
                pass
        self.call(name="weight_logs_get", method="GET", path_template="/api/weight/logs", headers=h, expected_statuses={200})
        if self.context.weight_log_id:
            self.call(name="weight_log_patch", method="PATCH", path_template="/api/weight/log/{log_id}", path=f"/api/weight/log/{self.context.weight_log_id}", headers=h, json_body={"notes": "Updated by API sweep"}, expected_statuses={200})
        else:
            self.skip(name="weight_log_patch", method="PATCH", path_template="/api/weight/log/{log_id}", note="Weight log create did not return an id")
        self.call(name="weight_projection", method="GET", path_template="/api/weight/projection", headers=h, expected_statuses={200})

        # Workout
        library = self.call(name="workout_exercise_library", method="GET", path_template="/api/workout/exercises/library", headers=h, expected_statuses={200})
        exercise_id = "manual-squat"
        exercise_name = "Manual Squat"
        if library is not None and library.status_code == 200:
            try:
                items = library.json()
            except Exception:
                items = []
            if items:
                exercise_id = items[0]["id"]
                exercise_name = items[0]["name"]
        workout_create = self.call(
            name="workout_log_post",
            method="POST",
            path_template="/api/workout/log",
            headers=h,
            json_body={"date": TODAY_STR, "exercise_id": exercise_id, "exercise_name": exercise_name, "sets": [{"set_number": 1, "reps": 10, "weight": 50.0}], "duration_minutes": 20, "notes": "API sweep workout"},
            expected_statuses={201},
        )
        if workout_create is not None and workout_create.status_code == 201:
            try:
                self.context.workout_log_id = workout_create.json()["id"]
            except Exception:
                pass
        self.call(name="workout_logs_date", method="GET", path_template="/api/workout/logs/{target_date}", path=f"/api/workout/logs/{TODAY_STR}", headers=h, expected_statuses={200})
        self.call(name="workout_logs_range", method="GET", path_template="/api/workout/logs-range", params={"start_date": WEEK_AGO_STR, "end_date": TODAY_STR}, headers=h, expected_statuses={200})
        self.call(name="workout_trends", method="GET", path_template="/api/workout/trends", headers=h, expected_statuses={200})
        self.call(name="workout_analyze_form", method="POST", path_template="/api/workout/analyze-form", headers=h, json_body={"video_base64": VIDEO_BASE64, "exercise_name": exercise_name}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 402}, note="402 is acceptable when premium entitlement is required")

        # Progress photos + weekly checkins + proof shares
        photo_h = temp_h or h
        photo_one = self.call(name="progress_photo_post_1", method="POST", path_template="/api/progress-photos", headers=photo_h, json_body={"image_base64": PNG_BASE64, "notes": "API sweep photo 1", "weight_kg": 80.0, "body_fat_pct": 20.0}, timeout=TIMEOUT_HEAVY)
        if photo_one is not None and photo_one.status_code == 200:
            try:
                self.context.progress_photo_ids.append(photo_one.json()["id"])
            except Exception:
                pass
        photo_two = self.call(name="progress_photo_post_2", method="POST", path_template="/api/progress-photos", headers=photo_h, json_body={"image_base64": PNG_BASE64, "notes": "API sweep photo 2", "weight_kg": 79.5, "body_fat_pct": 19.7}, timeout=TIMEOUT_HEAVY)
        if photo_two is not None and photo_two.status_code == 200:
            try:
                self.context.progress_photo_ids.append(photo_two.json()["id"])
            except Exception:
                pass
        photos_get = self.call(name="progress_photos_get", method="GET", path_template="/api/progress-photos", headers=photo_h, expected_statuses={200})
        if photos_get is not None and photos_get.status_code == 200 and not self.context.progress_photo_ids:
            try:
                self.context.progress_photo_ids = [item["id"] for item in photos_get.json()[:2]]
            except Exception:
                pass
        if self.context.progress_photo_ids:
            first_photo_id = self.context.progress_photo_ids[0]
            self.call(name="progress_photo_get_one", method="GET", path_template="/api/progress-photos/{photo_id}", path=f"/api/progress-photos/{first_photo_id}", headers=photo_h, expected_statuses={200})
        else:
            self.skip(name="progress_photo_get_one", method="GET", path_template="/api/progress-photos/{photo_id}", note="No progress photo id available")
        if len(self.context.progress_photo_ids) >= 2:
            first_photo_id, second_photo_id = self.context.progress_photo_ids[:2]
            self.call(name="progress_photos_compare", method="GET", path_template="/api/progress-photos/compare/{photo_id_1}/{photo_id_2}", path=f"/api/progress-photos/compare/{first_photo_id}/{second_photo_id}", headers=photo_h, expected_statuses={200})
            share_create = self.call(
                name="proof_shares_create",
                method="POST",
                path_template="/api/proof-shares",
                headers=photo_h,
                json_body={"progress_photo_id": first_photo_id, "week_marker": 1, "source": "api_sweep"},
            )
            if share_create is not None and share_create.status_code == 200:
                try:
                    payload = share_create.json()
                    self.context.proof_share_id = payload["id"]
                    self.context.proof_share_token = payload["token"]
                except Exception:
                    pass
        else:
            self.skip(name="progress_photos_compare", method="GET", path_template="/api/progress-photos/compare/{photo_id_1}/{photo_id_2}", note="Need two progress photo ids to compare")
            self.skip(name="proof_shares_create", method="POST", path_template="/api/proof-shares", note="Need at least one progress photo id to create a proof share")
        self.call(name="proof_shares_list", method="GET", path_template="/api/proof-shares", headers=photo_h, expected_statuses={200})
        if self.context.proof_share_token:
            token = self.context.proof_share_token
            self.call(name="proof_share_public", method="GET", path_template="/api/proof-shares/public/{token}", path=f"/api/proof-shares/public/{token}", expected_statuses={200})
            self.call(name="proof_share_public_image", method="GET", path_template="/api/proof-shares/public/{token}/image", path=f"/api/proof-shares/public/{token}/image")
            self.call(name="proof_share_public_try", method="GET", path_template="/api/proof-shares/public/{token}/try", path=f"/api/proof-shares/public/{token}/try", expected_statuses={307}, allow_redirects=False)
        else:
            self.skip(name="proof_share_public", method="GET", path_template="/api/proof-shares/public/{token}", note="No proof share token available from create/list")
            self.skip(name="proof_share_public_image", method="GET", path_template="/api/proof-shares/public/{token}/image", note="No proof share token available from create/list")
            self.skip(name="proof_share_public_try", method="GET", path_template="/api/proof-shares/public/{token}/try", note="No proof share token available from create/list")
        self.call(name="weekly_checkin_latest_before", method="GET", path_template="/api/weekly-checkins/latest", headers=photo_h, expected_statuses={200, 404})
        self.call(name="weekly_checkin_analyze", method="POST", path_template="/api/weekly-checkins/analyze", headers=photo_h, json_body={"image_base64": BODY_IMAGE_BASE64, "notes": "API sweep weekly proof", "weight_kg": 79.8, "ownership_confirmed": True}, timeout=TIMEOUT_HEAVY, expected_statuses={200, 422}, note="422 is acceptable when the sample fails body-photo quality checks")
        self.call(name="weekly_checkin_latest_after", method="GET", path_template="/api/weekly-checkins/latest", headers=photo_h, expected_statuses={200, 404})

        # Cleanup and destructive endpoints
        if self.context.proof_share_id:
            self.call(name="proof_shares_delete", method="DELETE", path_template="/api/proof-shares/{share_id}", path=f"/api/proof-shares/{self.context.proof_share_id}", headers=photo_h, expected_statuses={200})
        else:
            self.skip(name="proof_shares_delete", method="DELETE", path_template="/api/proof-shares/{share_id}", note="No proof share id available to revoke")
        for idx, photo_id in enumerate(list(self.context.progress_photo_ids or []), start=1):
            self.call(name=f"progress_photo_delete_{idx}", method="DELETE", path_template="/api/progress-photos/{photo_id}", path=f"/api/progress-photos/{photo_id}", headers=photo_h, expected_statuses={200})
        if self.context.workout_log_id:
            self.call(name="workout_log_delete", method="DELETE", path_template="/api/workout/log/{log_id}", path=f"/api/workout/log/{self.context.workout_log_id}", headers=h, expected_statuses={200})
        else:
            self.skip(name="workout_log_delete", method="DELETE", path_template="/api/workout/log/{log_id}", note="Workout log create did not return an id")
        if self.context.food_log_id:
            self.call(name="food_log_delete", method="DELETE", path_template="/api/food/log/{log_id}", path=f"/api/food/log/{self.context.food_log_id}", headers=h, expected_statuses={200})
        else:
            self.skip(name="food_log_delete", method="DELETE", path_template="/api/food/log/{log_id}", note="Food log create did not return an id")
        if self.context.weight_log_id:
            self.call(name="weight_log_delete", method="DELETE", path_template="/api/weight/log/{log_id}", path=f"/api/weight/log/{self.context.weight_log_id}", headers=h, expected_statuses={204})
        else:
            self.skip(name="weight_log_delete", method="DELETE", path_template="/api/weight/log/{log_id}", note="Weight log create did not return an id")
        self.call(name="chat_history_delete", method="DELETE", path_template="/api/chat/history", headers=h, expected_statuses={200})
        self.call(name="auth_logout", method="POST", path_template="/api/auth/logout", headers=h, expected_statuses={200})
        if temp_h:
            self.call(name="auth_account_delete", method="DELETE", path_template="/api/auth/account", headers=temp_h, expected_statuses={200})
        else:
            self.skip(name="auth_account_delete", method="DELETE", path_template="/api/auth/account", note="Temp account token unavailable")

        attempted = sorted(self.attempted_templates)
        attempted_set = set(attempted)
        openapi_set = set(self.openapi_routes)
        unattempted = [
            {"method": method, "path": path}
            for method, path in sorted(openapi_set - attempted_set)
        ]
        summary = {
            "base_url": self.base_url,
            "generated_at": NOW.isoformat(),
            "openapi_route_count": len(self.openapi_routes),
            "attempted_route_count": len(attempted),
            "result_count": len(self.results),
            "ok_count": sum(1 for row in self.results if row.get("ok")),
            "fail_count": sum(1 for row in self.results if row.get("ok") is False and not row.get("skipped")),
            "skipped_count": sum(1 for row in self.results if row.get("skipped")),
            "unattempted_routes": unattempted,
        }
        return {"summary": summary, "results": self.results}


def main() -> None:
    sweep = ApiSweep(BASE_URL)
    payload = sweep.run()
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
    out_path = Path("qa") / f"api_http_sweep_results_{timestamp}.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(out_path)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
