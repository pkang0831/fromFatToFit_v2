from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
import httpx
from ..middleware.auth_middleware import get_current_user
from ..services.food_database_service import get_food_database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search")
async def search_foods(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Search foods in database with autocomplete
    
    Returns matching foods with relevance scoring
    """
    try:
        db = get_food_database()
        results = db.search_foods(query=q, limit=limit, category=category)
        
        return {
            "query": q,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error searching foods: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/categories")
async def get_categories():
    """Get list of all food categories"""
    try:
        db = get_food_database()
        categories = db.get_all_categories()
        
        return {
            "categories": categories,
            "count": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@router.get("/search-external")
async def search_external_foods(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=25),
    current_user: dict = Depends(get_current_user),
):
    """Search foods from Open Food Facts API when local DB doesn't have results."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://world.openfoodfacts.org/cgi/search.pl",
                params={
                    "search_terms": q,
                    "search_simple": 1,
                    "action": "process",
                    "json": 1,
                    "page_size": limit,
                    "fields": "product_name,brands,nutriments,serving_size,image_small_url,code,nutriscore_grade",
                },
                timeout=8.0,
            )

            if response.status_code != 200:
                return {"results": [], "source": "openfoodfacts"}

            data = response.json()
            products = data.get("products", [])

            results = []
            for p in products:
                name = p.get("product_name", "").strip()
                if not name:
                    continue

                nutriments = p.get("nutriments", {})
                brand = p.get("brands", "").strip()

                results.append({
                    "id": f"off_{p.get('code', '')}",
                    "food_name": f"{name}" + (f" ({brand})" if brand else ""),
                    "brand": brand,
                    "barcode": p.get("code", ""),
                    "nutrition_per_100g": {
                        "calories": round(nutriments.get("energy-kcal_100g", 0), 1),
                        "protein": round(nutriments.get("proteins_100g", 0), 1),
                        "carbs": round(nutriments.get("carbohydrates_100g", 0), 1),
                        "fat": round(nutriments.get("fat_100g", 0), 1),
                    },
                    "serving_size": p.get("serving_size", "100g"),
                    "image_url": p.get("image_small_url", ""),
                    "source": "openfoodfacts",
                    "nutriscore": p.get("nutriscore_grade", ""),
                })

            return {"results": results, "source": "openfoodfacts", "total": len(results)}
    except httpx.TimeoutException:
        return {"results": [], "source": "openfoodfacts", "error": "timeout"}
    except Exception:
        return {"results": [], "source": "openfoodfacts", "error": "failed"}


@router.get("/{food_id}")
async def get_food_details(food_id: str):
    """Get detailed information for a specific food"""
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
async def calculate_nutrition(
    food_id: str,
    amount_grams: float
):
    """
    Calculate nutrition values for a specific amount
    
    Args:
        food_id: Food ID from database
        amount_grams: Amount in grams
        
    Returns:
        Calculated nutrition values
    """
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


@router.get("/barcode/{barcode}")
async def lookup_barcode(barcode: str, current_user: dict = Depends(get_current_user)):
    """Look up a food item by barcode using Open Food Facts API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json",
                timeout=10.0,
            )

            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Product not found")

            data = response.json()

            if data.get("status") != 1:
                raise HTTPException(status_code=404, detail="Product not found")

            product = data.get("product", {})
            nutriments = product.get("nutriments", {})

            return {
                "barcode": barcode,
                "food_name": product.get("product_name", "Unknown Product"),
                "brand": product.get("brands", ""),
                "image_url": product.get("image_url", ""),
                "serving_size": product.get("serving_size", "100g"),
                "nutrition_per_100g": {
                    "calories": nutriments.get("energy-kcal_100g", 0),
                    "protein": nutriments.get("proteins_100g", 0),
                    "carbs": nutriments.get("carbohydrates_100g", 0),
                    "fat": nutriments.get("fat_100g", 0),
                    "fiber": nutriments.get("fiber_100g", 0),
                    "sugar": nutriments.get("sugars_100g", 0),
                    "sodium": nutriments.get("sodium_100g", 0),
                },
                "categories": product.get("categories", ""),
                "nutriscore_grade": product.get("nutriscore_grade", ""),
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Food database timeout")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Barcode lookup failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to lookup barcode")


@router.get("/stats/overview")
async def get_database_stats():
    """Get database statistics"""
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
