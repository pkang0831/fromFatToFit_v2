import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import HologramPreview from '../components/HologramPreview';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { dashboardApi, homeApi, HomeSummary } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

type ActionCard = {
  key: string;
  eyebrow: string;
  title: string;
  detail: string;
  meta: string;
  screen: string;
};

type WorkflowRow = {
  key: string;
  step: string;
  label: string;
  value: string;
};

export default function HomeScreen({ navigation }: any) {
  const { user } = useAuth();
  const { isPremium } = useSubscription();
  const tabBarHeight = useBottomTabBarHeight();
  const insets = useSafeAreaInsets();
  const [stats, setStats] = useState<any>(null);
  const [summary, setSummary] = useState<HomeSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    void loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoadError(null);
    try {
      const [quickStatsResult, homeSummaryResult] = await Promise.allSettled([
        dashboardApi.getQuickStats(),
        homeApi.getSummary(),
      ]);

      setStats(quickStatsResult.status === 'fulfilled' ? quickStatsResult.value.data : null);
      setSummary(homeSummaryResult.status === 'fulfilled' ? homeSummaryResult.value.data : null);

      if (quickStatsResult.status === 'rejected' && homeSummaryResult.status === 'rejected') {
        setLoadError('We could not load your weekly proof right now.');
      } else if (quickStatsResult.status === 'rejected' || homeSummaryResult.status === 'rejected') {
        setLoadError('Some dashboard data is unavailable right now. Showing what we can.');
      }
    } catch (error) {
      setLoadError('We could not load your weekly proof right now.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    void loadDashboard();
  };

  const latest = summary?.latest_weekly_checkin ?? null;
  const firstName = user?.full_name?.trim()?.split(' ')[0] || 'there';
  const statusTone =
    latest?.weekly_status === 'improved'
      ? colors.success
      : latest?.weekly_status === 'regressed'
        ? colors.error
        : latest?.weekly_status === 'low_confidence'
          ? colors.warning
          : colors.primary;
  const statusLabel =
    latest == null
      ? 'Awaiting first check-in'
      : latest.is_first_checkin
        ? 'Baseline saved'
        : latest.weekly_status === 'improved'
          ? 'Improved'
          : latest.weekly_status === 'regressed'
            ? 'Needs review'
            : latest.weekly_status === 'low_confidence'
              ? 'Low confidence'
              : 'Stable';
  const summaryLine =
    latest?.qualitative_summary?.[0] ??
    (summary?.goal_summary.has_saved_plan
      ? 'Your target is saved. Add one weekly proof to turn this dashboard into a real read.'
      : 'Save your target and first weekly proof so the rest of the dashboard becomes real.');
  const heroMetaLabel = summary?.scan_summary.next_check_in_label
    ? latest
      ? `${summary.scan_summary.next_check_in_label}`
      : 'First scan'
    : 'This week';
  const bodyFatLabel =
    latest != null
      ? `${latest.estimated_ranges.body_fat_percent_min}–${latest.estimated_ranges.body_fat_percent_max}%`
      : summary?.goal_summary.current_bf != null
        ? `${summary.goal_summary.current_bf.toFixed(1)}%`
        : 'Tracking';
  const bodyHighlights = (latest?.regional_visualization ?? []).slice(0, 2);
  const bodyConfidenceText = latest ? `${Math.round(latest.comparison_confidence * 100)}% read confidence` : 'Baseline pending';
  const bodyStageTitle = latest ? 'Weekly body read.' : 'Body read starts here.';
  const bodyStageSubtitle = latest
    ? 'The same GLB body preview used on web, anchored to this week.'
    : 'Same GLB body preview as web. Save one proof to personalize it.';
  const bodyPrimarySignal =
    latest?.qualitative_summary?.[0] ??
    'One weekly proof beats daily mirror noise.';
  const bodyReadTitle = latest ? statusLabel : 'Baseline pending';
  const bodySecondarySignal =
    bodyHighlights.length > 0
      ? 'Highlights show where change is being picked up first.'
      : latest
        ? 'Next week will sharpen this read.'
        : 'Save one proof to unlock regional notes.';
  const bodyStatusShort = latest ? statusLabel : 'Baseline';
  const heroQuickStats = useMemo(
    () => [
      {
        key: 'proof',
        label: 'Proof',
        value: latest ? bodyStatusShort : 'Start',
      },
      {
        key: 'body-fat',
        label: 'Body fat',
        value: bodyFatLabel,
      },
      {
        key: 'photos',
        label: 'Photos',
        value: `${summary?.progress_summary.photo_count ?? 0}`,
      },
    ],
    [bodyFatLabel, bodyStatusShort, latest, summary?.progress_summary.photo_count],
  );
  const condensedSummaryLine = summaryLine.length > 72 ? `${summaryLine.slice(0, 69).trimEnd()}...` : summaryLine;

  const snapshotCards = useMemo(
    () => [
      {
        key: 'goal',
        label: 'Goal proximity',
        value: latest ? latest.derived_scores.goal_proximity_score.toFixed(1) : 'Not yet',
        detail: latest ? `${Math.round(latest.comparison_confidence * 100)}% confidence` : 'Needs baseline',
      },
      {
        key: 'body-fat',
        label: 'Body fat',
        value: bodyFatLabel,
        detail:
          summary?.goal_summary.target_bf != null
            ? `Target ${summary.goal_summary.target_bf.toFixed(1)}%`
            : 'Target pending',
      },
      {
        key: 'photos',
        label: 'Saved photos',
        value: `${summary?.progress_summary.photo_count ?? 0}`,
        detail: `${summary?.scan_summary.scan_count ?? 0} scans saved`,
      },
      {
        key: 'calories',
        label: 'Calories today',
        value: `${stats?.today_calories ?? 0}`,
        detail: `Goal ${stats?.calorie_goal ?? 2000}`,
      },
    ],
    [bodyFatLabel, latest, stats, summary],
  );

  const actionCards = useMemo<ActionCard[]>(
    () => [
      {
        key: 'check-in',
        eyebrow: 'WEEKLY PROOF',
        title: latest ? "Upload this week's photo" : 'Start weekly check-in',
        detail: latest ? 'Keep your weekly record clean.' : 'Save your first baseline.',
        meta: latest ? statusLabel : 'One clean capture',
        screen: 'BodyScan',
      },
      {
        key: 'progress',
        eyebrow: 'TREND',
        title: 'Open progress',
        detail: 'Review your path and pace.',
        meta: 'Chart + proof',
        screen: 'Progress',
      },
    ],
    [latest, statusLabel],
  );

  const workflowRows = useMemo<WorkflowRow[]>(
    () => [
      {
        key: 'proof',
        step: '01',
        label: latest ? 'Weekly proof status' : 'First weekly proof',
        value: latest ? statusLabel : 'Start now',
      },
      {
        key: 'goal',
        step: '02',
        label: summary?.goal_summary.has_saved_plan ? 'Saved goal' : 'Goal setup',
        value: summary?.goal_summary.has_saved_plan ? 'Ready' : 'Needs target',
      },
      {
        key: 'rhythm',
        step: '03',
        label: 'Daily rhythm',
        value: `${stats?.today_calories ?? 0} kcal · ${stats?.workouts_this_week ?? 0} workouts`,
      },
    ],
    [latest, stats, statusLabel, summary?.goal_summary.has_saved_plan],
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!summary && !stats) {
    return (
      <ScrollView
        style={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
        contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
      >
        <View style={styles.errorCard}>
          <Text style={styles.errorEyebrow}>Weekly proof unavailable</Text>
          <Text style={styles.errorTitle}>We couldn’t load your dashboard yet.</Text>
          <Text style={styles.errorBody}>
            Pull to retry. Once it loads, you’ll see your latest check-in, snapshot, and next action here.
          </Text>
          <View style={styles.errorActions}>
            <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.secondaryButton} onPress={() => navigation.navigate('BodyScan')}>
              <Text style={styles.secondaryButtonText}>Go to check-in</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primary} />}
    >
      {loadError ? (
        <View style={styles.inlineBanner}>
          <Text style={styles.inlineBannerTitle}>Partial load</Text>
          <Text style={styles.inlineBannerBody}>{loadError}</Text>
        </View>
      ) : null}

      <View style={styles.header}>
        <View style={styles.headerCopy}>
          <Text style={styles.headerEyebrow}>DASHBOARD</Text>
          <Text style={styles.greeting}>Hello, {firstName}.</Text>
        </View>
        {isPremium ? (
          <View style={styles.premiumBadge}>
            <Text style={styles.premiumText}>PREMIUM</Text>
          </View>
        ) : null}
      </View>

      <View style={styles.heroCard}>
        <View style={styles.heroMetaRow}>
          <View style={[styles.statusPill, { borderColor: statusTone, backgroundColor: `${statusTone}22` }]}>
            <Text style={[styles.statusPillText, { color: statusTone }]}>{statusLabel}</Text>
          </View>
          <Text style={styles.heroMetaText}>Next: {heroMetaLabel}</Text>
        </View>
        <Text style={styles.heroTitle}>
          {latest?.weekly_status === 'improved'
            ? 'Sharper this week'
            : latest?.weekly_status === 'regressed'
              ? 'Review this week'
              : latest?.weekly_status === 'stable'
                ? 'Steady this week'
                : summary?.goal_summary.has_saved_plan
                  ? 'Start the proof loop'
                  : 'Start weekly proof'}
        </Text>
        <Text numberOfLines={1} style={styles.heroBody}>{condensedSummaryLine}</Text>
        <View style={styles.heroQuickStatsRow}>
          {heroQuickStats.map((item) => (
            <View key={item.key} style={styles.heroQuickStat}>
              <Text numberOfLines={1} style={styles.heroQuickStatInline}>
                <Text style={styles.heroQuickStatLabel}>{item.label}</Text>
                <Text style={styles.heroQuickStatSeparator}> · </Text>
                <Text style={styles.heroQuickStatValue}>{item.value}</Text>
              </Text>
            </View>
          ))}
        </View>
        <View style={styles.heroActions}>
          <TouchableOpacity style={styles.primaryAction} onPress={() => navigation.navigate('BodyScan')}>
            <Text style={styles.primaryActionText}>{latest ? 'Upload photo' : 'Start check-in'}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryAction} onPress={() => navigation.navigate('Progress')}>
            <Text style={styles.secondaryActionText}>Progress</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.bodyViewCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>WEEKLY BODY VIEW</Text>
            <Text style={styles.sectionTitle}>{bodyStageTitle}</Text>
            <Text numberOfLines={2} style={styles.sectionSubtitle}>{bodyStageSubtitle}</Text>
          </View>
          <TouchableOpacity onPress={() => navigation.navigate('Progress')}>
            <Text style={styles.sectionLink}>Open</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.bodyStage}>
          <View style={styles.bodyStageMetaRow}>
            <View style={styles.bodyStageMetaGroup}>
              <View style={styles.bodyStageMetaPill}>
                <Text style={styles.bodyStageMetaPillText}>WEB GLB</Text>
              </View>
              <Text style={styles.bodyStageMetaTitle}>{bodyReadTitle}</Text>
            </View>
            <Text style={styles.bodyStageMetaText}>{bodyConfidenceText}</Text>
          </View>
          <View style={styles.bodyVisualWrap}>
            <HologramPreview style={styles.hologramPreview} />
            <View style={styles.bodyReadOverlay}>
              <Text style={styles.bodyReadOverlayEyebrow}>CURRENT READ</Text>
              <Text style={styles.bodyReadOverlayTitle}>{bodyPrimarySignal}</Text>
              <Text style={styles.bodyReadOverlaySupport}>{bodySecondarySignal}</Text>
            </View>
          </View>
          <View style={styles.bodyLegendCompact}>
            <View style={styles.bodyLegendCopy}>
              <Text style={styles.bodyLegendText}>Pair this view with one weekly photo and the trend line.</Text>
            </View>
            {bodyHighlights.length > 0 ? (
              <View style={styles.bodyInsightRow}>
                {bodyHighlights.map((item) => (
                  <View key={`${item.region}-${item.label}`} style={styles.bodyInsightCard}>
                    <Text style={styles.bodyInsightLabel}>{item.label}</Text>
                    <Text style={styles.bodyInsightValue}>{item.value}</Text>
                    <Text numberOfLines={1} style={styles.bodyInsightNote}>{item.note}</Text>
                  </View>
                ))}
              </View>
            ) : null}
          </View>
        </View>

        <View style={styles.bodyStatsRow}>
          <View style={styles.bodyStatCard}>
            <Text style={styles.bodyStatLabel}>Confidence</Text>
            <Text style={styles.bodyStatValue}>
              {latest ? `${Math.round(latest.comparison_confidence * 100)}%` : '--'}
            </Text>
          </View>
          <View style={styles.bodyStatCard}>
            <Text style={styles.bodyStatLabel}>Photos</Text>
            <Text style={styles.bodyStatValue}>{summary?.progress_summary.photo_count ?? 0}</Text>
          </View>
          <View style={styles.bodyStatCard}>
            <Text style={styles.bodyStatLabel}>Status</Text>
            <Text style={styles.bodyStatValue}>{bodyStatusShort}</Text>
          </View>
        </View>
      </View>

      <View style={styles.snapshotCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>SNAPSHOT</Text>
            <Text style={styles.sectionTitle}>What matters right now.</Text>
            <Text style={styles.sectionSubtitle}>The shortest possible read before you open the deeper views.</Text>
          </View>
        </View>
        <View style={styles.snapshotGrid}>
          {snapshotCards.map((item) => (
            <View key={item.key} style={styles.snapshotMetric}>
              <Text style={styles.snapshotLabel}>{item.label}</Text>
              <Text style={styles.snapshotValue}>{item.value}</Text>
              <Text style={styles.snapshotDetail}>{item.detail}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.todayCard}>
        <Text style={styles.sectionEyebrow}>TODAY</Text>
        <Text style={styles.sectionTitle}>Stay close to the basics.</Text>
        <Text style={styles.sectionSubtitle}>Keep the daily layer clean enough for the weekly read to mean something.</Text>
        <View style={styles.todayGrid}>
          <View style={styles.todayMetric}>
            <Text style={styles.todayValue}>{stats?.today_calories ?? 0}</Text>
            <Text style={styles.todayLabel}>Calories</Text>
          </View>
          <View style={styles.todayMetric}>
            <Text style={styles.todayValue}>{stats?.today_protein ?? 0}g</Text>
            <Text style={styles.todayLabel}>Protein</Text>
          </View>
          <View style={styles.todayMetric}>
            <Text style={styles.todayValue}>{stats?.workouts_this_week ?? 0}</Text>
            <Text style={styles.todayLabel}>Workouts</Text>
          </View>
        </View>
      </View>

      <View style={styles.actionsCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>FLOW</Text>
            <Text style={styles.sectionTitle}>Keep the system tight.</Text>
            <Text style={styles.sectionSubtitle}>Proof first, then trend, then the daily inputs that support both.</Text>
          </View>
        </View>
        <View style={styles.workflowColumn}>
          {workflowRows.map((item) => (
            <View key={item.key} style={styles.workflowRow}>
              <Text style={styles.workflowIndex}>{item.step}</Text>
              <Text style={styles.workflowLabel}>{item.label}</Text>
              <Text style={styles.workflowValue}>{item.value}</Text>
            </View>
          ))}
        </View>
        <View style={styles.actionGrid}>
          {actionCards.map((item) => (
            <TouchableOpacity
              key={item.key}
              style={styles.actionCard}
              onPress={() => navigation.navigate(item.screen)}
            >
              <Text style={styles.actionEyebrow}>{item.eyebrow}</Text>
              <Text style={styles.actionTitle}>{item.title}</Text>
              <Text style={styles.actionDetail}>{item.detail}</Text>
              <Text style={styles.actionMeta}>{item.meta}</Text>
              <Text style={styles.actionLink}>Open</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {!isPremium ? (
        <TouchableOpacity style={styles.upgradeCard} onPress={() => navigation.navigate('Paywall')}>
          <Text style={styles.upgradeEyebrow}>PREMIUM</Text>
          <Text style={styles.upgradeTitle}>Unlock more scans and fewer interruptions.</Text>
          <Text style={styles.upgradeText}>
            Premium keeps your check-ins, form analysis, and extra AI scans in one plan.
          </Text>
        </TouchableOpacity>
      ) : null}
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
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingTop: spacing.xs,
  },
  headerCopy: {
    gap: 2,
  },
  headerEyebrow: {
    ...typography.overline,
    color: colors.textLight,
  },
  greeting: {
    ...typography.h2,
    color: colors.text,
  },
  premiumBadge: {
    backgroundColor: `${colors.premium}22`,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: `${colors.premium}55`,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  premiumText: {
    ...typography.overline,
    color: colors.premium,
    fontWeight: '700',
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
  heroCard: {
    backgroundColor: '#120E0B',
    padding: spacing.xs + 6,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: 'rgba(231, 204, 152, 0.18)',
    ...shadows.medium,
  },
  heroMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: 4,
  },
  statusPill: {
    borderWidth: 1,
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  statusPillText: {
    ...typography.caption,
    fontWeight: '700',
  },
  heroMetaText: {
    ...typography.caption,
    color: colors.textLight,
  },
  heroTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: 4,
    lineHeight: 32,
  },
  heroBody: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 16,
    marginBottom: spacing.xs,
  },
  heroQuickStatsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginBottom: 4,
  },
  heroQuickStat: {
    flex: 1,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.08)',
    backgroundColor: 'rgba(255, 255, 255, 0.025)',
    paddingVertical: 5,
    paddingHorizontal: spacing.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  heroQuickStatInline: {
    ...typography.caption,
    color: colors.text,
  },
  heroQuickStatLabel: {
    ...typography.caption,
    color: colors.textLight,
    textTransform: 'uppercase',
    fontSize: 9,
  },
  heroQuickStatSeparator: {
    ...typography.caption,
    color: colors.textLight,
  },
  heroQuickStatValue: {
    ...typography.buttonSmall,
    color: colors.text,
  },
  heroActions: {
    flexDirection: 'row',
    gap: spacing.xs + 2,
  },
  primaryAction: {
    flex: 1.25,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.xs + 1,
    paddingHorizontal: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryActionText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  secondaryAction: {
    flex: 0.72,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.xs + 1,
    paddingHorizontal: spacing.sm,
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.12)',
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondaryActionText: {
    ...typography.button,
    color: colors.text,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  sectionEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  sectionTitle: {
    ...typography.h5,
    color: colors.text,
  },
  sectionSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
    lineHeight: 16,
  },
  sectionLink: {
    ...typography.buttonSmall,
    color: colors.primary,
    marginTop: 2,
  },
  bodyViewCard: {
    backgroundColor: '#120E0B',
    borderWidth: 1,
    borderColor: 'rgba(231, 204, 152, 0.16)',
    borderRadius: borderRadius.xl,
    padding: spacing.sm,
    ...shadows.small,
  },
  bodyStage: {
    backgroundColor: '#0B0806',
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: 'rgba(231, 204, 152, 0.18)',
    padding: spacing.xs + 4,
    marginBottom: spacing.sm,
    flexDirection: 'column',
    alignItems: 'stretch',
    gap: spacing.xs + 2,
  },
  bodyStageMetaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  bodyStageMetaGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: spacing.sm,
    flex: 1,
  },
  bodyStageMetaPill: {
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    backgroundColor: 'rgba(231, 204, 152, 0.14)',
    borderWidth: 1,
    borderColor: 'rgba(231, 204, 152, 0.28)',
  },
  bodyStageMetaPillText: {
    ...typography.overline,
    color: colors.primaryLight,
  },
  bodyStageMetaTitle: {
    ...typography.button,
    color: colors.text,
  },
  bodyStageMetaText: {
    ...typography.caption,
    color: colors.primaryLight,
    textAlign: 'right',
    maxWidth: '36%',
  },
  bodyVisualWrap: {
    width: '100%',
    height: 192,
    alignItems: 'center',
    justifyContent: 'center',
  },
  hologramPreview: {
    flex: 1,
    width: '100%',
  },
  bodyReadOverlay: {
    position: 'absolute',
    left: spacing.sm,
    right: spacing.sm,
    bottom: spacing.xs,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.12)',
    backgroundColor: 'rgba(7, 6, 5, 0.84)',
    paddingVertical: spacing.xs + 1,
    paddingHorizontal: spacing.xs + 6,
  },
  bodyReadOverlayEyebrow: {
    ...typography.overline,
    color: colors.secondaryLight,
    marginBottom: spacing.xs,
  },
  bodyReadOverlayTitle: {
    ...typography.body2,
    color: colors.text,
    marginBottom: 2,
    fontWeight: '700',
  },
  bodyReadOverlaySupport: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 15,
  },
  bodyLegendCompact: {
    gap: 6,
  },
  bodyLegendCopy: {
    gap: spacing.xs,
  },
  bodyLegendText: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 15,
  },
  bodyInsightRow: {
    flexDirection: 'row',
    flexWrap: 'nowrap',
    gap: spacing.sm,
  },
  bodyInsightCard: {
    flex: 1,
    backgroundColor: 'rgba(9, 7, 5, 0.54)',
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.08)',
    borderRadius: borderRadius.lg,
    padding: spacing.sm - 2,
  },
  bodyInsightLabel: {
    ...typography.caption,
    color: colors.textLight,
    marginBottom: 2,
  },
  bodyInsightValue: {
    ...typography.buttonSmall,
    color: colors.text,
    marginBottom: 2,
  },
  bodyInsightNote: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  bodyStatsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  bodyStatCard: {
    flex: 1,
    backgroundColor: '#1B1511',
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.08)',
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.xs + 4,
    paddingHorizontal: spacing.sm,
  },
  bodyStatLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  bodyStatValue: {
    ...typography.h6,
    color: colors.text,
  },
  snapshotCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.small,
  },
  snapshotGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  snapshotMetric: {
    width: '46.5%',
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  snapshotLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  snapshotValue: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  snapshotDetail: {
    ...typography.caption,
    color: colors.textLight,
  },
  todayCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.small,
  },
  todayGrid: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  todayMetric: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.sm,
    alignItems: 'center',
  },
  todayValue: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  todayLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  actionsCard: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.small,
  },
  actionGrid: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.md,
  },
  actionCard: {
    flex: 1,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    padding: spacing.md,
    minHeight: 148,
  },
  actionEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.sm,
  },
  actionTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  actionDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.sm,
  },
  actionMeta: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  actionLink: {
    ...typography.buttonSmall,
    color: colors.primary,
    marginTop: 'auto',
  },
  workflowColumn: {
    gap: spacing.sm,
  },
  workflowRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: colors.borderLight,
  },
  workflowIndex: {
    ...typography.caption,
    color: colors.textLight,
    width: 28,
    fontWeight: '700',
    letterSpacing: 0.9,
  },
  workflowLabel: {
    ...typography.body2,
    color: colors.text,
    flex: 1,
  },
  workflowValue: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  upgradeCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: `${colors.premium}35`,
    padding: spacing.lg,
    ...shadows.small,
  },
  upgradeEyebrow: {
    ...typography.overline,
    color: colors.premium,
    marginBottom: spacing.sm,
  },
  upgradeTitle: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  upgradeText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
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
  retryButton: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  retryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  secondaryButton: {
    flex: 1,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
  },
});
