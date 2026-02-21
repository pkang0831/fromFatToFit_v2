'use client';

import { Lightbulb, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface RemainingMacros {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

interface FoodRecommendation {
  food_id: string;
  food_name: string;
  category: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  serving_size: string;
  reason: string;
  match_score: number;
}

interface RecommendationResponse {
  meal_type: string;
  remaining: RemainingMacros;
  recommendations: FoodRecommendation[];
  ai_explanation: string;
}

interface Props {
  recommendations: RecommendationResponse;
  onSelectFood: (foodId: string) => void;
}

const MEAL_TYPE_LABELS = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
};

export function FoodRecommendations({ recommendations, onSelectFood }: Props) {
  return (
    <div className="space-y-6">
      {/* Remaining Macros */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Remaining Daily Nutrition
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center bg-white/70 p-4 rounded-lg">
              <div className="text-3xl font-bold text-blue-600">
                {recommendations.remaining.calories.toFixed(0)}
              </div>
              <div className="text-sm text-gray-600 mt-1">kcal</div>
            </div>
            <div className="text-center bg-white/70 p-4 rounded-lg">
              <div className="text-3xl font-bold text-green-600">
                {recommendations.remaining.protein.toFixed(0)}g
              </div>
              <div className="text-sm text-gray-600 mt-1">Protein</div>
            </div>
            <div className="text-center bg-white/70 p-4 rounded-lg">
              <div className="text-3xl font-bold text-orange-600">
                {recommendations.remaining.carbs.toFixed(0)}g
              </div>
              <div className="text-sm text-gray-600 mt-1">Carbs</div>
            </div>
            <div className="text-center bg-white/70 p-4 rounded-lg">
              <div className="text-3xl font-bold text-purple-600">
                {recommendations.remaining.fat.toFixed(0)}g
              </div>
              <div className="text-sm text-gray-600 mt-1">Fat</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Strategy */}
      <Card className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-purple-600" />
            Today's Strategy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-800 leading-relaxed">{recommendations.ai_explanation}</p>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <div>
        <h3 className="text-2xl font-bold mb-4">
          {MEAL_TYPE_LABELS[recommendations.meal_type as keyof typeof MEAL_TYPE_LABELS] || recommendations.meal_type} Picks
        </h3>
        <div className="space-y-4">
          {recommendations.recommendations.map((food, idx) => (
            <Card 
              key={food.food_id} 
              className="hover:shadow-xl transition border-2 border-gray-200 hover:border-blue-400"
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    {/* Rank Badge */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className={`
                        flex items-center justify-center w-12 h-12 rounded-full font-bold text-lg
                        ${idx === 0 ? 'bg-yellow-400 text-yellow-900' : 
                          idx === 1 ? 'bg-gray-300 text-gray-800' : 
                          idx === 2 ? 'bg-orange-300 text-orange-900' : 
                          'bg-blue-100 text-blue-900'}
                      `}>
                        #{idx + 1}
                      </div>
                      <div>
                        <h4 className="font-bold text-xl">{food.food_name}</h4>
                        <p className="text-sm text-gray-600">{food.category}</p>
                      </div>
                    </div>
                    
                    {/* Nutrition Info */}
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Calories:</span>
                        <span className="font-semibold">{food.calories.toFixed(0)} kcal</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Protein:</span>
                        <span className="font-semibold">{food.protein.toFixed(1)}g</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Carbs:</span>
                        <span className="font-semibold">{food.carbs.toFixed(1)}g</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className="text-gray-600">Fat:</span>
                        <span className="font-semibold">{food.fat.toFixed(1)}g</span>
                      </div>
                    </div>
                    
                    {/* AI Reason */}
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg mb-3">
                      <p className="text-sm text-gray-800 leading-relaxed">
                        <span className="font-semibold text-blue-700">💡 Why:</span> {food.reason}
                      </p>
                    </div>
                    
                    {/* Match Score */}
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="bg-gray-200 rounded-full h-3 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(food.match_score, 100)}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-sm font-semibold text-gray-700 min-w-[60px]">
                        {food.match_score.toFixed(0)}% match
                      </span>
                    </div>
                  </div>
                  
                  {/* Select Button */}
                  <Button
                    onClick={() => onSelectFood(food.food_id)}
                    className="ml-4 h-auto py-3 px-6"
                    size="lg"
                  >
                    Select
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {recommendations.recommendations.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-gray-600 text-lg">
              No food recommendations match your current criteria.
            </p>
            <p className="text-gray-500 text-sm mt-2">
              Try adjusting settings or selecting a different meal time.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
