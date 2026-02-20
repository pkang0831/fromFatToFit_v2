"""
Food Recommendation Service - Hybrid rule-based + AI recommendations
"""
from typing import List, Dict, Optional
from datetime import date
import logging

logger = logging.getLogger(__name__)


class FoodRecommendationService:
    """Service to recommend foods based on remaining macros and user preferences"""
    
    def __init__(self, db_client, food_db_service, ai_service):
        self.db = db_client
        self.food_db = food_db_service
        self.ai = ai_service
    
    async def recommend_foods(
        self,
        user_id: str,
        meal_type: str,
        target_date: date,
        just_ate_food_id: Optional[str] = None
    ) -> dict:
        """
        Hybrid recommendation: Rule-based filtering + AI explanation
        
        Returns:
            {
                'meal_type': str,
                'remaining': {...},
                'recommendations': [...],
                'ai_explanation': str
            }
        """
        try:
            # 1. Get remaining macros
            daily_stats = await self._get_daily_stats(user_id, target_date)
            remaining = self._calculate_remaining(daily_stats)
            
            # 2. Get user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # 3. Rule-based filtering
            candidates = self._filter_candidates(
                remaining, preferences, meal_type
            )
            
            if not candidates:
                # Fallback: relax constraints
                candidates = self._filter_candidates(
                    remaining, preferences, meal_type, relax=True
                )
            
            # 4. Score and rank
            ranked_foods = self._rank_by_nutritional_fit(
                candidates, remaining, preferences
            )[:5]
            
            # 5. AI explanation for each (async batch)
            recommendations = []
            for food in ranked_foods:
                reason = await self._generate_ai_reason(
                    food, remaining, preferences, meal_type
                )
                
                # Calculate serving size
                serving_sizes = food.get('common_serving_sizes', [])
                serving_size = serving_sizes[0]['name'] if serving_sizes else "100g"
                
                recommendations.append({
                    'food_id': food['id'],
                    'food_name': food['name'],
                    'category': food['category'],
                    'calories': food['nutrition_per_100g']['calories'],
                    'protein': food['nutrition_per_100g']['protein'],
                    'carbs': food['nutrition_per_100g']['carbs'],
                    'fat': food['nutrition_per_100g']['fat'],
                    'serving_size': serving_size,
                    'reason': reason,
                    'match_score': food['score']
                })
            
            # 6. Overall AI strategy
            ai_explanation = await self._generate_overall_strategy(
                remaining, preferences, meal_type, recommendations
            )
            
            return {
                'meal_type': meal_type,
                'remaining': remaining,
                'recommendations': recommendations,
                'ai_explanation': ai_explanation
            }
            
        except Exception as e:
            logger.error(f"Error in recommend_foods: {e}")
            raise
    
    def _calculate_remaining(self, daily_stats: dict) -> dict:
        """Calculate remaining macros for the day"""
        return {
            'calories': max(daily_stats['calorie_goal'] - daily_stats['consumed_calories'], 0),
            'protein': max((daily_stats.get('protein_goal', 100) or 100) - daily_stats['consumed_protein'], 0),
            'carbs': max((daily_stats.get('carbs_goal', 250) or 250) - daily_stats['consumed_carbs'], 0),
            'fat': max((daily_stats.get('fat_goal', 65) or 65) - daily_stats['consumed_fat'], 0)
        }
    
    def _filter_candidates(
        self,
        remaining: dict,
        preferences: dict,
        meal_type: str,
        relax: bool = False
    ) -> List[dict]:
        """
        Rule-based filtering from foods.json (1903 items)
        """
        all_foods = self.food_db.foods
        candidates = []
        
        # Meal-specific calorie targets
        meal_calorie_ratios = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.35,
            'snack': 0.15
        }
        
        expected_meal_calories = remaining['calories'] * meal_calorie_ratios.get(meal_type, 0.3)
        
        for food in all_foods:
            nutrition = food['nutrition_per_100g']
            food_calories = nutrition['calories']
            
            # Skip disliked (unless relaxing)
            if not relax and food['id'] in preferences.get('disliked_foods', []):
                continue
            
            # Always skip allergens
            food_name_lower = food['name'].lower()
            if any(allergen.lower() in food_name_lower for allergen in preferences.get('allergies', [])):
                continue
            
            # Dietary restrictions check
            dietary_restrictions = preferences.get('dietary_restrictions', [])
            if 'vegetarian' in dietary_restrictions and food['category'] in ['meat_poultry', 'seafood']:
                continue
            if 'vegan' in dietary_restrictions and food['category'] in ['meat_poultry', 'seafood', 'dairy']:
                continue
            
            # Calorie check (reasonable portion size)
            # For 100g serving, check if it's reasonable for this meal
            if relax:
                max_multiplier = 2.0
            else:
                max_multiplier = 1.5
            
            if food_calories < expected_meal_calories * max_multiplier:
                candidates.append(food)
        
        return candidates
    
    def _rank_by_nutritional_fit(
        self,
        candidates: List[dict],
        remaining: dict,
        preferences: dict
    ) -> List[dict]:
        """
        Score each food based on nutritional fit
        """
        scored = []
        
        for food in candidates:
            nutrition = food['nutrition_per_100g']
            score = 0
            
            # === Protein scoring ===
            if preferences.get('prefer_high_protein') and nutrition['protein'] > 15:
                score += nutrition['protein'] * 2
            
            # Protein adequacy
            if remaining['protein'] > 30 and nutrition['protein'] > 20:
                score += 25
            
            # === Calorie efficiency ===
            if remaining['calories'] > 0:
                calorie_ratio = nutrition['calories'] / remaining['calories']
                # Sweet spot: 10-40% of remaining calories
                if 0.1 < calorie_ratio < 0.4:
                    score += 20
            
            # === Favorite bonus ===
            if food['id'] in preferences.get('favorite_foods', []):
                score += 30
            
            # === Category bonuses ===
            # Prioritize whole foods
            if food['category'] in ['vegetables', 'fruits', 'grains', 'nuts_seeds']:
                score += 10
            
            # Lean proteins
            if food['category'] in ['seafood', 'meat_poultry'] and nutrition['fat'] < 10:
                score += 15
            
            # === Macro balance ===
            # Check if food helps balance macros
            protein_ratio = nutrition['protein'] / nutrition['calories'] if nutrition['calories'] > 0 else 0
            if protein_ratio > 0.2:  # High protein-to-calorie ratio
                score += 10
            
            scored.append({**food, 'score': score})
        
        return sorted(scored, key=lambda x: x['score'], reverse=True)
    
    async def _generate_ai_reason(
        self,
        food: dict,
        remaining: dict,
        preferences: dict,
        meal_type: str
    ) -> str:
        """
        Use AI to generate friendly explanation (GPT-4o-mini)
        """
        try:
            nutrition = food['nutrition_per_100g']
            
            prompt = f"""As a friendly nutrition coach, explain in 1-2 sentences why {food['name']} is a good choice for {meal_type}.

Context:
- Remaining calories: {int(remaining['calories'])} kcal
- Remaining protein: {int(remaining['protein'])}g
- Food calories (per 100g): {int(nutrition['calories'])} kcal
- Food protein (per 100g): {int(nutrition['protein'])}g

Be encouraging, specific, and mention nutritional benefits. Keep it under 40 words."""
            
            response = await self.ai.simple_completion(prompt, max_tokens=100)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI reason: {e}")
            # Fallback to simple reason
            nutrition = food['nutrition_per_100g']
            if nutrition['protein'] > 20:
                return f"단백질이 풍부한 선택입니다 ({int(nutrition['protein'])}g)"
            elif nutrition['calories'] < 150:
                return f"저칼로리 옵션입니다 ({int(nutrition['calories'])}kcal)"
            else:
                return "균형잡힌 영양을 제공합니다"
    
    async def _generate_overall_strategy(
        self,
        remaining: dict,
        preferences: dict,
        meal_type: str,
        recommendations: List[dict]
    ) -> str:
        """
        Overall meal strategy from AI
        """
        try:
            rec_names = [r['food_name'] for r in recommendations[:3]]
            
            prompt = f"""As a supportive nutrition coach, provide 2-3 sentences of encouragement for {meal_type}.

Context:
- Remaining calories: {int(remaining['calories'])} kcal
- Remaining protein: {int(remaining['protein'])}g
- Top recommendations: {', '.join(rec_names)}

Focus on positive encouragement and the benefits of these choices. Keep it under 60 words."""
            
            response = await self.ai.simple_completion(prompt, max_tokens=150)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating overall strategy: {e}")
            return f"남은 {int(remaining['calories'])}kcal를 현명하게 사용하세요! 위의 추천 음식들은 영양 균형을 맞추는데 도움이 될 거예요."
    
    async def _get_daily_stats(self, user_id: str, target_date: date) -> dict:
        """Get user's daily nutrition stats"""
        try:
            # Try daily_summaries first
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
            
            # Calculate from food_logs
            logs_result = self.db.table('food_logs').select(
                'calories, protein, carbs, fat'
            ).eq('user_id', user_id).eq('date', target_date.isoformat()).execute()
            
            total_calories = sum(float(log.get('calories', 0)) for log in logs_result.data)
            total_protein = sum(float(log.get('protein', 0)) for log in logs_result.data)
            total_carbs = sum(float(log.get('carbs', 0)) for log in logs_result.data)
            total_fat = sum(float(log.get('fat', 0)) for log in logs_result.data)
            
            # Get calorie goal
            profile_result = self.db.table('user_profiles').select(
                'calorie_goal'
            ).eq('user_id', user_id).execute()
            
            calorie_goal = 2000
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
