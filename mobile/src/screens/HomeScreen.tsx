import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { dashboardApi, homeApi, HomeSummary } from '../services/api';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function HomeScreen({ navigation }: any) {
  const { user } = useAuth();
  const { isPremium } = useSubscription();
  const [stats, setStats] = useState<any>(null);
  const [summary, setSummary] = useState<HomeSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoadError(null);
    try {
      const [quickStatsResult, homeSummaryResult] = await Promise.allSettled([
        dashboardApi.getQuickStats(),
        homeApi.getSummary(),
      ]);

      if (quickStatsResult.status === 'fulfilled') {
        setStats(quickStatsResult.value.data);
      } else {
        setStats(null);
      }

      if (homeSummaryResult.status === 'fulfilled') {
        setSummary(homeSummaryResult.value.data);
      } else {
        setSummary(null);
      }

      if (quickStatsResult.status === 'rejected' && homeSummaryResult.status === 'rejected') {
        setLoadError('We could not load your weekly proof right now.');
      } else if (quickStatsResult.status === 'rejected' || homeSummaryResult.status === 'rejected') {
        setLoadError('Some dashboard data is unavailable right now. Showing what we can.');
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
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
  const bodyFatLabel =
    latest != null
      ? `${latest.estimated_ranges.body_fat_percent_min}–${latest.estimated_ranges.body_fat_percent_max}%`
      : summary?.goal_summary.current_bf != null
        ? `${summary.goal_summary.current_bf.toFixed(1)}%`
        : 'Tracking';
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
    summary?.primary_cta.description ??
    'Upload one full-body photo to begin weekly visual tracking.';
  const heroMetaLabel = summary?.scan_summary.next_check_in_label
    ? `Next scan: ${summary.scan_summary.next_check_in_label}`
    : 'This week';

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
      >
        <View style={styles.errorCard}>
          <Text style={styles.errorEyebrow}>Weekly proof unavailable</Text>
          <Text style={styles.errorTitle}>We couldn’t load your dashboard yet.</Text>
          <Text style={styles.errorBody}>
            Pull to retry. Once it loads, you’ll see your latest check-in, progress snapshot, and next action here.
          </Text>
          <View style={styles.errorActions}>
            <TouchableOpacity style={styles.retryButton} onPress={onRefresh}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.secondaryAction} onPress={() => navigation.navigate('BodyScan')}>
              <Text style={styles.secondaryActionText}>Go to check-in</Text>
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
    >
      {loadError && (
        <View style={styles.inlineBanner}>
          <Text style={styles.inlineBannerTitle}>Partial load</Text>
          <Text style={styles.inlineBannerBody}>{loadError}</Text>
        </View>
      )}

      <View style={styles.header}>
        <Text style={styles.greeting}>
          Hello, {user?.full_name || 'there'}!
        </Text>
        {isPremium && (
          <View style={styles.premiumBadge}>
            <Text style={styles.premiumText}>PREMIUM</Text>
          </View>
        )}
      </View>

      <View style={styles.heroCard}>
        <View style={styles.heroMetaRow}>
          <View style={[styles.statusPill, { borderColor: statusTone, backgroundColor: `${statusTone}22` }]}>
            <Text style={[styles.statusPillText, { color: statusTone }]}>{statusLabel}</Text>
          </View>
          <Text style={styles.heroMetaText}>{heroMetaLabel}</Text>
        </View>
        <Text style={styles.heroTitle}>
          {latest?.weekly_status === 'improved'
            ? 'Looking better this week'
            : latest?.weekly_status === 'regressed'
              ? 'Review this week closely'
              : latest?.weekly_status === 'stable'
                ? 'Holding steady this week'
                : 'Ready for your next check-in'}
        </Text>
        <Text style={styles.heroBody}>{summaryLine}</Text>
        <View style={styles.heroActions}>
          <TouchableOpacity
            style={styles.primaryAction}
            onPress={() => navigation.navigate('BodyScan')}
          >
            <Text style={styles.primaryActionText}>
              {latest ? "Upload this week's photo" : 'Start weekly check-in'}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.secondaryAction}
            onPress={() => navigation.navigate('Progress')}
          >
            <Text style={styles.secondaryActionText}>View progress</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.metricsRow}>
        <View style={[styles.metricCard, styles.metricCardLarge]}>
          <Text style={styles.metricLabel}>Goal proximity</Text>
          <Text style={styles.metricValue}>
            {latest ? latest.derived_scores.goal_proximity_score.toFixed(1) : 'Not yet'}
          </Text>
          <Text style={styles.metricSubtext}>
            {latest ? `${Math.round(latest.comparison_confidence * 100)}% confidence` : 'Needs a baseline photo'}
          </Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricLabel}>Body fat range</Text>
          <Text style={styles.metricValue}>{bodyFatLabel}</Text>
          <Text style={styles.metricSubtext}>
            {summary?.goal_summary.target_bf != null
              ? `Target ${summary.goal_summary.target_bf.toFixed(1)}%`
              : 'Target pending'}
          </Text>
        </View>
      </View>

      <View style={styles.secondaryStatsRow}>
        <View style={styles.secondaryStat}>
          <Text style={styles.secondaryStatLabel}>Scans</Text>
          <Text style={styles.secondaryStatValue}>{summary?.scan_summary.scan_count ?? 0}</Text>
        </View>
        <View style={styles.secondaryStat}>
          <Text style={styles.secondaryStatLabel}>Photos</Text>
          <Text style={styles.secondaryStatValue}>{summary?.progress_summary.photo_count ?? 0}</Text>
        </View>
        <View style={styles.secondaryStat}>
          <Text style={styles.secondaryStatLabel}>Calories</Text>
          <Text style={styles.secondaryStatValue}>{stats?.today_calories || 0}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Today's Progress</Text>
        <View style={styles.statsRow}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{stats?.today_calories || 0}</Text>
            <Text style={styles.statLabel}>Calories</Text>
            <Text style={styles.statSubLabel}>
              Goal: {stats?.calorie_goal || 2000}
            </Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{stats?.today_protein || 0}g</Text>
            <Text style={styles.statLabel}>Protein</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{stats?.workouts_this_week || 0}</Text>
            <Text style={styles.statLabel}>Workouts</Text>
            <Text style={styles.statSubLabel}>This week</Text>
          </View>
        </View>
      </View>

      <View style={styles.featuresGrid}>
        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('Progress')}
        >
          <Text style={styles.featureIcon}>📈</Text>
          <Text style={styles.featureTitle}>Progress</Text>
          <Text style={styles.featureDescription}>View your weekly trend</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('BodyScan')}
        >
          <Text style={styles.featureIcon}>✨</Text>
          <Text style={styles.featureTitle}>Weekly check-in</Text>
          <Text style={styles.featureDescription}>Upload a progress photo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('Food')}
        >
          <Text style={styles.featureIcon}>🍽️</Text>
          <Text style={styles.featureTitle}>Food Tracker</Text>
          <Text style={styles.featureDescription}>Log meals & calories</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('Workout')}
        >
          <Text style={styles.featureIcon}>💪</Text>
          <Text style={styles.featureTitle}>Workouts</Text>
          <Text style={styles.featureDescription}>Log & track exercise</Text>
        </TouchableOpacity>
      </View>

      {!isPremium && (
        <TouchableOpacity
          style={styles.upgradeCard}
          onPress={() => navigation.navigate('Paywall')}
        >
          <Text style={styles.upgradeTitle}>⭐ Upgrade to Premium</Text>
          <Text style={styles.upgradeText}>
            Unlimited AI scans, form analysis, and more!
          </Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
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
    alignItems: 'center',
    padding: spacing.lg,
  },
  greeting: {
    ...typography.h2,
    color: colors.text,
  },
  premiumBadge: {
    backgroundColor: colors.premium,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
  },
  premiumText: {
    ...typography.overline,
    color: colors.textOnPrimary,
    fontWeight: '700',
  },
  heroCard: {
    backgroundColor: colors.surface,
    marginHorizontal: spacing.md,
    marginBottom: spacing.md,
    padding: spacing.lg,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.medium,
  },
  inlineBanner: {
    marginHorizontal: spacing.md,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
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
  heroMetaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.md,
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
    ...typography.body2,
    color: colors.textSecondary,
    flexShrink: 1,
  },
  heroTitle: {
    ...typography.h1,
    marginBottom: spacing.sm,
  },
  heroBody: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  primaryAction: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  primaryActionText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  heroActions: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  secondaryAction: {
    flex: 1,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
  },
  secondaryActionText: {
    ...typography.button,
    color: colors.text,
  },
  errorCard: {
    margin: spacing.lg,
    padding: spacing.lg,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.surface,
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
  metricsRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  metricCard: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  metricCardLarge: {
    flex: 1.2,
  },
  metricLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
    textTransform: 'uppercase',
  },
  metricValue: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  metricSubtext: {
    ...typography.caption,
    color: colors.textLight,
  },
  secondaryStatsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  secondaryStat: {
    flex: 1,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  secondaryStatLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  secondaryStatValue: {
    ...typography.h5,
    color: colors.text,
  },
  card: {
    backgroundColor: colors.surface,
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.medium,
  },
  cardTitle: {
    ...typography.h4,
    marginBottom: spacing.md,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    ...typography.number,
    fontSize: 28,
  },
  statLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
  statSubLabel: {
    ...typography.caption,
    color: colors.textLight,
    textAlign: 'center',
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: spacing.sm,
  },
  featureCard: {
    width: '47%',
    backgroundColor: colors.surface,
    margin: spacing.sm,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.small,
  },
  featureIcon: {
    fontSize: 40,
    marginBottom: spacing.sm,
  },
  featureTitle: {
    ...typography.h6,
    textAlign: 'center',
    marginBottom: spacing.xs,
  },
  featureDescription: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  upgradeCard: {
    backgroundColor: colors.primary,
    margin: spacing.lg,
    padding: spacing.xl,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    ...shadows.large,
  },
  upgradeTitle: {
    ...typography.h4,
    color: colors.textOnPrimary,
    marginBottom: spacing.sm,
  },
  upgradeText: {
    ...typography.body1,
    color: colors.textOnPrimary,
    textAlign: 'center',
  },
});
