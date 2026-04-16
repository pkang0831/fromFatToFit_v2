import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { foodApi } from '../services/api';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

type MealEntry = {
  id: string;
  food_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  meal_type: MealType;
  created_at?: string;
};

type DailySummary = {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  calorie_goal?: number | null;
  meals: MealEntry[];
};

const MEAL_TYPES: Array<{ key: MealType; label: string; hint: string }> = [
  { key: 'breakfast', label: 'Breakfast', hint: 'Morning meal' },
  { key: 'lunch', label: 'Lunch', hint: 'Midday meal' },
  { key: 'dinner', label: 'Dinner', hint: 'Evening meal' },
  { key: 'snack', label: 'Snack', hint: 'Quick bite' },
];

const getToday = () => new Date().toISOString().split('T')[0];

export default function CalorieTrackerScreen({ navigation }: any) {
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [mealType, setMealType] = useState<MealType>('lunch');
  const [foodName, setFoodName] = useState('');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');
  const [carbs, setCarbs] = useState('');
  const [fat, setFat] = useState('');

  const todayMeals = summary?.meals ?? [];
  const totals = useMemo(() => ({
    calories: summary?.total_calories ?? 0,
    protein: summary?.total_protein ?? 0,
    carbs: summary?.total_carbs ?? 0,
    fat: summary?.total_fat ?? 0,
  }), [summary]);

  const loadTodaysMeals = useCallback(async (opts?: { refreshing?: boolean }) => {
    const isRefresh = opts?.refreshing ?? false;
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      setError(null);
      const { data } = await foodApi.getDailyFood(getToday());
      setSummary(data as DailySummary);
    } catch (err) {
      console.error('Error loading meals:', err);
      setError('We could not load today’s meals right now. Check your connection and try again.');
      setSummary(null);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadTodaysMeals();
  }, [loadTodaysMeals]);

  const resetForm = () => {
    setFoodName('');
    setCalories('');
    setProtein('');
    setCarbs('');
    setFat('');
    setMealType('lunch');
  };

  const handleAddFood = async () => {
    const caloriesValue = Number.parseFloat(calories);
    if (!foodName.trim() || Number.isNaN(caloriesValue)) {
      setError('Please enter a food name and calories before saving.');
      return;
    }

    setSubmitting(true);
    try {
      await foodApi.logFood({
        date: getToday(),
        meal_type: mealType,
        food_name: foodName.trim(),
        calories: caloriesValue,
        protein: protein ? Number.parseFloat(protein) : 0,
        carbs: carbs ? Number.parseFloat(carbs) : 0,
        fat: fat ? Number.parseFloat(fat) : 0,
        source: 'manual',
      });

      resetForm();
      setShowAddForm(false);
      await loadTodaysMeals({ refreshing: true });
    } catch (err) {
      console.error('Failed to log food:', err);
      setError('We could not save that meal. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const progressPct = summary?.calorie_goal && summary.calorie_goal > 0
    ? Math.min((totals.calories / summary.calorie_goal) * 100, 100)
    : 0;

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading today’s meals…</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={(
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => void loadTodaysMeals({ refreshing: true })}
          tintColor={colors.primary}
        />
      )}
      contentContainerStyle={styles.content}
    >
      <View style={styles.summaryCard}>
        <Text style={styles.summaryEyebrow}>Today</Text>
        <Text style={styles.summaryTitle}>Calorie tracker</Text>
        <Text style={styles.summaryCopy}>
          Log meals fast, keep macros readable, and open the camera when you want a photo estimate.
        </Text>
        <Text style={styles.summaryCalories}>{Math.round(totals.calories)}</Text>
        <Text style={styles.summaryLabel}>calories logged</Text>
        <Text style={styles.summaryProtein}>{totals.protein.toFixed(1)}g protein</Text>

        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${progressPct}%` }]} />
        </View>
        <Text style={styles.summaryGoal}>
          {summary?.calorie_goal ? `Goal ${Math.round(summary.calorie_goal)} kcal` : 'No calorie goal set yet'}
        </Text>
      </View>

      {error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Could not load tracker</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => void loadTodaysMeals()}
          >
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.cameraButton]}
          onPress={() => navigation.navigate('FoodCamera')}
        >
          <Text style={[styles.actionButtonText, styles.cameraButtonText]}>Open food camera</Text>
          <Text style={[styles.actionButtonSubtext, styles.cameraButtonSubtext]}>Scan a meal photo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => setShowAddForm(prev => !prev)}
        >
          <Text style={styles.actionButtonText}>
            {showAddForm ? 'Close meal form' : 'Add meal manually'}
          </Text>
          <Text style={styles.actionButtonSubtext}>
            {showAddForm ? 'Hide quick log form' : 'Log calories in seconds'}
          </Text>
        </TouchableOpacity>
      </View>

      {showAddForm && (
        <View style={styles.formCard}>
          <Text style={styles.formTitle}>Add a meal</Text>
          <Text style={styles.formSubtitle}>Keep it quick. You can log the macros you know and skip the rest.</Text>

          <View style={styles.pillRow}>
            {MEAL_TYPES.map(type => (
              <TouchableOpacity
                key={type.key}
                style={[
                  styles.pill,
                  mealType === type.key && styles.pillActive,
                ]}
                onPress={() => setMealType(type.key)}
              >
                <Text style={[styles.pillLabel, mealType === type.key && styles.pillLabelActive]}>
                  {type.label}
                </Text>
                <Text style={[styles.pillHint, mealType === type.key && styles.pillHintActive]}>
                  {type.hint}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          <TextInput
            style={styles.input}
            placeholder="Food or meal name"
            placeholderTextColor={colors.textSecondary}
            value={foodName}
            onChangeText={setFoodName}
          />
          <View style={styles.rowInputs}>
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Calories"
              placeholderTextColor={colors.textSecondary}
              value={calories}
              onChangeText={setCalories}
              keyboardType="numeric"
            />
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Protein g"
              placeholderTextColor={colors.textSecondary}
              value={protein}
              onChangeText={setProtein}
              keyboardType="numeric"
            />
          </View>
          <View style={styles.rowInputs}>
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Carbs g"
              placeholderTextColor={colors.textSecondary}
              value={carbs}
              onChangeText={setCarbs}
              keyboardType="numeric"
            />
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Fat g"
              placeholderTextColor={colors.textSecondary}
              value={fat}
              onChangeText={setFat}
              keyboardType="numeric"
            />
          </View>

          <TouchableOpacity
            style={[styles.submitButton, submitting && styles.disabledButton]}
            onPress={handleAddFood}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color={colors.textOnPrimary} />
            ) : (
              <Text style={styles.submitButtonText}>Save meal</Text>
            )}
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.mealsList}>
        <View style={styles.sectionHeader}>
          <Text style={styles.mealsTitle}>Today’s meals</Text>
          <Text style={styles.mealsCount}>{todayMeals.length} logged</Text>
        </View>

        {todayMeals.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Nothing logged yet</Text>
            <Text style={styles.emptyText}>
              Start with a quick manual meal or scan a photo to keep the day moving.
            </Text>
            <View style={styles.emptyActions}>
              <TouchableOpacity style={[styles.actionButton, styles.cameraButton]} onPress={() => navigation.navigate('FoodCamera')}>
                <Text style={[styles.actionButtonText, styles.cameraButtonText]}>Use food camera</Text>
                <Text style={[styles.actionButtonSubtext, styles.cameraButtonSubtext]}>Fastest way to start</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => setShowAddForm(true)}>
                <Text style={styles.actionButtonText}>Add first meal</Text>
                <Text style={styles.actionButtonSubtext}>Open the quick log form</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          todayMeals.map((meal) => (
            <View key={meal.id} style={styles.mealCard}>
              <View style={styles.mealHeader}>
                <Text style={styles.mealName}>{meal.food_name}</Text>
                <View style={styles.mealTag}>
                  <Text style={styles.mealTagText}>{meal.meal_type}</Text>
                </View>
              </View>
              <Text style={styles.mealCalories}>{Math.round(meal.calories)} cal</Text>
              <View style={styles.macroRow}>
                <Text style={styles.mealMacro}>{meal.protein.toFixed(1)}g protein</Text>
                <Text style={styles.mealMacro}>{meal.carbs.toFixed(1)}g carbs</Text>
                <Text style={styles.mealMacro}>{meal.fat.toFixed(1)}g fat</Text>
              </View>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    paddingBottom: spacing.xxl,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.md,
  },
  loadingText: {
    ...typography.body1,
    color: colors.textSecondary,
  },
  summaryCard: {
    backgroundColor: colors.primary,
    padding: spacing.xl,
    borderRadius: borderRadius.xl,
    ...shadows.medium,
  },
  summaryEyebrow: {
    ...typography.caption,
    color: colors.textOnPrimary,
    opacity: 0.85,
    textTransform: 'uppercase',
    letterSpacing: 1.2,
  },
  summaryTitle: {
    ...typography.h2,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
  },
  summaryCopy: {
    ...typography.body2,
    color: colors.textOnPrimary,
    opacity: 0.86,
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  summaryCalories: {
    ...typography.number,
    fontSize: 56,
    color: colors.textOnPrimary,
    marginTop: spacing.md,
  },
  summaryLabel: {
    ...typography.body1,
    color: colors.textOnPrimary,
    opacity: 0.95,
  },
  summaryProtein: {
    ...typography.body2,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
    opacity: 0.95,
  },
  summaryGoal: {
    ...typography.body2,
    color: colors.textOnPrimary,
    marginTop: spacing.sm,
    opacity: 0.9,
  },
  progressTrack: {
    marginTop: spacing.md,
    height: 10,
    borderRadius: 999,
    backgroundColor: 'rgba(255,255,255,0.22)',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 999,
    backgroundColor: colors.textOnPrimary,
  },
  errorCard: {
    backgroundColor: `${colors.error}12`,
    borderWidth: 1,
    borderColor: `${colors.error}33`,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  errorTitle: {
    ...typography.h5,
    color: colors.error,
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  retryButton: {
    marginTop: spacing.md,
    backgroundColor: colors.error,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.md,
    alignSelf: 'flex-start',
  },
  retryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  actions: {
    flexDirection: 'column',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  actionButton: {
    backgroundColor: colors.surfaceAlt,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  cameraButton: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  actionButtonText: {
    ...typography.h5,
    color: colors.text,
  },
  cameraButtonText: {
    color: colors.textOnPrimary,
  },
  actionButtonSubtext: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  cameraButtonSubtext: {
    color: `${colors.textOnPrimary}CC`,
  },
  formCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    marginTop: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.small,
  },
  formTitle: {
    ...typography.h4,
    marginBottom: spacing.xs,
  },
  formSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  pill: {
    flexGrow: 1,
    minWidth: '46%',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  pillActive: {
    backgroundColor: `${colors.primary}14`,
    borderColor: colors.primary,
  },
  pillLabel: {
    ...typography.body1,
    fontWeight: '700',
  },
  pillLabelActive: {
    color: colors.primary,
  },
  pillHint: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  pillHintActive: {
    color: colors.primary,
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    marginBottom: spacing.sm,
    ...typography.body1,
    color: colors.text,
  },
  rowInputs: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  flexInput: {
    flex: 1,
  },
  submitButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  submitButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  disabledButton: {
    opacity: 0.7,
  },
  mealsList: {
    marginTop: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  mealsTitle: {
    ...typography.h4,
  },
  mealsCount: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyState: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  emptyTitle: {
    ...typography.h5,
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  emptyActions: {
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  mealCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: spacing.sm,
    ...shadows.small,
  },
  mealHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  mealName: {
    ...typography.body1,
    fontWeight: '700',
    flex: 1,
    color: colors.text,
  },
  mealTag: {
    backgroundColor: `${colors.primary}12`,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
  },
  mealTagText: {
    ...typography.caption,
    color: colors.primary,
    textTransform: 'capitalize',
  },
  mealCalories: {
    ...typography.number,
    fontSize: 24,
    marginTop: spacing.sm,
    color: colors.primary,
  },
  macroRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
    marginTop: spacing.xs,
  },
  mealMacro: {
    ...typography.body2,
    color: colors.textSecondary,
  },
});
