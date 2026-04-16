import React, { useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

type UsageKey = 'food_scan' | 'body_fat_scan' | 'percentile_scan' | 'form_check' | 'transformation';

type UsageCard = {
  key: UsageKey;
  label: string;
  detail: string;
  premium: boolean;
};

export default function ProfileScreen({ navigation }: any) {
  const { user, signOut, refreshProfile } = useAuth();
  const { isPremium, usageLimits, loading, error, refreshLimits } = useSubscription();
  const [refreshing, setRefreshing] = useState(false);
  const [signOutLoading, setSignOutLoading] = useState(false);
  const [localMessage, setLocalMessage] = useState<string | null>(null);

  const displayName = user?.full_name?.trim() || 'Your profile';
  const email = user?.email?.trim() || 'No email on file';
  const initials = displayName
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('');

  const usageCards = useMemo<UsageCard[]>(() => {
    const list: Array<{ key: UsageKey; label: string }> = [
      { key: 'food_scan', label: 'Food scans' },
      { key: 'body_fat_scan', label: 'Body scans' },
      { key: 'percentile_scan', label: 'Percentile checks' },
      { key: 'form_check', label: 'Form checks' },
      { key: 'transformation', label: 'Transformation previews' },
    ];

    return list.map((item) => {
      const limit = usageLimits?.[item.key];
      const premium = limit?.is_premium ?? false;
      return {
        ...item,
        premium,
        detail: limit
          ? premium
            ? 'Included in Premium'
            : `${limit.current_count} used · ${limit.remaining} left`
          : loading
            ? 'Loading usage status...'
            : 'Usage details unavailable',
      };
    });
  }, [loading, usageLimits]);

  const planLabel = isPremium ? 'Premium active' : 'Free plan active';
  const planDescription = isPremium
    ? 'This account has active Premium access. Your scans and progress stay in sync across devices.'
    : 'You are on the free plan. Premium unlocks more scans, more previews, and fewer interruptions.';

  const planActionLabel = isPremium ? 'Refresh Premium Access' : 'View Premium';
  const premiumFeatureCount = usageCards.filter((card) => card.premium).length;
  const freeFeatureCount = usageCards.length - premiumFeatureCount;

  const handleRefresh = async () => {
    setRefreshing(true);
    setLocalMessage(null);
    try {
      await Promise.all([refreshProfile(), refreshLimits()]);
    } finally {
      setRefreshing(false);
    }
  };

  const handleOpenPaywall = () => {
    navigation.navigate('Paywall');
  };

  const confirmSignOut = () => {
    Alert.alert(
      'Sign out?',
      'You will return to the sign-in screen. Your data stays synced when you sign in again.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign out',
          style: 'destructive',
          onPress: () => {
            void handleSignOut();
          },
        },
      ],
    );
  };

  const handleSignOut = async () => {
    setSignOutLoading(true);
    setLocalMessage(null);
    try {
      await signOut();
    } catch (error: any) {
      setLocalMessage(error?.message || 'We could not sign you out right now. Please try again.');
    } finally {
      setSignOutLoading(false);
    }
  };

  const actionMessage = localMessage || error;
  const showUsageLoading = loading && !usageLimits;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor={colors.primary} />
      }
    >
      <View style={styles.heroCard}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{initials || 'D'}</Text>
        </View>
        <View style={styles.heroCopy}>
          <View style={styles.heroRow}>
            <Text style={styles.title}>{displayName}</Text>
            <View style={[styles.planPill, isPremium ? styles.planPillPremium : styles.planPillFree]}>
              <Text style={styles.planPillText}>{isPremium ? 'PREMIUM' : 'FREE'}</Text>
            </View>
          </View>
          <Text style={styles.email}>{email}</Text>
          <Text style={styles.subtitle}>
            Manage your plan, usage, and account in one place. Pull to refresh if your entitlement just changed.
          </Text>
          <View style={styles.heroStatsRow}>
            <View style={styles.heroStat}>
              <Text style={styles.heroStatValue}>{isPremium ? 'Premium' : 'Free'}</Text>
              <Text style={styles.heroStatLabel}>Plan</Text>
            </View>
            <View style={styles.heroStat}>
              <Text style={styles.heroStatValue}>{premiumFeatureCount}</Text>
              <Text style={styles.heroStatLabel}>Premium</Text>
            </View>
            <View style={styles.heroStat}>
              <Text style={styles.heroStatValue}>{freeFeatureCount}</Text>
              <Text style={styles.heroStatLabel}>Free</Text>
            </View>
          </View>
        </View>
      </View>

      {actionMessage ? (
        <View style={[styles.banner, error ? styles.bannerError : styles.bannerInfo]}>
          <Text style={styles.bannerTitle}>{error ? 'Plan status needs attention' : 'Account update'}</Text>
          <Text style={styles.bannerText}>{actionMessage}</Text>
          {error && (
            <TouchableOpacity style={styles.bannerAction} onPress={handleRefresh} activeOpacity={0.85}>
              <Text style={styles.bannerActionText}>Retry refresh</Text>
            </TouchableOpacity>
          )}
        </View>
      ) : null}

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Plan status</Text>
        <View style={styles.planCard}>
          <View style={styles.planHeader}>
            <View>
              <Text style={styles.planLabel}>{planLabel}</Text>
              <Text style={styles.planDescription}>{planDescription}</Text>
            </View>
            {showUsageLoading ? (
              <ActivityIndicator color={colors.primary} />
            ) : (
              <View style={[styles.statusDot, isPremium ? styles.statusDotPremium : styles.statusDotFree]} />
            )}
          </View>

          <View style={styles.planActions}>
            <TouchableOpacity
              style={[styles.primaryButton, (refreshing || signOutLoading) && styles.buttonDisabled]}
              onPress={isPremium ? handleRefresh : handleOpenPaywall}
              disabled={refreshing || signOutLoading}
              activeOpacity={0.9}
            >
              {refreshing && isPremium ? (
                <View style={styles.buttonRow}>
                  <ActivityIndicator color={colors.textOnPrimary} />
                  <Text style={styles.primaryButtonText}>Refreshing...</Text>
                </View>
              ) : (
                <Text style={styles.primaryButtonText}>{planActionLabel}</Text>
              )}
            </TouchableOpacity>

            {!isPremium && (
              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={handleOpenPaywall}
                activeOpacity={0.85}
              >
                <Text style={styles.secondaryButtonText}>See Premium benefits</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Usage</Text>
        <View style={styles.usageGrid}>
          {usageCards.map((item) => (
            <View key={item.key} style={styles.usageCard}>
              <View style={[styles.usageBadge, item.premium ? styles.usageBadgePremium : styles.usageBadgeFree]}>
                <Text style={styles.usageBadgeText}>{item.premium ? 'PREMIUM' : 'FREE'}</Text>
              </View>
              <Text style={styles.usageLabel}>{item.label}</Text>
              <Text style={styles.usageDetail}>{item.detail}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.accountCard}>
          <Text style={styles.accountText}>
            Signed in as <Text style={styles.accountTextBold}>{email}</Text>
          </Text>
          <Text style={styles.accountHint}>
            Your profile, scan limits, and progress stay synced across mobile and web.
          </Text>
        </View>
      </View>

      <View style={styles.footerActions}>
        <TouchableOpacity
          style={[styles.logoutButton, signOutLoading && styles.buttonDisabled]}
          onPress={confirmSignOut}
          disabled={signOutLoading}
          activeOpacity={0.85}
        >
          {signOutLoading ? (
            <View style={styles.buttonRow}>
              <ActivityIndicator color={colors.textOnPrimary} />
              <Text style={styles.logoutButtonText}>Signing out...</Text>
            </View>
          ) : (
            <Text style={styles.logoutButtonText}>Sign out</Text>
          )}
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
    padding: spacing.lg,
    paddingBottom: spacing.xl,
    gap: spacing.lg,
  },
  heroCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    flexDirection: 'row',
    gap: spacing.md,
    ...shadows.medium,
  },
  avatar: {
    width: 58,
    height: 58,
    borderRadius: 29,
    backgroundColor: `${colors.primary}22`,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    ...typography.h4,
    color: colors.primary,
  },
  heroCopy: {
    flex: 1,
    gap: spacing.xs,
  },
  heroRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    justifyContent: 'space-between',
  },
  title: {
    ...typography.h3,
    flex: 1,
  },
  planPill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 5,
    borderRadius: borderRadius.round,
  },
  planPillPremium: {
    backgroundColor: `${colors.premium}22`,
  },
  planPillFree: {
    backgroundColor: `${colors.primary}20`,
  },
  planPillText: {
    ...typography.overline,
    color: colors.text,
  },
  email: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  subtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
    marginTop: spacing.xs,
  },
  heroStatsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  heroStat: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border,
  },
  heroStatValue: {
    ...typography.button,
    color: colors.text,
    marginBottom: 2,
    textAlign: 'center',
  },
  heroStatLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  banner: {
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
  },
  bannerError: {
    backgroundColor: `${colors.error}12`,
    borderColor: `${colors.error}40`,
  },
  bannerInfo: {
    backgroundColor: `${colors.primary}12`,
    borderColor: `${colors.primary}35`,
  },
  bannerTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  bannerText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  bannerAction: {
    marginTop: spacing.md,
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  bannerActionText: {
    ...typography.buttonSmall,
    color: colors.text,
  },
  section: {
    gap: spacing.md,
  },
  sectionTitle: {
    ...typography.h5,
  },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.small,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: spacing.md,
  },
  planLabel: {
    ...typography.h4,
    marginBottom: spacing.xs,
  },
  planDescription: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
    maxWidth: 260,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginTop: 6,
  },
  statusDotPremium: {
    backgroundColor: colors.premium,
  },
  statusDotFree: {
    backgroundColor: colors.primary,
  },
  planActions: {
    gap: spacing.md,
    marginTop: spacing.lg,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  primaryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  secondaryButton: {
    backgroundColor: colors.surfaceAlt,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
  },
  usageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md,
  },
  usageCard: {
    width: '48%',
    minWidth: 150,
    flexGrow: 1,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.small,
  },
  usageBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.round,
    marginBottom: spacing.sm,
  },
  usageBadgePremium: {
    backgroundColor: `${colors.premium}22`,
  },
  usageBadgeFree: {
    backgroundColor: `${colors.primary}20`,
  },
  usageBadgeText: {
    ...typography.overline,
    color: colors.text,
  },
  usageLabel: {
    ...typography.h6,
    marginBottom: spacing.xs,
  },
  usageDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  usageEmpty: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    alignItems: 'center',
  },
  usageEmptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
  },
  accountCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    gap: spacing.sm,
  },
  accountText: {
    ...typography.body1,
    color: colors.text,
  },
  accountTextBold: {
    ...typography.button,
    color: colors.text,
  },
  accountHint: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  footerActions: {
    marginTop: spacing.xs,
  },
  logoutButton: {
    backgroundColor: `${colors.error}22`,
    borderWidth: 1,
    borderColor: `${colors.error}40`,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
  },
  logoutButtonText: {
    ...typography.button,
    color: colors.error,
  },
  buttonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
});
