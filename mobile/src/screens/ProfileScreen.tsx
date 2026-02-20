import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function ProfileScreen() {
  const { user, signOut } = useAuth();
  const { isPremium, usageLimits } = useSubscription();

  const handleSignOut = async () => {
    Alert.alert('Sign Out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Sign Out',
        style: 'destructive',
        onPress: async () => {
          await signOut();
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.name}>{user?.full_name || 'User'}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        {isPremium && (
          <View style={styles.premiumBadge}>
            <Text style={styles.premiumText}>⭐ Premium Member</Text>
          </View>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Usage Limits</Text>
        {!isPremium && usageLimits && (
          <>
            <View style={styles.limitCard}>
              <Text style={styles.limitLabel}>Food Photo Scans</Text>
              <Text style={styles.limitValue}>
                {usageLimits.food_scan?.remaining || 0} / {usageLimits.food_scan?.limit || 0} remaining
              </Text>
            </View>
            <View style={styles.limitCard}>
              <Text style={styles.limitLabel}>Body Fat Scans</Text>
              <Text style={styles.limitValue}>
                {usageLimits.body_fat_scan?.remaining || 0} / {usageLimits.body_fat_scan?.limit || 0} remaining
              </Text>
            </View>
          </>
        )}
        {isPremium && (
          <Text style={styles.unlimitedText}>✅ Unlimited access to all features</Text>
        )}
      </View>

      <TouchableOpacity style={styles.signOutButton} onPress={handleSignOut}>
        <Text style={styles.signOutText}>Sign Out</Text>
      </TouchableOpacity>
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
  name: {
    ...typography.h3,
    color: colors.textOnPrimary,
    marginBottom: spacing.xs,
  },
  email: {
    ...typography.body1,
    color: colors.textOnPrimary,
  },
  premiumBadge: {
    backgroundColor: colors.premium,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    marginTop: spacing.md,
  },
  premiumText: {
    ...typography.button,
    color: colors.text,
  },
  section: {
    padding: spacing.lg,
  },
  sectionTitle: {
    ...typography.h5,
    marginBottom: spacing.md,
  },
  limitCard: {
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
    ...shadows.small,
  },
  limitLabel: {
    ...typography.body1,
    marginBottom: spacing.xs,
  },
  limitValue: {
    ...typography.body2,
    color: colors.primary,
    fontWeight: '600',
  },
  unlimitedText: {
    ...typography.body1,
    color: colors.success,
    textAlign: 'center',
    marginTop: spacing.md,
  },
  signOutButton: {
    backgroundColor: colors.error,
    margin: spacing.lg,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  signOutText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
});
