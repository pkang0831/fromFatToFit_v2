import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

# Path to food database
FOOD_DB_PATH = Path(__file__).parent.parent.parent / "data" / "foods.json"


class FoodDatabaseService:
    """Service for managing and searching the food nutrition database"""
    
    def __init__(self):
        self.foods: List[Dict[str, Any]] = []
        self.foods_by_id: Dict[str, Dict[str, Any]] = {}
        self.categories: set = set()
        self.load_database()
    
    def load_database(self):
        """Load food database from JSON file"""
        try:
            if not FOOD_DB_PATH.exists():
                logger.error(f"Food database not found at {FOOD_DB_PATH}")
                return
            
            with open(FOOD_DB_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.foods = data.get('foods', [])
            self.foods_by_id = {food['id']: food for food in self.foods}
            self.categories = {food['category'] for food in self.foods if 'category' in food}
            
            logger.info(f"✅ Loaded {len(self.foods)} foods from database")
            logger.info(f"📁 Categories: {', '.join(sorted(self.categories))}")
            
        except Exception as e:
            logger.error(f"Error loading food database: {e}")
            self.foods = []
            self.foods_by_id = {}
    
    def search_foods(self, query: str, limit: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search foods by name and keywords with fuzzy matching
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            category: Optional category filter
            
        Returns:
            List of matching food items with relevance score
        """
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        results = []
        
        for food in self.foods:
            # Filter by category if specified
            if category and food.get('category') != category:
                continue
            
            # Calculate relevance score
            score = 0
            name_lower = food['name'].lower()
            
            # Exact match in name (highest priority)
            if query_lower == name_lower:
                score += 100
            # Starts with query
            elif name_lower.startswith(query_lower):
                score += 80
            # Contains query
            elif query_lower in name_lower:
                score += 60
            
            # Check keywords
            keywords = food.get('search_keywords', [])
            for keyword in keywords:
                if query_lower == keyword.lower():
                    score += 50
                elif keyword.lower().startswith(query_lower):
                    score += 40
                elif query_lower in keyword.lower():
                    score += 20
            
            # Add to results if relevant
            if score > 0:
                results.append({
                    **food,
                    'relevance_score': score
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_food_by_id(self, food_id: str) -> Optional[Dict[str, Any]]:
        """Get food details by ID"""
        return self.foods_by_id.get(food_id)
    
    def get_all_categories(self) -> List[str]:
        """Get list of all food categories"""
        return sorted(list(self.categories))
    
    def calculate_nutrition(
        self, 
        food_id: str, 
        amount_grams: float
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate nutrition for a specific amount of food
        
        Args:
            food_id: Food ID from database
            amount_grams: Amount in grams
            
        Returns:
            Dictionary with calculated nutrition values
        """
        food = self.get_food_by_id(food_id)
        if not food:
            return None
        
        nutrition_per_100g = food['nutrition_per_100g']
        multiplier = amount_grams / 100.0
        
        return {
            'food_id': food_id,
            'food_name': food['name'],
            'amount_grams': amount_grams,
            'calories': round(nutrition_per_100g['calories'] * multiplier, 1),
            'protein': round(nutrition_per_100g['protein'] * multiplier, 1),
            'carbs': round(nutrition_per_100g['carbs'] * multiplier, 1),
            'fat': round(nutrition_per_100g['fat'] * multiplier, 1),
            'nutrition_per_100g': nutrition_per_100g
        }


# Singleton instance
_food_db_service: Optional[FoodDatabaseService] = None


def get_food_database() -> FoodDatabaseService:
    """Get singleton instance of FoodDatabaseService"""
    global _food_db_service
    if _food_db_service is None:
        _food_db_service = FoodDatabaseService()
    return _food_db_service


def reload_food_database():
    """Reload food database (useful for testing/updates)"""
    global _food_db_service
    _food_db_service = FoodDatabaseService()
    return _food_db_service
