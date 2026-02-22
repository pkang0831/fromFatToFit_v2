from fastapi import APIRouter, HTTPException, status, Depends
import logging
from typing import Dict, Any
from ..middleware.auth_middleware import get_current_user
from ..services.notification_service import (
    get_notification_preferences,
    update_notification_preferences,
    save_push_subscription,
    remove_push_subscription,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/preferences")
async def get_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's notification preferences"""
    try:
        prefs = await get_notification_preferences(current_user["id"])
        return prefs
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification preferences"
        )


@router.put("/preferences")
async def update_preferences(
    updates: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update user's notification preferences"""
    try:
        prefs = await update_notification_preferences(current_user["id"], updates)
        return prefs
    except Exception as e:
        logger.error(f"Error updating notification preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.post("/push/subscribe")
async def subscribe_push(
    subscription: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Register a push notification subscription"""
    try:
        result = await save_push_subscription(current_user["id"], subscription)
        return result
    except Exception as e:
        logger.error(f"Error subscribing to push: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe to push notifications"
        )


@router.post("/push/unsubscribe")
async def unsubscribe_push(
    data: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """Unsubscribe from push notifications"""
    try:
        endpoint = data.get("endpoint", "")
        result = await remove_push_subscription(current_user["id"], endpoint)
        return result
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe from push notifications"
        )
