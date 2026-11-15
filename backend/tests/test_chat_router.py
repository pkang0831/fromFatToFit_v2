import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.requests import Request


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _request() -> Request:
    return Request({
        "type": "http",
        "method": "POST",
        "path": "/api/chat/message",
        "headers": [],
        "query_string": b"",
    })


def test_get_chat_status_uses_reconciled_premium_truth():
    from app.domains.coach.router import get_chat_status, PRO_DAILY_LIMIT

    with (
        patch("app.domains.coach.router.check_premium_status", AsyncMock(return_value=True)),
        patch("app.domains.coach.router._count_today_messages", AsyncMock(return_value=4)),
    ):
        result = _run(get_chat_status({"id": "user-123", "premium_status": False}))

    assert result["daily_limit"] == PRO_DAILY_LIMIT
    assert result["remaining"] == PRO_DAILY_LIMIT - 4


def test_send_message_blocks_free_user_at_reconciled_limit():
    from app.domains.coach.router import send_message, ChatMessageRequest, FREE_DAILY_LIMIT

    with (
        patch("app.domains.coach.router.check_premium_status", AsyncMock(return_value=False)),
        patch("app.domains.coach.router._count_today_messages", AsyncMock(return_value=FREE_DAILY_LIMIT)),
    ):
        with pytest.raises(Exception) as exc_info:
            _run(send_message(
                request=_request(),
                chat_request=ChatMessageRequest(message="hello"),
                current_user={"id": "user-123", "premium_status": True},
            ))

    assert getattr(exc_info.value, "status_code", None) == 429


def test_send_message_uses_reconciled_premium_limit_for_paid_user():
    from app.domains.coach.router import send_message, ChatMessageRequest, PRO_DAILY_LIMIT

    with (
        patch("app.domains.coach.router.check_premium_status", AsyncMock(return_value=True)),
        patch("app.domains.coach.router._count_today_messages", AsyncMock(return_value=50)),
        patch("app.domains.coach.router.get_chat_history", AsyncMock(return_value=[])),
        patch("app.domains.coach.router.generate_answer", AsyncMock(return_value={"answer": "ok", "sources": []})),
        patch("app.domains.coach.router.save_message", AsyncMock()),
        ):
        result = _run(send_message(
            request=_request(),
            chat_request=ChatMessageRequest(message="hello"),
            current_user={"id": "user-123", "premium_status": False},
        ))

    assert result.daily_limit == PRO_DAILY_LIMIT
    assert result.messages_today == 51
