from fastapi import APIRouter, HTTPException, Request, status, Depends
import logging
from typing import Dict, Any
from ..middleware.auth_middleware import get_current_user
from ..services.notification_service import (
    get_notification_preferences, update_notification_preferences,
    save_push_subscription, remove_push_subscription,
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
        result = await save_push_subscription(current_user["id"], subscription)
        return result
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to subscribe to push notifications")


@router.post("/push/unsubscribe")
@limiter.limit("10/minute")
async def unsubscribe_push(request: Request, data: Dict[str, str], current_user: dict = Depends(get_current_user)):
    try:
        endpoint = data.get("endpoint", "")
        result = await remove_push_subscription(current_user["id"], endpoint)
        return result
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to unsubscribe from push notifications")
