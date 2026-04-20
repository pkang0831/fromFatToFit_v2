import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { foodApi } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';
import { getLocalDateString } from '../utils/date';

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
  { key: 'breakfast', label: 'Breakfast', hint: 'Start light' },
  { key: 'lunch', label: 'Lunch', hint: 'Midday anchor' },
  { key: 'dinner', label: 'Dinner', hint: 'Close the day' },
  { key: 'snack', label: 'Snack', hint: 'Quick add' },
];

const getToday = () => getLocalDateString();

const formatMealTime = (value?: string) => {
  if (!value) return 'Saved today';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Saved today';

  return date.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
};

export default function CalorieTrackerScreen({ navigation }: any) {
  const tabBarHeight = useBottomTabBarHeight();
  const insets = useSafeAreaInsets();
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

  const totals = useMemo(
    () => ({
      calories: summary?.total_calories ?? 0,
      protein: summary?.total_protein ?? 0,
      carbs: summary?.total_carbs ?? 0,
      fat: summary?.total_fat ?? 0,
    }),
    [summary],
  );

  const groupedMeals = useMemo(
    () =>
      MEAL_TYPES.map((type) => {
        const meals = (summary?.meals ?? []).filter((meal) => meal.meal_type === type.key);
        const total = meals.reduce((sum, meal) => sum + meal.calories, 0);

        return {
          ...type,
          meals,
          total,
        };
      }).filter((section) => section.meals.length > 0),
    [summary],
  );

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
      setError('We could not save that meal. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const calorieGoal = summary?.calorie_goal ?? null;
  const goalDelta = calorieGoal ? calorieGoal - totals.calories : null;
  const progressPct =
    calorieGoal && calorieGoal > 0 ? Math.min((totals.calories / calorieGoal) * 100, 100) : 0;
  const helperPills = ['Protein first', 'Camera ready', 'Log what is obvious'];

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading today’s meals...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => void loadTodaysMeals({ refreshing: true })}
          tintColor={colors.primary}
        />
      }
      contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
    >
      <View style={styles.heroCard}>
        <View style={styles.heroHeader}>
          <View style={styles.heroCopy}>
            <Text style={styles.eyebrow}>CALORIES</Text>
            <Text style={styles.heroTitle}>Keep today clear.</Text>
            <Text style={styles.heroBody}>
              Log fast, keep your macros visible, and use the camera when a meal is easier to snap than type.
            </Text>
          </View>
          <View style={styles.statusPill}>
            <Text style={styles.statusPillText}>{summary?.meals?.length ?? 0} meals</Text>
          </View>
        </View>

        <View style={styles.metricGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Today</Text>
            <Text style={styles.metricValue}>{Math.round(totals.calories)}</Text>
            <Text style={styles.metricHint}>kcal logged</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Target</Text>
            <Text style={styles.metricValue}>{calorieGoal ? Math.round(calorieGoal) : '--'}</Text>
            <Text style={styles.metricHint}>{calorieGoal ? 'daily goal' : 'set on web'}</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Protein</Text>
            <Text style={styles.metricValue}>{totals.protein.toFixed(0)}g</Text>
            <Text style={styles.metricHint}>anchor macro</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Carbs + fat</Text>
            <Text style={styles.metricValue}>{Math.round(totals.carbs + totals.fat)}g</Text>
            <Text style={styles.metricHint}>energy split</Text>
          </View>
        </View>

        <View style={styles.goalRow}>
          <Text style={styles.goalTitle}>
            {goalDelta === null
              ? 'No calorie goal synced yet'
              : goalDelta >= 0
                ? `${Math.round(goalDelta)} kcal left for today`
                : `${Math.round(Math.abs(goalDelta))} kcal over goal`}
          </Text>
          <Text style={styles.goalSubtitle}>
            {goalDelta === null ? 'You can still log meals and review today.' : 'Treat this as direction, not judgment.'}
          </Text>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${progressPct}%` }]} />
          </View>
        </View>

        <View style={styles.heroPillRow}>
          {helperPills.map((pill) => (
            <View key={pill} style={styles.heroInfoPill}>
              <Text style={styles.heroInfoPillText}>{pill}</Text>
            </View>
          ))}
        </View>

        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.primaryAction} onPress={() => navigation.navigate('FoodCamera')}>
            <Text style={styles.primaryActionText}>Open food camera</Text>
            <Text style={styles.primaryActionHint}>Scan a meal photo</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryAction} onPress={() => setShowAddForm((prev) => !prev)}>
            <Text style={styles.secondaryActionText}>{showAddForm ? 'Hide quick log' : 'Quick log'}</Text>
            <Text style={styles.secondaryActionHint}>Add one meal manually</Text>
          </TouchableOpacity>
        </View>
      </View>

      {error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Could not load calories</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => void loadTodaysMeals()}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {showAddForm ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionEyebrow}>QUICK LOG</Text>
          <Text style={styles.sectionTitle}>Add one meal.</Text>
          <Text style={styles.sectionBody}>Keep it short. Log what you know and skip what you do not.</Text>

          <View style={styles.pillRow}>
            {MEAL_TYPES.map((type) => {
              const active = mealType === type.key;
              return (
                <TouchableOpacity
                  key={type.key}
                  style={[styles.pill, active && styles.pillActive]}
                  onPress={() => setMealType(type.key)}
                >
                  <Text style={[styles.pillLabel, active && styles.pillLabelActive]}>{type.label}</Text>
                  <Text style={[styles.pillHint, active && styles.pillHintActive]}>{type.hint}</Text>
                </TouchableOpacity>
              );
            })}
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
            style={[styles.submitButton, submitting && styles.buttonDisabled]}
            onPress={() => void handleAddFood()}
            disabled={submitting}
          >
            {submitting ? (
              <ActivityIndicator color={colors.textOnPrimary} />
            ) : (
              <>
                <Text style={styles.submitButtonText}>Save meal</Text>
                <Text style={styles.submitButtonHint}>Add it to today</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={styles.inlineGhostButton} onPress={() => setShowAddForm(false)}>
            <Text style={styles.inlineGhostButtonText}>Hide quick log</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>TODAY</Text>
        <Text style={styles.sectionTitle}>Meals at a glance.</Text>
        <Text style={styles.sectionBody}>
          The point is not perfect logging. It is keeping the day readable enough to learn from it.
        </Text>

        {groupedMeals.length > 0 ? (
          groupedMeals.map((section) => (
            <View key={section.key} style={styles.mealSection}>
              <View style={styles.mealSectionHeader}>
                <View>
                  <Text style={styles.mealSectionEyebrow}>{section.hint}</Text>
                  <Text style={styles.mealSectionTitle}>{section.label}</Text>
                  <Text style={styles.mealSectionMeta}>
                    {section.meals.length} item{section.meals.length === 1 ? '' : 's'}
                  </Text>
                </View>
                <Text style={styles.mealSectionCalories}>{Math.round(section.total)} kcal</Text>
              </View>

              {section.meals.map((meal) => (
                <View key={meal.id} style={styles.mealCard}>
                  <View style={styles.mealCardHeader}>
                    <Text style={styles.mealName}>{meal.food_name}</Text>
                    <Text style={styles.mealCalories}>{Math.round(meal.calories)} kcal</Text>
                  </View>
                  <Text style={styles.mealMeta}>
                    {meal.protein.toFixed(0)}p · {meal.carbs.toFixed(0)}c · {meal.fat.toFixed(0)}f
                  </Text>
                  <Text style={styles.mealTime}>{formatMealTime(meal.created_at)}</Text>
                </View>
              ))}
            </View>
          ))
        ) : (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyTitle}>No meals logged yet.</Text>
            <Text style={styles.emptyText}>Start with one meal or use the food camera to create your first entry for today.</Text>
          </View>
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
    paddingBottom: spacing.xl,
    gap: spacing.lg,
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
  heroCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.medium,
  },
  heroHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
  },
  heroCopy: {
    flex: 1,
  },
  eyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  heroTitle: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  heroBody: {
    ...typography.body1,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  statusPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statusPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  metricGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  metricCard: {
    width: '48%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  metricLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: spacing.xs,
  },
  metricValue: {
    ...typography.h3,
    color: colors.text,
    marginBottom: 4,
  },
  metricHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  goalRow: {
    marginTop: spacing.lg,
    gap: spacing.sm,
  },
  goalTitle: {
    ...typography.button,
    color: colors.text,
  },
  goalSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  progressTrack: {
    height: 8,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    overflow: 'hidden',
    marginTop: spacing.xs,
  },
  progressFill: {
    height: '100%',
    borderRadius: borderRadius.round,
    backgroundColor: colors.primary,
  },
  heroPillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  heroInfoPill: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  heroInfoPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  actionRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  primaryAction: {
    flex: 1.2,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  primaryActionText: {
    ...typography.button,
    color: colors.textOnPrimary,
    marginBottom: spacing.xs,
  },
  primaryActionHint: {
    ...typography.caption,
    color: colors.textOnPrimary,
    opacity: 0.88,
  },
  secondaryAction: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryActionText: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  secondaryActionHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  errorCard: {
    backgroundColor: `${colors.error}12`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.error}40`,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  errorTitle: {
    ...typography.button,
    color: colors.text,
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  retryButton: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  retryButtonText: {
    ...typography.button,
    color: colors.text,
  },
  sectionCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    ...shadows.small,
  },
  sectionEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  sectionBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
  },
  pill: {
    minWidth: '47%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  pillActive: {
    backgroundColor: `${colors.primary}16`,
    borderColor: `${colors.primary}55`,
  },
  pillLabel: {
    ...typography.button,
    color: colors.text,
    marginBottom: 4,
  },
  pillLabelActive: {
    color: colors.primary,
  },
  pillHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  pillHintActive: {
    color: colors.primary,
  },
  input: {
    ...typography.body1,
    color: colors.text,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    marginBottom: spacing.sm,
  },
  rowInputs: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  flexInput: {
    flex: 1,
  },
  submitButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  submitButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  submitButtonHint: {
    ...typography.caption,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
    opacity: 0.88,
  },
  inlineGhostButton: {
    alignSelf: 'flex-start',
    marginTop: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inlineGhostButtonText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  mealSection: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  mealSectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  mealSectionEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: 2,
  },
  mealSectionTitle: {
    ...typography.button,
    color: colors.text,
  },
  mealSectionMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  mealSectionCalories: {
    ...typography.button,
    color: colors.primary,
  },
  mealCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
  },
  mealCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.md,
    alignItems: 'center',
  },
  mealName: {
    ...typography.button,
    color: colors.text,
    flex: 1,
  },
  mealCalories: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  mealMeta: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  mealTime: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.sm,
  },
  emptyTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});
