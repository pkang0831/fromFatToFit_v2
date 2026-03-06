import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from ..dependencies import get_current_user
from ..services import fashion_service
from ..services.usage_limiter import get_credit_balance
from ..services.payment_service import deduct_credits
from ..rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter()

FASHION_RECOMMEND_COST = 5
FASHION_IMAGES_COST = 15


class FashionRecommendRequest(BaseModel):
    season: str  # spring, summer, fall, winter
    gender: str = "female"
    height_cm: Optional[float] = None
    body_notes: str = ""
    personal_color: str = ""
    best_colors: str = ""
    image_base64: Optional[str] = None
    generate_images: bool = False


class FashionRecommendResponse(BaseModel):
    season: str
    outfits: List[Dict[str, Any]]
    credits_used: int = 0


@router.post("/recommend", response_model=FashionRecommendResponse)
@limiter.limit("5/minute")
async def recommend_fashion(
    request: Request,
    body: FashionRecommendRequest,
    user=Depends(get_current_user),
):
    """Get seasonal outfit recommendations + optionally generate outfit images."""
    user_id = user["id"]

    total_cost = FASHION_RECOMMEND_COST
    if body.generate_images:
        total_cost += FASHION_IMAGES_COST

    balance = await get_credit_balance(user_id)
    if balance["total_credits"] < total_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Not enough credits. Need {total_cost}, have {balance['total_credits']}.",
        )

    try:
        result = await fashion_service.recommend_outfits(
            gender=body.gender,
            season=body.season,
            height_cm=body.height_cm,
            body_notes=body.body_notes,
            personal_color=body.personal_color,
            best_colors=body.best_colors,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Fashion recommendation failed: {e}")
        raise HTTPException(status_code=500, detail="Fashion recommendation failed")

    await deduct_credits(user_id, FASHION_RECOMMEND_COST, "fashion_recommend")

    outfits = result.get("outfits", [])

    if body.generate_images and outfits:
        try:
            outfits = await fashion_service.generate_outfit_images(
                body.image_base64,
                outfits,
                body.gender,
            )
            await deduct_credits(user_id, FASHION_IMAGES_COST, "fashion_images")
        except Exception as e:
            logger.error(f"Outfit image generation failed: {e}")

    return FashionRecommendResponse(
        season=body.season,
        outfits=outfits,
        credits_used=total_cost if body.generate_images else FASHION_RECOMMEND_COST,
    )
