import asyncio
import base64
import hashlib
import hmac
from datetime import datetime, timezone
from math import floor
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import status
from starlette.requests import Request


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _summary(entry_state: str, scan_count: int = 1):
    return SimpleNamespace(
        entry_state=entry_state,
        scan_summary=SimpleNamespace(scan_count=scan_count),
    )


def test_build_weekly_proof_reminder_path_matches_supported_states():
    from app.services.notification_service import build_weekly_proof_reminder_path

    assert build_weekly_proof_reminder_path("progress_proof") == "/progress?tab=photos&focus=upload&from=weekly_reminder"
    assert build_weekly_proof_reminder_path("weekly_scan") == "/body-scan?tab=journey&from=weekly_reminder#transformation"


def test_weekly_proof_candidate_allows_opted_in_progress_proof_user():
    from app.services.notification_service import _build_weekly_proof_candidate

    candidate = _build_weekly_proof_candidate(
        profile={"user_id": "user-1", "email": "user@example.com", "onboarding_completed": True},
        prefs={"email_weekly_summary": True},
        summary=_summary("progress_proof", scan_count=2),
        last_event=None,
        now=__import__("datetime").datetime(2026, 3, 31, tzinfo=__import__("datetime").timezone.utc),
    )

    assert candidate is not None
    assert candidate["entry_state"] == "progress_proof"
    assert candidate["next_path"] == "/progress?tab=photos&focus=upload&from=weekly_reminder"
    assert candidate["channel"] == "email"


def test_weekly_proof_candidate_respects_opt_out():
    from app.services.notification_service import _build_weekly_proof_candidate

    candidate = _build_weekly_proof_candidate(
        profile={"user_id": "user-1", "email": "user@example.com", "onboarding_completed": True},
        prefs={"email_weekly_summary": False},
        summary=_summary("progress_proof", scan_count=2),
        last_event=None,
        now=__import__("datetime").datetime(2026, 3, 31, tzinfo=__import__("datetime").timezone.utc),
    )

    assert candidate is None


def test_weekly_proof_candidate_excludes_deleted_user():
    from app.services.notification_service import _build_weekly_proof_candidate

    candidate = _build_weekly_proof_candidate(
        profile={
            "user_id": "user-1",
            "email": "user@example.com",
            "onboarding_completed": True,
            "deleted_at": "2026-03-31T00:00:00+00:00",
        },
        prefs={"email_weekly_summary": True},
        summary=_summary("progress_proof", scan_count=2),
        last_event=None,
        now=__import__("datetime").datetime(2026, 3, 31, tzinfo=__import__("datetime").timezone.utc),
    )

    assert candidate is None


def test_weekly_proof_candidate_respects_cooldown():
    from app.services.notification_service import _build_weekly_proof_candidate
    from app.config import settings

    now = __import__("datetime").datetime(2026, 3, 31, tzinfo=__import__("datetime").timezone.utc)
    recent_sent = {"sent_at": "2026-03-29T12:00:00+00:00", "status": "sent"}

    with patch.object(settings, "weekly_proof_reminder_cooldown_hours", 72):
        candidate = _build_weekly_proof_candidate(
            profile={"user_id": "user-1", "email": "user@example.com", "onboarding_completed": True},
            prefs={"email_weekly_summary": True},
            summary=_summary("weekly_scan", scan_count=3),
            last_event=recent_sent,
            now=now,
        )

    assert candidate is None


def test_weekly_proof_status_requires_provider_readiness():
    from app.services.notification_service import get_weekly_proof_reminder_status
    from app.config import settings

    with (
        patch.object(settings, "enable_weekly_proof_reminders", True),
        patch.object(settings, "weekly_proof_reminder_provider_ready", False),
        patch.object(settings, "weekly_proof_reminder_channel", "email"),
    ):
        status = get_weekly_proof_reminder_status()

    assert status["active"] is False
    assert status["reason"] == "provider_not_ready"


def test_evaluate_weekly_proof_reminder_candidates_filters_ineligible_users():
    from app.services.notification_service import evaluate_weekly_proof_reminder_candidates

    with (
        patch("app.services.notification_service.get_weekly_proof_reminder_status", return_value={"active": True, "channel": "email", "reason": None}),
        patch("app.services.notification_service._list_candidate_profiles", return_value=[
            {"user_id": "eligible-user", "email": "eligible@example.com", "onboarding_completed": True},
            {"user_id": "no-email", "email": "", "onboarding_completed": True},
            {"user_id": "no-scan", "email": "noscan@example.com", "onboarding_completed": True},
        ]),
        patch(
            "app.services.notification_service.get_notification_preferences",
            AsyncMock(side_effect=[
                {"email_weekly_summary": True},
                {"email_weekly_summary": True},
                {"email_weekly_summary": True},
            ]),
        ),
        patch(
            "app.services.notification_service._get_home_summary_for_user",
            AsyncMock(side_effect=[
                _summary("progress_proof", scan_count=1),
                _summary("progress_proof", scan_count=1),
                _summary("progress_proof", scan_count=0),
            ]),
        ),
        patch("app.services.notification_service._get_latest_weekly_reminder_event", return_value=None),
    ):
        candidates = _run(evaluate_weekly_proof_reminder_candidates())

    assert len(candidates) == 1
    assert candidates[0]["user_id"] == "eligible-user"


def test_send_weekly_proof_email_builds_tracking_link_and_returns_message_id():
    from app.services.notification_service import _send_weekly_proof_email
    from app.config import settings

    candidate = {
        "email": "user@example.com",
        "subject": "Upload proof",
        "headline": "Headline",
        "body": "Body",
        "next_path": "/progress?tab=photos&focus=upload&from=weekly_reminder",
    }

    with (
        patch.object(settings, "public_api_url", "https://api.denevira.test/api"),
        patch.object(settings, "smtp_from_email", "hello@denevira.test"),
        patch("app.services.notification_service.asyncio.to_thread", AsyncMock(return_value=None)) as to_thread,
    ):
        provider_message_id = _run(_send_weekly_proof_email(candidate, "event-1"))

    assert provider_message_id.startswith("<")
    sent_message = to_thread.call_args.args[1]
    assert "event-1" in sent_message.get_body(preferencelist=("plain",)).get_content()
    assert "https://api.denevira.test/api/notifications/reminders/open/event-1" in sent_message.get_body(preferencelist=("html",)).get_content()
    assert sent_message["List-Unsubscribe"] == "<https://api.denevira.test/api/notifications/reminders/unsubscribe/event-1>"
    assert sent_message["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"


def test_run_weekly_proof_reminder_job_marks_sent_and_logs_analytics():
    from app.services.notification_service import run_weekly_proof_reminder_job

    candidate = {
        "user_id": "user-1",
        "email": "user@example.com",
        "channel": "email",
        "entry_state": "progress_proof",
        "next_path": "/progress?tab=photos&focus=upload&from=weekly_reminder",
        "subject": "Upload proof",
        "headline": "Headline",
        "body": "Body",
    }

    with (
        patch("app.services.notification_service.get_weekly_proof_reminder_status", return_value={"active": True, "channel": "email", "reason": None}),
        patch("app.services.notification_service._claim_weekly_proof_job_run", return_value={"job_key": "weekly_proof:123"}),
        patch("app.services.notification_service._finish_weekly_proof_job_run") as finish_job,
        patch("app.services.notification_service.evaluate_weekly_proof_reminder_candidates", AsyncMock(return_value=[candidate])),
        patch("app.services.notification_service._create_reminder_event", return_value={"id": "event-1"}),
        patch("app.services.notification_service._send_weekly_proof_email", AsyncMock(return_value="<message-id>")),
        patch("app.services.notification_service._update_reminder_event") as update_event,
        patch("app.services.notification_service.log_retention_event", AsyncMock()) as log_event,
    ):
        result = _run(run_weekly_proof_reminder_job())

    assert result["sent"] == 1
    assert result["failed"] == 0
    assert update_event.call_args_list[0].args[1]["status"] == "sending"
    assert update_event.call_args_list[1].args[1]["status"] == "sent"
    assert update_event.call_args.args[0] == "event-1"
    assert update_event.call_args.args[1]["status"] == "sent"
    log_event.assert_awaited_once()
    assert log_event.await_args.args[1] == "notification_sent"
    finish_job.assert_called_once()


def test_run_weekly_proof_reminder_job_skips_when_already_claimed():
    from app.services.notification_service import run_weekly_proof_reminder_job

    with (
        patch("app.services.notification_service.get_weekly_proof_reminder_status", return_value={"active": True, "channel": "email", "reason": None}),
        patch("app.services.notification_service._claim_weekly_proof_job_run", return_value=None),
        patch("app.services.notification_service.evaluate_weekly_proof_reminder_candidates", AsyncMock()) as evaluate_candidates,
    ):
        result = _run(run_weekly_proof_reminder_job())

    assert result["skipped"] is True
    assert result["reason"] == "job_already_claimed"
    evaluate_candidates.assert_not_awaited()


def test_open_weekly_proof_reminder_marks_open_and_redirects():
    from app.routers.notifications import open_weekly_proof_reminder
    request = Request({"type": "http", "method": "GET", "path": "/api/notifications/reminders/open/event-1", "headers": []})

    with patch(
        "app.routers.notifications.mark_weekly_proof_reminder_opened",
        AsyncMock(return_value="https://app.denevira.test/progress?tab=photos&focus=upload&from=weekly_reminder"),
    ) as mark_opened:
        response = _run(open_weekly_proof_reminder(request, "event-1", "/progress?tab=photos&focus=upload&from=weekly_reminder"))

    mark_opened.assert_awaited_once()
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == "https://app.denevira.test/progress?tab=photos&focus=upload&from=weekly_reminder"


def test_mark_weekly_proof_reminder_opened_updates_event_and_logs():
    from app.services.notification_service import mark_weekly_proof_reminder_opened
    from app.config import settings

    with (
        patch.object(settings, "public_app_url", "https://app.denevira.test"),
        patch(
            "app.services.notification_service._get_reminder_event",
            return_value={"id": "event-1", "user_id": "user-1", "channel": "email", "entry_state": "weekly_scan"},
        ),
        patch("app.services.notification_service._update_reminder_event") as update_event,
        patch("app.services.notification_service.log_retention_event", AsyncMock()) as log_event,
    ):
        redirect_url = _run(mark_weekly_proof_reminder_opened("event-1", "/body-scan?tab=journey&from=weekly_reminder#transformation"))

    assert redirect_url == "https://app.denevira.test/body-scan?tab=journey&from=weekly_reminder#transformation"
    update_event.assert_called_once()
    assert update_event.call_args.args[1]["status"] == "clicked"
    log_event.assert_awaited_once()
    assert log_event.await_args.args[1] == "notification_opened"


def test_process_resend_webhook_updates_delivered_status():
    from app.services.notification_service import process_resend_webhook

    payload = {
        "type": "email.delivered",
        "created_at": "2026-03-31T12:00:00+00:00",
        "data": {
            "to": ["user@example.com"],
            "email_id": "email_123",
        },
    }

    with (
        patch("app.services.notification_service.verify_resend_webhook", return_value=payload),
        patch("app.services.notification_service._record_reminder_webhook_event", return_value={"svix_id": "msg_1"}),
        patch(
            "app.services.notification_service._resolve_reminder_event_for_webhook",
            return_value={"id": "event-1", "user_id": "user-1", "status": "sent", "recipient_email": "user@example.com"},
        ),
        patch("app.services.notification_service._update_reminder_event") as update_event,
        patch("app.services.notification_service._update_reminder_webhook_event") as update_webhook_event,
    ):
        result = _run(process_resend_webhook("{}", {"svix-id": "msg_1"}))

    assert result["status"] == "processed"
    assert result["event_type"] == "email.delivered"
    assert update_event.call_args.args[0] == "event-1"
    assert update_event.call_args.args[1]["status"] == "delivered"
    assert update_event.call_args.args[1]["provider_email_id"] == "email_123"
    assert update_webhook_event.call_args.args[1]["processing_status"] == "processed"


def test_process_resend_webhook_updates_opt_out_on_unsubscribe():
    from app.services.notification_service import process_resend_webhook

    payload = {
        "type": "contact.updated",
        "created_at": "2026-03-31T12:00:00+00:00",
        "data": {
            "email": "user@example.com",
            "unsubscribed": True,
        },
    }

    with (
        patch("app.services.notification_service.verify_resend_webhook", return_value=payload),
        patch("app.services.notification_service._record_reminder_webhook_event", return_value={"svix_id": "msg_2"}),
        patch(
            "app.services.notification_service._resolve_reminder_event_for_webhook",
            return_value={"id": "event-2", "user_id": "user-2", "status": "sent", "recipient_email": "user@example.com"},
        ),
        patch("app.services.notification_service._update_reminder_event") as update_event,
        patch("app.services.notification_service._disable_weekly_proof_reminders_for_user", AsyncMock()) as disable_prefs,
        patch("app.services.notification_service._update_reminder_webhook_event") as update_webhook_event,
    ):
        result = _run(process_resend_webhook("{}", {"svix-id": "msg_2"}))

    assert result["status"] == "processed"
    assert update_event.call_args.args[1]["status"] == "unsubscribed"
    disable_prefs.assert_awaited_once_with("user-2")
    assert update_webhook_event.call_args.args[1]["processing_status"] == "processed"


def test_process_resend_webhook_ignores_duplicate_svix_id():
    from app.services.notification_service import process_resend_webhook

    payload = {
        "type": "email.delivered",
        "data": {"to": ["user@example.com"], "email_id": "email_123"},
    }

    with (
        patch("app.services.notification_service.verify_resend_webhook", return_value=payload),
        patch("app.services.notification_service._record_reminder_webhook_event", return_value=None),
        patch("app.services.notification_service._resolve_reminder_event_for_webhook") as resolve_event,
    ):
        result = _run(process_resend_webhook("{}", {"svix-id": "msg_dup"}))

    assert result["status"] == "duplicate"
    resolve_event.assert_not_called()


def test_process_resend_webhook_surfaces_verification_cause():
    import pytest

    from app.services.notification_service import process_resend_webhook

    with patch(
        "app.services.notification_service.verify_resend_webhook",
        side_effect=RuntimeError("No matching signature found"),
    ):
        with pytest.raises(ValueError) as exc_info:
            _run(process_resend_webhook("{}", {"svix-id": "msg_bad"}))

    assert str(exc_info.value) == "invalid_webhook_signature:RuntimeError:No matching signature found"


def test_verify_resend_webhook_accepts_webhook_header_names():
    from app.services.notification_service import verify_resend_webhook
    from app.config import settings

    payload = '{"type":"email.sent"}'
    timestamp = datetime(2026, 3, 31, 20, 0, 0, tzinfo=timezone.utc)
    timestamp_str = str(floor(timestamp.timestamp()))
    secret = "whsec_ZmFrZV9yZXNlbmRfc2VjcmV0X2tleQ=="
    secret_bytes = base64.b64decode("ZmFrZV9yZXNlbmRfc2VjcmV0X2tleQ==")
    msg_id = "msg_123"
    signature = base64.b64encode(
        hmac.new(
            secret_bytes,
            f"{msg_id}.{timestamp_str}.{payload}".encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    headers = {
        "webhook-id": msg_id,
        "webhook-timestamp": timestamp_str,
        "webhook-signature": f"v1,{signature}",
    }

    frozen_now = datetime(2026, 3, 31, 20, 0, 30, tzinfo=timezone.utc)

    with (
        patch.object(settings, "resend_webhook_secret", secret),
        patch("app.services.notification_service.datetime") as mock_datetime,
    ):
        mock_datetime.now.return_value = frozen_now
        mock_datetime.fromtimestamp.side_effect = datetime.fromtimestamp
        mock_datetime.fromisoformat.side_effect = datetime.fromisoformat
        result = verify_resend_webhook(payload, headers)

    assert result["type"] == "email.sent"
