import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { CreditBalanceResponse, paymentApi } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

type UsageKey = 'food_scan' | 'body_fat_scan' | 'percentile_scan' | 'form_check' | 'transformation';

type UsageCard = {
  key: UsageKey;
  label: string;
  status: string;
  detail: string;
  premium: boolean;
};

type CreditState = CreditBalanceResponse | null;

type ValueCard = {
  label: string;
  value: string;
  detail: string;
};

type SpendCard = {
  key: string;
  label: string;
  detail: string;
  helper: string;
  value: string;
  runsLabel: string;
  isHighest: boolean;
};

export default function ProfileScreen({ navigation }: any) {
  const tabBarHeight = useBottomTabBarHeight();
  const insets = useSafeAreaInsets();
  const { user, signOut, refreshProfile } = useAuth();
  const { isPremium, usageLimits, loading, error, refreshLimits } = useSubscription();
  const [refreshing, setRefreshing] = useState(false);
  const [signOutLoading, setSignOutLoading] = useState(false);
  const [localMessage, setLocalMessage] = useState<string | null>(null);
  const [credits, setCredits] = useState<CreditState>(null);

  useEffect(() => {
    void loadCredits();
  }, [user?.id]);

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
      let status = 'Status pending';
      let detail = 'Usage details unavailable';

      if (limit) {
        if (premium && !isPremium) {
          status = 'Premium only';
          detail = 'Upgrade to open this tool on mobile and web.';
        } else if (isPremium) {
          status = premium ? 'Open on Premium' : 'Included';
          detail = `${limit.current_count} used this cycle${limit.remaining >= 999 ? ' · unlimited room' : ` · ${limit.remaining} left`}`;
        } else {
          status = `${limit.remaining} left`;
          detail = `${limit.current_count} used this cycle on free.`;
        }
      } else if (loading) {
        status = 'Loading';
        detail = 'Checking plan and usage status...';
      }

      return {
        ...item,
        premium,
        status,
        detail,
      };
    });
  }, [isPremium, loading, usageLimits]);

  const planLabel = isPremium ? 'Premium active' : 'Free plan active';
  const planDescription = isPremium
    ? 'Premium keeps weekly proof open and heavier tools usable across mobile and web.'
    : 'Free keeps the starter loop open. Premium removes proof caps and opens heavier tools.';
  const premiumFeatureCount = usageCards.filter((card) => card.premium).length;
  const actionMessage = localMessage || error;
  const showUsageLoading = loading && !usageLimits;
  const resetLabel = useMemo(() => {
    if (!credits?.reset_date) {
      return null;
    }

    const parsedDate = new Date(credits.reset_date);
    if (Number.isNaN(parsedDate.getTime())) {
      return null;
    }

    return parsedDate.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    });
  }, [credits?.reset_date]);

  const premiumValueCards = useMemo<ValueCard[]>(
    () => [
      {
        label: 'Weekly proof',
        value: isPremium ? 'Open' : 'Limited',
        detail: isPremium
          ? 'Weekly check-ins and progress review stay open.'
          : 'Premium keeps the proof loop open.',
      },
      {
        label: 'Premium tools',
        value: isPremium ? `${premiumFeatureCount} open now` : 'Locked on free',
        detail: isPremium
          ? 'Transforms and deeper reads are already open on this account.'
          : 'Premium opens higher-value scans and heavier tools.',
      },
      {
        label: 'Wallet rules',
        value: 'Plan + credits',
        detail: 'Credits are only for heavier tools.',
      },
    ],
    [isPremium, premiumFeatureCount],
  );

  const toolEconomyCards = useMemo<SpendCard[]>(() => {
    const toolMeta = [
      { key: 'transformation', label: 'Transform', detail: 'future preview', helper: 'Heaviest spend' },
      { key: 'form_check', label: 'Form check', detail: 'movement review', helper: 'Good mid-cost read' },
      { key: 'percentile_scan', label: 'Percentile', detail: 'position read', helper: 'Lightest quick look' },
    ];

    const maxCost = Math.max(...toolMeta.map((item) => credits?.credit_costs?.[item.key] ?? 0), 0);

    return toolMeta.map((item) => {
      const cost = credits?.credit_costs?.[item.key];
      const runs =
        credits?.total_credits != null && cost != null && cost > 0
          ? Math.floor(credits.total_credits / cost)
          : null;

      return {
        ...item,
        value: cost != null ? `${cost} credits` : '—',
        runsLabel:
          runs == null
            ? 'Coverage pending'
            : runs > 0
              ? `${runs} runs at current balance`
              : 'Needs more credits',
        isHighest: cost != null && cost === maxCost && cost > 0,
      };
    });
  }, [credits]);

  const walletCoverage = useMemo(() => {
    const totalCredits = credits?.total_credits;
    const transformCost = credits?.credit_costs?.transformation;
    const formCheckCost = credits?.credit_costs?.form_check;

    if (!totalCredits || !transformCost || !formCheckCost) {
      return null;
    }

    const transformRuns = Math.floor(totalCredits / transformCost);
    const formChecks = Math.floor(totalCredits / formCheckCost);

    return `Today’s balance covers about ${transformRuns} transform previews or ${formChecks} form checks.`;
  }, [credits]);
  const economySignal = useMemo(() => {
    if (isPremium) {
      return 'Premium keeps the plan and wallet moving together, so weekly proof stays open while heavier tools stay usable.';
    }

    return 'Free gives you starter room. Premium turns weekly proof, premium tools, and the wallet into one system instead of separate ceilings.';
  }, [isPremium]);

  const walletSummaryCards = useMemo<ValueCard[]>(
    () => [
      {
        label: 'Ready now',
        value: credits?.total_credits != null ? `${credits.total_credits} credits` : 'Syncing',
        detail: walletCoverage || 'Use this balance for the heavier AI tools when you want deeper reads.',
      },
      {
        label: 'Monthly reset',
        value: resetLabel ?? 'Monthly',
        detail: resetLabel
          ? `Monthly credits refresh around ${resetLabel}.`
          : 'Monthly credits refill on your next billing cycle.',
      },
      {
        label: 'Bonus credits',
        value: credits?.bonus_credits != null ? `${credits.bonus_credits}` : '—',
        detail: 'Bonus credits stay in reserve until you spend them.',
      },
    ],
    [credits?.bonus_credits, credits?.total_credits, resetLabel, walletCoverage],
  );

  const costCards = toolEconomyCards;

  const loadCredits = async () => {
    if (!user) {
      setCredits(null);
      return;
    }

    try {
      const { data } = await paymentApi.getCredits();
      setCredits(data);
    } catch (creditError) {
      setCredits(null);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setLocalMessage(null);
    try {
      await Promise.all([refreshProfile(), refreshLimits(), loadCredits()]);
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
    } catch (err: any) {
      setLocalMessage(err?.message || 'We could not sign you out right now. Please try again.');
    } finally {
      setSignOutLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor={colors.primary} />}
    >
      <View style={styles.heroCard}>
        <Text style={styles.heroEyebrow}>PROFILE</Text>
        <View style={styles.heroRow}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>{initials || 'D'}</Text>
          </View>
          <View style={styles.heroCopy}>
            <View style={styles.titleRow}>
              <Text style={styles.title}>{displayName}</Text>
              <View style={[styles.planPill, isPremium ? styles.planPillPremium : styles.planPillFree]}>
                <Text style={styles.planPillText}>{isPremium ? 'PREMIUM' : 'FREE'}</Text>
              </View>
            </View>
            <Text style={styles.email}>{email}</Text>
            <Text style={styles.subtitle}>
              Plan, wallet, and tool access.
            </Text>
          </View>
        </View>

        <View style={styles.snapshotGrid}>
          <View style={styles.snapshotMetric}>
            <Text style={styles.snapshotLabel}>Plan</Text>
            <Text style={styles.snapshotValue}>{isPremium ? 'Premium' : 'Free'}</Text>
          </View>
          <View style={styles.snapshotMetric}>
            <Text style={styles.snapshotLabel}>Premium access</Text>
            <Text style={styles.snapshotValue}>{isPremium ? 'Active' : 'Not active'}</Text>
          </View>
          <View style={styles.snapshotMetric}>
            <Text style={styles.snapshotLabel}>Wallet</Text>
            <Text style={styles.snapshotValue}>{credits?.total_credits != null ? `${credits.total_credits} credits` : 'Loading wallet'}</Text>
          </View>
        </View>
      </View>

      {actionMessage ? (
        <View style={[styles.banner, error ? styles.bannerError : styles.bannerInfo]}>
          <Text style={styles.bannerTitle}>{error ? 'Plan status needs attention' : 'Account update'}</Text>
          <Text style={styles.bannerText}>{actionMessage}</Text>
          {error ? (
            <TouchableOpacity style={styles.bannerAction} onPress={handleRefresh} activeOpacity={0.85}>
              <Text style={styles.bannerActionText}>Retry refresh</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      ) : null}

      <View style={styles.accessCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>ACCESS</Text>
            <Text style={styles.sectionTitle}>{planLabel}</Text>
          </View>
          {showUsageLoading ? (
            <ActivityIndicator color={colors.primary} />
          ) : (
            <View style={[styles.statusDot, isPremium ? styles.statusDotPremium : styles.statusDotFree]} />
          )}
        </View>

        <Text style={styles.accessDescription}>{planDescription}</Text>

        <View style={styles.valueGrid}>
          {premiumValueCards.map((item) => (
            <View
              key={item.label}
              style={[styles.valueCard, item.label === 'Wallet rules' && styles.valueCardWide]}
            >
              <Text style={styles.valueLabel}>{item.label}</Text>
              <Text style={styles.valueValue}>{item.value}</Text>
              <Text style={styles.valueDetail}>{item.detail}</Text>
            </View>
          ))}
        </View>

        <View style={styles.accessNoteCard}>
          <Text style={styles.accessNoteEyebrow}>HOW IT WORKS</Text>
          <Text style={styles.accessNoteText}>
            Weekly proof follows your plan. Credits only cover heavier AI tools.
          </Text>
        </View>

        <View style={styles.accessActions}>
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
              <Text style={styles.primaryButtonText}>{isPremium ? 'Refresh Premium Access' : 'View Premium'}</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={styles.secondaryButton} onPress={handleOpenPaywall} activeOpacity={0.85}>
            <Text style={styles.secondaryButtonText}>{isPremium ? 'Manage billing' : 'See Premium benefits'}</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.creditsCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>CREDITS</Text>
        <Text style={styles.sectionTitle}>Credit wallet</Text>
          </View>
          <View style={styles.creditStatusPill}>
            <Text style={styles.creditStatusPillText}>{isPremium ? 'Premium wallet' : 'Free wallet'}</Text>
          </View>
        </View>

        <Text style={styles.creditsDescription}>
          Credits are your wallet for transforms and deeper reads, not for the core weekly proof loop.
        </Text>

        <View style={styles.walletBanner}>
          <Text style={styles.walletBannerTitle}>
            {credits?.total_credits != null ? `${credits.total_credits} credits ready now` : 'Wallet syncing now'}
          </Text>
          <Text style={styles.walletBannerText}>
            {walletCoverage ||
              (resetLabel
                ? `Monthly credits refresh around ${resetLabel}. Bonus credits stay available until you spend them.`
                : 'Monthly credits refill on your next cycle. Bonus credits stay available until you spend them.')}
          </Text>
        </View>
        <View style={styles.economySignalCard}>
          <Text style={styles.economySignalEyebrow}>VALUE SIGNAL</Text>
          <Text style={styles.economySignalText}>{economySignal}</Text>
        </View>

        <View style={styles.walletGrid}>
          {walletSummaryCards.map((item) => (
            <View
              key={item.label}
              style={[styles.walletCard, item.label === 'Ready now' && styles.walletCardWide]}
            >
              <Text style={styles.walletCardLabel}>{item.label}</Text>
              <Text style={styles.walletCardValue}>{item.value}</Text>
              <Text style={styles.walletCardDetail}>{item.detail}</Text>
            </View>
          ))}
        </View>

        <View style={styles.toolEconomyHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>TOOL COSTS</Text>
            <Text style={styles.toolEconomyTitle}>What spends credits</Text>
          </View>
            <Text style={styles.toolEconomyHint}>Heavier tools spend faster.</Text>
          </View>

        <View style={styles.costGrid}>
          {costCards.map((item) => (
            <View key={item.key} style={styles.costCard}>
              {item.isHighest ? (
                <View style={styles.costBadge}>
                  <Text style={styles.costBadgeText}>HEAVIEST</Text>
                </View>
              ) : null}
              <Text style={styles.costLabel}>{item.label}</Text>
              <Text style={styles.costValue}>{item.value}</Text>
              <Text style={styles.costDetail}>{item.detail}</Text>
              <Text style={styles.costHelper}>{item.helper}</Text>
              <Text style={styles.costCoverage}>{item.runsLabel}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.usageSection}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>USAGE</Text>
            <Text style={styles.sectionTitle}>What your plan covers now.</Text>
          </View>
        </View>
        <View style={styles.usageGrid}>
          {usageCards.map((item) => (
            <View key={item.key} style={styles.usageCard}>
              <View style={[styles.usageBadge, item.premium ? styles.usageBadgePremium : styles.usageBadgeFree]}>
                <Text style={styles.usageBadgeText}>{item.premium ? 'PREMIUM' : 'FREE'}</Text>
              </View>
              <Text style={styles.usageLabel}>{item.label}</Text>
              <Text style={styles.usageStatus}>{item.status}</Text>
              <Text style={styles.usageDetail}>{item.detail}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.accountCard}>
        <Text style={styles.sectionEyebrow}>ACCOUNT</Text>
        <Text style={styles.accountTitle}>Primary account</Text>
        <Text style={styles.accountText}>
          Signed in as <Text style={styles.accountTextBold}>{email}</Text>
        </Text>
        <Text style={styles.accountHint}>
          Your profile, scan limits, and progress stay synced across mobile and web.
        </Text>
      </View>

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
    gap: spacing.sm + 2,
  },
  heroCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.md + 2,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.medium,
  },
  heroEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.sm,
  },
  heroRow: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.sm,
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
  titleRow: {
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
    lineHeight: 19,
    marginTop: 2,
  },
  snapshotGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.sm,
  },
  snapshotMetric: {
    width: '31.5%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.xs,
    alignItems: 'center',
  },
  snapshotLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: 4,
    textAlign: 'center',
  },
  snapshotValue: {
    ...typography.button,
    color: colors.text,
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
  accessCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.small,
  },
  creditsCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.small,
  },
  usageSection: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.small,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: spacing.md,
    marginBottom: 4,
  },
  sectionEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.text,
  },
  accessDescription: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: 4,
  },
  valueGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginTop: spacing.sm,
  },
  valueCard: {
    width: '48%',
    minWidth: 148,
    flexGrow: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
  },
  valueCardWide: {
    width: '100%',
  },
  valueLabel: {
    ...typography.caption,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  valueValue: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  valueDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  accessNoteCard: {
    marginTop: spacing.xs,
    backgroundColor: `${colors.primary}10`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.primary}24`,
    padding: spacing.sm,
  },
  accessNoteEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  accessNoteText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  creditsDescription: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
    marginBottom: 4,
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
  creditStatusPill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  creditStatusPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  walletBanner: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
    marginBottom: 4,
  },
  walletBannerTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  walletBannerText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  economySignalCard: {
    backgroundColor: `${colors.primary}10`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.primary}28`,
    padding: spacing.sm,
    marginBottom: 4,
  },
  economySignalEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  economySignalText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  walletGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    marginBottom: 4,
  },
  walletCard: {
    width: '48%',
    minWidth: 148,
    flexGrow: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
  },
  walletCardWide: {
    width: '100%',
  },
  walletCardLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  walletCardValue: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  walletCardDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  toolEconomyHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: spacing.md,
    marginBottom: spacing.xs,
  },
  toolEconomyTitle: {
    ...typography.h5,
    color: colors.text,
  },
  toolEconomyHint: {
    ...typography.caption,
    color: colors.textLight,
    textAlign: 'right',
    maxWidth: 96,
  },
  costGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  costCard: {
    width: '48%',
    minWidth: 148,
    flexGrow: 1,
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
  },
  costBadge: {
    alignSelf: 'flex-start',
    marginBottom: spacing.xs,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.round,
    backgroundColor: `${colors.premium}22`,
  },
  costBadgeText: {
    ...typography.overline,
    color: colors.text,
  },
  costLabel: {
    ...typography.caption,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  costValue: {
    ...typography.button,
    color: colors.text,
    marginBottom: 2,
  },
  costDetail: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  costHelper: {
    ...typography.caption,
    color: colors.textLight,
    marginTop: spacing.xs,
  },
  costCoverage: {
    ...typography.caption,
    color: colors.primary,
    marginTop: 6,
    fontWeight: '700',
  },
  accessActions: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    flex: 1,
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
    flex: 1,
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
  },
  usageGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  usageCard: {
    width: '47%',
    minWidth: 148,
    flexGrow: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    padding: spacing.sm + 2,
    borderWidth: 1,
    borderColor: colors.border,
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
    marginBottom: 4,
  },
  usageStatus: {
    ...typography.buttonSmall,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  usageDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  accountCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.md + 2,
    borderWidth: 1,
    borderColor: colors.borderLight,
    ...shadows.small,
  },
  accountTitle: {
    ...typography.h4,
    marginBottom: spacing.sm,
  },
  accountText: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  accountTextBold: {
    color: colors.text,
    fontWeight: '700',
  },
  accountHint: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  logoutButton: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  logoutButtonText: {
    ...typography.button,
    color: colors.text,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
});
