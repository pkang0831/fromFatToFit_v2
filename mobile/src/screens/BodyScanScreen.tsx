import React, { useMemo, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Image,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { colors, typography, spacing, borderRadius } from '../theme';
import { weeklyCheckinsApi, WeeklyCheckinAnalysis } from '../services/api';

export default function BodyScanScreen({ navigation }: any) {
  const [asset, setAsset] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WeeklyCheckinAnalysis | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const regionalHighlights = useMemo(
    () => (result?.regional_visualization ?? []).slice(0, 3),
    [result]
  );

  const selectFromLibrary = async () => {
    const response = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.9,
      base64: true,
    });

    if (!response.canceled) {
      setAsset(response.assets[0]);
      setResult(null);
      setAnalysisError(null);
    }
  };

  const capturePhoto = async () => {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (permission.status !== 'granted') {
      Alert.alert('Camera access needed', 'Please allow camera access to capture a weekly check-in.');
      return;
    }

    const response = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.9,
      base64: true,
    });

    if (!response.canceled) {
      setAsset(response.assets[0]);
      setResult(null);
      setAnalysisError(null);
    }
  };

  const analyzeWeeklyCheckin = async () => {
    if (!asset?.base64) {
      Alert.alert('No photo selected', 'Choose or capture a full-body image first.');
      return;
    }

    setAnalysisError(null);
    setLoading(true);
    try {
      const { data } = await weeklyCheckinsApi.analyze({
        image_base64: asset.base64,
        ownership_confirmed: true,
      });
      setResult(data);
    } catch (error: any) {
      setAnalysisError(error?.response?.data?.detail ?? 'Please try again with a clearer full-body photo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Weekly check-in</Text>
      <Text style={styles.subtitle}>
        Capture one clean full-body photo. We compare it with your last check-in and turn it into a weekly proof update.
      </Text>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryLabel}>What works best</Text>
        <Text style={styles.summaryText}>Front-facing. Full body visible. Good natural light. No editing.</Text>
        <View style={styles.summaryPills}>
          <View style={styles.summaryPill}><Text style={styles.summaryPillText}>Front-facing</Text></View>
          <View style={styles.summaryPill}><Text style={styles.summaryPillText}>Full body</Text></View>
          <View style={styles.summaryPill}><Text style={styles.summaryPillText}>Weekly proof</Text></View>
        </View>
      </View>

      {asset ? (
        <Image source={{ uri: asset.uri }} style={styles.previewImage} />
      ) : (
        <View style={styles.placeholder}>
          <Text style={styles.placeholderTitle}>No photo selected</Text>
          <Text style={styles.placeholderText}>
            Tap the camera or pick a photo to start your weekly check-in.
          </Text>
        </View>
      )}

      <View style={styles.actions}>
        <TouchableOpacity style={[styles.button, styles.primaryButton]} onPress={capturePhoto} disabled={loading}>
          <Text style={[styles.buttonText, styles.primaryButtonText]}>Take photo</Text>
          <Text style={styles.buttonSubtext}>Camera capture</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={selectFromLibrary} disabled={loading}>
          <Text style={styles.buttonText}>Choose from library</Text>
          <Text style={styles.buttonSubtext}>Import progress photo</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={[styles.analyzeButton, (!asset || loading) && styles.disabledButton]}
        onPress={analyzeWeeklyCheckin}
        disabled={!asset || loading}
      >
        {loading ? (
          <ActivityIndicator color={colors.textOnPrimary} />
        ) : (
          <>
            <Text style={styles.analyzeButtonText}>Analyze weekly check-in</Text>
            <Text style={styles.analyzeButtonSubtext}>This uses the production weekly check-in pipeline</Text>
          </>
        )}
      </TouchableOpacity>

      {analysisError && (
        <View style={styles.errorCard}>
          <Text style={styles.errorLabel}>Could not analyze this check-in</Text>
          <Text style={styles.errorText}>{analysisError}</Text>
        </View>
      )}

      {result ? (
        <View style={styles.resultCard}>
          <View style={styles.resultHeader}>
            <View
              style={[
                styles.statusBadge,
                {
                  backgroundColor:
                    result.weekly_status === 'improved'
                      ? `${colors.success}22`
                      : result.weekly_status === 'regressed'
                        ? `${colors.error}22`
                        : `${colors.primary}22`,
                  borderColor:
                    result.weekly_status === 'improved'
                      ? colors.success
                      : result.weekly_status === 'regressed'
                        ? colors.error
                        : colors.primary,
                },
              ]}
            >
              <Text style={styles.statusBadgeText}>{result.weekly_status.replace('_', ' ')}</Text>
            </View>
            <Text style={styles.resultMeta}>
              {Math.round(result.comparison_confidence * 100)}% confidence
            </Text>
          </View>

          <Text style={styles.resultTitle}>
            Goal proximity {result.derived_scores.goal_proximity_score.toFixed(1)}
          </Text>
          {result.qualitative_summary.slice(0, 3).map((line) => (
            <Text key={line} style={styles.resultLine}>
              {line}
            </Text>
          ))}

          <View style={styles.highlightList}>
            {regionalHighlights.map((item) => (
              <View key={`${item.region}-${item.label}`} style={styles.highlightCard}>
                <Text style={styles.highlightLabel}>{item.label}</Text>
                <Text style={styles.highlightValue}>{item.value}</Text>
                <Text style={styles.highlightNote}>{item.note}</Text>
              </View>
            ))}
          </View>

          <TouchableOpacity
            style={styles.progressButton}
            onPress={() => navigation.navigate('MainTabs', { screen: 'Progress' })}
          >
            <Text style={styles.progressButtonText}>View progress</Text>
          </TouchableOpacity>
        </View>
      ) : null}
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
  },
  title: {
    ...typography.h2,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.xl,
  },
  placeholder: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.xl,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 260,
    marginBottom: spacing.lg,
  },
  placeholderTitle: {
    ...typography.h4,
    marginBottom: spacing.sm,
  },
  placeholderText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  previewImage: {
    width: '100%',
    height: 420,
    borderRadius: borderRadius.xl,
    marginBottom: spacing.lg,
  },
  actions: {
    gap: spacing.md,
  },
  button: {
    backgroundColor: colors.surface,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    alignItems: 'flex-start',
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  buttonText: {
    ...typography.h5,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  primaryButtonText: {
    color: colors.textOnPrimary,
  },
  buttonSubtext: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  summaryCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  summaryLabel: {
    ...typography.overline,
    color: colors.accent,
    marginBottom: spacing.sm,
  },
  summaryText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  summaryPills: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  summaryPill: {
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    backgroundColor: colors.surfaceAlt,
  },
  summaryPillText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '600',
  },
  analyzeButton: {
    backgroundColor: colors.secondary,
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    alignItems: 'center',
    marginTop: spacing.sm,
    marginBottom: spacing.xl,
  },
  disabledButton: {
    opacity: 0.5,
  },
  analyzeButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
    marginBottom: spacing.xs,
  },
  analyzeButtonSubtext: {
    ...typography.caption,
    color: colors.textOnPrimary,
  },
  resultCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  errorCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
  },
  errorLabel: {
    ...typography.caption,
    color: colors.error,
    marginBottom: spacing.xs,
    fontWeight: '700',
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  statusBadge: {
    borderWidth: 1,
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  statusBadgeText: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '700',
    textTransform: 'capitalize',
  },
  resultMeta: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  resultTitle: {
    ...typography.h4,
    marginBottom: spacing.md,
  },
  resultLine: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.sm,
  },
  highlightList: {
    gap: spacing.md,
    marginTop: spacing.md,
  },
  highlightCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
  },
  highlightLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  highlightValue: {
    ...typography.h5,
    marginBottom: spacing.xs,
  },
  highlightNote: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  progressButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  progressButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
});
