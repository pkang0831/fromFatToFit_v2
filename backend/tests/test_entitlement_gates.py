import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

from starlette.requests import Request


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _request(path: str) -> Request:
    return Request({
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": [],
        "query_string": b"",
    })


def _future_iso(days: int = 30) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def test_check_premium_status_never_grants_from_stale_profile_fallback():
    from app.services.payment_service import check_premium_status

    with patch(
        "app.services.payment_service.get_subscription_diagnostics",
        AsyncMock(side_effect=RuntimeError("diagnostics unavailable")),
    ):
        result = _run(check_premium_status("user-123"))

    assert result is False


def test_verify_purchase_upserts_revenuecat_subscription_and_returns_reconciled_truth():
    from app.routers.payments import verify_purchase
    from app.schemas.payment_schemas import VerifyPurchaseRequest

    with (
        patch(
            "app.routers.payments.verify_revenuecat_purchase",
            AsyncMock(return_value={
                "is_valid": True,
                "status": "active",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "end_date": _future_iso(),
                "auto_renew": True,
                "entitlement_id": "premium_access",
            }),
        ),
        patch("app.routers.payments._upsert_external_subscription", AsyncMock()) as upsert_external,
        patch(
            "app.routers.payments.get_subscription_diagnostics",
            AsyncMock(return_value={
                "premium_status": True,
                "deletion_blocked": True,
                "deletion_block_reason": "active_billing_requires_cancellation",
                "entitlement_source": "subscription_record",
            }),
        ),
    ):
        result = _run(verify_purchase(
            VerifyPurchaseRequest(receipt_token="receipt-123", platform="ios"),
            current_user={"id": "user-123"},
        ))

    upsert_external.assert_awaited_once()
    assert upsert_external.await_args.kwargs["provider"] == "revenuecat_ios"
    assert upsert_external.await_args.kwargs["subscription_id"] == "revenuecat:ios:user-123:premium_access"
    assert result["premium_status"] is True
    assert result["deletion_block_reason"] == "active_billing_requires_cancellation"


def test_beauty_gate_reads_authoritative_subscription_truth_for_credit_balance():
    from app.routers.beauty import analyze_beauty, BeautyAnalyzeRequest

    with (
        patch("app.routers.beauty.check_premium_status", AsyncMock(return_value=True)),
        patch("app.routers.beauty.get_credit_balance", AsyncMock(return_value={"total_credits": 100})) as get_balance,
        patch("app.routers.beauty.beauty_service.analyze_face", AsyncMock(return_value={"styling_suggestions": []})),
        patch("app.routers.beauty.deduct_credits", AsyncMock()),
    ):
        _run(analyze_beauty(
            request=_request("/api/beauty/analyze"),
            body=BeautyAnalyzeRequest(image_base64="ZmFrZQ==", gender="female", generate_images=False),
            user={"id": "user-123"},
        ))

    get_balance.assert_awaited_once_with("user-123", True)


def test_fashion_gate_reads_authoritative_subscription_truth_for_credit_balance():
    from app.routers.fashion import recommend_fashion, FashionRecommendRequest

    with (
        patch("app.routers.fashion.check_premium_status", AsyncMock(return_value=False)),
        patch("app.routers.fashion.get_credit_balance", AsyncMock(return_value={"total_credits": 100})) as get_balance,
        patch("app.routers.fashion.fashion_service.recommend_outfits", AsyncMock(return_value={"outfits": []})),
        patch("app.routers.fashion.deduct_credits", AsyncMock()),
    ):
        _run(recommend_fashion(
            request=_request("/api/fashion/recommend"),
            body=FashionRecommendRequest(season="summer", gender="female", image_base64=None, generate_images=False),
            user={"id": "user-123"},
        ))

    get_balance.assert_awaited_once_with("user-123", False)
