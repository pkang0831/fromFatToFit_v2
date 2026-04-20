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
import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
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
import { getLocalDateString } from '../utils/date';

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
    return 'Save a goal';
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
  const tabBarHeight = useBottomTabBarHeight();
  const insets = useSafeAreaInsets();
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
    void loadOverview();
  }, []);

  useEffect(() => {
    if (!loading) {
      void loadProjectionOnly();
    }
  }, [targetDeficit]);

  const loadProjectionOnly = async () => {
    try {
      const { data } = await weightApi.getProjection({ days_history: 30, target_deficit: targetDeficit });
      setProjection(data);
      setLoadError(null);
    } catch (error) {
      setLoadError((current) => current ?? 'Some progress data is unavailable right now. Showing what we have.');
    }
  };

  const loadOverview = async () => {
    setLoadError(null);
    try {
      const [summaryResult, quickStatsResult, projectionResult] = await Promise.allSettled([
        homeApi.getSummary(),
        dashboardApi.getQuickStats(),
        weightApi.getProjection({ days_history: 30, target_deficit: targetDeficit }),
      ]);

      setSummary(summaryResult.status === 'fulfilled' ? summaryResult.value.data : null);
      setQuickStats(quickStatsResult.status === 'fulfilled' ? quickStatsResult.value.data : null);
      setProjection(projectionResult.status === 'fulfilled' ? projectionResult.value.data : null);

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
      setLoadError(error?.response?.data?.detail ?? 'Please try again in a moment.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    void loadOverview();
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
        date: getLocalDateString(),
        weight_kg: parsedWeight,
        body_fat_percentage: parsedBodyFat,
      });
      setWeightInput('');
      setBodyFatInput('');
      await loadOverview();
    } catch (error: any) {
      Alert.alert('Could not save entry', error?.response?.data?.detail ?? 'Please try again.');
    } finally {
      setSavingWeight(false);
    }
  };

  const hasActualProjection = (projection?.actual_projection_data?.length ?? 0) > 0;
  const actualPaceLooksNoisy = Math.abs(projection?.avg_daily_deficit ?? 0) > 1200;

  const chartModel = useMemo(() => {
    if (!projection) {
      return null;
    }

    const historical = projection.historical_data.slice(-10);
    const future = projection.projection_data.slice(0, 21);
    const actualFuture = projection.actual_projection_data.slice(0, 21);
    const points = [...historical.map((point) => point.date), ...future.map((point) => point.date)];
    const loggedPath = historical.map((point) => point.weight_kg);
    const trendPath = historical.map((point) => point.moving_avg_weight);
    const plannedPath = [
      ...historical.map((point) => point.moving_avg_weight),
      ...future.map((point) => point.projected_weight),
    ];
    const recentPacePath = hasActualProjection
      ? [
          ...historical.map((point) => point.moving_avg_weight),
          ...actualFuture.map((point) => point.projected_weight),
        ]
      : [];
    const targetLine = points.map(() => projection.target_weight ?? projection.current_weight);

    return {
      labels: buildLabels(points),
      datasets: [
        {
          data: loggedPath,
          color: () => '#4A86F7',
          strokeWidth: 2.4,
        },
        {
          data: trendPath,
          color: () => 'rgba(194, 171, 143, 0.95)',
          strokeWidth: 2.4,
          withDots: false,
        },
        {
          data: plannedPath,
          color: () => '#F1B033',
          strokeWidth: 3,
          strokeDashArray: [6, 4],
          withDots: false,
        },
        ...(hasActualProjection
          ? [
              {
                data: recentPacePath,
                color: () => '#F05D71',
                strokeWidth: 2,
                strokeDashArray: [3, 4],
                withDots: false,
              },
            ]
          : []),
        {
          data: targetLine,
          color: () => '#4ED0B3',
          strokeWidth: 2,
          withDots: false,
        },
      ],
    };
  }, [hasActualProjection, projection]);

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
        ? 'Review this week closely'
        : weeklyStatus === 'low_confidence'
          ? 'Cleaner photo needed'
          : summary?.latest_weekly_checkin
            ? 'Holding steady'
            : 'Start your first proof';
  const goalMetaLabel = projection?.target_weight != null ? `Target ${projection.target_weight.toFixed(1)} kg` : 'Need target';
  const paceMetaLabel = hasActualProjection
    ? `Recent pace ${projection?.avg_daily_deficit?.toFixed(0) ?? 0} kcal/day`
    : 'Planned pace only';
  const chartSupportLine = actualPaceLooksNoisy
    ? 'Recent pace looks noisy, so read this as direction instead of precision.'
    : hasActualProjection
      ? 'Gold is your plan. Red is the pace suggested by recent logs.'
      : 'Gold is the plan. Save more entries to unlock a recent-pace comparison.';

  const proofMetrics = [
    {
      key: 'current',
      label: 'Current',
      value: projection?.current_weight != null ? `${projection.current_weight.toFixed(1)} kg` : '--',
      hint: projection?.moving_avg_weight != null ? `3-day trend ${projection.moving_avg_weight.toFixed(1)} kg` : 'No trend yet',
    },
    {
      key: 'target',
      label: 'Target',
      value: projection?.target_weight != null ? `${projection.target_weight.toFixed(1)} kg` : '--',
      hint:
        projection?.target_weight != null
          ? summary?.goal_summary.gap != null
            ? `${summary.goal_summary.gap.toFixed(1)}% body-fat gap`
            : 'Active target'
          : 'Save a goal',
    },
    {
      key: 'deficit',
      label: 'Deficit',
      value: `${targetDeficit}`,
      hint: 'kcal / day',
    },
    {
      key: 'date',
      label: 'Goal date',
      value: projection?.estimated_days_to_goal != null ? `${projection.estimated_days_to_goal} days` : '--',
      hint: formatGoalDate(projection?.estimated_goal_date),
    },
  ];

  const snapshotMetrics = [
    {
      key: 'calories',
      label: 'Calories',
      value: `${Math.round(quickStats?.today_calories ?? 0)}`,
      hint: 'today',
    },
    {
      key: 'protein',
      label: 'Protein',
      value: `${Math.round(quickStats?.today_protein ?? 0)}g`,
      hint: 'anchor',
    },
    {
      key: 'workouts',
      label: 'Workouts',
      value: `${quickStats?.workouts_this_week ?? 0}`,
      hint: 'this week',
    },
    {
      key: 'proof',
      label: 'Proof',
      value: summary?.latest_weekly_checkin ? weeklyLabel : 'Pending',
      hint: summary?.scan_summary.next_check_in_label ?? 'next check-in',
    },
  ];

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
        contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
      >
        <View style={styles.errorCard}>
          <Text style={styles.errorEyebrow}>Progress unavailable</Text>
          <Text style={styles.errorTitle}>We couldn’t load your progress yet.</Text>
          <Text style={styles.errorBody}>
            Pull to retry. Once the data loads, you’ll see your weekly proof, path to goal, and today’s log here.
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
      contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
    >
      {loadError ? (
        <View style={styles.inlineBanner}>
          <Text style={styles.inlineBannerTitle}>Partial load</Text>
          <Text style={styles.inlineBannerBody}>{loadError}</Text>
        </View>
      ) : null}

      <View style={styles.proofHeroCard}>
        <View style={styles.proofHeroTopRow}>
          <Text style={styles.eyebrow}>WEEKLY PROOF</Text>
          <View style={[styles.statusPill, { borderColor: weeklyTone, backgroundColor: `${weeklyTone}22` }]}>
            <Text style={[styles.statusPillText, { color: weeklyTone }]}>{weeklyLabel}</Text>
          </View>
        </View>

        <View style={styles.proofHeroTop}>
          <View style={styles.proofHeroCopy}>
            <Text style={styles.heroTitle}>
              {projection?.target_weight
                ? `At ${targetDeficit} kcal/day, you could reach ${projection.target_weight.toFixed(1)} kg around ${formatGoalDate(projection.estimated_goal_date)}.`
                : 'Save a target weight to turn this into a real path to goal.'}
            </Text>
            <Text style={styles.heroBody}>
              {projection?.message ??
                'We use your recent weight trend and planned deficit to keep the direction honest.'}
            </Text>
            <Text style={styles.heroSupport}>
              {actualPaceLooksNoisy
                ? 'Recent logging pace looks unusually aggressive or noisy, so use this chart as direction only.'
                : hasActualProjection
                  ? `Your recent pace from logged data is about ${projection?.avg_daily_deficit?.toFixed(0) ?? 0} kcal/day.`
                  : 'This is a directional forecast, not a precise prescription.'}
            </Text>
          </View>

          <View style={styles.heroSignalCard}>
            <Text style={styles.heroSignalEyebrow}>READ THIS FIRST</Text>
            <View style={styles.heroSignalContent}>
              <Text style={styles.heroSignalTitle}>{goalMetaLabel}</Text>
              <Text style={styles.heroSignalBody}>{paceMetaLabel}</Text>
            </View>
          </View>
        </View>

        <View style={styles.proofHeroMetrics}>
          {proofMetrics.map((item) => (
            <View key={item.key} style={styles.proofHeroMetric}>
              <Text style={styles.proofHeroMetricLabel}>{item.label}</Text>
              <Text style={styles.proofHeroMetricValue}>{item.value}</Text>
              <Text style={styles.proofHeroMetricHint}>{item.hint}</Text>
            </View>
          ))}
        </View>

        <View style={styles.heroControlsCard}>
          <View style={styles.heroControlsHeader}>
            <View>
              <Text style={styles.heroControlsEyebrow}>PACE SCENARIO</Text>
                <Text style={styles.heroControlsTitle}>Read one planned deficit.</Text>
              </View>
            <Text style={styles.heroControlsHint}>Plan line</Text>
            </View>
          <View style={styles.choiceRow}>
            {[300, 500, 700].map((choice) => (
              <TouchableOpacity
                key={choice}
                style={[styles.choicePill, choice === targetDeficit && styles.choicePillActive]}
                onPress={() => setTargetDeficit(choice)}
              >
                <Text style={[styles.choicePillText, choice === targetDeficit && styles.choicePillTextActive]}>
                  {choice} kcal
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <TouchableOpacity style={styles.heroAction} onPress={() => navigation.navigate('BodyScan')}>
          <Text style={styles.heroActionText}>{summary?.latest_weekly_checkin ? 'Review latest proof' : 'Start weekly check-in'}</Text>
          <Text style={styles.heroActionHint}>One weekly photo keeps this forecast honest.</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.chartCard}>
        <View style={styles.chartHeader}>
          <View style={styles.chartHeaderCopy}>
            <Text style={styles.chartEyebrow}>PATH TO GOAL</Text>
            <Text style={styles.chartTitle}>Daily weight path to goal.</Text>
            <Text style={styles.chartSubtitle}>{chartSupportLine}</Text>
          </View>
          <View style={styles.chartMetaColumn}>
            <View style={styles.chartMetaPill}>
              <Text style={styles.chartMetaText}>21 day read</Text>
            </View>
            <View style={styles.chartMetaPillSecondary}>
              <Text style={styles.chartMetaTextSecondary}>{hasActualProjection ? 'Plan + recent pace' : 'Plan only'}</Text>
            </View>
          </View>
        </View>
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
            <View style={styles.chartSupportInline}>
              <Text style={styles.chartSupportInlineLabel}>Read</Text>
              <Text style={styles.chartSupportInlineText}>
                Blue logged, gray trend, gold plan, red recent pace, green target.
              </Text>
            </View>
            <View style={styles.chartLegend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: '#4A86F7' }]} />
                <Text style={styles.legendText}>Logged weight</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: 'rgba(194, 171, 143, 0.95)' }]} />
                <Text style={styles.legendText}>3-day trend</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: '#F1B033' }]} />
                <Text style={styles.legendText}>Your plan</Text>
              </View>
              {hasActualProjection ? (
                <View style={styles.legendItem}>
                  <View style={[styles.legendSwatch, { backgroundColor: '#F05D71' }]} />
                  <Text style={styles.legendText}>Your recent pace</Text>
                </View>
              ) : null}
              <View style={styles.legendItem}>
                <View style={[styles.legendSwatch, { backgroundColor: '#4ED0B3' }]} />
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

      <View style={styles.snapshotCard}>
        <View style={styles.sectionLeadRow}>
          <View>
            <Text style={styles.snapshotEyebrow}>TODAY SNAPSHOT</Text>
            <Text style={styles.snapshotTitle}>Stay close to the basics.</Text>
          </View>
          <View style={styles.sectionLeadPill}>
            <Text style={styles.sectionLeadPillText}>Daily read</Text>
          </View>
        </View>
        <Text style={styles.snapshotSubtitle}>Food, protein, workouts, and proof in one quick read.</Text>
        <View style={styles.snapshotGrid}>
          {snapshotMetrics.map((item) => (
            <View key={item.key} style={styles.snapshotMetric}>
              <Text style={styles.snapshotLabel}>{item.label}</Text>
              <Text style={styles.snapshotValue}>{item.value}</Text>
              <Text style={styles.snapshotHint}>{item.hint}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.logCard}>
        <View style={styles.sectionLeadRow}>
          <View>
            <Text style={styles.logEyebrow}>LOG TODAY</Text>
            <Text style={styles.logTitle}>Keep the projection grounded.</Text>
          </View>
          <View style={styles.sectionLeadPill}>
            <Text style={styles.sectionLeadPillText}>One clean entry</Text>
          </View>
        </View>
        <Text style={styles.logSubtitle}>Morning weigh-in, same scale, optional body fat.</Text>
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
    gap: spacing.lg,
  },
  loadingContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
  },
  inlineBanner: {
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
  proofHeroCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md + 2,
    ...shadows.medium,
  },
  proofHeroTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  proofHeroTop: {
    flexDirection: 'column',
    alignItems: 'stretch',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  proofHeroCopy: {
    flex: 1,
    gap: spacing.xs,
  },
  eyebrow: {
    ...typography.overline,
    color: colors.textLight,
  },
  heroTitle: {
    ...typography.h3,
    color: colors.text,
  },
  heroBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  heroSupport: {
    ...typography.caption,
    color: colors.textLight,
    lineHeight: 18,
  },
  heroSignalCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    gap: spacing.sm,
  },
  heroSignalContent: {
    flexDirection: 'row',
    gap: spacing.md,
    alignItems: 'flex-start',
  },
  heroSignalEyebrow: {
    ...typography.overline,
    color: colors.textLight,
  },
  heroSignalTitle: {
    ...typography.h6,
    color: colors.text,
    flex: 1,
  },
  heroSignalBody: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 18,
    flex: 1,
  },
  statusPill: {
    alignSelf: 'flex-start',
    borderWidth: 1,
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  statusPillText: {
    ...typography.caption,
    fontWeight: '700',
  },
  proofHeroMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  proofHeroMetric: {
    width: '46.5%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.sm + 2,
  },
  proofHeroMetricLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  proofHeroMetricValue: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  proofHeroMetricHint: {
    ...typography.caption,
    color: colors.textLight,
  },
  heroControlsCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
  },
  heroControlsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  heroControlsEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  heroControlsTitle: {
    ...typography.body2,
    color: colors.text,
    lineHeight: 19,
  },
  heroControlsHint: {
    ...typography.caption,
    color: colors.textLight,
    textAlign: 'right',
    maxWidth: 72,
  },
  choiceRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  choicePill: {
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
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
  heroAction: {
    marginTop: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.sm + 2,
    alignItems: 'center',
  },
  heroActionText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  heroActionHint: {
    ...typography.caption,
    color: `${colors.textOnPrimary}CC`,
    marginTop: spacing.xs,
  },
  chartCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    ...shadows.small,
  },
  chartHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  chartHeaderCopy: {
    flex: 1,
  },
  chartEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  chartTitle: {
    ...typography.h4,
    marginBottom: spacing.xs,
  },
  chartSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  chartMetaColumn: {
    alignItems: 'flex-end',
    gap: spacing.xs,
  },
  chartMetaPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  chartMetaText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  chartMetaPillSecondary: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: borderRadius.round,
    backgroundColor: `${colors.primary}12`,
    borderWidth: 1,
    borderColor: `${colors.primary}24`,
  },
  chartMetaTextSecondary: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '700',
  },
  chart: {
    marginTop: spacing.sm,
    marginBottom: spacing.sm,
    borderRadius: borderRadius.lg,
  },
  chartSupportInline: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  chartSupportInlineLabel: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  chartSupportInlineText: {
    ...typography.caption,
    color: colors.text,
    flex: 1,
  },
  chartLegend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
  },
  legendSwatch: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  legendText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyChart: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  emptyChartTitle: {
    ...typography.h5,
    marginBottom: spacing.sm,
  },
  emptyChartBody: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  snapshotCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    ...shadows.small,
  },
  sectionLeadRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  sectionLeadPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionLeadPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  snapshotEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  snapshotTitle: {
    ...typography.h4,
  },
  snapshotSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: spacing.sm,
  },
  snapshotGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  snapshotMetric: {
    width: '48%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.md,
  },
  snapshotLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  snapshotValue: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  snapshotHint: {
    ...typography.caption,
    color: colors.textLight,
  },
  logCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    ...shadows.small,
  },
  logEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  logTitle: {
    ...typography.h4,
  },
  logSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: spacing.sm,
  },
  inputRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  input: {
    ...typography.body1,
    flex: 1,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    color: colors.text,
  },
  inputPrimary: {
    flex: 1.25,
  },
  logButton: {
    backgroundColor: colors.secondary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.sm + 2,
    alignItems: 'center',
  },
  logButtonDisabled: {
    opacity: 0.6,
  },
  logButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
});
