from fastapi import APIRouter, HTTPException, status, Depends
from starlette.requests import Request
import logging
import json
from datetime import datetime, timezone
from app.domains.body.schemas import (
    SegmentRequest,
    SegmentResponse,
    RegionTransformRequest,
    RegionTransformResponse,
    AutoSegmentRequest,
    AutoSegmentResponse,
    SegClassInfo,
    CandidateSegmentInfo,
)
from app.core.database import get_supabase
from app.core.auth import get_current_user
from app.integrations.replicate import image_models
from app.integrations.replicate.sam import segment_body_part
from app.domains.billing.usage import get_credit_balance
from app.domains.billing.service import check_premium_status, deduct_credits
from app.core.rate_limit import limiter

from app.domains.body.common import (
    raise_body_unavailable,
    require_safe_body_photo,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/auto-segment", response_model=AutoSegmentResponse)
@limiter.limit("3/minute")
async def auto_segment_body(
    request: Request,
    seg_request: AutoSegmentRequest,
):
    """Run SAM2 auto-segmentation and return a semantic label map.

    The label map is a grayscale PNG at original resolution where each
    pixel value is a class ID (0=background, 1-7=body parts).
    left/right = person's anatomical left/right.
    """
    try:
        from app.vision.human_parser import FashnHumanParserSegmenter

        segmenter = FashnHumanParserSegmenter()
        result = await segmenter.segment(seg_request.image_base64)

        return AutoSegmentResponse(
            width=result.width,
            height=result.height,
            label_map_base64=result.label_map_b64,
            foreground_mask_base64=result.foreground_mask_b64,
            editable_region_base64=result.editable_region_b64,
            classes=[SegClassInfo(**c) for c in result.classes],
            candidate_segments=[
                CandidateSegmentInfo(**seg)
                for seg in result.candidate_segments
            ],
            debug_info=result.debug_info,
        )

    except Exception as e:
        logger.error(f"Auto-segmentation error: {e}", exc_info=True)
        raise_body_unavailable(e, default_detail="Auto-segmentation failed. Please try again.")


@router.post("/segment", response_model=SegmentResponse)
@limiter.limit("10/minute")
async def segment_body(
    request: Request,
    seg_request: SegmentRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Segment a body part using SAM-2. User clicks on the image and receives
    a binary mask for that region. Free to call (no credits deducted).
    """
    try:
        result = await segment_body_part(
            image_base64=seg_request.image_base64,
            click_x_norm=seg_request.click_x,
            click_y_norm=seg_request.click_y,
        )
        return SegmentResponse(**result)

    except Exception as e:
        if isinstance(e, (ValueError, IndexError, json.JSONDecodeError, RuntimeError)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Body segmentation failed for this image. Try a clearer photo or a different click point.",
            )
        logger.error(f"SAM segmentation error: {e}")
        raise_body_unavailable(e, default_detail="Body segmentation failed. Please try clicking a different area.")


@router.post("/transform-region", response_model=RegionTransformResponse)
@limiter.limit("5/minute")
async def transform_body_region(
    request: Request,
    transform_request: RegionTransformRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Transform a specific body region using ControlNet + SAM mask compositing.
    Credits are deducted for this operation.
    """
    try:
        await require_safe_body_photo(
            transform_request.image_base64,
            route_name="transform_region",
            user_id=current_user["id"],
            ownership_confirmed=transform_request.ownership_confirmed,
            stated_age=current_user.get("age"),
        )

        is_premium = await check_premium_status(current_user["id"])
        REGION_TRANSFORM_COST = 15

        balance = await get_credit_balance(current_user["id"], is_premium)
        if not is_premium and balance["total_credits"] < REGION_TRANSFORM_COST:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Not enough credits. Need {REGION_TRANSFORM_COST}, have {balance['total_credits']}.",
            )

        result = await image_models.controlnet_transform_region(
            image_base64=transform_request.image_base64,
            mask_base64=transform_request.mask_base64,
            body_part=transform_request.body_part,
            goal=transform_request.goal,
            gender=transform_request.gender,
            intensity=transform_request.intensity,
        )

        supabase = get_supabase()
        scan_id = None
        scan_data = {
            "user_id": current_user["id"],
            "scan_type": "region_transform",
            "result_data": {
                "body_part": result["body_part"],
                "goal": result["goal"],
                "direction": result["direction"],
            },
            "ai_analysis": {
                "body_part": result["body_part"],
                "goal": result["goal"],
                "intensity": transform_request.intensity,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            persist_result = supabase.table("body_scans").insert(scan_data).execute()
            scan_id = persist_result.data[0]["id"] if persist_result.data else None
        except Exception as scan_error:
            logger.warning(
                "Region transform generated successfully but body_scans persistence failed; continuing without scan_id: %s",
                scan_error,
            )

        await deduct_credits(current_user["id"], REGION_TRANSFORM_COST, "region_transform")

        return RegionTransformResponse(
            transformed_image_url=result["transformed_image_url"],
            body_part=result["body_part"],
            goal=result["goal"],
            direction=result["direction"],
            scan_id=scan_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Region transform error: {e}")
        raise_body_unavailable(e, default_detail="Region transformation failed. Please try again.")
