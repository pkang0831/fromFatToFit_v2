from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
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
