"""
Weight Tracking and Goal Projection Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..middleware.auth_middleware import get_current_user
from ..schemas.weight_schemas import (
    WeightLogCreate,
    WeightLogUpdate,
    WeightLogResponse,
    GoalUpdate,
    GoalProjectionResponse
)
from ..services.weight_tracking_service import WeightTrackingService

router = APIRouter(prefix="/weight", tags=["Weight Tracking"])


@router.post("/log", response_model=WeightLogResponse, status_code=status.HTTP_201_CREATED)
async def create_weight_log(
    log_data: WeightLogCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create or update a weight log entry"""
    try:
        return await WeightTrackingService.create_weight_log(
            user_id=current_user["id"],
            log_data=log_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logs", response_model=List[WeightLogResponse])
async def get_weight_logs(
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get weight logs for specified number of days"""
    try:
        return await WeightTrackingService.get_weight_logs(
            user_id=current_user["id"],
            days=days
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/log/{log_id}", response_model=WeightLogResponse)
async def update_weight_log(
    log_id: str,
    update_data: WeightLogUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing weight log"""
    try:
        return await WeightTrackingService.update_weight_log(
            user_id=current_user["id"],
            log_id=log_id,
            update_data=update_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/log/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weight_log(
    log_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a weight log"""
    try:
        await WeightTrackingService.delete_weight_log(
            user_id=current_user["id"],
            log_id=log_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/goals")
async def update_goals(
    goals: GoalUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update weight and body fat goals"""
    try:
        return await WeightTrackingService.update_goals(
            user_id=current_user["id"],
            goals=goals
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/projection", response_model=GoalProjectionResponse)
async def get_goal_projection(
    days_history: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """
    Get goal projection based on current trends
    
    Returns:
    - Historical weight/body fat data with 3-day moving average
    - Current rate of change
    - Estimated days to reach goal
    - Future projection
    """
    try:
        return await WeightTrackingService.get_goal_projection(
            user_id=current_user["id"],
            days_history=days_history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
