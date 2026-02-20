import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function PaywallScreen({ navigation }: any) {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>⭐ Upgrade to Premium</Text>
        <Text style={styles.subtitle}>Unlock all features and unlimited access</Text>
      </View>

      <View style={styles.features}>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✅</Text>
          <Text style={styles.featureText}>Unlimited food photo analysis</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✅</Text>
          <Text style={styles.featureText}>Unlimited body scans and tracking</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✅</Text>
          <Text style={styles.featureText}>Video form analysis for workouts</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✅</Text>
          <Text style={styles.featureText}>Body transformation previews</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✅</Text>
          <Text style={styles.featureText}>Advanced analytics and insights</Text>
        </View>
      </View>

      <View style={styles.pricing}>
        <TouchableOpacity style={styles.pricingCard}>
          <Text style={styles.pricingLabel}>Monthly</Text>
          <Text style={styles.pricingPrice}>$9.99/month</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.pricingCard, styles.pricingCardPopular]}>
          <View style={styles.popularBadge}>
            <Text style={styles.popularText}>MOST POPULAR</Text>
          </View>
          <Text style={styles.pricingLabel}>Yearly</Text>
          <Text style={styles.pricingPrice}>$79.99/year</Text>
          <Text style={styles.pricingSave}>Save 33%</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.subscribeButton}>
        <Text style={styles.subscribeButtonText}>Start Free Trial</Text>
      </TouchableOpacity>

      <Text style={styles.disclaimer}>
        7-day free trial, then auto-renews. Cancel anytime.
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    backgroundColor: colors.primary,
    padding: spacing.xl,
    alignItems: 'center',
  },
  title: {
    ...typography.h2,
    color: colors.textOnPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textOnPrimary,
    textAlign: 'center',
  },
  features: {
    padding: spacing.lg,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: spacing.md,
  },
  featureText: {
    ...typography.body1,
    flex: 1,
  },
  pricing: {
    padding: spacing.lg,
    gap: spacing.md,
  },
  pricingCard: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.border,
    ...shadows.medium,
  },
  pricingCardPopular: {
    borderColor: colors.premium,
    backgroundColor: colors.surfaceAlt,
  },
  popularBadge: {
    backgroundColor: colors.premium,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
    marginBottom: spacing.sm,
  },
  popularText: {
    ...typography.overline,
    color: colors.text,
    fontWeight: '700',
  },
  pricingLabel: {
    ...typography.h5,
    marginBottom: spacing.xs,
  },
  pricingPrice: {
    ...typography.h3,
    color: colors.primary,
  },
  pricingSave: {
    ...typography.caption,
    color: colors.success,
    marginTop: spacing.xs,
  },
  subscribeButton: {
    backgroundColor: colors.premium,
    margin: spacing.lg,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    ...shadows.large,
  },
  subscribeButtonText: {
    ...typography.button,
    fontSize: 18,
    color: colors.text,
  },
  disclaimer: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    padding: spacing.lg,
  },
});
