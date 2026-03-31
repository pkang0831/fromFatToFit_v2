import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_get_notification_preferences_normalizes_legacy_row():
    from app.services.notification_service import get_notification_preferences

    result = MagicMock()
    result.data = [{
        "user_id": "user-123",
        "email_enabled": False,
        "push_enabled": True,
        "weekly_report": False,
    }]

    chain = MagicMock()
    chain.select.return_value = chain
    chain.eq.return_value = chain
    chain.execute.return_value = result

    supabase = MagicMock()
    supabase.table.return_value = chain

    with patch("app.services.notification_service.get_supabase", return_value=supabase):
        prefs = _run(get_notification_preferences("user-123"))

    assert prefs["email_weekly_summary"] is False
    assert prefs["email_inactivity_reminder"] is False
    assert prefs["email_credit_low"] is False
    assert prefs["push_weekly_body_scan"] is True
    assert prefs["push_meal_reminder"] is True


def test_update_notification_preferences_falls_back_to_legacy_columns():
    from app.services.notification_service import update_notification_preferences

    update_chain = MagicMock()
    update_chain.eq.return_value = update_chain
    update_chain.execute.side_effect = [Exception("column email_weekly_summary does not exist"), MagicMock()]

    table_chain = MagicMock()
    table_chain.update.return_value = update_chain

    supabase = MagicMock()
    supabase.table.return_value = table_chain

    with (
        patch("app.services.notification_service.get_supabase", return_value=supabase),
        patch(
            "app.services.notification_service.get_notification_preferences",
            AsyncMock(side_effect=[
                {
                    "email_weekly_summary": True,
                    "email_inactivity_reminder": True,
                    "email_credit_low": True,
                    "push_meal_reminder": True,
                    "push_workout_reminder": True,
                    "push_daily_summary": False,
                    "push_weekly_body_scan": True,
                    "meal_reminder_time": "12:00",
                    "workout_reminder_days": ["monday", "wednesday", "friday"],
                },
                {
                    "email_weekly_summary": False,
                    "email_inactivity_reminder": True,
                    "email_credit_low": True,
                    "push_meal_reminder": True,
                    "push_workout_reminder": True,
                    "push_daily_summary": False,
                    "push_weekly_body_scan": True,
                    "meal_reminder_time": "12:00",
                    "workout_reminder_days": ["monday", "wednesday", "friday"],
                },
            ]),
        ),
    ):
        prefs = _run(update_notification_preferences("user-123", {"email_weekly_summary": False}))

    assert prefs["email_weekly_summary"] is False

    first_update = table_chain.update.call_args_list[0].args[0]
    second_update = table_chain.update.call_args_list[1].args[0]

    assert "email_weekly_summary" in first_update
    assert second_update["weekly_report"] is False
