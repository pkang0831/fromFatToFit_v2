"""
Food Decision Service - Determines if user should eat a food
"""
from typing import Dict, List, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class FoodDecisionService:
    """Service to make food eating decisions based on user's daily stats and preferences"""
    
    def __init__(self, db_client):
        self.db = db_client
        
    async def should_i_eat(
        self,
        user_id: str,
        food_items: List[dict],
        current_date: date
    ) -> dict:
        """
        Determines if user should eat the food based on:
        - Remaining calories
        - Nutritional balance
        - User preferences and allergies
        - Sodium/sugar content
        
        Returns:
            {
                'decision': 'green|yellow|red',
                'reasons': [...],
                'impact': {...},
                'alternatives': [...],
                'current_stats': {...}
            }
        """
        try:
            # 1. Get user's daily stats
            daily_stats = await self._get_daily_stats(user_id, current_date)
            
            # 2. Get user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # 3. Calculate totals from food items
            total_calories = sum(item.get('calories', 0) for item in food_items)
            total_protein = sum(item.get('protein', 0) for item in food_items)
            total_carbs = sum(item.get('carbs', 0) for item in food_items)
            total_fat = sum(item.get('fat', 0) for item in food_items)
            total_sodium = sum(item.get('sodium', 0) for item in food_items)
            total_sugar = sum(item.get('sugar', 0) for item in food_items)
            
            # 4. Calculate remaining macros
            remaining_calories = daily_stats['calorie_goal'] - daily_stats['consumed_calories']
            remaining_protein = (daily_stats.get('protein_goal', 0) or 0) - daily_stats['consumed_protein']
            remaining_carbs = (daily_stats.get('carbs_goal', 0) or 0) - daily_stats['consumed_carbs']
            remaining_fat = (daily_stats.get('fat_goal', 0) or 0) - daily_stats['consumed_fat']
            
            # Avoid division by zero
            if remaining_calories <= 0:
                calorie_percentage = 999
            else:
                calorie_percentage = (total_calories / remaining_calories) * 100
            
            # 5. Decision Logic
            reasons = []
            decision = "green"
            
            # === CRITICAL CHECKS (RED) ===
            
            # Allergy check
            for item in food_items:
                item_name_lower = item.get('name', '').lower()
                for allergen in preferences.get('allergies', []):
                    if allergen.lower() in item_name_lower:
                        decision = "red"
                        reasons.append({
                            'type': 'allergy',
                            'message': f'⚠️ 알레르기 경고: {allergen}이(가) 포함되어 있습니다!',
                            'severity': 'critical'
                        })
            
            # Extreme calorie overshoot
            if calorie_percentage > 100:
                decision = "red"
                overshoot = int(calorie_percentage - 100)
                reasons.append({
                    'type': 'calorie',
                    'message': f'남은 칼로리를 {overshoot}% 초과합니다 ({int(total_calories - remaining_calories)}kcal 초과)',
                    'severity': 'critical'
                })
            
            # === WARNING CHECKS (YELLOW) ===
            
            # High calorie usage (70-100%)
            elif calorie_percentage > 70:
                if decision == "green":
                    decision = "yellow"
                reasons.append({
                    'type': 'calorie',
                    'message': f'남은 칼로리의 {int(calorie_percentage)}%를 사용합니다',
                    'severity': 'warning'
                })
            
            # Sodium check
            if preferences.get('avoid_high_sodium') and total_sodium > 800:
                if decision == "green":
                    decision = "yellow"
                reasons.append({
                    'type': 'sodium',
                    'message': f'나트륨 함량이 높습니다: {int(total_sodium)}mg',
                    'severity': 'warning'
                })
            
            # Sugar check
            if preferences.get('avoid_high_sugar') and total_sugar > 25:
                if decision == "green":
                    decision = "yellow"
                reasons.append({
                    'type': 'sugar',
                    'message': f'당 함량이 높습니다: {int(total_sugar)}g',
                    'severity': 'warning'
                })
            
            # Protein deficiency
            if remaining_protein > 30 and total_protein < 10:
                if decision == "green":
                    decision = "yellow"
                reasons.append({
                    'type': 'macro',
                    'message': f'단백질이 부족합니다. {int(remaining_protein)}g 더 필요해요',
                    'severity': 'warning'
                })
            
            # === INFO CHECKS (GREEN) ===
            
            # Good calorie range
            if 20 <= calorie_percentage <= 40 and decision == "green":
                reasons.append({
                    'type': 'calorie',
                    'message': f'적절한 칼로리 범위입니다 ({int(total_calories)}kcal)',
                    'severity': 'info'
                })
            
            # High protein
            if total_protein > 20 and decision == "green":
                reasons.append({
                    'type': 'macro',
                    'message': f'단백질이 풍부합니다 ({int(total_protein)}g)',
                    'severity': 'info'
                })
            
            # 6. Get alternatives if needed
            alternatives = None
            if decision in ["yellow", "red"]:
                alternatives = await self._find_alternatives(
                    food_items, 
                    remaining_calories,
                    remaining_protein,
                    preferences
                )
            
            return {
                'decision': decision,
                'reasons': reasons,
                'impact': {
                    'calories_used_percentage': min(calorie_percentage, 100),
                    'remaining_calories': max(remaining_calories - total_calories, 0),
                    'remaining_protein': max(remaining_protein - total_protein, 0),
                    'remaining_carbs': max(remaining_carbs - total_carbs, 0),
                    'remaining_fat': max(remaining_fat - total_fat, 0)
                },
                'alternatives': alternatives,
                'current_stats': daily_stats,
                'totals': {
                    'calories': total_calories,
                    'protein': total_protein,
                    'carbs': total_carbs,
                    'fat': total_fat,
                    'sodium': total_sodium,
                    'sugar': total_sugar
                }
            }
            
        except Exception as e:
            logger.error(f"Error in should_i_eat: {e}")
            raise
    
    async def _get_daily_stats(self, user_id: str, target_date: date) -> dict:
        """Get user's daily nutrition stats"""
        try:
            # First try to get from daily_summaries
            result = self.db.table('daily_summaries').select(
                'total_calories, total_protein, total_carbs, total_fat, calorie_goal'
            ).eq('user_id', user_id).eq('date', target_date.isoformat()).execute()
            
            if result.data and len(result.data) > 0:
                summary = result.data[0]
                return {
                    'consumed_calories': float(summary.get('total_calories', 0)),
                    'consumed_protein': float(summary.get('total_protein', 0)),
                    'consumed_carbs': float(summary.get('total_carbs', 0)),
                    'consumed_fat': float(summary.get('total_fat', 0)),
                    'calorie_goal': float(summary.get('calorie_goal', 2000))
                }
            
            # If not in summaries, calculate from food_logs
            logs_result = self.db.table('food_logs').select(
                'calories, protein, carbs, fat'
            ).eq('user_id', user_id).eq('date', target_date.isoformat()).execute()
            
            total_calories = sum(float(log.get('calories', 0)) for log in logs_result.data)
            total_protein = sum(float(log.get('protein', 0)) for log in logs_result.data)
            total_carbs = sum(float(log.get('carbs', 0)) for log in logs_result.data)
            total_fat = sum(float(log.get('fat', 0)) for log in logs_result.data)
            
            # Get calorie goal from user_profiles
            profile_result = self.db.table('user_profiles').select(
                'calorie_goal'
            ).eq('user_id', user_id).execute()
            
            calorie_goal = 2000  # Default
            if profile_result.data and len(profile_result.data) > 0:
                calorie_goal = float(profile_result.data[0].get('calorie_goal', 2000))
            
            return {
                'consumed_calories': total_calories,
                'consumed_protein': total_protein,
                'consumed_carbs': total_carbs,
                'consumed_fat': total_fat,
                'calorie_goal': calorie_goal
            }
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            # Return defaults on error
            return {
                'consumed_calories': 0,
                'consumed_protein': 0,
                'consumed_carbs': 0,
                'consumed_fat': 0,
                'calorie_goal': 2000
            }
    
    async def _get_user_preferences(self, user_id: str) -> dict:
        """Get user food preferences (with caching)"""
        try:
            from .preference_cache import get_cached_preferences
            return await get_cached_preferences(self.db, user_id)
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {
                'favorite_foods': [],
                'disliked_foods': [],
                'allergies': [],
                'dietary_restrictions': [],
                'avoid_high_sodium': False,
                'avoid_high_sugar': False,
                'prefer_high_protein': False
            }
    
    async def _find_alternatives(
        self,
        original_foods: List[dict],
        remaining_calories: float,
        remaining_protein: float,
        preferences: dict
    ) -> List[dict]:
        """Find healthier alternative foods from the database"""
        try:
            from app.services.food_database_service import get_food_database
            
            food_db = get_food_database()
            alternatives = []
            
            # Target: 50-80% of remaining calories
            target_min_calories = remaining_calories * 0.3
            target_max_calories = remaining_calories * 0.8
            
            # Get original food categories for similar alternatives
            original_categories = set(item.get('category', '') for item in original_foods if item.get('category'))
            
            # Search for alternatives
            for food in food_db.foods:
                nutrition = food['nutrition_per_100g']
                food_calories = nutrition['calories']
                
                # Skip if in disliked list
                if food['id'] in preferences.get('disliked_foods', []):
                    continue
                
                # Skip if contains allergens
                food_name_lower = food['name'].lower()
                if any(allergen.lower() in food_name_lower for allergen in preferences.get('allergies', [])):
                    continue
                
                # Check if calories are in a better range
                if target_min_calories <= food_calories <= target_max_calories:
                    # Prefer similar categories
                    category_match = food['category'] in original_categories
                    
                    # Prefer high protein if user wants it
                    high_protein = nutrition['protein'] > 15
                    
                    # Score the alternative
                    score = 50
                    if category_match:
                        score += 20
                    if high_protein and preferences.get('prefer_high_protein'):
                        score += 15
                    if food['id'] in preferences.get('favorite_foods', []):
                        score += 25
                    
                    # Lower calories is better
                    calorie_savings = (sum(item.get('calories', 0) for item in original_foods) - food_calories)
                    if calorie_savings > 100:
                        score += 20
                    
                    alternatives.append({
                        'food_id': food['id'],
                        'name': food['name'],
                        'category': food['category'],
                        'calories': food_calories,
                        'protein': nutrition['protein'],
                        'carbs': nutrition['carbs'],
                        'fat': nutrition['fat'],
                        'score': score,
                        'reason': self._generate_alternative_reason(
                            food, nutrition, calorie_savings
                        )
                    })
            
            # Sort by score and return top 3
            alternatives.sort(key=lambda x: x['score'], reverse=True)
            return alternatives[:3]
            
        except Exception as e:
            logger.error(f"Error finding alternatives: {e}")
            return []
    
    def _generate_alternative_reason(self, food: dict, nutrition: dict, calorie_savings: float) -> str:
        """Generate a simple reason for why this is a good alternative"""
        reasons = []
        
        if calorie_savings > 100:
            reasons.append(f"{int(calorie_savings)}kcal 절약")
        
        if nutrition['protein'] > 20:
            reasons.append("고단백")
        
        if nutrition['calories'] < 150:
            reasons.append("저칼로리")
        
        if not reasons:
            reasons.append("균형잡힌 영양")
        
        return " · ".join(reasons)
    
    def get_decision_text(self, decision: str) -> str:
        """Get user-friendly decision text"""
        texts = {
            'green': '좋은 선택이에요! 드셔도 됩니다 😊',
            'yellow': '조금 주의가 필요해요. 반만 드시거나 다른 옵션을 고려해보세요 🤔',
            'red': '지금은 다른 음식을 선택하는 게 좋겠어요 💭'
        }
        return texts.get(decision, '분석 결과를 확인해주세요')
