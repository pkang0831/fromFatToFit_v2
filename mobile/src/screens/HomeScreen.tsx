import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useSubscription } from '../contexts/SubscriptionContext';
import { dashboardApi } from '../services/api';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function HomeScreen({ navigation }: any) {
  const { user } = useAuth();
  const { isPremium } = useSubscription();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const { data } = await dashboardApi.getQuickStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
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

      {/* Today's Stats */}
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

      {/* Feature Cards */}
      <View style={styles.featuresGrid}>
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
          onPress={() => navigation.navigate('FoodCamera')}
        >
          <Text style={styles.featureIcon}>📸</Text>
          <Text style={styles.featureTitle}>AI Food Scan</Text>
          <Text style={styles.featureDescription}>Photo analysis</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('Workout')}
        >
          <Text style={styles.featureIcon}>💪</Text>
          <Text style={styles.featureTitle}>Workouts</Text>
          <Text style={styles.featureDescription}>Log & track exercise</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.featureCard}
          onPress={() => navigation.navigate('BodyScan')}
        >
          <Text style={styles.featureIcon}>📊</Text>
          <Text style={styles.featureTitle}>Body Scan</Text>
          <Text style={styles.featureDescription}>Track progress</Text>
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
    color: colors.text,
    fontWeight: '700',
  },
  card: {
    backgroundColor: colors.surface,
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
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
  },
  statSubLabel: {
    ...typography.caption,
    color: colors.textLight,
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
