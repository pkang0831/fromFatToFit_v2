'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Camera, TrendingUp, Utensils, Clock, Plus, ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { FoodLogForm } from '@/components/features/FoodLogForm';
import { MealCard } from '@/components/features/MealCard';
import { foodApi } from '@/lib/api/services';
import { getTodayString, formatDateLong, formatLocalDateKR } from '@/lib/utils/date';
import type { DailySummaryResponse, TrendResponse, RecentFoodItem } from '@/types/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { formatDateShort } from '@/lib/utils/date';

export default function CaloriesPage() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<string>(getTodayString());
  const [dailyData, setDailyData] = useState<DailySummaryResponse | null>(null);
  const [trendData, setTrendData] = useState<TrendResponse | null>(null);
  const [recentFoods, setRecentFoods] = useState<RecentFoodItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDays, setSelectedDays] = useState<7 | 30>(7);
  const [quickLogging, setQuickLogging] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [dailyResponse, trendResponse, recentResponse] = await Promise.all([
        foodApi.getDailyFood(selectedDate),
        foodApi.getTrends(selectedDays),
        foodApi.getRecentFoods(7, 8),
      ]);
      setDailyData(dailyResponse.data);
      setTrendData(trendResponse.data);
      setRecentFoods(recentResponse.data.recent_foods);
    } catch (error) {
      console.error('Failed to load calorie data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedDate, selectedDays]);

  const handlePreviousDay = () => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() - 1);
    setSelectedDate(date.toISOString().split('T')[0]);
  };

  const handleNextDay = () => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + 1);
    const today = new Date(getTodayString());
    const nextDate = new Date(date.toISOString().split('T')[0]);
    
    // Don't allow going beyond today
    if (nextDate <= today) {
      setSelectedDate(date.toISOString().split('T')[0]);
    }
  };

  const handleToday = () => {
    setSelectedDate(getTodayString());
  };

  const isToday = selectedDate === getTodayString();
  const canGoForward = selectedDate < getTodayString();

  const handleFoodLogged = () => {
    loadData();
  };

  const handleQuickLog = async (food: RecentFoodItem) => {
    try {
      setQuickLogging(food.food_name);
      await foodApi.logFood({
        date: selectedDate,
        food_name: food.food_name,
        calories: food.calories,
        protein: food.protein,
        carbs: food.carbs,
        fat: food.fat,
        serving_size: food.serving_size || '1 serving',
        meal_type: food.meal_type as 'breakfast' | 'lunch' | 'dinner' | 'snack',
      });
      await loadData();
    } catch (error) {
      console.error('Failed to quick log food:', error);
      alert('Failed to log food. Please try again.');
    } finally {
      setQuickLogging(null);
    }
  };

  const calorieProgress = dailyData
    ? Math.min((dailyData.total_calories / dailyData.calorie_goal) * 100, 100)
    : 0;

  // Group meals by type
  const mealsByType = dailyData?.meals.reduce((acc, meal) => {
    if (!acc[meal.meal_type]) {
      acc[meal.meal_type] = [];
    }
    acc[meal.meal_type].push(meal);
    return acc;
  }, {} as Record<string, typeof dailyData.meals>) || {};

  const mealOrder = ['breakfast', 'lunch', 'dinner', 'snack'];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text">Calorie Tracker</h1>
          <p className="text-text-secondary mt-1">{formatDateLong(selectedDate)}</p>
        </div>
        <Button
          variant="secondary"
          onClick={() => router.push('/food-camera')}
        >
          <Camera className="h-5 w-5 mr-2" />
          Scan Food
        </Button>
      </div>

      {/* Date Navigation */}
      <Card variant="outlined">
        <CardContent className="p-4">
          <div className="flex items-center justify-between gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePreviousDay}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              이전 날
            </Button>

            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-primary" />
              <div className="text-center">
                <p className="text-lg font-bold text-text">
                  {formatLocalDateKR(selectedDate)}
                </p>
                {!isToday && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleToday}
                    className="text-xs text-primary mt-1"
                  >
                    오늘로 이동
                  </Button>
                )}
              </div>
              <input
                type="date"
                value={selectedDate}
                max={getTodayString()}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={handleNextDay}
              disabled={!canGoForward}
              className="flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              다음 날
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Daily Summary */}
      {loading ? (
        <Card className="animate-pulse">
          <CardContent className="p-6 h-32" />
        </Card>
      ) : dailyData ? (
        <Card variant="elevated">
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
              <div>
                <p className="text-sm text-text-secondary mb-1">Calories</p>
                <p className="text-3xl font-bold text-text">
                  {Math.round(dailyData.total_calories)}
                </p>
                <p className="text-sm text-text-light">/ {dailyData.calorie_goal}</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Protein</p>
                <p className="text-3xl font-bold text-text">{Math.round(dailyData.total_protein)}g</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Carbs</p>
                <p className="text-3xl font-bold text-text">{Math.round(dailyData.total_carbs)}g</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Fat</p>
                <p className="text-3xl font-bold text-text">{Math.round(dailyData.total_fat)}g</p>
              </div>
              <div>
                <p className="text-sm text-text-secondary mb-1">Progress</p>
                <p className="text-3xl font-bold text-text">{Math.round(calorieProgress)}%</p>
                <div className="mt-2 h-2 bg-border-light rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary transition-all duration-300"
                    style={{ width: `${calorieProgress}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : null}

      {/* Food Log Form */}
      <FoodLogForm onSuccess={handleFoodLogged} initialDate={selectedDate} />

      {/* Quick Log - Recent Foods */}
      {recentFoods.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Quick Log
              </CardTitle>
              <Badge variant="info" className="text-xs">
                {recentFoods.length} recent items
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-text-secondary mb-4">
              Click to quickly log foods you've eaten recently
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
              {recentFoods.map((food, idx) => (
                <button
                  key={`${food.food_name}-${idx}`}
                  onClick={() => handleQuickLog(food)}
                  disabled={quickLogging === food.food_name}
                  className="p-4 border-2 border-gray-200 rounded-lg hover:border-primary hover:bg-primary/5 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-md"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-text line-clamp-2">
                      {food.food_name}
                    </h4>
                    {quickLogging === food.food_name ? (
                      <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
                    ) : (
                      <Plus className="h-4 w-4 text-primary flex-shrink-0 ml-2" />
                    )}
                  </div>
                  <div className="space-y-1 text-xs text-text-secondary">
                    <div className="flex justify-between">
                      <span>Calories:</span>
                      <span className="font-medium text-primary">
                        {Math.round(food.calories)} kcal
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>P: {Math.round(food.protein)}g</span>
                      <span>C: {Math.round(food.carbs)}g</span>
                      <span>F: {Math.round(food.fat)}g</span>
                    </div>
                  </div>
                  <Badge variant="default" className="mt-2 text-xs capitalize">
                    {food.meal_type}
                  </Badge>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Meals for Selected Date */}
      <div>
        <h2 className="text-2xl font-bold text-text mb-4">
          {isToday ? "오늘의 식사" : `${formatLocalDateKR(selectedDate, { month: 'long', day: 'numeric' })}의 식사`}
        </h2>
        {dailyData && dailyData.meals.length > 0 ? (
          <div className="space-y-6">
            {mealOrder.map((mealType) => {
              const meals = mealsByType[mealType];
              if (!meals || meals.length === 0) return null;

              return (
                <div key={mealType}>
                  <h3 className="text-lg font-semibold text-text capitalize mb-3">
                    {mealType}
                  </h3>
                  <div className="space-y-3">
                    {meals.map((meal) => (
                      <MealCard
                        key={meal.id}
                        meal={meal}
                        onDelete={handleFoodLogged}
                        onUpdate={handleFoodLogged}
                      />
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <Card className="border-dashed border-2">
            <CardContent className="py-16 text-center">
              <Utensils className="h-20 w-20 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                아직 오늘의 식사 기록이 없어요
              </h3>
              <p className="text-gray-500 mb-6">
                첫 식사를 기록하고 칼로리 추적을 시작해보세요!
              </p>
              <div className="flex gap-4 justify-center">
                <Button size="lg" onClick={() => router.push('/food-camera')}>
                  <Camera className="h-5 w-5 mr-2" />
                  사진으로 기록
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Trend Chart */}
      {trendData && trendData.data.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center">
                <TrendingUp className="h-5 w-5 mr-2" />
                Calorie Trends
              </CardTitle>
              <div className="flex gap-2">
                <Button
                  variant={selectedDays === 7 ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDays(7)}
                >
                  7 Days
                </Button>
                <Button
                  variant={selectedDays === 30 ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedDays(30)}
                >
                  30 Days
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#EFEBE9" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(date) => formatDateShort(date)}
                  stroke="#6D4C41"
                />
                <YAxis stroke="#6D4C41" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    border: '1px solid #D7CCC8',
                    borderRadius: '0.5rem',
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="calories"
                  stroke="#8B4513"
                  strokeWidth={2}
                  name="Calories"
                />
                <Line
                  type="monotone"
                  dataKey="goal"
                  stroke="#D2691E"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Goal"
                />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-center text-sm text-text-secondary mt-4">
              Average: {Math.round(trendData.average_calories)} calories/day
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
