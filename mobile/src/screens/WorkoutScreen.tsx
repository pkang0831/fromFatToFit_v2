import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';
import { workoutApi } from '../services/api';

type ExerciseLibraryItem = {
  id: string;
  name: string;
  category: string;
  muscle_groups: string[];
  form_instructions: string;
  difficulty?: string;
  met_value?: number | null;
  exercise_type?: 'cardio' | 'strength' | string;
};

type WorkoutLog = {
  id: string;
  exercise_name: string;
  duration_minutes?: number | null;
  calories_burned?: number | null;
  notes?: string | null;
  created_at: string;
  sets: Array<{
    set_number: number;
    reps: number;
    weight?: number | null;
  }>;
};

type SetDraft = {
  set_number: number;
  reps: string;
  weight: string;
};

const getToday = () => new Date().toISOString().split('T')[0];

export default function WorkoutScreen() {
  const [library, setLibrary] = useState<ExerciseLibraryItem[]>([]);
  const [logs, setLogs] = useState<WorkoutLog[]>([]);
  const [selectedExerciseId, setSelectedExerciseId] = useState('');
  const [sets, setSets] = useState<SetDraft[]>([{ set_number: 1, reps: '', weight: '' }]);
  const [durationMinutes, setDurationMinutes] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [libraryError, setLibraryError] = useState<string | null>(null);
  const [logsError, setLogsError] = useState<string | null>(null);

  const selectedExercise = useMemo(
    () => library.find(item => item.id === selectedExerciseId) ?? null,
    [library, selectedExerciseId],
  );

  const loadWorkoutData = useCallback(async (opts?: { refreshing?: boolean }) => {
    const isRefresh = opts?.refreshing ?? false;
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setLibraryError(null);
    setLogsError(null);

    try {
      const [libraryRes, logsRes] = await Promise.allSettled([
        workoutApi.getExerciseLibrary(),
        workoutApi.getWorkoutLogs(getToday()),
      ]);

      if (libraryRes.status === 'fulfilled') {
        const items = (libraryRes.value.data ?? []) as ExerciseLibraryItem[];
        setLibrary(items);
        setSelectedExerciseId(prev => prev || items[0]?.id || '');
      } else {
        console.error('Failed to load exercise library:', libraryRes.reason);
        setLibrary([]);
        setLibraryError('We could not load the exercise library. Retry to see the log form.');
      }

      if (logsRes.status === 'fulfilled') {
        setLogs((logsRes.value.data ?? []) as WorkoutLog[]);
      } else {
        console.error('Failed to load workout logs:', logsRes.reason);
        setLogs([]);
        setLogsError('We could not load today’s workout history right now.');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    void loadWorkoutData();
  }, [loadWorkoutData]);

  const totalCaloriesBurned = useMemo(
    () => logs.reduce((sum, workout) => sum + (workout.calories_burned ?? 0), 0),
    [logs],
  );

  const totalSets = useMemo(
    () => logs.reduce((sum, workout) => sum + (workout.sets?.length ?? 0), 0),
    [logs],
  );

  const totalDuration = useMemo(
    () => logs.reduce((sum, workout) => sum + (workout.duration_minutes ?? 0), 0),
    [logs],
  );

  const updateSet = (index: number, key: 'reps' | 'weight', value: string) => {
    setSets(prev => prev.map((set, i) => (i === index ? { ...set, [key]: value } : set)));
  };

  const addSet = () => {
    setSets(prev => [
      ...prev,
      {
        set_number: prev.length + 1,
        reps: '',
        weight: '',
      },
    ]);
  };

  const removeSet = (index: number) => {
    setSets(prev => {
      if (prev.length === 1) return prev;
      const filtered = prev.filter((_, i) => i !== index);
      return filtered.map((set, idx) => ({ ...set, set_number: idx + 1 }));
    });
  };

  const resetForm = () => {
    setSets([{ set_number: 1, reps: '', weight: '' }]);
    setDurationMinutes('');
    setNotes('');
  };

  const handleSaveWorkout = async () => {
    if (!selectedExercise) {
      setLogsError('Choose an exercise first.');
      return;
    }

    const builtSets = sets
      .map(set => ({
        set_number: set.set_number,
        reps: Number.parseInt(set.reps, 10),
        weight: set.weight ? Number.parseFloat(set.weight) : undefined,
      }))
      .filter(set => Number.isFinite(set.reps) && set.reps > 0);

    if (builtSets.length === 0) {
      setLogsError('Add at least one set with reps before saving.');
      return;
    }

    const durationValue = durationMinutes ? Number.parseInt(durationMinutes, 10) : undefined;

    setSaving(true);
    try {
      await workoutApi.logWorkout({
        date: getToday(),
        exercise_id: selectedExercise.id,
        exercise_name: selectedExercise.name,
        sets: builtSets,
        duration_minutes: Number.isFinite(durationValue as number) ? durationValue : undefined,
        notes: notes.trim() || undefined,
      });

      resetForm();
      await loadWorkoutData({ refreshing: true });
    } catch (error) {
      console.error('Failed to log workout:', error);
      setLogsError('We could not save that workout. Try again with the same details.');
    } finally {
      setSaving(false);
    }
  };

  const topExercises = library.slice(0, 8);

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading workout tracker…</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={(
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => void loadWorkoutData({ refreshing: true })}
          tintColor={colors.primary}
        />
      )}
    >
      <View style={styles.heroCard}>
        <Text style={styles.heroEyebrow}>Today</Text>
        <Text style={styles.title}>Workout tracker</Text>
        <Text style={styles.subtitle}>
          Log a set, keep the exercise library visible, and see today’s session totals without hunting through menus.
        </Text>

        <View style={styles.summaryRow}>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryValue}>{logs.length}</Text>
            <Text style={styles.summaryLabel}>sessions</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryValue}>{totalSets}</Text>
            <Text style={styles.summaryLabel}>sets</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryValue}>{Math.round(totalCaloriesBurned)}</Text>
            <Text style={styles.summaryLabel}>kcal</Text>
          </View>
        </View>
        <Text style={styles.summaryHint}>
          {totalDuration > 0 ? `${totalDuration} total minutes logged` : 'No workout time logged yet'}
        </Text>
      </View>

      {libraryError ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Exercise library unavailable</Text>
          <Text style={styles.errorText}>{libraryError}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={() => void loadWorkoutData()}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {logsError ? (
        <View style={styles.warningCard}>
          <Text style={styles.warningTitle}>Workout history could not load</Text>
          <Text style={styles.warningText}>{logsError}</Text>
        </View>
      ) : null}

      <View style={styles.formCard}>
        <Text style={styles.sectionTitle}>Log a workout</Text>
        <Text style={styles.sectionSubtitle}>Pick an exercise, add your sets, and save the session.</Text>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.exerciseStrip}>
          {topExercises.length > 0 ? topExercises.map(item => {
            const active = item.id === selectedExerciseId;
            return (
              <TouchableOpacity
                key={item.id}
                style={[styles.exerciseChip, active && styles.exerciseChipActive]}
                onPress={() => setSelectedExerciseId(item.id)}
              >
                <Text style={[styles.exerciseChipTitle, active && styles.exerciseChipTitleActive]}>{item.name}</Text>
                <Text style={[styles.exerciseChipMeta, active && styles.exerciseChipMetaActive]}>{item.category}</Text>
              </TouchableOpacity>
            );
          }) : (
            <Text style={styles.emptyText}>No exercises loaded yet.</Text>
          )}
        </ScrollView>

        {selectedExercise ? (
          <View style={styles.exerciseDetail}>
            <View style={styles.exerciseDetailHeader}>
              <Text style={styles.exerciseDetailTitle}>{selectedExercise.name}</Text>
              <View style={styles.exerciseTag}>
                <Text style={styles.exerciseTagText}>{selectedExercise.exercise_type ?? 'strength'}</Text>
              </View>
            </View>
            <Text style={styles.exerciseDetailMeta}>
              {selectedExercise.difficulty ?? 'intermediate'} · {selectedExercise.category}
            </Text>
            <Text style={styles.exerciseInstruction}>{selectedExercise.form_instructions}</Text>
            <Text style={styles.exerciseMuscles}>
              {selectedExercise.muscle_groups?.length ? selectedExercise.muscle_groups.join(' · ') : 'No muscle groups listed'}
            </Text>
          </View>
        ) : (
          <View style={styles.emptySelection}>
            <Text style={styles.emptySelectionTitle}>Choose an exercise to begin</Text>
            <Text style={styles.emptySelectionText}>
              The workout log needs an exercise before it can be saved.
            </Text>
          </View>
        )}

        <View style={styles.formSection}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionSubheading}>Sets</Text>
            <TouchableOpacity onPress={addSet}>
              <Text style={styles.inlineAction}>+ Add set</Text>
            </TouchableOpacity>
          </View>

          {sets.map((set, index) => (
            <View key={`${set.set_number}-${index}`} style={styles.setRow}>
              <View style={styles.setLabelWrap}>
                <Text style={styles.setLabel}>Set {set.set_number}</Text>
                {sets.length > 1 ? (
                  <TouchableOpacity onPress={() => removeSet(index)}>
                    <Text style={styles.inlineDanger}>Remove</Text>
                  </TouchableOpacity>
                ) : null}
              </View>
              <View style={styles.setInputs}>
                <TextInput
                  style={[styles.input, styles.flexInput]}
                  placeholder="Reps"
                  placeholderTextColor={colors.textSecondary}
                  keyboardType="numeric"
                  value={set.reps}
                  onChangeText={value => updateSet(index, 'reps', value)}
                />
                <TextInput
                  style={[styles.input, styles.flexInput]}
                  placeholder="Weight"
                  placeholderTextColor={colors.textSecondary}
                  keyboardType="numeric"
                  value={set.weight}
                  onChangeText={value => updateSet(index, 'weight', value)}
                />
              </View>
            </View>
          ))}
        </View>

        <View style={styles.formSection}>
          <Text style={styles.sectionSubheading}>Session details</Text>
          <View style={styles.setInputs}>
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Duration (min)"
              placeholderTextColor={colors.textSecondary}
              keyboardType="numeric"
              value={durationMinutes}
              onChangeText={setDurationMinutes}
            />
            <TextInput
              style={[styles.input, styles.flexInput]}
              placeholder="Notes"
              placeholderTextColor={colors.textSecondary}
              value={notes}
              onChangeText={setNotes}
            />
          </View>
        </View>

        <TouchableOpacity
          style={[styles.primaryButton, saving && styles.disabledButton]}
          onPress={handleSaveWorkout}
          disabled={saving || !selectedExercise}
        >
          {saving ? (
            <ActivityIndicator color={colors.textOnPrimary} />
          ) : (
            <Text style={styles.primaryButtonText}>Log workout</Text>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.listSection}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Today’s workouts</Text>
          <Text style={styles.sectionMeta}>{logs.length} logged</Text>
        </View>

        {logs.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No workouts logged yet</Text>
            <Text style={styles.emptyText}>
              Pick an exercise above and add your first set to make the screen feel alive.
            </Text>
          </View>
        ) : (
          logs.map(log => (
            <View key={log.id} style={styles.logCard}>
              <View style={styles.logHeader}>
                <Text style={styles.logTitle}>{log.exercise_name}</Text>
                {log.calories_burned != null ? (
                  <Text style={styles.logCalories}>{Math.round(log.calories_burned)} cal</Text>
                ) : null}
              </View>
              <Text style={styles.logMeta}>
                {log.duration_minutes ? `${log.duration_minutes} min` : 'Duration not set'}
                {log.sets?.length ? ` · ${log.sets.length} set${log.sets.length === 1 ? '' : 's'}` : ''}
              </Text>
              <View style={styles.setSummary}>
                {log.sets.map(set => (
                  <View key={`${log.id}-${set.set_number}`} style={styles.setPill}>
                    <Text style={styles.setPillText}>
                      Set {set.set_number}: {set.reps} reps{set.weight != null ? ` · ${set.weight}kg` : ''}
                    </Text>
                  </View>
                ))}
              </View>
              {log.notes ? <Text style={styles.logNotes}>{log.notes}</Text> : null}
            </View>
          ))
        )}
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
    paddingBottom: spacing.xxl,
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
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    ...shadows.medium,
  },
  heroEyebrow: {
    ...typography.caption,
    color: colors.primary,
    textTransform: 'uppercase',
    letterSpacing: 1.1,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    marginTop: spacing.xs,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  summaryRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  summaryCard: {
    flex: 1,
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  summaryValue: {
    ...typography.number,
    fontSize: 24,
    color: colors.primary,
    textAlign: 'center',
  },
  summaryLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
    textTransform: 'uppercase',
  },
  summaryHint: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.sm,
  },
  errorCard: {
    backgroundColor: colors.surfaceAlt,
    borderColor: `${colors.error}30`,
    borderWidth: 1,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  errorTitle: {
    ...typography.h5,
    color: colors.error,
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  retryButton: {
    alignSelf: 'flex-start',
    marginTop: spacing.md,
    backgroundColor: colors.error,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  retryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  warningCard: {
    backgroundColor: colors.surfaceAlt,
    borderColor: `${colors.warning}30`,
    borderWidth: 1,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  warningTitle: {
    ...typography.h5,
  },
  warningText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  formCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.lg,
    ...shadows.small,
  },
  sectionTitle: {
    ...typography.h4,
  },
  sectionSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.md,
  },
  exerciseStrip: {
    gap: spacing.sm,
    paddingBottom: spacing.sm,
  },
  exerciseChip: {
    width: 160,
    backgroundColor: colors.surface,
    borderColor: colors.borderLight,
    borderWidth: 1,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  exerciseChipActive: {
    backgroundColor: `${colors.primary}14`,
    borderColor: colors.primary,
  },
  exerciseChipTitle: {
    ...typography.body1,
    fontWeight: '700',
    color: colors.text,
  },
  exerciseChipTitleActive: {
    color: colors.primary,
  },
  exerciseChipMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
    textTransform: 'capitalize',
  },
  exerciseChipMetaActive: {
    color: colors.primary,
  },
  exerciseDetail: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    marginTop: spacing.md,
    gap: spacing.xs,
  },
  exerciseDetailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  exerciseDetailTitle: {
    ...typography.h5,
    flex: 1,
  },
  exerciseTag: {
    backgroundColor: `${colors.primary}12`,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
  },
  exerciseTagText: {
    ...typography.caption,
    color: colors.primary,
    textTransform: 'capitalize',
  },
  exerciseDetailMeta: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  exerciseInstruction: {
    ...typography.body2,
    color: colors.text,
  },
  exerciseMuscles: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptySelection: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: `${colors.warning}30`,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  emptySelectionTitle: {
    ...typography.body1,
    fontWeight: '700',
  },
  emptySelectionText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  formSection: {
    marginTop: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  sectionSubheading: {
    ...typography.body1,
    fontWeight: '700',
  },
  inlineAction: {
    ...typography.body2,
    color: colors.primary,
    fontWeight: '700',
  },
  inlineDanger: {
    ...typography.caption,
    color: colors.error,
    fontWeight: '700',
  },
  setRow: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  setLabelWrap: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  setLabel: {
    ...typography.body1,
    fontWeight: '700',
  },
  setInputs: {
    flexDirection: 'column',
    gap: spacing.sm,
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.borderLight,
    borderRadius: borderRadius.md,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    ...typography.body1,
    color: colors.text,
  },
  flexInput: {
    flex: 1,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  primaryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  disabledButton: {
    opacity: 0.7,
  },
  listSection: {
    marginTop: spacing.lg,
  },
  sectionMeta: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptyState: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  emptyTitle: {
    ...typography.h5,
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xs,
  },
  logCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: spacing.sm,
    ...shadows.small,
  },
  logHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  logTitle: {
    ...typography.body1,
    fontWeight: '700',
    flex: 1,
  },
  logCalories: {
    ...typography.body2,
    color: colors.primary,
    fontWeight: '700',
  },
  logMeta: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  setSummary: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginTop: spacing.sm,
  },
  setPill: {
    backgroundColor: `${colors.primary}10`,
    borderRadius: 999,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
  },
  setPillText: {
    ...typography.caption,
    color: colors.primary,
  },
  logNotes: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    fontStyle: 'italic',
  },
});
