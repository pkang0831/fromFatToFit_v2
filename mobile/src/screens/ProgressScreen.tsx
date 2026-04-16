import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Dimensions,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { format, parseISO } from 'date-fns';
import { LineChart } from 'react-native-chart-kit';

import {
  dashboardApi,
  GoalProjectionResponse,
  homeApi,
  HomeSummary,
  weightApi,
} from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

const CHART_WIDTH = Dimensions.get('window').width - spacing.md * 2 - spacing.lg * 2;

function formatDateLabel(value: string) {
  try {
    return format(parseISO(value), 'M/d');
  } catch {
    return value;
  }
}

function formatGoalDate(value?: string | null) {
  if (!value) {
    return 'Adjust your plan';
  }

  try {
    return format(parseISO(value), 'MMM d');
  } catch {
    return value;
  }
}

function buildLabels(points: string[]) {
  const step = Math.max(1, Math.ceil(points.length / 4));
  return points.map((point, index) => {
    if (index === 0 || index === points.length - 1 || index % step === 0) {
      return formatDateLabel(point);
    }
    return '';
  });
}

export default function ProgressScreen({ navigation }: any) {
  const [summary, setSummary] = useState<HomeSummary | null>(null);
  const [quickStats, setQuickStats] = useState<any>(null);
  const [projection, setProjection] = useState<GoalProjectionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [savingWeight, setSavingWeight] = useState(false);
  const [targetDeficit, setTargetDeficit] = useState(500);
  const [weightInput, setWeightInput] = useState('');
  const [bodyFatInput, setBodyFatInput] = useState('');
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    void loadProgress();
  }, [targetDeficit]);

  const loadProgress = async () => {
    setLoadError(null);
    try {
      const [summaryResult, quickStatsResult, projectionResult] = await Promise.allSettled([
        homeApi.getSummary(),
        dashboardApi.getQuickStats(),
        weightApi.getProjection({ days_history: 30, target_deficit: targetDeficit }),
      ]);

      if (summaryResult.status === 'fulfilled') {
        setSummary(summaryResult.value.data);
      } else {
        setSummary(null);
      }

      if (quickStatsResult.status === 'fulfilled') {
        setQuickStats(quickStatsResult.value.data);
      } else {
        setQuickStats(null);
      }

      if (projectionResult.status === 'fulfilled') {
        setProjection(projectionResult.value.data);
      } else {
        setProjection(null);
      }

      if (
        summaryResult.status === 'rejected' &&
        quickStatsResult.status === 'rejected' &&
        projectionResult.status === 'rejected'
      ) {
        setLoadError('We could not load your progress yet.');
      } else if (
        summaryResult.status === 'rejected' ||
        quickStatsResult.status === 'rejected' ||
        projectionResult.status === 'rejected'
      ) {
        setLoadError('Some progress data is unavailable right now. Showing what we have.');
      }
    } catch (error: any) {
      console.error('Error loading progress:', error);
      setLoadError(error?.response?.data?.detail ?? 'Please try again in a moment.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    void loadProgress();
  };

  const saveWeightEntry = async () => {
    if (!weightInput.trim()) {
      Alert.alert('Weight needed', 'Enter today’s scale reading first.');
      return;
    }

    const parsedWeight = Number(weightInput);
    const parsedBodyFat = bodyFatInput.trim() ? Number(bodyFatInput) : undefined;

    if (!Number.isFinite(parsedWeight) || parsedWeight <= 0) {
      Alert.alert('Invalid weight', 'Enter a valid weight in kilograms.');
      return;
    }

    if (parsedBodyFat != null && (!Number.isFinite(parsedBodyFat) || parsedBodyFat < 0 || parsedBodyFat > 100)) {
      Alert.alert('Invalid body fat', 'Body fat should be a percentage between 0 and 100.');
      return;
    }

    setSavingWeight(true);
    try {
      await weightApi.createLog({
        date: new Date().toISOString().split('T')[0],
        weight_kg: parsedWeight,
        body_fat_percentage: parsedBodyFat,
      });
      setWeightInput('');
      setBodyFatInput('');
      await loadProgress();
    } catch (error: any) {
      Alert.alert('Could not save entry', error?.response?.data?.detail ?? 'Please try again.');
    } finally {
      setSavingWeight(false);
    }
  };

  const chartModel = useMemo(() => {
    if (!projection) {
      return null;
    }

    const historical = projection.historical_data.slice(-10);
    const future = projection.projection_data.slice(0, 21);
    const points = [...historical.map((point) => point.date), ...future.map((point) => point.date)];
    const currentPath = [
      ...historical.map((point) => point.moving_avg_weight),
      ...future.map((point) => point.projected_weight),
    ];
    const targetLine = points.map(() => projection.target_weight ?? projection.current_weight);

    return {
      labels: buildLabels(points),
      datasets: [
        {
          data: currentPath,
          color: () => colors.chartPrimary,
          strokeWidth: 3,
        },
        {
          data: targetLine,
          color: () => colors.secondary,
          strokeWidth: 2,
          withDots: false,
        },
      ],
      legend: ['Your path', 'Target'],
    };
  }, [projection]);

  const weeklyStatus = summary?.latest_weekly_checkin?.weekly_status ?? null;
  const weeklyTone =
    weeklyStatus === 'improved'
      ? colors.success
      : weeklyStatus === 'regressed'
        ? colors.error
        : weeklyStatus === 'low_confidence'
          ? colors.warning
          : colors.primary;
  const weeklyLabel =
    weeklyStatus === 'improved'
      ? 'Looking better this week'
      : weeklyStatus === 'regressed'
        ? 'Weekly check-in needs review'
        : weeklyStatus === 'low_confidence'
          ? 'Weekly check-in needs a cleaner photo'
          : summary?.latest_weekly_checkin
            ? 'Weekly check-in is stable'
            : 'No weekly check-in yet';

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!summary && !quickStats && !projection) {
    return (
      <ScrollView
        style={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
        contentContainerStyle={styles.content}
      >
        <View style={styles.errorCard}>
          <Text style={styles.errorEyebrow}>Progress unavailable</Text>
          <Text style={styles.errorTitle}>We couldn’t load your progress yet.</Text>
          <Text style={styles.errorBody}>
            Pull to retry. Once the data loads, you’ll see your weekly proof, goal path, and a place to log today’s weight.
          </Text>
          <View style={styles.errorActions}>
            <TouchableOpacity style={styles.errorPrimaryAction} onPress={onRefresh}>
              <Text style={styles.errorPrimaryActionText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.errorSecondaryAction} onPress={() => navigation.navigate('BodyScan')}>
              <Text style={styles.errorSecondaryActionText}>Go to check-in</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
      contentContainerStyle={styles.content}
    >
      {loadError && (
        <View style={styles.inlineBanner}>
          <Text style={styles.inlineBannerTitle}>Partial load</Text>
          <Text style={styles.inlineBannerBody}>{loadError}</Text>
        </View>
      )}

      <View style={styles.heroCard}>
        <Text style={styles.eyebrow}>WEEKLY PROOF</Text>
        <Text style={styles.heroTitle}>
          {projection?.target_weight
            ? `At ${targetDeficit} kcal/day, you could reach ${projection.target_weight.toFixed(1)} kg around ${formatGoalDate(projection.estimated_goal_date)}.`
            : 'Add a target weight to see a realistic path to goal.'}
        </Text>
        <Text style={styles.heroBody}>
          {projection?.message ?? 'We use your recent trend and your planned calorie deficit to estimate a clear next step.'}
        </Text>
      </View>

      <View style={styles.metricRow}>
        <View style={[styles.metricCard, styles.metricCardBlue]}>
          <Text style={styles.metricLabel}>Current weight</Text>
          <Text style={styles.metricValue}>{projection?.current_weight?.toFixed(1) ?? '--'} kg</Text>
          <Text style={styles.metricSubtext}>3-day trend: {projection?.moving_avg_weight?.toFixed(1) ?? '--'} kg</Text>
        </View>
        <View style={[styles.metricCard, styles.metricCardGreen]}>
          <Text style={styles.metricLabel}>Target weight</Text>
          <Text style={styles.metricValue}>{projection?.target_weight?.toFixed(1) ?? '--'} kg</Text>
          <Text style={styles.metricSubtext}>
            {summary?.goal_summary.gap != null ? `${summary.goal_summary.gap.toFixed(1)}% body-fat gap` : 'Target from saved plan'}
          </Text>
        </View>
      </View>

      <View style={styles.metricRow}>
        <View style={[styles.metricCard, styles.metricCardPurple]}>
          <Text style={styles.metricLabel}>Planned daily deficit</Text>
          <Text style={styles.metricValue}>{targetDeficit}</Text>
          <Text style={styles.metricSubtext}>kcal/day</Text>
          <View style={styles.choiceRow}>
            {[300, 500, 700].map((choice) => (
              <TouchableOpacity
                key={choice}
                style={[styles.choicePill, choice === targetDeficit && styles.choicePillActive]}
                onPress={() => setTargetDeficit(choice)}
              >
                <Text style={[styles.choicePillText, choice === targetDeficit && styles.choicePillTextActive]}>
                  {choice}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        <View style={[styles.metricCard, styles.metricCardAmber]}>
          <Text style={styles.metricLabel}>Goal date</Text>
          <Text style={styles.metricValue}>
            {projection?.estimated_days_to_goal != null ? `${projection.estimated_days_to_goal} days` : '--'}
          </Text>
          <Text style={styles.metricSubtext}>{formatGoalDate(projection?.estimated_goal_date)}</Text>
        </View>
      </View>

      <View style={[styles.statusCard, { borderColor: `${weeklyTone}55` }]}>
        <Text style={[styles.statusHeadline, { color: weeklyTone }]}>{weeklyLabel}</Text>
        <Text style={styles.statusBody}>
          {summary?.latest_weekly_checkin?.qualitative_summary?.[0] ??
            'Weekly proof keeps the trend honest. Add a front-facing check-in photo when you are ready.'}
        </Text>
        <TouchableOpacity style={styles.statusAction} onPress={() => navigation.navigate('BodyScan')}>
          <Text style={styles.statusActionText}>
            {summary?.latest_weekly_checkin ? "Upload this week's photo" : 'Start first weekly check-in'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.chartCard}>
        <Text style={styles.chartTitle}>Daily path to goal</Text>
        <Text style={styles.chartSubtitle}>
          One clean line is your current path. The green line is your goal weight.
        </Text>
        {chartModel ? (
          <>
            <LineChart
              data={chartModel}
              width={CHART_WIDTH}
              height={260}
              withShadow={false}
              withInnerLines
              withOuterLines={false}
              withVerticalLines={false}
              fromZero={false}
              bezier
              yAxisSuffix="kg"
              chartConfig={{
                backgroundGradientFrom: colors.surface,
                backgroundGradientTo: colors.surface,
                decimalPlaces: 1,
                color: (opacity = 1) => `rgba(244, 247, 251, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(164, 173, 194, ${opacity})`,
                propsForDots: {
                  r: '2',
                  strokeWidth: '0',
                },
                propsForBackgroundLines: {
                  stroke: colors.chartGrid,
                },
              }}
              style={styles.chart}
            />
            <View style={styles.chartLegend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: colors.chartPrimary }]} />
                <Text style={styles.legendText}>Your path</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: colors.secondary }]} />
                <Text style={styles.legendText}>Target</Text>
              </View>
            </View>
          </>
        ) : (
          <View style={styles.emptyChart}>
            <Text style={styles.emptyChartTitle}>Add your first weight entry</Text>
            <Text style={styles.emptyChartBody}>
              Once we have a trend, we can show a clearer path toward your target.
            </Text>
          </View>
        )}
      </View>

      <View style={styles.logCard}>
        <Text style={styles.logTitle}>Log today’s weight</Text>
        <Text style={styles.logSubtitle}>One clean entry keeps the projection grounded in reality.</Text>
        <View style={styles.inputRow}>
          <TextInput
            style={[styles.input, styles.inputPrimary]}
            placeholder="Weight kg"
            placeholderTextColor={colors.textSecondary}
            keyboardType="decimal-pad"
            value={weightInput}
            onChangeText={setWeightInput}
          />
          <TextInput
            style={styles.input}
            placeholder="Body fat %"
            placeholderTextColor={colors.textSecondary}
            keyboardType="decimal-pad"
            value={bodyFatInput}
            onChangeText={setBodyFatInput}
          />
        </View>
        <TouchableOpacity
          style={[styles.logButton, savingWeight && styles.logButtonDisabled]}
          disabled={savingWeight}
          onPress={saveWeightEntry}
        >
          <Text style={styles.logButtonText}>{savingWeight ? 'Saving...' : 'Save today’s entry'}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footerStats}>
        <View style={styles.footerStat}>
          <Text style={styles.footerLabel}>Calories today</Text>
          <Text style={styles.footerValue}>{Math.round(quickStats?.today_calories ?? 0)}</Text>
        </View>
        <View style={styles.footerStat}>
          <Text style={styles.footerLabel}>Protein</Text>
          <Text style={styles.footerValue}>{Math.round(quickStats?.today_protein ?? 0)}g</Text>
        </View>
        <View style={styles.footerStat}>
          <Text style={styles.footerLabel}>Workouts</Text>
          <Text style={styles.footerValue}>{quickStats?.workouts_this_week ?? 0}</Text>
        </View>
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
    padding: spacing.md,
    paddingBottom: spacing.xxl,
    gap: spacing.md,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
  },
  inlineBanner: {
    marginBottom: spacing.md,
    padding: spacing.md,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surfaceAlt,
  },
  inlineBannerTitle: {
    ...typography.caption,
    color: colors.warning,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    fontWeight: '700',
  },
  inlineBannerBody: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  errorCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    ...shadows.medium,
  },
  errorEyebrow: {
    ...typography.overline,
    color: colors.warning,
    marginBottom: spacing.sm,
  },
  errorTitle: {
    ...typography.h3,
    marginBottom: spacing.sm,
  },
  errorBody: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  errorActions: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  errorPrimaryAction: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  errorPrimaryActionText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  errorSecondaryAction: {
    flex: 1,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  errorSecondaryActionText: {
    ...typography.button,
    color: colors.text,
  },
  heroCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    ...shadows.medium,
  },
  eyebrow: {
    ...typography.overline,
    color: colors.accent,
    marginBottom: spacing.sm,
  },
  heroTitle: {
    ...typography.h2,
    marginBottom: spacing.sm,
  },
  heroBody: {
    ...typography.body1,
    color: colors.textSecondary,
  },
  metricRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  metricCard: {
    flex: 1,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    overflow: 'hidden',
  },
  metricCardBlue: {
    backgroundColor: 'rgba(54, 80, 128, 0.18)',
    borderColor: 'rgba(143, 180, 217, 0.18)',
  },
  metricCardGreen: {
    backgroundColor: 'rgba(54, 121, 88, 0.18)',
    borderColor: 'rgba(105, 241, 142, 0.18)',
  },
  metricCardPurple: {
    backgroundColor: 'rgba(111, 83, 177, 0.18)',
    borderColor: 'rgba(166, 127, 255, 0.18)',
  },
  metricCardAmber: {
    backgroundColor: 'rgba(171, 102, 36, 0.18)',
    borderColor: 'rgba(212, 178, 118, 0.18)',
  },
  metricLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  metricValue: {
    ...typography.h2,
    marginBottom: spacing.xs,
  },
  metricSubtext: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  choiceRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  choicePill: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    backgroundColor: colors.surface,
  },
  choicePillActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  choicePillText: {
    ...typography.buttonSmall,
    color: colors.text,
  },
  choicePillTextActive: {
    color: colors.textOnPrimary,
  },
  statusCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    padding: spacing.lg,
  },
  statusHeadline: {
    ...typography.h4,
    marginBottom: spacing.sm,
  },
  statusBody: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  statusAction: {
    alignSelf: 'flex-start',
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  statusActionText: {
    ...typography.buttonSmall,
    color: colors.text,
  },
  chartCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    ...shadows.medium,
  },
  chartTitle: {
    ...typography.h3,
    marginBottom: spacing.xs,
  },
  chartSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  chart: {
    borderRadius: borderRadius.lg,
    marginLeft: -spacing.sm,
  },
  chartLegend: {
    flexDirection: 'row',
    gap: spacing.lg,
    marginTop: spacing.md,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  legendSwatch: {
    width: 12,
    height: 12,
    borderRadius: 999,
  },
  legendText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyChart: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    padding: spacing.xl,
    alignItems: 'center',
  },
  emptyChartTitle: {
    ...typography.h5,
    marginBottom: spacing.sm,
  },
  emptyChartBody: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  logCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
  },
  logTitle: {
    ...typography.h4,
    marginBottom: spacing.xs,
  },
  logSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  inputRow: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  input: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    color: colors.text,
  },
  inputPrimary: {
    flex: 1.2,
  },
  logButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  logButtonDisabled: {
    opacity: 0.6,
  },
  logButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  footerStats: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  footerStat: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  footerLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  footerValue: {
    ...typography.h4,
  },
});
