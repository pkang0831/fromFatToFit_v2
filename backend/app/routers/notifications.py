from fastapi import APIRouter, HTTPException, Request, status, Depends, Response
from fastapi.responses import RedirectResponse, HTMLResponse
import logging
from typing import Dict, Any
from ..middleware.auth_middleware import get_current_user
from ..services.notification_service import (
    get_notification_preferences, update_notification_preferences,
    save_push_subscription, remove_push_subscription,
    get_weekly_proof_reminder_status_for_user, mark_weekly_proof_reminder_opened,
    process_resend_webhook, unsubscribe_weekly_proof_reminder,
)
from ..rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/preferences")
@limiter.limit("30/minute")
async def get_preferences(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        prefs = await get_notification_preferences(current_user["id"])
        return prefs
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get notification preferences")


@router.get("/reminder-status")
@limiter.limit("30/minute")
async def get_reminder_status(request: Request, current_user: dict = Depends(get_current_user)):
    return await get_weekly_proof_reminder_status_for_user(current_user["id"])


@router.put("/preferences")
@limiter.limit("20/minute")
async def update_preferences(request: Request, updates: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    try:
        prefs = await update_notification_preferences(current_user["id"], updates)
        return prefs
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update notification preferences")


@router.post("/push/subscribe")
@limiter.limit("10/minute")
async def subscribe_push(request: Request, subscription: Dict[str, Any], current_user: dict = Depends(get_current_user)):
    try:
        result = await save_push_subscription(
            current_user["id"],
            subscription,
            access_token=current_user.get("access_token"),
        )
        return result
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to subscribe to push notifications")


@router.post("/push/unsubscribe")
@limiter.limit("10/minute")
async def unsubscribe_push(request: Request, data: Dict[str, str], current_user: dict = Depends(get_current_user)):
    try:
        endpoint = data.get("endpoint", "")
        result = await remove_push_subscription(
            current_user["id"],
            endpoint,
            access_token=current_user.get("access_token"),
        )
        return result
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unsubscribe from push notifications")


@router.get("/reminders/open/{reminder_event_id}")
@limiter.limit("60/minute")
async def open_weekly_proof_reminder(request: Request, reminder_event_id: str, next: str = "/home"):
    try:
        redirect_url = await mark_weekly_proof_reminder_opened(reminder_event_id, next)
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    except LookupError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder link is no longer valid")
    except Exception as e:
        logger.error(f"Error opening reminder {reminder_event_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to open reminder link")


@router.get("/reminders/unsubscribe/{reminder_event_id}")
@limiter.limit("60/minute")
async def unsubscribe_weekly_proof_reminder_get(request: Request, reminder_event_id: str):
    try:
        result = await unsubscribe_weekly_proof_reminder(reminder_event_id)
        if result["status"] == "not_found":
            return HTMLResponse("<html><body><p>This reminder link is no longer valid.</p></body></html>", status_code=404)
        return HTMLResponse(
            "<html><body><p>Weekly proof reminder emails have been turned off for this account.</p></body></html>",
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error unsubscribing reminder {reminder_event_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unsubscribe from reminder emails")


@router.post("/reminders/unsubscribe/{reminder_event_id}")
@limiter.limit("60/minute")
async def unsubscribe_weekly_proof_reminder_post(request: Request, reminder_event_id: str):
    try:
        result = await unsubscribe_weekly_proof_reminder(reminder_event_id)
        if result["status"] == "not_found":
            return Response(status_code=404)
        return Response(status_code=202)
    except Exception as e:
        logger.error(f"Error handling one-click unsubscribe for reminder {reminder_event_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process reminder unsubscribe")


@router.post("/webhooks/resend")
async def resend_webhook(request: Request):
    try:
        payload = await request.body()
        result = await process_resend_webhook(payload.decode("utf-8"), request.headers)
        return result
    except ValueError as e:
        logger.error(f"Invalid Resend webhook: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")
    except Exception as e:
        logger.error(f"Error processing Resend webhook: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process webhook")
