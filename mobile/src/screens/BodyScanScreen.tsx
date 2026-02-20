import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

export default function BodyScanScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Body Analysis</Text>
      <Text style={styles.subtitle}>Track your body composition and progress</Text>

      <TouchableOpacity style={[styles.button, styles.primaryButton]}>
        <Text style={styles.buttonText}>📸 Body Fat Estimate</Text>
        <Text style={styles.buttonSubtext}>1 free scan</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>📊 Percentile Ranking</Text>
        <Text style={styles.buttonSubtext}>1 free scan</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.button, styles.premiumButton]}>
        <Text style={styles.buttonText}>✨ Transformation Preview</Text>
        <Text style={styles.buttonSubtext}>Premium only</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.lg,
    justifyContent: 'center',
  },
  title: {
    ...typography.h2,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xxl,
  },
  button: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    borderRadius: borderRadius.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  premiumButton: {
    backgroundColor: colors.premium,
    borderColor: colors.premiumDark,
  },
  buttonText: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  buttonSubtext: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
