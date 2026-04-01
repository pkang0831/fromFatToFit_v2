"""
Tests for Food Decision Service
"""
import pytest
import inspect
from datetime import date
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from app.services.food_decision_service import FoodDecisionService


class TestFoodDecisionService:
    """Test suite for FoodDecisionService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock Supabase client"""
        mock = Mock()
        mock.table = Mock(return_value=mock)
        mock.select = Mock(return_value=mock)
        mock.eq = Mock(return_value=mock)
        mock.execute = Mock(return_value=Mock(data=[]))
        return mock
    
    @pytest.fixture
    def service(self, mock_db):
        """Create FoodDecisionService instance with mocked DB"""
        return FoodDecisionService(mock_db)
    
    @pytest.mark.asyncio
    async def test_should_i_eat_green_decision(self, service, mock_db):
        """Test green (go ahead) decision for appropriate food"""
        # Mock daily stats - user has plenty of calories left
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                'total_calories': 500,
                'total_protein': 30,
                'total_carbs': 60,
                'total_fat': 20,
                'calorie_goal': 2000
            }]
        )
        
        # Mock preferences - no restrictions
        with patch.object(service, '_get_user_preferences', new_callable=AsyncMock) as mock_prefs:
            mock_prefs.return_value = {
                'allergies': [],
                'avoid_high_sodium': False,
                'avoid_high_sugar': False,
                'prefer_high_protein': False,
                'disliked_foods': [],
                'dietary_restrictions': [],
                'favorite_foods': []
            }
            
            # Test food items - moderate calories
            food_items = [
                {'name': 'Chicken Breast', 'calories': 300, 'protein': 35, 'carbs': 0, 'fat': 7, 'sodium': 100, 'sugar': 0}
            ]
            
            result = await service.should_i_eat('user123', food_items, date.today())
            
            assert result['decision'] == 'green'
            assert result['impact']['calories_used_percentage'] < 50
    
    @pytest.mark.asyncio
    async def test_should_i_eat_red_decision_allergy(self, service, mock_db):
        """Test red (don't eat) decision due to allergy"""
        # Mock daily stats
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                'total_calories': 500,
                'total_protein': 30,
                'total_carbs': 60,
                'total_fat': 20,
                'calorie_goal': 2000
            }]
        )
        
        # Mock preferences with peanut allergy
        with patch.object(service, '_get_user_preferences', new_callable=AsyncMock) as mock_prefs:
            mock_prefs.return_value = {
                'allergies': ['peanuts'],
                'avoid_high_sodium': False,
                'avoid_high_sugar': False,
                'prefer_high_protein': False,
                'disliked_foods': [],
                'dietary_restrictions': [],
                'favorite_foods': []
            }
            
            # Test food with peanuts
            food_items = [
                {'name': 'Peanut Butter Sandwich', 'calories': 350, 'protein': 15, 'carbs': 30, 'fat': 18}
            ]
            
            result = await service.should_i_eat('user123', food_items, date.today())
            
            assert result['decision'] == 'red'
            assert any(r['type'] == 'allergy' for r in result['reasons'])
            assert any(r['severity'] == 'critical' for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_should_i_eat_red_decision_calorie_overshoot(self, service, mock_db):
        """Test red decision when food exceeds remaining calories"""
        # Mock daily stats - already consumed most calories
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                'total_calories': 1800,
                'total_protein': 80,
                'total_carbs': 200,
                'total_fat': 60,
                'calorie_goal': 2000
            }]
        )
        
        with patch.object(service, '_get_user_preferences', new_callable=AsyncMock) as mock_prefs:
            mock_prefs.return_value = {
                'allergies': [],
                'avoid_high_sodium': False,
                'avoid_high_sugar': False,
                'prefer_high_protein': False,
                'disliked_foods': [],
                'dietary_restrictions': [],
                'favorite_foods': []
            }
            
            # Large meal that exceeds remaining calories
            food_items = [
                {'name': 'Large Pizza', 'calories': 800, 'protein': 35, 'carbs': 90, 'fat': 35}
            ]
            
            result = await service.should_i_eat('user123', food_items, date.today())
            
            assert result['decision'] == 'red'
            assert any(r['type'] == 'calorie' and r['severity'] == 'critical' for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_should_i_eat_yellow_decision_high_sodium(self, service, mock_db):
        """Test yellow (caution) decision for high sodium food"""
        # Mock daily stats
        mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                'total_calories': 800,
                'total_protein': 50,
                'total_carbs': 100,
                'total_fat': 30,
                'calorie_goal': 2000
            }]
        )
        
        # User prefers to avoid high sodium
        with patch.object(service, '_get_user_preferences', new_callable=AsyncMock) as mock_prefs:
            mock_prefs.return_value = {
                'allergies': [],
                'avoid_high_sodium': True,
                'avoid_high_sugar': False,
                'prefer_high_protein': False,
                'disliked_foods': [],
                'dietary_restrictions': [],
                'favorite_foods': []
            }
            
            # Food with high sodium
            food_items = [
                {'name': 'Ramen', 'calories': 400, 'protein': 12, 'carbs': 50, 'fat': 15, 'sodium': 1200}
            ]
            
            result = await service.should_i_eat('user123', food_items, date.today())
            
            assert result['decision'] in ['yellow', 'red']
            assert any(r['type'] == 'sodium' for r in result['reasons'])
    
    @pytest.mark.asyncio
    async def test_find_alternatives(self, service, mock_db):
        """Test alternative food suggestions"""
        with patch('app.services.food_database_service.get_food_database') as mock_food_db:
            # Mock food database
            mock_food_db.return_value.foods = [
                {
                    'id': 'chicken_breast',
                    'name': 'Chicken Breast Grilled',
                    'category': 'meat_poultry',
                    'nutrition_per_100g': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6}
                },
                {
                    'id': 'salmon',
                    'name': 'Salmon Baked',
                    'category': 'seafood',
                    'nutrition_per_100g': {'calories': 206, 'protein': 22, 'carbs': 0, 'fat': 12}
                }
            ]
            
            original_foods = [
                {'name': 'Fried Chicken', 'calories': 500, 'category': 'meat_poultry'}
            ]
            
            preferences = {
                'disliked_foods': [],
                'allergies': [],
                'prefer_high_protein': True,
                'favorite_foods': []
            }
            
            alternatives = await service._find_alternatives(
                original_foods, 400, 50, preferences
            )
            
            assert len(alternatives) > 0
            assert all('food_id' in alt for alt in alternatives)
            assert all('reason' in alt for alt in alternatives)


class TestFoodDecisionLogic:
    """Test decision logic edge cases"""
    
    def test_decision_text_generation(self):
        """Test user-friendly decision texts"""
        service = FoodDecisionService(Mock())
        
        assert 'Good' in service.get_decision_text('green')
        assert 'caution' in service.get_decision_text('yellow')
        assert 'different' in service.get_decision_text('red')
    
    def test_alternative_reason_generation(self):
        """Test alternative food reason generation"""
        service = FoodDecisionService(Mock())
        
        food = {'name': 'Test Food', 'category': 'test'}
        nutrition = {'calories': 100, 'protein': 25, 'carbs': 5, 'fat': 2}
        
        reason = service._generate_alternative_reason(food, nutrition, 150)
        
        assert isinstance(reason, str)
        assert len(reason) > 0
        assert 'protein' in reason or 'saved' in reason or 'calorie' in reason.lower()


class TestFoodDecisionRouter:
    @pytest.mark.asyncio
    async def test_should_i_eat_increments_food_scan_usage_after_success(self):
        from app.routers.food_decision import should_i_eat
        from app.schemas.food_decision_schemas import ShouldIEatRequest

        endpoint = inspect.unwrap(should_i_eat)
        decision_payload = {
            'decision': 'green',
            'reasons': [],
            'impact': {
                'calories_used_percentage': 10,
                'remaining_calories': 1800,
                'remaining_protein': 120,
                'remaining_carbs': 150,
                'remaining_fat': 40,
            },
            'alternatives': None,
            'current_stats': {
                'consumed_calories': 200,
                'consumed_protein': 20,
                'consumed_carbs': 25,
                'consumed_fat': 10,
                'calorie_goal': 2000,
            },
            'totals': {
                'calories': 120,
                'protein': 0,
                'carbs': 0,
                'fat': 0,
                'sodium': 0,
                'sugar': 0,
            },
        }

        with patch('app.routers.food_decision.get_supabase', return_value=Mock()), \
             patch('app.routers.food_decision.check_premium_status', new=AsyncMock(return_value=False)), \
             patch('app.routers.food_decision.check_usage_limit', new=AsyncMock(return_value={
                 'allowed': True,
                 'current_count': 0,
                 'limit': 5,
                 'remaining': 5,
             })), \
             patch('app.routers.food_decision.increment_usage', new=AsyncMock()) as mock_increment_usage, \
             patch('app.routers.food_decision.openai_service.analyze_food_image', new=AsyncMock(return_value={
                 'items': [{'name': 'Diet Coke', 'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}],
                 'confidence': 'high',
             })), \
             patch('app.routers.food_decision.FoodDecisionService.should_i_eat', new=AsyncMock(return_value=decision_payload)), \
             patch('app.routers.food_decision._generate_ai_advice', new=AsyncMock(return_value='Looks good.')):
            response = await endpoint(Mock(), ShouldIEatRequest(image_base64='abc123'), {'id': 'user-1'})

        assert response.decision == 'green'
        mock_increment_usage.assert_awaited_once_with('user-1', 'food_scan')

    @pytest.mark.asyncio
    async def test_should_i_eat_returns_402_when_food_scan_limit_is_reached(self):
        from app.routers.food_decision import should_i_eat
        from app.schemas.food_decision_schemas import ShouldIEatRequest

        endpoint = inspect.unwrap(should_i_eat)

        with patch('app.routers.food_decision.get_supabase', return_value=Mock()), \
             patch('app.routers.food_decision.check_premium_status', new=AsyncMock(return_value=False)), \
             patch('app.routers.food_decision.check_usage_limit', new=AsyncMock(side_effect=Exception('Usage limit exceeded for food_scan. Upgrade to premium for unlimited access.'))):
            with pytest.raises(HTTPException) as exc:
                await endpoint(Mock(), ShouldIEatRequest(image_base64='abc123'), {'id': 'user-1'})

        assert exc.value.status_code == 402
        assert 'usage limit exceeded' in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_should_i_eat_returns_422_when_no_food_detected(self):
        from app.routers.food_decision import should_i_eat
        from app.schemas.food_decision_schemas import ShouldIEatRequest

        endpoint = inspect.unwrap(should_i_eat)

        with patch('app.routers.food_decision.get_supabase', return_value=Mock()), \
             patch('app.routers.food_decision.check_premium_status', new=AsyncMock(return_value=False)), \
             patch('app.routers.food_decision.check_usage_limit', new=AsyncMock(return_value={
                 'allowed': True,
                 'current_count': 0,
                 'limit': 5,
                 'remaining': 5,
             })), \
             patch('app.routers.food_decision.openai_service.analyze_food_image', new=AsyncMock(return_value={
                 'items': [],
                 'confidence': 'low',
             })):
            with pytest.raises(HTTPException) as exc:
                await endpoint(Mock(), ShouldIEatRequest(image_base64='abc123'), {'id': 'user-1'})

        assert exc.value.status_code == 422
        assert 'food or drink' in exc.value.detail.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
