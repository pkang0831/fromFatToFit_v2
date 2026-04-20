import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import * as WebBrowser from 'expo-web-browser';
import * as Linking from 'expo-linking';
import { useSubscription } from '../contexts/SubscriptionContext';
import { paymentApi } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

type FeatureRow = {
  label: string;
  detail: string;
  premium: boolean;
};

type PathStep = {
  key: string;
  number: string;
  title: string;
  detail: string;
};

type OfferCard = {
  key: string;
  eyebrow: string;
  title: string;
  detail: string;
  highlights: string[];
  recommended: boolean;
  fit: string;
  emphasis: string;
  decisionLine: string;
};

type PressureCard = {
  key: string;
  label: string;
  remaining: string;
  tone: 'warning' | 'neutral';
};

export default function PaywallScreen({ navigation }: any) {
  const { isPremium, usageLimits, loading, error, refreshLimits } = useSubscription();
  const [restoring, setRestoring] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [billingLoading, setBillingLoading] = useState(false);
  const [restoreMessage, setRestoreMessage] = useState<string | null>(null);
  const [billingPortalAvailable, setBillingPortalAvailable] = useState(false);
  const premiumPriceId = process.env.EXPO_PUBLIC_STRIPE_PREMIUM_PRICE_ID || '';
  const appReturnUrl = Linking.createURL('paywall');

  const featureRows = useMemo<FeatureRow[]>(() => {
    const food = usageLimits?.food_scan;
    const body = usageLimits?.body_fat_scan;
    const form = usageLimits?.form_check;
    const transform = usageLimits?.transformation;

    return [
      {
        label: 'Food scans',
        detail: food ? `${food.remaining} / ${food.limit} left on free` : 'Track meals with less interruption',
        premium: false,
      },
      {
        label: 'Weekly check-ins',
        detail: body ? `${body.remaining} / ${body.limit} left on free` : 'Keep weekly proof open',
        premium: true,
      },
      {
        label: 'Workout checks',
        detail: form ? `${form.remaining} / ${form.limit} left on free` : 'Keep training feedback available',
        premium: true,
      },
      {
        label: 'Transformation previews',
        detail: transform ? `${transform.remaining} / ${transform.limit} left on free` : 'Unlock a wider preview range',
        premium: true,
      },
    ];
  }, [usageLimits]);

  const pathSteps = useMemo<PathStep[]>(
    () => [
      {
        key: 'proof',
        number: '01',
        title: 'Keep proof open',
        detail: 'Weekly check-ins stay available when your rhythm finally starts working.',
      },
      {
        key: 'sync',
        number: '02',
        title: 'Stay in sync',
        detail: 'The same account state follows you across mobile and web.',
      },
      {
        key: 'refresh',
        number: '03',
        title: 'Refresh safely',
        detail: 'If access changes, re-check it here without guessing what is active.',
      },
    ],
    [],
  );
  const trustPills = ['Web + mobile sync', 'Safe refresh path', 'Premium tied to account'];
  const offerCards = useMemo<OfferCard[]>(
    () => [
      {
        key: 'premium',
        eyebrow: 'BEST FIT',
        title: 'Premium',
        detail: 'Best when you already want the full weekly proof loop to keep running.',
        highlights: [
          'Keeps weekly proof open when free limits tighten',
          'Syncs cleanly across mobile and web',
        ],
        recommended: true,
        fit: 'Best if weekly proof is already shaping your routine.',
        emphasis: 'Protect momentum',
        decisionLine: 'Live price appears in secure checkout before you confirm.',
      },
      {
        key: 'free',
        eyebrow: 'STARTER',
        title: 'Free',
        detail: 'Good for first scans and a lightweight weekly rhythm.',
        highlights: [
          featureRows.find((row) => row.label === 'Food scans')?.detail ?? 'Basic usage',
          featureRows.find((row) => row.label === 'Weekly check-ins')?.detail ?? 'Weekly proof capped',
        ],
        recommended: false,
        fit: 'Best if you are still testing the baseline.',
        emphasis: 'Limited proof loop',
        decisionLine: 'Stay here if you are still evaluating the first layer of the product.',
      },
    ],
    [featureRows],
  );
  const pressureLine = bodyPressureLine(usageLimits);
  const valueBullets = useMemo(
    () => [
      {
        key: 'proof',
        title: 'Keep the proof loop open',
        detail: 'Stay in weekly check-ins and progress reads instead of waiting for free limits to reset.',
      },
      {
        key: 'transform',
        title: 'Use the premium tools that change decisions',
        detail: 'Transformation previews and workout checks stay available when you are actively iterating.',
      },
      {
        key: 'sync',
        title: 'Keep one account across web and mobile',
        detail: 'Premium access follows the same account state, so your workflow does not split by device.',
      },
    ],
    [],
  );
  const pressureCards = useMemo<PressureCard[]>(
    () => [
      {
        key: 'body',
        label: 'Weekly proof',
        remaining:
          usageLimits?.body_fat_scan != null
            ? `${usageLimits.body_fat_scan.remaining} left`
            : 'check status',
        tone: (usageLimits?.body_fat_scan?.remaining ?? 0) <= 1 ? 'warning' : 'neutral',
      },
      {
        key: 'form',
        label: 'Form checks',
        remaining:
          usageLimits?.form_check != null
            ? `${usageLimits.form_check.remaining} left`
            : 'check status',
        tone: (usageLimits?.form_check?.remaining ?? 0) <= 1 ? 'warning' : 'neutral',
      },
      {
        key: 'transform',
        label: 'Transform',
        remaining:
          usageLimits?.transformation != null
            ? `${usageLimits.transformation.remaining} left`
            : 'check status',
        tone: (usageLimits?.transformation?.remaining ?? 0) <= 1 ? 'warning' : 'neutral',
      },
    ],
    [usageLimits],
  );
  const heroHighlights = useMemo(
    () => (
      isPremium
        ? ['Weekly proof open', 'Mobile + web synced', 'Billing tools attached']
        : ['Weekly proof stays open', 'Live price before confirm', 'Mobile + web synced']
    ),
    [isPremium],
  );
  const comparisonCards = useMemo(
    () => [
      {
        key: 'free',
        eyebrow: 'FREE',
        title: 'Good for testing',
        detail: pressureLine,
      },
      {
        key: 'premium',
        eyebrow: 'PREMIUM',
        title: isPremium ? 'Already unlocked here' : 'Recommended once proof matters',
        detail: isPremium
          ? 'Your strongest plan is already active on this account.'
          : 'Premium is the plan once weekly proof is shaping real decisions.',
      },
    ],
    [isPremium, pressureLine],
  );
  const primaryActionTitle = isPremium
    ? billingPortalAvailable
      ? 'Manage premium plan'
      : 'Refresh premium access'
    : 'Open secure checkout';
  const primaryActionHint = isPremium
    ? billingPortalAvailable
      ? 'Billing + account controls'
      : 'Re-check this account'
    : 'See live price before you confirm';
  const secondaryActionTitle = isPremium ? 'Continue in app' : 'Already upgraded on web?';
  const secondaryActionHint = isPremium ? 'Close this and keep moving' : 'Refresh premium on this account';

  useEffect(() => {
    void loadSubscriptionState();
  }, []);

  const loadSubscriptionState = async () => {
    try {
      const { data } = await paymentApi.getSubscriptionStatus();
      setBillingPortalAvailable(Boolean(data?.billing_portal_available));
    } catch (subscriptionError) {
      setBillingPortalAvailable(false);
    }
  };

  const handleRestore = async () => {
    setRestoring(true);
    setRestoreMessage(null);
    try {
      const refreshed = await refreshLimits();
      if (refreshed?.is_premium) {
        setRestoreMessage('Premium access is active on this account.');
      } else {
        setRestoreMessage(
          'No active premium entitlement was found yet. If you just upgraded, try again in a moment.',
        );
      }
    } catch {
      setRestoreMessage('We could not refresh premium status right now. Please try again.');
    } finally {
      setRestoring(false);
    }
  };

  const handleUpgrade = async () => {
    if (!premiumPriceId) {
      setRestoreMessage('Premium checkout is not configured in this build yet.');
      return;
    }

    setCheckoutLoading(true);
    setRestoreMessage(null);
    try {
      const { data } = await paymentApi.createCheckoutSession(
        premiumPriceId,
        appReturnUrl,
        appReturnUrl,
      );
      await WebBrowser.openBrowserAsync(data.checkout_url);
      setRestoreMessage(
        'Checkout opened in your browser. Once it closes, you should land back in the app here.',
      );
    } catch (checkoutError) {
      setRestoreMessage('We could not open premium checkout right now. Please try again.');
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleManageBilling = async () => {
    setBillingLoading(true);
    setRestoreMessage(null);
    try {
      const { data } = await paymentApi.createBillingPortalSession(appReturnUrl);
      await WebBrowser.openBrowserAsync(data.url);
      setRestoreMessage('Billing portal opened in your browser.');
    } catch (billingError) {
      setRestoreMessage('We could not open billing management right now. Please try again.');
    } finally {
      setBillingLoading(false);
    }
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
      <View style={styles.heroCard}>
        <View style={styles.heroHeader}>
          <View style={styles.heroCopy}>
            <Text style={styles.eyebrow}>{isPremium ? 'PREMIUM ACTIVE' : 'PREMIUM ACCESS'}</Text>
            <Text style={styles.heroTitle}>
              {isPremium ? 'Your full toolkit is already on.' : 'Keep the weekly proof loop open.'}
            </Text>
            <Text style={styles.heroBody}>
              {isPremium
                ? 'This account already has premium access. Refresh or manage billing here whenever you want to confirm the live state.'
                : 'Premium removes the caps that interrupt weekly proof, scans, and the heavier tools.'}
            </Text>
          </View>

          <View style={[styles.statusPill, isPremium && styles.statusPillActive]}>
            <Text style={[styles.statusPillText, isPremium && styles.statusPillTextActive]}>
              {isPremium ? 'Active' : 'Free plan'}
            </Text>
          </View>
        </View>

        <View style={styles.heroRecommendationCard}>
          <View style={styles.heroRecommendationHeader}>
            <Text style={styles.heroRecommendationEyebrow}>
              {isPremium ? 'CURRENT PLAN' : 'RECOMMENDED'}
            </Text>
            {!isPremium ? (
              <View style={styles.heroRecommendationBadge}>
                <Text style={styles.heroRecommendationBadgeText}>BEST FIT</Text>
              </View>
            ) : null}
          </View>
          <Text style={styles.heroRecommendationLead}>
            {isPremium
              ? 'Premium is already active on this account.'
              : 'Premium fits once weekly proof shapes real decisions.'}
          </Text>
          <Text style={styles.heroRecommendationBody}>
            {isPremium
              ? 'Billing tools and refresh keep mobile and web aligned on the same account.'
              : 'Secure checkout shows the live price first, then this account stays aligned on mobile and web.'}
          </Text>
          <View style={styles.heroHighlightList}>
            {heroHighlights.map((item) => (
              <View key={item} style={styles.heroHighlightPill}>
                <Text style={styles.heroHighlightText}>{item}</Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.actionRow}>
          <TouchableOpacity
            style={[
              styles.primaryButton,
              (restoring || checkoutLoading || billingLoading || loading) && styles.buttonDisabled,
            ]}
            onPress={() =>
              void (isPremium ? (billingPortalAvailable ? handleManageBilling() : handleRestore()) : handleUpgrade())
            }
            disabled={restoring || checkoutLoading || billingLoading || loading}
          >
            {checkoutLoading || billingLoading ? (
              <View style={styles.inlineLoader}>
                <ActivityIndicator color={colors.textOnPrimary} />
                <Text style={styles.primaryButtonText}>
                  {isPremium ? 'Opening billing...' : 'Opening checkout...'}
                </Text>
              </View>
            ) : restoring ? (
              <View style={styles.inlineLoader}>
                <ActivityIndicator color={colors.textOnPrimary} />
                <Text style={styles.primaryButtonText}>Refreshing access...</Text>
              </View>
            ) : (
              <>
                <Text style={styles.primaryButtonText}>{primaryActionTitle}</Text>
                <Text style={styles.primaryButtonHint}>{primaryActionHint}</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => void (isPremium ? navigation.goBack() : handleRestore())}
            disabled={restoring || checkoutLoading || billingLoading || loading}
          >
            <Text style={styles.secondaryButtonText}>{secondaryActionTitle}</Text>
            <Text style={styles.secondaryButtonHint}>{secondaryActionHint}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.pressureStrip}>
          <Text style={styles.pressureStripEyebrow}>{isPremium ? 'ACCOUNT STATE' : 'FREE LIMITS'}</Text>
          <View style={styles.pressureGrid}>
            {pressureCards.map((card) => (
              <View
                key={card.key}
                style={[
                  styles.pressureCard,
                  card.tone === 'warning' && styles.pressureCardWarning,
                ]}
              >
                <Text style={styles.pressureLabel}>{card.label}</Text>
                <Text
                  style={[
                    styles.pressureValue,
                    card.tone === 'warning' && styles.pressureValueWarning,
                  ]}
                >
                  {isPremium ? 'Open' : card.remaining}
                </Text>
              </View>
            ))}
          </View>
        </View>

        <View style={styles.metricGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Plan</Text>
            <Text style={styles.metricValue}>{isPremium ? 'Premium' : 'Free'}</Text>
            <Text style={styles.metricHint}>current state</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Proof</Text>
            <Text style={styles.metricValue}>{isPremium ? 'Open' : 'Capped'}</Text>
            <Text style={styles.metricHint}>weekly proof</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Sync</Text>
            <Text style={styles.metricValue}>{usageLimits ? 'Ready' : 'Pending'}</Text>
            <Text style={styles.metricHint}>mobile + web</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Price</Text>
            <Text style={styles.metricValueSmall}>{isPremium ? 'Included' : 'Live in checkout'}</Text>
            <Text style={styles.metricHint}>{isPremium ? 'current plan' : 'shown before confirm'}</Text>
          </View>
        </View>

        <View style={styles.trustPillRow}>
          {trustPills.map((pill) => (
            <View key={pill} style={styles.trustPill}>
              <Text style={styles.trustPillText}>{pill}</Text>
            </View>
          ))}
        </View>
      </View>

      {(error || restoreMessage) && (
        <View style={[styles.banner, error ? styles.bannerError : styles.bannerInfo]}>
          <Text style={styles.bannerTitle}>{error ? 'Plan status needs attention' : 'Access update'}</Text>
          <Text style={styles.bannerText}>{error || restoreMessage}</Text>
        </View>
      )}

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>PLAN VIEW</Text>
        <Text style={styles.sectionTitle}>Choose the plan that matches your pace.</Text>
        <Text style={styles.sectionBody}>
          Free is enough for a baseline. Premium is for the point where weekly proof is already shaping the next move.
        </Text>

        <View style={styles.offerGrid}>
          {offerCards.map((offer) => (
            <View
              key={offer.key}
              style={[styles.offerCard, offer.recommended && styles.offerCardRecommended]}
            >
              <View style={styles.offerHeader}>
                <View style={styles.offerTitleWrap}>
                  <Text style={styles.offerEyebrow}>{offer.eyebrow}</Text>
                  <Text style={styles.offerTitle}>{offer.title}</Text>
                  <Text style={styles.offerEmphasis}>{offer.emphasis}</Text>
                </View>
                {offer.recommended ? (
                  <View style={styles.offerBadge}>
                    <Text style={styles.offerBadgeText}>RECOMMENDED</Text>
                  </View>
                ) : null}
              </View>
              <Text style={styles.offerDetail}>{offer.detail}</Text>
              <Text style={styles.offerFit}>{offer.fit}</Text>
              <Text style={[styles.offerDecisionLine, offer.recommended && styles.offerDecisionLineRecommended]}>
                {offer.decisionLine}
              </Text>
              <View style={styles.offerHighlightList}>
                {offer.highlights.map((item) => (
                  <Text key={item} style={styles.offerHighlight}>
                    • {item}
                  </Text>
                ))}
              </View>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>WHAT OPENS</Text>
        <Text style={styles.sectionTitle}>What opens with Premium</Text>
        <Text style={styles.sectionBody}>
          Premium is less about extras and more about removing the caps that interrupt a working weekly routine.
        </Text>

        <View style={styles.valueColumn}>
          {valueBullets.map((bullet) => (
            <View key={bullet.key} style={styles.valueCard}>
              <Text style={styles.valueTitle}>{bullet.title}</Text>
              <Text style={styles.valueDetail}>{bullet.detail}</Text>
            </View>
          ))}
        </View>

        <View style={styles.featureGrid}>
          {featureRows.map((feature) => (
            <View key={feature.label} style={styles.featureCard}>
              <View
                style={[
                  styles.featureBadge,
                  feature.premium ? styles.featureBadgePremium : styles.featureBadgeFree,
                ]}
              >
                <Text
                  style={[
                    styles.featureBadgeText,
                    feature.premium ? styles.featureBadgeTextPremium : styles.featureBadgeTextFree,
                  ]}
                >
                  {feature.premium ? 'PREMIUM' : 'FREE'}
                </Text>
              </View>
              <Text style={styles.featureTitle}>{feature.label}</Text>
              <Text style={styles.featureDetail}>{feature.detail}</Text>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>ACCOUNT SYNC</Text>
        <Text style={styles.sectionTitle}>Keep one account everywhere.</Text>
        <Text style={styles.sectionBody}>
          Upgrade state stays tied to the same account you already use on web and mobile, so proof and access stay aligned.
        </Text>

        <View style={styles.stepColumn}>
          {pathSteps.map((step) => (
            <View key={step.key} style={styles.stepCard}>
              <Text style={styles.stepNumber}>{step.number}</Text>
              <View style={styles.stepCopy}>
                <Text style={styles.stepTitle}>{step.title}</Text>
                <Text style={styles.stepDetail}>{step.detail}</Text>
              </View>
            </View>
          ))}
        </View>
      </View>

      <View style={styles.noteCard}>
        <Text style={styles.noteTitle}>
          {billingPortalAvailable ? 'Billing tools are ready here.' : 'Premium stays account-based.'}
        </Text>
        <Text style={styles.noteText}>
          {billingPortalAvailable
            ? 'If billing changes on web, come back here and refresh access so mobile reflects the same state.'
            : 'Even before billing tools are visible here, premium state syncs against the same account you use on web.'}
        </Text>
      </View>

      <TouchableOpacity style={styles.footerLink} onPress={() => navigation.goBack()}>
        <Text style={styles.footerLinkText}>
          {isPremium || billingPortalAvailable ? 'Continue to the app' : 'Continue on free for now'}
        </Text>
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
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    ...shadows.medium,
  },
  heroHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.md,
    alignItems: 'flex-start',
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
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  heroRecommendationCard: {
    marginTop: spacing.sm,
    backgroundColor: `${colors.primary}10`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.primary}35`,
    padding: spacing.sm + 2,
    gap: spacing.xs,
  },
  heroRecommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  heroRecommendationEyebrow: {
    ...typography.overline,
    color: colors.primary,
  },
  heroRecommendationBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 5,
    borderRadius: borderRadius.round,
    backgroundColor: `${colors.primary}22`,
  },
  heroRecommendationBadgeText: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '700',
  },
  heroRecommendationLead: {
    ...typography.h4,
    color: colors.text,
  },
  heroRecommendationBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  heroHighlightList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  heroHighlightPill: {
    backgroundColor: 'rgba(10, 8, 6, 0.22)',
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: `${colors.primary}28`,
    paddingHorizontal: spacing.sm,
    paddingVertical: 7,
  },
  heroHighlightText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '700',
  },
  statusPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statusPillActive: {
    backgroundColor: `${colors.primary}16`,
    borderColor: `${colors.primary}55`,
  },
  statusPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  statusPillTextActive: {
    color: colors.primary,
  },
  metricGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginTop: spacing.xs,
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
  metricValueSmall: {
    ...typography.button,
    color: colors.text,
    marginBottom: 4,
  },
  metricHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  trustPillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  trustPill: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.sm + 2,
    paddingVertical: 7,
  },
  trustPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  pressureStrip: {
    marginTop: spacing.xs,
    gap: spacing.xs,
  },
  pressureStripEyebrow: {
    ...typography.overline,
    color: colors.textLight,
  },
  pressureGrid: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  pressureCard: {
    flex: 1,
    backgroundColor: 'rgba(9, 7, 5, 0.28)',
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.sm,
  },
  pressureCardWarning: {
    borderColor: `${colors.primary}45`,
    backgroundColor: 'rgba(231, 204, 152, 0.08)',
  },
  pressureLabel: {
    ...typography.caption,
    color: colors.textLight,
    marginBottom: 4,
  },
  pressureValue: {
    ...typography.button,
    color: colors.text,
  },
  pressureValueWarning: {
    color: colors.primaryLight,
  },
  actionRow: {
    flexDirection: 'row',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  primaryButton: {
    flex: 1.2,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.md,
    justifyContent: 'center',
  },
  primaryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
    marginBottom: spacing.xs,
  },
  primaryButtonHint: {
    ...typography.caption,
    color: colors.textOnPrimary,
    opacity: 0.88,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.sm + 2,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
    justifyContent: 'center',
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  secondaryButtonHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  inlineLoader: {
    flexDirection: 'row',
    gap: spacing.sm,
    alignItems: 'center',
  },
  buttonDisabled: {
    opacity: 0.7,
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
    lineHeight: 19,
  },
  footerLink: {
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  footerLinkText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  sectionCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    ...shadows.small,
  },
  sectionEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  sectionTitle: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  sectionBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
    marginBottom: spacing.sm,
  },
  featureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  offerGrid: {
    gap: spacing.xs,
  },
  offerCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    gap: spacing.xs,
  },
  offerCardRecommended: {
    borderColor: `${colors.primary}55`,
    backgroundColor: `${colors.primary}10`,
  },
  offerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  offerTitleWrap: {
    flex: 1,
    gap: 2,
  },
  offerEyebrow: {
    ...typography.overline,
    color: colors.primary,
  },
  offerTitle: {
    ...typography.h5,
    color: colors.text,
  },
  offerEmphasis: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.7,
  },
  offerBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 5,
    borderRadius: borderRadius.round,
    backgroundColor: `${colors.primary}22`,
  },
  offerBadgeText: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '700',
  },
  offerDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  offerFit: {
    ...typography.body2,
    color: colors.text,
    lineHeight: 19,
  },
  offerDecisionLine: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  offerDecisionLineRecommended: {
    color: colors.primary,
  },
  offerHighlightList: {
    gap: spacing.xs,
  },
  offerHighlight: {
    ...typography.body2,
    color: colors.text,
    lineHeight: 19,
  },
  valueColumn: {
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  valueCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    gap: spacing.xs,
  },
  valueTitle: {
    ...typography.button,
    color: colors.text,
  },
  valueDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  featureCard: {
    width: '48%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    gap: spacing.xs,
  },
  featureBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.round,
  },
  featureBadgePremium: {
    backgroundColor: `${colors.primary}16`,
  },
  featureBadgeFree: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  featureBadgeText: {
    ...typography.caption,
    fontWeight: '700',
  },
  featureBadgeTextPremium: {
    color: colors.primary,
  },
  featureBadgeTextFree: {
    color: colors.textSecondary,
  },
  featureTitle: {
    ...typography.button,
    color: colors.text,
  },
  featureDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  stepColumn: {
    gap: spacing.xs,
  },
  stepCard: {
    flexDirection: 'row',
    gap: spacing.md,
    alignItems: 'flex-start',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
  },
  stepNumber: {
    ...typography.overline,
    color: colors.primary,
    minWidth: 24,
    marginTop: 2,
  },
  stepCopy: {
    flex: 1,
  },
  stepTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  stepDetail: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
  noteCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    ...shadows.small,
  },
  noteTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  noteText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 19,
  },
});

function bodyPressureLine(
  usageLimits:
    | {
        body_fat_scan?: { remaining: number; limit: number };
        transformation?: { remaining: number; limit: number };
      }
    | null
    | undefined,
) {
  const body = usageLimits?.body_fat_scan;
  const transform = usageLimits?.transformation;

  if (body && transform) {
    return `Right now free keeps ${body.remaining}/${body.limit} weekly proof reads and ${transform.remaining}/${transform.limit} transformation previews. Premium is the better fit once you want the full system to stay open.`;
  }

  return 'Premium matters most once weekly proof, transformation previews, and sync start carrying real momentum for you.';
}
