import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..dependencies import get_current_user
from ..services import beauty_service
from ..services.usage_limiter import get_credit_balance
from ..services.payment_service import deduct_credits, check_premium_status
from ..rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

BEAUTY_SCAN_COST = 10
BEAUTY_STYLING_COST = 30


class BeautyAnalyzeRequest(BaseModel):
    image_base64: str
    gender: str = "female"
    generate_images: bool = False


class BeautyAnalyzeResponse(BaseModel):
    analysis: Dict[str, Any]
    styled_images: List[Dict[str, Any]] = []
    credits_used: int = 0


@router.post("/analyze", response_model=BeautyAnalyzeResponse)
@limiter.limit("5/minute")
async def analyze_beauty(
    request: Request,
    body: BeautyAnalyzeRequest,
    user=Depends(get_current_user),
):
    """Analyze face for beauty consultation + optionally generate styled images."""
    user_id = user["id"]
    is_premium = await check_premium_status(user_id)

    total_cost = BEAUTY_SCAN_COST
    if body.generate_images:
        total_cost += BEAUTY_STYLING_COST

    balance = await get_credit_balance(user_id, is_premium)
    if balance["total_credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Not enough credits. Need {total_cost}, have {balance['total_credits']}.",
        )

    try:
        analysis = await beauty_service.analyze_face(body.image_base64, body.gender)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Beauty analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Beauty analysis failed")

    await deduct_credits(user_id, BEAUTY_SCAN_COST, "beauty_scan")

    styled_images = []
    if body.generate_images and analysis.get("styling_suggestions"):
        try:
            styled_images = await beauty_service.generate_styled_images(
                body.image_base64,
                analysis["styling_suggestions"],
                body.gender,
            )
            await deduct_credits(user_id, BEAUTY_STYLING_COST, "beauty_styling")
        except Exception as e:
            logger.error(f"Styled image generation failed: {e}")

    return BeautyAnalyzeResponse(
        analysis=analysis,
        styled_images=styled_images,
        credits_used=total_cost if body.generate_images else BEAUTY_SCAN_COST,
    )
