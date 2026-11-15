from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, Request
from typing import Optional
import logging
import httpx
from app.core.auth import get_current_user
from app.core.database import get_supabase
from app.domains.food.database import get_food_database
from app.core.rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

OPEN_FOOD_FACTS_BASE = "https://world.openfoodfacts.org"
# Open Food Facts asks API clients to identify themselves.
OPEN_FOOD_FACTS_HEADERS = {"User-Agent": "Devenira/1.0 (https://www.devenira.com)"}


def _round(value) -> float:
    try:
        return round(float(value or 0), 1)
    except (TypeError, ValueError):
        return 0.0


def _search_food_cache(query: str, limit: int) -> list:
    try:
        rows = (
            get_supabase()
            .table("food_cache")
            .select("*")
            .ilike("food_name", f"%{query}%")
            .limit(limit)
            .execute()
        ).data or []
    except Exception as e:
        logger.warning(f"Food cache lookup failed: {e}")
        return []
    return [
        {
            "id": r["id"],
            "food_name": r["food_name"],
            "brand": r.get("brand", ""),
            "barcode": r.get("barcode", ""),
            "nutrition_per_100g": {
                "calories": r.get("calories", 0),
                "protein": r.get("protein", 0),
                "carbs": r.get("carbs", 0),
                "fat": r.get("fat", 0),
            },
            "serving_size": r.get("serving_size", "100g"),
            "image_url": r.get("image_url", ""),
            "source": "cache",
            "nutriscore": r.get("nutriscore", ""),
        }
        for r in rows
    ]


def _save_to_food_cache(items: list, query: str):
    try:
        sb = get_supabase()
        for item in items:
            n = item["nutrition_per_100g"]
            sb.table("food_cache").upsert(
                {
                    "id": item["id"],
                    "food_name": item["food_name"],
                    "brand": item.get("brand", ""),
                    "barcode": item.get("barcode", ""),
                    "calories": n.get("calories", 0),
                    "protein": n.get("protein", 0),
                    "carbs": n.get("carbs", 0),
                    "fat": n.get("fat", 0),
                    "serving_size": item.get("serving_size", "100g"),
                    "image_url": item.get("image_url", ""),
                    "source": "openfoodfacts",
                    "nutriscore": item.get("nutriscore", ""),
                    "search_terms": [query.lower()],
                },
                on_conflict="id",
            ).execute()
    except Exception as e:
        logger.warning(f"Failed to cache food results: {e}")


@router.get("/search")
@limiter.limit("60/minute")
async def search_foods(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    try:
        db = get_food_database()
        results = db.search_foods(query=q, limit=limit, category=category)
        return {"query": q, "count": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error searching foods: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/categories")
@limiter.limit("30/minute")
async def get_categories(request: Request):
    try:
        db = get_food_database()
        categories = db.get_all_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@router.get("/search-external")
@limiter.limit("30/minute")
async def search_external_foods(
    request: Request,
    background_tasks: BackgroundTasks,
    q: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(10, ge=1, le=25),
    current_user: dict = Depends(get_current_user),
):
    """Search packaged foods: Supabase cache first, then Open Food Facts."""
    cached = _search_food_cache(q, limit)
    if len(cached) >= 3:
        return {"results": cached, "source": "cache", "total": len(cached)}

    api_results = []
    try:
        async with httpx.AsyncClient(headers=OPEN_FOOD_FACTS_HEADERS) as client:
            response = await client.get(
                f"{OPEN_FOOD_FACTS_BASE}/cgi/search.pl",
                params={
                    "search_terms": q,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1,
                    "page_size": limit,
                    "fields": "product_name,brands,nutriments,serving_size,image_small_url,code,nutriscore_grade",
                },
                timeout=15.0,
            )
        if response.status_code == 200:
            for p in response.json().get("products", []):
                name = (p.get("product_name") or "").strip()
                if not name:
                    continue
                nutriments = p.get("nutriments") or {}
                brand = (p.get("brands") or "").strip()
                api_results.append({
                    "id": f"off_{p.get('code', '')}",
                    "food_name": name + (f" ({brand})" if brand else ""),
                    "brand": brand,
                    "barcode": p.get("code", ""),
                    "nutrition_per_100g": {
                        "calories": _round(nutriments.get("energy-kcal_100g")),
                        "protein": _round(nutriments.get("proteins_100g")),
                        "carbs": _round(nutriments.get("carbohydrates_100g")),
                        "fat": _round(nutriments.get("fat_100g")),
                    },
                    "serving_size": p.get("serving_size") or "100g",
                    "image_url": p.get("image_small_url", ""),
                    "source": "openfoodfacts",
                    "nutriscore": p.get("nutriscore_grade", ""),
                })
    except httpx.TimeoutException:
        logger.warning(f"Open Food Facts timeout for query: {q}")
    except Exception as e:
        logger.warning(f"Open Food Facts error: {e}")

    if api_results:
        background_tasks.add_task(_save_to_food_cache, api_results, q)

    seen_ids = {r["id"] for r in cached}
    merged = list(cached)
    for r in api_results:
        if r["id"] not in seen_ids:
            merged.append(r)
            seen_ids.add(r["id"])

    source = "openfoodfacts" if api_results else "cache" if cached else "none"
    return {"results": merged[:limit], "source": source, "total": len(merged)}


@router.get("/barcode/{barcode}")
@limiter.limit("30/minute")
async def lookup_barcode(
    request: Request,
    barcode: str = Path(..., pattern=r"^\d{8,14}$"),
    current_user: dict = Depends(get_current_user),
):
    """Look up a packaged food by EAN/UPC barcode via Open Food Facts."""
    try:
        async with httpx.AsyncClient(headers=OPEN_FOOD_FACTS_HEADERS) as client:
            response = await client.get(
                f"{OPEN_FOOD_FACTS_BASE}/api/v2/product/{barcode}.json",
                timeout=10.0,
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Food database timeout")
    except Exception as e:
        logger.error(f"Barcode lookup failed: {e}")
        raise HTTPException(status_code=502, detail="Failed to lookup barcode")

    data = response.json() if response.status_code == 200 else {}
    if data.get("status") != 1:
        raise HTTPException(status_code=404, detail="Product not found")

    product = data.get("product") or {}
    nutriments = product.get("nutriments") or {}
    return {
        "barcode": barcode,
        "food_name": product.get("product_name") or "Unknown Product",
        "brand": product.get("brands", ""),
        "image_url": product.get("image_url", ""),
        "serving_size": product.get("serving_size") or "100g",
        "nutrition_per_100g": {
            "calories": _round(nutriments.get("energy-kcal_100g")),
            "protein": _round(nutriments.get("proteins_100g")),
            "carbs": _round(nutriments.get("carbohydrates_100g")),
            "fat": _round(nutriments.get("fat_100g")),
            "fiber": _round(nutriments.get("fiber_100g")),
            "sugar": _round(nutriments.get("sugars_100g")),
            "sodium": _round(nutriments.get("sodium_100g")),
        },
        "categories": product.get("categories", ""),
        "nutriscore_grade": product.get("nutriscore_grade", ""),
    }


@router.get("/{food_id}")
@limiter.limit("60/minute")
async def get_food_details(request: Request, food_id: str):
    try:
        db = get_food_database()
        food = db.get_food_by_id(food_id)
        if not food:
            raise HTTPException(status_code=404, detail="Food not found")
        return food
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting food details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get food details")


@router.post("/calculate")
@limiter.limit("60/minute")
async def calculate_nutrition(request: Request, food_id: str, amount_grams: float):
    try:
        db = get_food_database()
        result = db.calculate_nutrition(food_id, amount_grams)
        if not result:
            raise HTTPException(status_code=404, detail="Food not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating nutrition: {e}")
        raise HTTPException(status_code=500, detail="Calculation failed")


@router.get("/stats/overview")
@limiter.limit("30/minute")
async def get_database_stats(request: Request):
    try:
        db = get_food_database()
        return {
            "total_foods": len(db.foods),
            "categories": db.get_all_categories(),
            "category_counts": {
                cat: len([f for f in db.foods if f.get('category') == cat])
                for cat in db.categories
            }
        }
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")
