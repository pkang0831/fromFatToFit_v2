from fastapi import APIRouter, Depends

from ..middleware.auth_middleware import get_current_user
from ..schemas.home_schemas import RetentionEventRequest
from ..services.retention_event_service import log_retention_event

router = APIRouter()


@router.post("/retention")
async def capture_retention_event(
    body: RetentionEventRequest,
    current_user: dict = Depends(get_current_user),
):
    await log_retention_event(
        current_user["id"],
        body.event_name,
        body.surface,
        body.properties,
    )
    return {"status": "ok"}
