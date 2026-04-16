import React, { useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';
import { useSubscription } from '../contexts/SubscriptionContext';

type FeatureRow = {
  label: string;
  detail: string;
  premium: boolean;
};

export default function PaywallScreen({ navigation }: any) {
  const { isPremium, usageLimits, loading, error, refreshLimits } = useSubscription();
  const [restoring, setRestoring] = useState(false);
  const [restoreMessage, setRestoreMessage] = useState<string | null>(null);

  const featureRows = useMemo<FeatureRow[]>(() => {
    const food = usageLimits?.food_scan;
    const body = usageLimits?.body_fat_scan;
    const form = usageLimits?.form_check;
    const transform = usageLimits?.transformation;

    return [
      {
        label: 'Food scans',
        detail: food
          ? `${food.remaining} / ${food.limit} left on the free plan`
          : 'Free plan usage resets automatically',
        premium: false,
      },
      {
        label: 'Body scans',
        detail: body
          ? `${body.remaining} / ${body.limit} left on the free plan`
          : 'Free plan usage resets automatically',
        premium: false,
      },
      {
        label: 'Workout checks',
        detail: form
          ? `${form.remaining} / ${form.limit} left on the free plan`
          : 'Included as usage grows',
        premium: true,
      },
      {
        label: 'Transformation previews',
        detail: transform
          ? `${transform.remaining} / ${transform.limit} left on the free plan`
          : 'Premium unlocks more creative previews',
        premium: true,
      },
    ];
  }, [usageLimits]);

  const handleRestore = async () => {
    setRestoring(true);
    setRestoreMessage(null);
    try {
      const refreshed = await refreshLimits();
      if (refreshed?.is_premium) {
        setRestoreMessage('Premium access is active on this account.');
      } else {
        setRestoreMessage('No active premium entitlement was found yet. If you just upgraded, try again in a moment.');
      }
    } catch {
      setRestoreMessage('We could not refresh premium status right now. Please try again.');
    } finally {
      setRestoring(false);
    }
  };

  const closePaywall = () => {
    navigation.goBack();
  };

  if (loading && !usageLimits) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading your plan...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>{isPremium ? 'Premium active' : 'Upgrade to Premium'}</Text>
        <Text style={styles.title}>
          {isPremium ? 'You already have the full experience.' : 'Unlock more scans, previews, and guidance.'}
        </Text>
        <Text style={styles.subtitle}>
          {isPremium
            ? 'Your account is already entitled to Premium access. You can refresh access or return to the app.'
            : 'This is where you keep premium access honest, visible, and tied to the account you use across mobile and web.'}
        </Text>
        <View style={styles.heroPills}>
          <View style={styles.heroPill}>
            <Text style={styles.heroPillText}>Account aware</Text>
          </View>
          <View style={styles.heroPill}>
            <Text style={styles.heroPillText}>Usage linked</Text>
          </View>
          <View style={styles.heroPill}>
            <Text style={styles.heroPillText}>Refresh to verify</Text>
          </View>
        </View>
      </View>

      <View style={styles.snapshotCard}>
        <Text style={styles.sectionTitle}>Plan snapshot</Text>
        <View style={styles.snapshotRow}>
          <View style={styles.snapshotItem}>
            <Text style={styles.snapshotValue}>{isPremium ? 'Premium' : 'Free'}</Text>
            <Text style={styles.snapshotLabel}>Plan</Text>
          </View>
          <View style={styles.snapshotItem}>
            <Text style={styles.snapshotValue}>{usageLimits ? 'Synced' : 'Loading'}</Text>
            <Text style={styles.snapshotLabel}>Sync</Text>
          </View>
          <View style={styles.snapshotItem}>
            <Text style={styles.snapshotValue}>{usageLimits ? 'Live' : 'Pending'}</Text>
            <Text style={styles.snapshotLabel}>Usage</Text>
          </View>
        </View>
      </View>

      {(error || restoreMessage) && (
        <View style={[styles.banner, error ? styles.bannerError : styles.bannerInfo]}>
          <Text style={styles.bannerTitle}>{error ? 'Plan status needs attention' : 'Access update'}</Text>
          <Text style={styles.bannerText}>{error || restoreMessage}</Text>
        </View>
      )}

      <View style={styles.featureList}>
        {featureRows.map((feature) => (
          <View key={feature.label} style={styles.featureCard}>
            <View style={[styles.featureBadge, feature.premium ? styles.featureBadgePremium : styles.featureBadgeFree]}>
              <Text style={styles.featureBadgeText}>{feature.premium ? 'PREMIUM' : 'FREE'}</Text>
            </View>
            <Text style={styles.featureTitle}>{feature.label}</Text>
            <Text style={styles.featureDetail}>{feature.detail}</Text>
          </View>
        ))}
      </View>

      <View style={styles.planCard}>
        <Text style={styles.sectionTitle}>What Premium adds</Text>
        <View style={styles.bulletRow}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.bulletText}>More room for high-value scans and previews.</Text>
        </View>
        <View style={styles.bulletRow}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.bulletText}>Less interruption when you are in a weekly routine.</Text>
        </View>
        <View style={styles.bulletRow}>
          <Text style={styles.bullet}>•</Text>
          <Text style={styles.bulletText}>The same account stays in sync across your devices.</Text>
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.primaryButton, (restoring || loading) && styles.buttonDisabled]}
          onPress={handleRestore}
          disabled={restoring || loading}
          activeOpacity={0.9}
        >
          {restoring ? (
            <View style={styles.buttonRow}>
              <ActivityIndicator color={colors.textOnPrimary} />
              <Text style={styles.primaryButtonText}>Refreshing access...</Text>
            </View>
          ) : (
            <Text style={styles.primaryButtonText}>Refresh Premium Access</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={closePaywall}
          activeOpacity={0.85}
        >
          <Text style={styles.secondaryButtonText}>Continue with Free</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.caption}>
        If you already purchased through your app store account, refresh access here and the app will update your entitlements.
      </Text>
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
  hero: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.medium,
  },
  eyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  title: {
    ...typography.h2,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  heroPills: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  heroPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  heroPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  snapshotCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    marginBottom: spacing.lg,
  },
  snapshotRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  snapshotItem: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  snapshotValue: {
    ...typography.button,
    color: colors.text,
    marginBottom: 4,
    textAlign: 'center',
  },
  snapshotLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  banner: {
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
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
    marginBottom: spacing.xs,
    color: colors.text,
  },
  bannerText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  featureList: {
    gap: spacing.md,
    marginBottom: spacing.lg,
  },
  featureCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.small,
  },
  featureBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: borderRadius.round,
    marginBottom: spacing.sm,
  },
  featureBadgePremium: {
    backgroundColor: `${colors.premium}22`,
  },
  featureBadgeFree: {
    backgroundColor: `${colors.primary}18`,
  },
  featureBadgeText: {
    ...typography.overline,
    color: colors.text,
  },
  featureTitle: {
    ...typography.h5,
    marginBottom: spacing.xs,
  },
  featureDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sectionTitle: {
    ...typography.h4,
    marginBottom: spacing.md,
  },
  bulletRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  bullet: {
    ...typography.body1,
    color: colors.primary,
    lineHeight: 20,
  },
  bulletText: {
    ...typography.body1,
    color: colors.textSecondary,
    flex: 1,
    lineHeight: 21,
  },
  actions: {
    gap: spacing.md,
  },
  primaryButton: {
    backgroundColor: colors.premium,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    ...shadows.large,
  },
  primaryButtonText: {
    ...typography.button,
    fontSize: 16,
    color: colors.text,
  },
  secondaryButton: {
    backgroundColor: colors.surface,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  secondaryButtonText: {
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
  caption: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.lg,
    lineHeight: 18,
  },
});
