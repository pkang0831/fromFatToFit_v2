"""Weight Tracking and Goal Projection Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from typing import List, Optional
from ..middleware.auth_middleware import get_current_user
from ..schemas.weight_schemas import (
    WeightLogCreate, WeightLogUpdate, WeightLogResponse,
    GoalUpdate, GoalProjectionResponse
)
from ..services.weight_tracking_service import WeightTrackingService
from ..rate_limit import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weight", tags=["Weight Tracking"])


@router.post("/log", response_model=WeightLogResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_weight_log(
    request: Request,
    log_data: WeightLogCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await WeightTrackingService.create_weight_log(user_id=current_user["id"], log_data=log_data)
    except Exception as e:
        logger.error(f"Error creating weight log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create weight log")


@router.get("/logs", response_model=List[WeightLogResponse])
@limiter.limit("60/minute")
async def get_weight_logs(
    request: Request,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await WeightTrackingService.get_weight_logs(user_id=current_user["id"], days=days)
    except Exception as e:
        logger.error(f"Error getting weight logs: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get weight logs")


@router.patch("/log/{log_id}", response_model=WeightLogResponse)
@limiter.limit("30/minute")
async def update_weight_log(
    request: Request,
    log_id: str,
    update_data: WeightLogUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await WeightTrackingService.update_weight_log(user_id=current_user["id"], log_id=log_id, update_data=update_data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weight log not found")
    except Exception as e:
        logger.error(f"Error updating weight log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update weight log")


@router.delete("/log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_weight_log(
    request: Request,
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        await WeightTrackingService.delete_weight_log(user_id=current_user["id"], log_id=log_id)
    except Exception as e:
        logger.error(f"Error deleting weight log: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete weight log")


@router.patch("/goals")
@limiter.limit("20/minute")
async def update_goals(
    request: Request,
    goals: GoalUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        return await WeightTrackingService.update_goals(user_id=current_user["id"], goals=goals)
    except Exception as e:
        logger.error(f"Error updating goals: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update goals")


@router.get("/projection", response_model=GoalProjectionResponse)
@limiter.limit("30/minute")
async def get_goal_projection(
    request: Request,
    days_history: int = 30,
    target_deficit: Optional[float] = Query(None, description="User-specified target caloric deficit in kcal/day"),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await WeightTrackingService.get_goal_projection(
            user_id=current_user["id"], days_history=days_history, target_deficit=target_deficit
        )
    except Exception as e:
        logger.error(f"Error getting projection: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get goal projection")
