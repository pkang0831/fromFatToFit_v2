"""Guest endpoints — no authentication required, IP-rate-limited."""

import time

from fastapi import APIRouter, HTTPException, status
from starlette.requests import Request
import logging

from ..schemas.body_schemas import (
    GuestScanRequest,
    GuestScanResponse,
    BodyPhotoQualityRequest,
    BodyPhotoQualityResponse,
)
from ..rate_limit import limiter
from ..services.body_photo_quality import analyze_body_photo_quality
from .body import estimate_body_fat_with_fallback, _require_safe_body_photo

logger = logging.getLogger(__name__)
router = APIRouter()


def _bf_category_and_insight(bf: float, gender: str) -> tuple[str, str]:
    if gender == "male":
        if bf < 8:
            return "Competition", "Extremely lean — typical of bodybuilding stage condition, not sustainable long-term for most people."
        if bf < 12:
            return "Athletic", "Leaner than most regular gym-goers. Visible muscle definition."
        if bf < 16:
            return "Fit", "Healthy and fit range with good muscle definition."
        if bf < 20:
            return "Healthy", "Average for an active male. A solid baseline to build from."
        if bf < 25:
            return "Average", "Slightly above average. Structured training could show visible changes in 6-8 weeks."
        return "Above Average", "A consistent plan could make a visible difference in 8-12 weeks."
    else:
        if bf < 14:
            return "Competition", "Extremely lean — may affect hormone balance. Not sustainable for most people."
        if bf < 18:
            return "Athletic", "Leaner than most active women. Visible muscle tone."
        if bf < 23:
            return "Fit", "Healthy and toned. Good body composition."
        if bf < 28:
            return "Healthy", "Average for an active female. A solid baseline to build from."
        if bf < 33:
            return "Average", "Slightly above average. Consistent effort could show visible changes in 6-8 weeks."
        return "Above Average", "A structured plan could make a visible difference in 8-12 weeks."


@router.post("/validate-photo", response_model=BodyPhotoQualityResponse)
@limiter.limit("20/day")
async def guest_validate_photo(request: Request, body: BodyPhotoQualityRequest):
    """Framing + pose check for marketing / try flows — no auth, IP-limited."""
    client = request.client.host if request.client else "?"
    t0 = time.monotonic()
    # WARNING so logs appear when LOG_LEVEL is WARNING (production).
    logger.warning(
        "[guest] validate-photo START framing=%s client=%s b64_len=%s",
        body.framing,
        client,
        len(body.image_base64 or ""),
    )
    try:
        result = await analyze_body_photo_quality(
            body.image_base64,
            framing=body.framing,
        )
        elapsed = time.monotonic() - t0
        logger.warning(
            "[guest] validate-photo DONE ok=%s elapsed=%.2fs body_area_ratio=%.4f pose=%s",
            result.ok,
            elapsed,
            result.body_area_ratio,
            result.pose_detected,
        )
        d = result.to_dict()
        return BodyPhotoQualityResponse(
            ok=d["ok"],
            body_area_ratio=d["body_area_ratio"],
            bbox_area_ratio=d["bbox_area_ratio"],
            mask_fill_ratio=d["mask_fill_ratio"],
            is_front_facing=d["is_front_facing"],
            pose_detected=d["pose_detected"],
            is_shirtless=d["is_shirtless"],
            brightness=d["brightness"],
            failure_codes=d["failure_codes"],
            messages=d["messages"],
            width=d["width"],
            height=d["height"],
            framing=d["framing"],
            min_body_area_ratio=d["min_body_area_ratio"],
            min_mask_fill_ratio=d["min_mask_fill_ratio"],
        )
    except Exception as e:
        # This path is server errors only. Photo *quality* failures return HTTP 200 with ok=false + messages.
        logger.error(f"Guest validate-photo error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Server error during segmentation/pose — not a photo-quality score. "
                "See backend logs for the exception."
            ),
        )


@router.post("/body-scan", response_model=GuestScanResponse)
@limiter.limit("3/day")
async def guest_body_scan(request: Request, scan_request: GuestScanRequest):
    """
    Free body-fat estimate — no account required.
    Limited to 3 scans per day per IP.  Result is not stored.
    """
    try:
        await _require_safe_body_photo(
            scan_request.image_base64,
            route_name="guest_body_scan",
            framing=scan_request.framing,
            source="guest",
            ownership_confirmed=scan_request.ownership_confirmed,
            adult_confirmed=scan_request.adult_confirmed,
            stated_age=scan_request.age,
        )

        analysis = await estimate_body_fat_with_fallback(
            scan_request.image_base64,
            scan_request.gender,
            scan_request.age,
        )

        bf = analysis["body_fat_percentage"]
        confidence = analysis.get("confidence", "medium")
        category, insight = _bf_category_and_insight(bf, scan_request.gender)

        return GuestScanResponse(
            body_fat_percentage=bf,
            confidence=confidence,
            category=category,
            insight=insight,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Guest body scan error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Body scan failed. Please try again.",
        )
