import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useBottomTabBarHeight } from '@react-navigation/bottom-tabs';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { workoutApi } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';
import { getLocalDateString } from '../utils/date';

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

const getToday = () => getLocalDateString();

const formatWorkoutTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Saved today';

  return date.toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
};

export default function WorkoutScreen() {
  const tabBarHeight = useBottomTabBarHeight();
  const insets = useSafeAreaInsets();
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
    () => library.find((item) => item.id === selectedExerciseId) ?? null,
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
        setSelectedExerciseId((prev) => prev || items[0]?.id || '');
      } else {
        setLibrary([]);
        setLibraryError('We could not load the exercise library. Retry to rebuild the workout form.');
      }

      if (logsRes.status === 'fulfilled') {
        setLogs((logsRes.value.data ?? []) as WorkoutLog[]);
      } else {
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
    setSets((prev) => prev.map((set, i) => (i === index ? { ...set, [key]: value } : set)));
  };

  const addSet = () => {
    setSets((prev) => [
      ...prev,
      {
        set_number: prev.length + 1,
        reps: '',
        weight: '',
      },
    ]);
  };

  const removeSet = (index: number) => {
    setSets((prev) => {
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
      .map((set) => ({
        set_number: set.set_number,
        reps: Number.parseInt(set.reps, 10),
        weight: set.weight ? Number.parseFloat(set.weight) : undefined,
      }))
      .filter((set) => Number.isFinite(set.reps) && set.reps > 0);

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
      setLogsError('We could not save that workout. Try again with the same details.');
    } finally {
      setSaving(false);
    }
  };

  const topExercises = library.slice(0, 8);
  const helperPills = ['Log what you hit', 'One lift at a time', 'Today over history'];

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
      contentContainerStyle={[styles.content, { paddingTop: insets.top + spacing.sm, paddingBottom: spacing.xxl + tabBarHeight }]}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={() => void loadWorkoutData({ refreshing: true })}
          tintColor={colors.primary}
        />
      }
    >
      <View style={styles.heroCard}>
        <View style={styles.heroHeader}>
          <View style={styles.heroCopy}>
            <Text style={styles.heroEyebrow}>WORKOUT</Text>
            <Text style={styles.heroTitle}>Keep the session honest.</Text>
            <Text style={styles.heroBody}>
              Pick one lift, log the sets you actually did, and keep today’s effort visible without overbuilding the form.
            </Text>
          </View>
          <View style={styles.heroPill}>
            <Text style={styles.heroPillText}>{logs.length} sessions</Text>
          </View>
        </View>

        <View style={styles.metricGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Sets</Text>
            <Text style={styles.metricValue}>{totalSets}</Text>
            <Text style={styles.metricHint}>logged today</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Minutes</Text>
            <Text style={styles.metricValue}>{totalDuration}</Text>
            <Text style={styles.metricHint}>training time</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Burn</Text>
            <Text style={styles.metricValue}>{Math.round(totalCaloriesBurned)}</Text>
            <Text style={styles.metricHint}>estimated kcal</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Exercise</Text>
            <Text style={styles.metricValueSmall}>{selectedExercise?.name ?? 'Choose one'}</Text>
            <Text style={styles.metricHint}>current focus</Text>
          </View>
        </View>

        <View style={styles.heroPillRow}>
          {helperPills.map((pill) => (
            <View key={pill} style={styles.heroInfoPill}>
              <Text style={styles.heroInfoPillText}>{pill}</Text>
            </View>
          ))}
        </View>
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
          <Text style={styles.warningTitle}>Workout history needs attention</Text>
          <Text style={styles.warningText}>{logsError}</Text>
        </View>
      ) : null}

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>EXERCISE</Text>
        <Text style={styles.sectionTitle}>Choose the movement.</Text>
        <Text style={styles.sectionBody}>Keep the selection fast. You can always switch before saving.</Text>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.exerciseStrip}>
          {topExercises.length > 0 ? (
            topExercises.map((item) => {
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
            })
          ) : (
            <Text style={styles.libraryEmptyText}>No exercises loaded yet.</Text>
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
              {(selectedExercise.difficulty ?? 'intermediate').toUpperCase()} · {selectedExercise.category}
            </Text>
            <Text style={styles.exerciseInstruction}>{selectedExercise.form_instructions}</Text>
            <Text style={styles.exerciseMuscles}>
              {selectedExercise.muscle_groups?.length
                ? selectedExercise.muscle_groups.join(' · ')
                : 'No muscle groups listed'}
            </Text>
          </View>
        ) : (
          <View style={styles.emptySelection}>
            <Text style={styles.emptySelectionTitle}>Choose an exercise to begin</Text>
            <Text style={styles.emptySelectionText}>The workout log needs one movement before it can be saved.</Text>
          </View>
        )}
      </View>

      <View style={styles.sectionCard}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionEyebrow}>LOG SESSION</Text>
            <Text style={styles.sectionTitle}>Add your sets.</Text>
          </View>
          <TouchableOpacity onPress={addSet} style={styles.inlineButton}>
            <Text style={styles.inlineButtonText}>+ Add set</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.sectionBody}>Save the reps and weight you actually hit. Leave the rest simple.</Text>

        {sets.map((set, index) => (
          <View key={`${set.set_number}-${index}`} style={styles.setCard}>
            <View style={styles.setHeader}>
              <Text style={styles.setTitle}>Set {set.set_number}</Text>
              {sets.length > 1 ? (
                <TouchableOpacity onPress={() => removeSet(index)}>
                  <Text style={styles.removeText}>Remove</Text>
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
                onChangeText={(value) => updateSet(index, 'reps', value)}
              />
              <TextInput
                style={[styles.input, styles.flexInput]}
                placeholder="Weight"
                placeholderTextColor={colors.textSecondary}
                keyboardType="numeric"
                value={set.weight}
                onChangeText={(value) => updateSet(index, 'weight', value)}
              />
            </View>
          </View>
        ))}

        <View style={styles.metaRow}>
          <TextInput
            style={[styles.input, styles.flexInput]}
            placeholder="Minutes"
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

        <TouchableOpacity
          style={[styles.primaryButton, saving && styles.buttonDisabled]}
          onPress={() => void handleSaveWorkout()}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator color={colors.textOnPrimary} />
          ) : (
            <>
              <Text style={styles.primaryButtonText}>Save workout</Text>
              <Text style={styles.primaryButtonHint}>Add it to today</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionEyebrow}>TODAY</Text>
        <Text style={styles.sectionTitle}>Session history.</Text>
        <Text style={styles.sectionBody}>This is your clean record for the day, not a giant training diary.</Text>

        {logs.length > 0 ? (
          logs.map((log) => (
            <View key={log.id} style={styles.logCard}>
              <View style={styles.logHeader}>
                <View>
                  <Text style={styles.logTitle}>{log.exercise_name}</Text>
                  <Text style={styles.logMeta}>{formatWorkoutTime(log.created_at)}</Text>
                </View>
                <Text style={styles.logKcal}>{Math.round(log.calories_burned ?? 0)} kcal</Text>
              </View>

              <View style={styles.logStatRow}>
                <Text style={styles.logStat}>{log.sets.length} sets</Text>
                <Text style={styles.logStat}>{log.duration_minutes ?? 0} min</Text>
              </View>

              <View style={styles.logSetWrap}>
                {log.sets.map((set) => (
                  <View key={`${log.id}-${set.set_number}`} style={styles.logSetChip}>
                    <Text style={styles.logSetText}>
                      S{set.set_number} · {set.reps} reps{set.weight ? ` · ${set.weight} kg` : ''}
                    </Text>
                  </View>
                ))}
              </View>

              {log.notes ? <Text style={styles.logNote}>{log.notes}</Text> : null}
            </View>
          ))
        ) : (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyTitle}>No workout logged yet.</Text>
            <Text style={styles.emptyText}>Choose one exercise, add a few sets, and keep today’s session visible.</Text>
          </View>
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
    paddingBottom: spacing.xl,
    gap: spacing.lg,
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
    padding: spacing.xl,
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
  heroEyebrow: {
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
    ...typography.body1,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  heroPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  heroPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  metricGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
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
  heroPillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  heroInfoPill: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  heroInfoPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  errorCard: {
    backgroundColor: `${colors.error}12`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.error}40`,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  errorTitle: {
    ...typography.button,
    color: colors.text,
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  warningCard: {
    backgroundColor: `${colors.primary}12`,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: `${colors.primary}35`,
    padding: spacing.lg,
    gap: spacing.xs,
  },
  warningTitle: {
    ...typography.button,
    color: colors.text,
  },
  warningText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  retryButton: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  retryButtonText: {
    ...typography.button,
    color: colors.text,
  },
  sectionCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    ...shadows.small,
  },
  sectionEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  sectionBody: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: spacing.md,
  },
  exerciseStrip: {
    gap: spacing.sm,
  },
  exerciseChip: {
    width: 138,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  exerciseChipActive: {
    backgroundColor: `${colors.primary}16`,
    borderColor: `${colors.primary}55`,
  },
  exerciseChipTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: 4,
  },
  exerciseChipTitleActive: {
    color: colors.primary,
  },
  exerciseChipMeta: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  exerciseChipMetaActive: {
    color: colors.primary,
  },
  exerciseDetail: {
    marginTop: spacing.md,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
  },
  exerciseDetailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.md,
    alignItems: 'center',
  },
  exerciseDetailTitle: {
    ...typography.button,
    color: colors.text,
    flex: 1,
  },
  exerciseTag: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 6,
    borderRadius: borderRadius.round,
    backgroundColor: `${colors.primary}16`,
  },
  exerciseTagText: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '700',
  },
  exerciseDetailMeta: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  exerciseInstruction: {
    ...typography.body2,
    color: colors.text,
    lineHeight: 20,
  },
  exerciseMuscles: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  emptySelection: {
    marginTop: spacing.md,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  emptySelectionTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  emptySelectionText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  libraryEmptyText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
    marginBottom: spacing.sm,
  },
  inlineButton: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  inlineButtonText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '700',
  },
  setCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  setHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  setTitle: {
    ...typography.button,
    color: colors.text,
  },
  removeText: {
    ...typography.caption,
    color: colors.error,
    fontWeight: '700',
  },
  setInputs: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  input: {
    ...typography.body1,
    color: colors.text,
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  flexInput: {
    flex: 1,
  },
  metaRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  primaryButton: {
    marginTop: spacing.md,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
  },
  primaryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  primaryButtonHint: {
    ...typography.caption,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
    opacity: 0.88,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  logCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  logHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing.md,
    alignItems: 'center',
  },
  logTitle: {
    ...typography.button,
    color: colors.text,
  },
  logMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  logKcal: {
    ...typography.body2,
    color: colors.primary,
  },
  logStatRow: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  logStat: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  logSetWrap: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  logSetChip: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  logSetText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  logNote: {
    ...typography.body2,
    color: colors.text,
    lineHeight: 20,
  },
  emptyCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.sm,
  },
  emptyTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});
