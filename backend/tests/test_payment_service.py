import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch


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
        self.operation = "select"
        self.filters = []
        self.payload = None
        self.on_conflict = None

    def select(self, *_args, **_kwargs):
        self.operation = "select"
        return self

    def eq(self, key, value):
        self.filters.append(lambda row, k=key, v=value: row.get(k) == v)
        return self

    def in_(self, key, values):
        accepted = set(values)
        self.filters.append(lambda row, k=key, allowed=accepted: row.get(k) in allowed)
        return self

    def update(self, payload):
        self.operation = "update"
        self.payload = dict(payload)
        return self

    def insert(self, payload):
        self.operation = "insert"
        self.payload = payload
        return self

    def upsert(self, payload, on_conflict=None):
        self.operation = "upsert"
        self.payload = payload
        self.on_conflict = on_conflict
        return self

    def execute(self):
        table = self.supabase.tables.setdefault(self.name, [])
        rows = [row for row in table if all(check(row) for check in self.filters)]

        if self.operation == "select":
            data = [dict(row) for row in rows]
        elif self.operation == "update":
            for row in rows:
                row.update(self.payload)
            data = [dict(row) for row in rows]
        elif self.operation == "insert":
            records = self.payload if isinstance(self.payload, list) else [self.payload]
            for record in records:
                table.append(dict(record))
            data = [dict(record) for record in records]
        elif self.operation == "upsert":
            records = self.payload if isinstance(self.payload, list) else [self.payload]
            conflict_keys = [key.strip() for key in (self.on_conflict or "id").split(",")]
            for record in records:
                existing = next(
                    (
                        row for row in table
                        if all(row.get(key) == record.get(key) for key in conflict_keys)
                    ),
                    None,
                )
                if existing:
                    existing.update(record)
                else:
                    table.append(dict(record))
            data = [dict(record) for record in records]
        else:
            raise AssertionError(f"Unsupported operation {self.operation}")

        self._reset()
        return _Result(data)


class _FakeSupabase:
    def __init__(self, tables):
        self.tables = {name: [dict(row) for row in rows] for name, rows in tables.items()}

    def table(self, name):
        return _FakeTable(self, name)


def _future_iso(days=30):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _past_iso(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def test_create_checkout_session_creates_and_links_stable_customer():
    from app.services.payment_service import create_checkout_session

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-123",
            "email": "user@example.com",
            "full_name": "Test User",
            "premium_status": False,
            "stripe_customer_id": None,
        }],
    })

    checkout_session = SimpleNamespace(id="cs_123", url="https://stripe.test/checkout")
    created_customer = SimpleNamespace(id="cus_123")

    with (
        patch("app.services.payment_service.get_supabase", return_value=supabase),
        patch("app.services.payment_service.stripe.Customer.create", return_value=created_customer) as create_customer,
        patch("app.services.payment_service.stripe.checkout.Session.create", return_value=checkout_session) as create_session,
    ):
        result = _run(create_checkout_session(
            user_id="user-123",
            price_id="price_123",
            success_url="https://app.test/success",
            cancel_url="https://app.test/cancel",
        ))

    assert result == {"session_id": "cs_123", "checkout_url": "https://stripe.test/checkout"}
    assert supabase.tables["user_profiles"][0]["stripe_customer_id"] == "cus_123"
    create_customer.assert_called_once()
    create_session.assert_called_once()
    assert create_session.call_args.kwargs["customer"] == "cus_123"
    assert create_session.call_args.kwargs["subscription_data"]["metadata"]["user_id"] == "user-123"


def test_handle_stripe_webhook_skips_duplicate_processed_event():
    from app.services.payment_service import handle_stripe_webhook

    supabase = _FakeSupabase({
        "stripe_webhook_events": [{
            "event_id": "evt_duplicate",
            "event_type": "checkout.session.completed",
            "processing_status": "processed",
            "processed_at": "2026-03-30T12:00:00+00:00",
        }],
    })

    event = {
        "id": "evt_duplicate",
        "type": "checkout.session.completed",
        "created": 1_700_000_000,
        "data": {
            "object": {
                "id": "cs_123",
                "client_reference_id": "user-123",
                "customer": "cus_123",
            }
        },
    }

    with (
        patch("app.services.payment_service.get_supabase", return_value=supabase),
        patch("app.services.payment_service.stripe.Webhook.construct_event", return_value=event),
        patch("app.services.payment_service.handle_checkout_completed", AsyncMock()) as handle_checkout,
    ):
        result = _run(handle_stripe_webhook(b"{}", "sig"))

    assert result["status"] == "duplicate"
    handle_checkout.assert_not_awaited()


def test_subscription_diagnostics_cancel_at_period_end_keeps_entitlement_but_allows_deletion():
    from app.services.payment_service import _derive_subscription_diagnostics

    diagnostics = _derive_subscription_diagnostics(
        {
            "user_id": "user-123",
            "premium_status": True,
            "stripe_customer_id": "cus_123",
        },
        [{
            "subscription_id": "sub_123",
            "user_id": "user-123",
            "subscription_type": "premium",
            "status": "active",
            "payment_provider": "stripe",
            "start_date": _past_iso(5),
            "end_date": _future_iso(10),
            "auto_renew": False,
            "cancel_at_period_end": True,
            "last_stripe_event_id": "evt_1",
            "last_stripe_event_type": "customer.subscription.updated",
            "last_webhook_processed_at": _future_iso(0),
        }],
    )

    assert diagnostics["premium_status"] is True
    assert diagnostics["deletion_blocked"] is False
    assert diagnostics["status"] == "active"
    assert diagnostics["cancel_at_period_end"] is True


def test_subscription_diagnostics_blocks_unresolved_billing_and_resume_state():
    from app.services.payment_service import _derive_subscription_diagnostics

    past_due = _derive_subscription_diagnostics(
        {
            "user_id": "user-123",
            "premium_status": True,
            "stripe_customer_id": "cus_123",
        },
        [{
            "subscription_id": "sub_123",
            "user_id": "user-123",
            "subscription_type": "premium",
            "status": "past_due",
            "payment_provider": "stripe",
            "start_date": _past_iso(20),
            "end_date": _future_iso(5),
            "auto_renew": True,
        }],
    )
    resumed = _derive_subscription_diagnostics(
        {
            "user_id": "user-123",
            "premium_status": False,
            "stripe_customer_id": "cus_123",
        },
        [{
            "subscription_id": "sub_123",
            "user_id": "user-123",
            "subscription_type": "premium",
            "status": "active",
            "payment_provider": "stripe",
            "start_date": _past_iso(2),
            "end_date": _future_iso(25),
            "auto_renew": True,
        }],
    )

    assert past_due["premium_status"] is True
    assert past_due["deletion_blocked"] is True
    assert past_due["deletion_block_reason"] == "unresolved_billing_requires_resolution"

    assert resumed["premium_status"] is True
    assert resumed["deletion_blocked"] is True
    assert resumed["deletion_block_reason"] == "active_billing_requires_cancellation"


def test_subscription_diagnostics_flags_profile_mismatch_without_subscription_row():
    from app.services.payment_service import _derive_subscription_diagnostics

    diagnostics = _derive_subscription_diagnostics(
        {
            "user_id": "user-123",
            "premium_status": True,
            "stripe_customer_id": "cus_123",
        },
        [],
    )

    assert diagnostics["status"] == "mismatch"
    assert diagnostics["premium_status"] is True
    assert diagnostics["deletion_blocked"] is True
    assert diagnostics["deletion_block_reason"] == "billing_state_mismatch_requires_reconciliation"
    assert diagnostics["billing_portal_available"] is True


def test_handle_subscription_updated_upserts_and_reconciles_profile_flag():
    from app.services.payment_service import handle_subscription_updated, get_subscription_diagnostics

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-123",
            "email": "user@example.com",
            "full_name": "Test User",
            "premium_status": False,
            "stripe_customer_id": None,
        }],
        "user_subscriptions": [],
    })

    subscription_data = {
        "id": "sub_123",
        "customer": "cus_123",
        "status": "active",
        "start_date": int((datetime.now(timezone.utc) - timedelta(days=2)).timestamp()),
        "current_period_start": int((datetime.now(timezone.utc) - timedelta(days=2)).timestamp()),
        "current_period_end": int((datetime.now(timezone.utc) + timedelta(days=28)).timestamp()),
        "cancel_at_period_end": False,
        "canceled_at": None,
        "metadata": {"user_id": "user-123"},
    }

    with patch("app.services.payment_service.get_supabase", return_value=supabase):
        _run(handle_subscription_updated(
            subscription_data,
            event_id="evt_sub_updated",
            event_created=int(datetime.now(timezone.utc).timestamp()),
        ))
        diagnostics = _run(get_subscription_diagnostics("user-123"))

    subscription_row = supabase.tables["user_subscriptions"][0]
    assert subscription_row["subscription_id"] == "sub_123"
    assert subscription_row["stripe_customer_id"] == "cus_123"
    assert subscription_row["auto_renew"] is True
    assert supabase.tables["user_profiles"][0]["premium_status"] is True
    assert supabase.tables["user_profiles"][0]["stripe_customer_id"] == "cus_123"
    assert diagnostics["premium_status"] is True
    assert diagnostics["deletion_blocked"] is True


def test_handle_checkout_completed_subscription_awards_upgrade_delta_after_reconciliation():
    from app.services.payment_service import handle_checkout_completed

    supabase = _FakeSupabase({
        "user_profiles": [{
            "user_id": "user-123",
            "email": "user@example.com",
            "full_name": "Test User",
            "premium_status": False,
            "stripe_customer_id": None,
        }],
        "user_subscriptions": [],
    })
    add_credits = AsyncMock(return_value={"total_credits": 100})
    log_event = AsyncMock()
    subscription = {
        "id": "sub_123",
        "customer": "cus_123",
        "status": "active",
        "start_date": int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp()),
        "current_period_start": int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp()),
        "current_period_end": int((datetime.now(timezone.utc) + timedelta(days=29)).timestamp()),
        "cancel_at_period_end": False,
        "metadata": {"user_id": "user-123"},
    }
    session_data = {
        "id": "cs_123",
        "client_reference_id": "user-123",
        "customer": "cus_123",
        "subscription": "sub_123",
        "metadata": {"purchase_type": "subscription", "source": "proof_share"},
    }

    with (
        patch("app.services.payment_service.get_supabase", return_value=supabase),
        patch("app.services.payment_service.stripe.Subscription.retrieve", return_value=subscription),
        patch("app.services.usage_limiter.add_credits", add_credits),
        patch("app.services.payment_service.log_retention_event", log_event),
    ):
        _run(handle_checkout_completed(session_data, event_id="evt_checkout", event_created=int(datetime.now(timezone.utc).timestamp())))

    add_credits.assert_awaited_once_with("user-123", 90, credit_type="monthly")
    assert supabase.tables["user_profiles"][0]["premium_status"] is True
    log_event.assert_awaited_once()
    assert log_event.await_args.args[0] == "user-123"
    assert log_event.await_args.args[1] == "purchase_completed"
    assert log_event.await_args.args[3]["source"] == "proof_share"
    assert log_event.await_args.args[3]["subscription_id"] == "sub_123"


def test_verify_purchase_logs_deduped_purchase_completed_event():
    from app.routers.payments import verify_purchase
    from app.schemas.payment_schemas import VerifyPurchaseRequest

    log_event = AsyncMock()

    with (
        patch("app.routers.payments.verify_revenuecat_purchase", AsyncMock(return_value={
            "is_valid": True,
            "status": "active",
            "entitlement_id": "premium_access",
            "start_date": "2026-03-31T00:00:00Z",
            "end_date": "2026-04-30T00:00:00Z",
            "auto_renew": True,
        })),
        patch("app.routers.payments._upsert_external_subscription", AsyncMock()),
        patch("app.routers.payments.get_subscription_diagnostics", AsyncMock(return_value={"premium_status": True, "deletion_blocked": True})),
        patch("app.routers.payments.log_retention_event", log_event),
    ):
        _run(verify_purchase(
            VerifyPurchaseRequest(receipt_token="receipt-1", platform="ios"),
            {"id": "user-1"},
        ))

    log_event.assert_awaited_once()
    assert log_event.await_args.args[1] == "purchase_completed"
    assert log_event.await_args.args[3]["dedupe_key"] == "revenuecat_ios:revenuecat:ios:user-1:premium_access:2026-03-31T00:00:00Z"
