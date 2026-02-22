'use client';

import { useState, FormEvent, useEffect } from 'react';
import toast from 'react-hot-toast';
import { ScanBarcode } from 'lucide-react';
import { Input, Select, Button, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { Autocomplete, AutocompleteOption } from '@/components/ui/Autocomplete';
import { BarcodeScanner } from '@/components/features/BarcodeScanner';
import { foodApi, foodDatabaseApi } from '@/lib/api/services';
import { getTodayString } from '@/lib/utils/date';
import { 
  calculateNutrition, 
  convertToGrams, 
  getWeightUnitOptions, 
  WeightUnit,
  NutritionPer100g 
} from '@/lib/utils/units';
import type { FoodLogCreate } from '@/types/api';

interface FoodLogFormProps {
  onSuccess: () => void;
  initialDate?: string;
}

export function FoodLogForm({ onSuccess, initialDate }: FoodLogFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Barcode scanner state
  const [showScanner, setShowScanner] = useState(false);

  // Autocomplete states
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<AutocompleteOption[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchDebounce, setSearchDebounce] = useState<NodeJS.Timeout | null>(null);
  
  // Selected food and calculation states
  const [selectedFood, setSelectedFood] = useState<any>(null);
  const [portionAmount, setPortionAmount] = useState<string>('100');
  const [portionUnit, setPortionUnit] = useState<WeightUnit>('g');
  const [calculatedNutrition, setCalculatedNutrition] = useState<{
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  } | null>(null);

  // Debounced search
  useEffect(() => {
    if (searchDebounce) {
      clearTimeout(searchDebounce);
    }

    if (searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    const timeout = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await foodDatabaseApi.searchFoods(searchQuery, 10);
        const foods = response.data.results || [];
        
        const options: AutocompleteOption[] = foods.map((food: any) => ({
          id: food.id,
          label: food.name,
          subtitle: `${food.nutrition_per_100g.calories} cal / 100g`,
          data: food,
        }));
        
        setSearchResults(options);

        if (foods.length < 5 && searchQuery.length >= 3) {
          try {
            const extRes = await foodDatabaseApi.searchExternal(searchQuery, 10 - foods.length);
            const extOptions: AutocompleteOption[] = (extRes.data.results || []).map((item: any) => ({
              id: item.id,
              label: item.food_name,
              subtitle: `${item.nutrition_per_100g.calories} kcal/100g · Open Food Facts`,
              data: { ...item, name: item.food_name, source: 'openfoodfacts' },
            }));
            setSearchResults(prev => [...prev, ...extOptions]);
          } catch {
            // External search failed silently
          }
        }
      } catch (err) {
        console.error('Search error:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    setSearchDebounce(timeout);

    return () => {
      if (timeout) clearTimeout(timeout);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery]);

  // Handle food selection from autocomplete
  const handleFoodSelect = (option: AutocompleteOption) => {
    setSelectedFood(option.data);
    setSearchQuery(option.label);
    
    // Auto-calculate with default 100g
    if (option.data?.nutrition_per_100g) {
      calculateAndSetNutrition(option.data.nutrition_per_100g, 100, 'g');
    }
  };

  // Calculate nutrition when amount/unit changes
  const calculateAndSetNutrition = (
    nutritionPer100g: NutritionPer100g,
    amount: number,
    unit: WeightUnit
  ) => {
    const result = calculateNutrition(nutritionPer100g, amount, unit);
    setCalculatedNutrition({
      calories: result.calories,
      protein: result.protein,
      carbs: result.carbs,
      fat: result.fat,
    });
  };

  // Recalculate when portion amount or unit changes
  useEffect(() => {
    if (selectedFood?.nutrition_per_100g && portionAmount) {
      const amount = parseFloat(portionAmount);
      if (!isNaN(amount) && amount > 0) {
        calculateAndSetNutrition(
          selectedFood.nutrition_per_100g,
          amount,
          portionUnit
        );
      }
    }
  }, [portionAmount, portionUnit, selectedFood]);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    
    // Use calculated nutrition if available, otherwise use manual input
    const data: FoodLogCreate = {
      date: initialDate || getTodayString(),
      meal_type: formData.get('meal_type') as any,
      food_name: selectedFood ? selectedFood.name : searchQuery,
      calories: calculatedNutrition ? calculatedNutrition.calories : Number(formData.get('calories')),
      protein: calculatedNutrition ? calculatedNutrition.protein : (formData.get('protein') ? Number(formData.get('protein')) : undefined),
      carbs: calculatedNutrition ? calculatedNutrition.carbs : (formData.get('carbs') ? Number(formData.get('carbs')) : undefined),
      fat: calculatedNutrition ? calculatedNutrition.fat : (formData.get('fat') ? Number(formData.get('fat')) : undefined),
      serving_size: selectedFood 
        ? `${portionAmount}${portionUnit}` 
        : (formData.get('serving_size') as string) || undefined,
      source: 'manual',
    };

    try {
      await foodApi.logFood(data);
      onSuccess();
      toast.success('Food logged successfully');
      
      // Reset form
      setSearchQuery('');
      setSelectedFood(null);
      setCalculatedNutrition(null);
      setPortionAmount('100');
      setPortionUnit('g');
      (e.target as HTMLFormElement).reset();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to log food');
    } finally {
      setIsLoading(false);
    }
  };

  const unitOptions = getWeightUnitOptions();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Log Food</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Meal Type Selection */}
          <Select name="meal_type" label="Meal Type" required>
            <option value="breakfast">Breakfast</option>
            <option value="lunch">Lunch</option>
            <option value="dinner">Dinner</option>
            <option value="snack">Snack</option>
          </Select>

          {/* Food Search with Autocomplete + Barcode Scanner */}
          <div className="space-y-2">
            <div className="flex items-end gap-2">
              <div className="flex-1">
                <Autocomplete
                  value={searchQuery}
                  onChange={setSearchQuery}
                  onSelect={handleFoodSelect}
                  options={searchResults}
                  placeholder="Search food (e.g., Chicken Breast, Rice, Broccoli)"
                  label="Food Name"
                  loading={isSearching}
                  required
                />
              </div>
              <button
                type="button"
                onClick={() => setShowScanner(true)}
                className="flex items-center gap-1.5 px-3 py-2 bg-primary/10 text-primary rounded-xl hover:bg-primary/20 transition-colors text-sm font-medium"
              >
                <ScanBarcode className="w-4 h-4" />
                Scan
              </button>
            </div>
          </div>

          {/* Smart Portion Calculator (shown when food is selected) */}
          {selectedFood && (
            <div className="p-4 bg-gray-100 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-700 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{selectedFood.name}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedFood.nutrition_per_100g.calories} cal / 100g
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFood(null);
                    setCalculatedNutrition(null);
                  }}
                  className="text-xs text-primary hover:underline"
                >
                  Clear
                </button>
              </div>

              {/* Portion Input with Unit Selection */}
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Amount"
                  type="number"
                  min="0"
                  step="0.1"
                  value={portionAmount}
                  onChange={(e) => setPortionAmount(e.target.value)}
                  placeholder="100"
                  required
                />
                <Select
                  label="Unit"
                  value={portionUnit}
                  onChange={(e) => setPortionUnit(e.target.value as WeightUnit)}
                  required
                >
                  {unitOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </Select>
              </div>

              {/* Calculated Nutrition Display */}
              {calculatedNutrition && (
                <div className="grid grid-cols-4 gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Calories</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {Math.round(calculatedNutrition.calories)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Protein</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {calculatedNutrition.protein.toFixed(1)}g
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Carbs</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {calculatedNutrition.carbs.toFixed(1)}g
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Fat</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-white">
                      {calculatedNutrition.fat.toFixed(1)}g
                    </p>
                  </div>
                </div>
              )}

              {/* Quick Serving Size Buttons */}
              {selectedFood.common_serving_sizes && selectedFood.common_serving_sizes.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  <p className="text-xs text-gray-600 dark:text-gray-400 w-full">Quick select:</p>
                  {selectedFood.common_serving_sizes.map((serving: any, index: number) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        setPortionAmount(serving.grams.toString());
                        setPortionUnit('g');
                      }}
                      className="px-3 py-1 text-xs bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-primary hover:text-white transition-colors"
                    >
                      {serving.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Manual Entry (fallback when no food selected) */}
          {!selectedFood && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Input
                name="calories"
                label="Calories"
                type="number"
                min="0"
                step="1"
                placeholder="0"
                required
              />
              <Input
                name="protein"
                label="Protein (g)"
                type="number"
                min="0"
                step="0.1"
                placeholder="0"
              />
              <Input
                name="carbs"
                label="Carbs (g)"
                type="number"
                min="0"
                step="0.1"
                placeholder="0"
              />
              <Input
                name="fat"
                label="Fat (g)"
                type="number"
                min="0"
                step="0.1"
                placeholder="0"
              />
            </div>
          )}

          {!selectedFood && (
            <Input
              name="serving_size"
              label="Serving Size"
              placeholder="e.g., 1 cup, 100g"
            />
          )}

          {error && (
            <div className="p-3 bg-error/10 border border-error rounded-lg">
              <p className="text-sm text-error">{error}</p>
            </div>
          )}

          <Button type="submit" variant="primary" isLoading={isLoading} className="w-full">
            Log Food
          </Button>

          {showScanner && (
            <BarcodeScanner
              onFoodFound={(food) => {
                setSearchQuery(food.food_name);
                setSelectedFood({
                  name: food.food_name,
                  nutrition_per_100g: food.nutrition_per_100g,
                });
                if (food.nutrition_per_100g) {
                  calculateAndSetNutrition(food.nutrition_per_100g, 100, 'g');
                }
                setShowScanner(false);
              }}
              onClose={() => setShowScanner(false)}
            />
          )}
        </form>
      </CardContent>
    </Card>
  );
}
