"""
Food Decision and Recommendation API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from datetime import date
import logging

from ..schemas.food_decision_schemas import (
    ShouldIEatRequest,
    ShouldIEatResponse,
    RecommendationRequest,
    RecommendationResponse,
    UserFoodPreferences,
    UpdatePreferencesRequest,
    FoodItemAnalysis,
    DecisionReason,
    ImpactAnalysis,
    CurrentDailyStats,
    AlternativeFood,
    RemainingMacros,
    FoodRecommendation
)
from ..services.food_decision_service import FoodDecisionService
from ..services.food_recommendation_service import FoodRecommendationService
from ..services.food_database_service import get_food_database
from ..services import openai_service
from ..middleware.auth_middleware import get_current_user
from ..database import get_supabase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/food-decision", tags=["Food Decision"])


def _get_decision_text(decision: str) -> str:
    """Get user-friendly decision text"""
    texts = {
        'green': '좋은 선택이에요! 드셔도 됩니다 😊',
        'yellow': '조금 주의가 필요해요. 반만 드시거나 다른 옵션을 고려해보세요 🤔',
        'red': '지금은 다른 음식을 선택하는 게 좋겠어요 💭'
    }
    return texts.get(decision, '분석 결과를 확인해주세요')


async def _generate_ai_advice(decision_data: dict, ai_result: dict) -> str:
    """Generate AI advice based on decision"""
    try:
        decision = decision_data['decision']
        reasons = decision_data['reasons']
        totals = decision_data['totals']
        impact = decision_data['impact']
        
        # Build context for AI
        reason_summary = "; ".join([r['message'] for r in reasons[:3]])
        
        prompt = f"""As a supportive nutrition coach, provide brief advice (2-3 sentences, max 60 words) for this eating decision.

Decision: {decision} (green=good, yellow=caution, red=avoid)
Food: {', '.join([item['name'] for item in ai_result['items'][:2]])}
Total calories: {int(totals['calories'])} kcal
Key reasons: {reason_summary}
Remaining calories after eating: {int(impact['remaining_calories'])} kcal

Be encouraging and specific about what to do next."""
        
        advice = await openai_service.simple_completion(prompt, max_tokens=120)
        return advice.strip()
        
    except Exception as e:
        logger.error(f"Error generating AI advice: {e}")
        # Fallback advice based on decision
        if decision_data['decision'] == 'green':
            return "좋은 선택입니다! 이 음식은 오늘 목표에 잘 맞아요. 맛있게 드세요! 😊"
        elif decision_data['decision'] == 'yellow':
            return "조금 주의가 필요한 선택이에요. 적당량만 드시거나, 아래 대안 음식을 고려해보세요."
        else:
            return "지금은 다른 음식을 선택하는 것이 좋겠어요. 아래 추천 음식들을 확인해보세요!"


@router.post("/should-i-eat", response_model=ShouldIEatResponse)
async def should_i_eat(
    request: ShouldIEatRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Analyzes food photo and determines if user should eat it
    
    Flow:
    1. Analyze image with AI vision
    2. Get daily stats and preferences
    3. Make decision (green/yellow/red)
    4. Generate AI advice and alternatives
    """
    try:
        supabase = get_supabase()
        
        # 1. Analyze photo with AI (using existing multi-provider strategy)
        # For now, use OpenAI - in production, use the hybrid strategy from food_camera
        ai_result = await openai_service.analyze_food_image(request.image_base64)
        
        # 2. Make decision
        decision_service = FoodDecisionService(supabase)
        decision = await decision_service.should_i_eat(
            user_id=current_user['id'],
            food_items=ai_result['items'],
            current_date=date.today()
        )
        
        # 3. Generate AI advice
        ai_advice = await _generate_ai_advice(decision, ai_result)
        
        # 4. Build response
        food_items = [
            FoodItemAnalysis(
                name=item['name'],
                calories=item.get('calories', 0),
                protein=item.get('protein', 0),
                carbs=item.get('carbs', 0),
                fat=item.get('fat', 0),
                serving_size=item.get('serving_size'),
                sodium=item.get('sodium'),
                sugar=item.get('sugar')
            )
            for item in ai_result['items']
        ]
        
        reasons = [
            DecisionReason(**reason) for reason in decision['reasons']
        ]
        
        alternatives = None
        if decision['alternatives']:
            alternatives = [
                AlternativeFood(**alt) for alt in decision['alternatives']
            ]
        
        return ShouldIEatResponse(
            decision=decision['decision'],
            decision_text=_get_decision_text(decision['decision']),
            food_items=food_items,
            total_calories=decision['totals']['calories'],
            total_protein=decision['totals']['protein'],
            total_carbs=decision['totals']['carbs'],
            total_fat=decision['totals']['fat'],
            total_sodium=decision['totals'].get('sodium'),
            total_sugar=decision['totals'].get('sugar'),
            impact=ImpactAnalysis(**decision['impact']),
            reasons=reasons,
            ai_advice=ai_advice,
            alternatives=alternatives,
            current_stats=CurrentDailyStats(**decision['current_stats']),
            confidence=ai_result.get('confidence', 'medium')
        )
        
    except Exception as e:
        logger.error(f"Error in should_i_eat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend", response_model=RecommendationResponse)
async def recommend_foods(
    request: RecommendationRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Recommends foods based on remaining macros and preferences
    
    Uses hybrid approach:
    - Rule-based filtering from 1903 food database
    - AI-generated explanations for each recommendation
    """
    try:
        supabase = get_supabase()
        food_db = get_food_database()
        
        recommendation_service = FoodRecommendationService(
            supabase, food_db, openai_service
        )
        
        result = await recommendation_service.recommend_foods(
            user_id=current_user['id'],
            meal_type=request.meal_type,
            target_date=request.target_date or date.today(),
            just_ate_food_id=request.just_ate_food_id
        )
        
        # Build response
        recommendations = [
            FoodRecommendation(**rec) for rec in result['recommendations']
        ]
        
        return RecommendationResponse(
            meal_type=result['meal_type'],
            remaining=RemainingMacros(**result['remaining']),
            recommendations=recommendations,
            ai_explanation=result['ai_explanation']
        )
        
    except Exception as e:
        logger.error(f"Error in recommend_foods endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preferences", response_model=UserFoodPreferences)
async def get_preferences(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Get user's food preferences
    """
    try:
        supabase = get_supabase()
        
        result = supabase.table('user_food_preferences').select('*').eq(
            'user_id', current_user['id']
        ).execute()
        
        if result.data and len(result.data) > 0:
            prefs = result.data[0]
            return UserFoodPreferences(
                favorite_foods=prefs.get('favorite_foods', []),
                disliked_foods=prefs.get('disliked_foods', []),
                allergies=prefs.get('allergies', []),
                dietary_restrictions=prefs.get('dietary_restrictions', []),
                avoid_high_sodium=prefs.get('avoid_high_sodium', False),
                avoid_high_sugar=prefs.get('avoid_high_sugar', False),
                prefer_high_protein=prefs.get('prefer_high_protein', False)
            )
        
        # Return empty preferences if not found
        return UserFoodPreferences()
        
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Update user's food preferences (upsert)
    """
    try:
        supabase = get_supabase()
        
        # Build update data (only include non-None values)
        update_data = {
            'user_id': current_user['id']
        }
        
        if request.favorite_foods is not None:
            update_data['favorite_foods'] = request.favorite_foods
        if request.disliked_foods is not None:
            update_data['disliked_foods'] = request.disliked_foods
        if request.allergies is not None:
            update_data['allergies'] = request.allergies
        if request.dietary_restrictions is not None:
            update_data['dietary_restrictions'] = request.dietary_restrictions
        if request.avoid_high_sodium is not None:
            update_data['avoid_high_sodium'] = request.avoid_high_sodium
        if request.avoid_high_sugar is not None:
            update_data['avoid_high_sugar'] = request.avoid_high_sugar
        if request.prefer_high_protein is not None:
            update_data['prefer_high_protein'] = request.prefer_high_protein
        
        # Upsert (insert or update)
        result = supabase.table('user_food_preferences').upsert(
            update_data,
            on_conflict='user_id'
        ).execute()
        
        # Invalidate cache after update
        from ..services.preference_cache import invalidate_user_cache
        await invalidate_user_cache(current_user['id'])
        
        return {
            "success": True,
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))
