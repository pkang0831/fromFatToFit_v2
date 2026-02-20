import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { colors, typography, spacing, borderRadius } from '../theme';

export default function WorkoutScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Workout Tracker</Text>
        <Text style={styles.subtitle}>Log your exercises and track progress</Text>
      </View>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>+ Log Workout</Text>
      </TouchableOpacity>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Exercise Library</Text>
        <Text style={styles.placeholder}>Coming soon: Browse exercises with form guides</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    padding: spacing.lg,
  },
  title: {
    ...typography.h3,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  button: {
    backgroundColor: colors.primary,
    margin: spacing.md,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  buttonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  section: {
    padding: spacing.md,
  },
  sectionTitle: {
    ...typography.h5,
    marginBottom: spacing.md,
  },
  placeholder: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xl,
  },
});
