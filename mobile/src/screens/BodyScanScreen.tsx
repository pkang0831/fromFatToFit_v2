import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useSubscription } from '../contexts/SubscriptionContext';
import { borderRadius, colors, spacing, typography } from '../theme';
import { weeklyCheckinsApi, WeeklyCheckinAnalysis } from '../services/api';

export default function BodyScanScreen({ navigation }: any) {
  const { checkFeatureAccess, isPremium } = useSubscription();
  const [asset, setAsset] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<WeeklyCheckinAnalysis | null>(null);
  const [latestResult, setLatestResult] = useState<WeeklyCheckinAnalysis | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [loadingLatest, setLoadingLatest] = useState(true);
  const bodyScanAccess = checkFeatureAccess('body_fat_scan');
  const accessBlocked = !isPremium && !bodyScanAccess.allowed;
  const displayResult = result ?? latestResult;

  useEffect(() => {
    void loadLatestResult();
  }, []);

  const loadLatestResult = async () => {
    setLoadingLatest(true);
    try {
      const { data } = await weeklyCheckinsApi.getLatest();
      setLatestResult(data);
    } catch (error: any) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail;
      if (
        status === 404 ||
        (typeof detail === 'string' && detail.toLowerCase().includes('no weekly check-ins'))
      ) {
        setLatestResult(null);
      }
    } finally {
      setLoadingLatest(false);
    }
  };

  const regionalHighlights = useMemo(
    () => (displayResult?.regional_visualization ?? []).slice(0, 4),
    [displayResult],
  );
  const statusTone =
    displayResult?.weekly_status === 'improved'
      ? colors.success
      : displayResult?.weekly_status === 'regressed'
        ? colors.error
        : displayResult?.weekly_status === 'low_confidence'
          ? colors.warning
          : colors.primary;
  const statusLabel =
    displayResult == null
      ? 'Awaiting proof'
      : displayResult.is_first_checkin
        ? 'Baseline saved'
        : displayResult.weekly_status.replace('_', ' ');
  const stageLabel = asset ? 'Photo ready' : 'Need photo';
  const outputLabel = displayResult ? 'Proof saved' : asset ? 'Ready to analyze' : 'No result yet';
  const confidenceLabel = displayResult ? `${Math.round(displayResult.comparison_confidence * 100)}%` : '--';
  const frameLabel = asset ? (asset.assetId ? 'Library frame' : 'Fresh capture') : 'No frame yet';
  const highlightsCountLabel = displayResult ? `${regionalHighlights.length}` : '--';
  const captureGuide = 'Front-facing · Full body · Simple light';
  const captureMetrics = displayResult
    ? [
        { key: 'stage', label: 'Stage', value: stageLabel, small: true },
        { key: 'output', label: 'Output', value: outputLabel, small: true },
        { key: 'confidence', label: 'Confidence', value: confidenceLabel, small: false },
        { key: 'highlights', label: 'Highlights', value: highlightsCountLabel, small: false },
      ]
    : [
        { key: 'stage', label: 'Stage', value: stageLabel, small: true },
        { key: 'output', label: 'Output', value: outputLabel, small: true },
      ];

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
    if (accessBlocked) {
      navigation.navigate('Paywall');
      return;
    }

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
      setLatestResult(data);
    } catch (error: any) {
      setAnalysisError(error?.response?.data?.detail ?? 'Please try again with a clearer full-body photo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.captureCard}>
        <View style={styles.captureHeader}>
          <View style={styles.captureHeaderCopy}>
            <Text style={styles.captureEyebrow}>WEEKLY CHECK-IN</Text>
            <Text style={styles.title}>Capture one clean proof.</Text>
            <Text style={styles.subtitle}>
              One clean frame against your last check-in, with a direction read you can use.
            </Text>
          </View>
        </View>
        <View style={[styles.statusPill, styles.captureStatusPill, { backgroundColor: `${statusTone}16`, borderColor: `${statusTone}45` }]}>
          <Text style={[styles.statusPillText, { color: statusTone }]}>{statusLabel}</Text>
        </View>

        <View style={styles.captureMetricGrid}>
          {captureMetrics.map((item) => (
            <View key={item.key} style={styles.captureMetricCard}>
              <Text style={styles.captureMetricLabel}>{item.label}</Text>
              <Text style={item.small ? styles.captureMetricValueSmall : styles.captureMetricValue}>
                {item.value}
              </Text>
            </View>
          ))}
        </View>

        <View style={styles.captureGuideBar}>
          <Text style={styles.captureGuideText}>{captureGuide}</Text>
        </View>

        {accessBlocked ? (
          <View style={styles.limitCard}>
            <Text style={styles.limitTitle}>Free weekly proof is capped right now.</Text>
            <Text style={styles.limitText}>
              You have used the free weekly check-ins for this cycle. Upgrade to keep proof open.
            </Text>
            <TouchableOpacity style={styles.limitButton} onPress={() => navigation.navigate('Paywall')}>
              <Text style={styles.limitButtonText}>View Premium</Text>
            </TouchableOpacity>
          </View>
        ) : null}

          {analysisError ? (
            <View style={styles.errorCard}>
              <Text style={styles.errorLabel}>Could not analyze this check-in</Text>
              <Text style={styles.errorText}>{analysisError}</Text>
            </View>
          ) : null}

        <View style={styles.stageCard}>
          <View style={styles.stageHeader}>
            <View>
              <Text style={styles.stageLabel}>CURRENT FRAME</Text>
              <Text style={styles.stageHeaderTitle}>{asset ? frameLabel : 'Waiting for a clean frame'}</Text>
            </View>
            <View style={styles.stageStatusPill}>
              <Text style={styles.stageStatusPillText}>{asset ? 'Ready' : 'Waiting'}</Text>
            </View>
          </View>
          <View style={styles.stageMetaRow}>
            <Text style={styles.stageMetaText}>{captureGuide}</Text>
          </View>
          {asset ? (
            <Image source={{ uri: asset.uri }} style={styles.previewImage} />
          ) : (
            <View style={styles.placeholder}>
              <Text style={styles.placeholderTitle}>No photo selected</Text>
              <Text style={styles.placeholderText}>
                Capture or import one clean full-body frame to start this week’s proof.
              </Text>
            </View>
          )}
        </View>

        <View style={styles.actionsRow}>
          <TouchableOpacity
            style={[styles.actionButton, styles.primaryActionButton]}
            onPress={capturePhoto}
            disabled={loading}
          >
            <Text style={[styles.actionButtonText, styles.primaryActionButtonText]}>Take photo</Text>
            <Text style={[styles.actionButtonHint, styles.primaryActionButtonHint]}>Use camera</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton} onPress={selectFromLibrary} disabled={loading}>
            <Text style={styles.actionButtonText}>Choose photo</Text>
            <Text style={styles.actionButtonHint}>From library</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.analyzeButton, (!asset || loading || accessBlocked) && styles.disabledButton]}
          onPress={analyzeWeeklyCheckin}
          disabled={!asset || loading || accessBlocked}
        >
          {loading ? (
            <ActivityIndicator color={colors.textOnPrimary} />
          ) : (
            <>
              <Text style={styles.analyzeButtonText}>
                {accessBlocked ? 'Upgrade to keep weekly proof open' : 'Analyze weekly check-in'}
              </Text>
              <Text style={styles.analyzeButtonSubtext}>
                {accessBlocked ? 'Open premium access' : 'Run this week’s proof read'}
              </Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.resultCard}>
        <View style={styles.resultHeader}>
          <View>
            <Text style={styles.resultEyebrow}>LATEST RESULT</Text>
            <Text style={styles.resultTitle}>
              {displayResult ? 'This week’s proof read' : 'Your next proof read will land here.'}
            </Text>
          </View>
          {displayResult ? (
            <View
              style={[
                styles.statusBadge,
                {
                  backgroundColor:
                    displayResult.weekly_status === 'improved'
                      ? `${colors.success}22`
                      : displayResult.weekly_status === 'regressed'
                        ? `${colors.error}22`
                        : `${colors.primary}22`,
                  borderColor:
                    displayResult.weekly_status === 'improved'
                      ? colors.success
                      : displayResult.weekly_status === 'regressed'
                        ? colors.error
                        : colors.primary,
                },
              ]}
            >
              <Text style={styles.statusBadgeText}>{displayResult.weekly_status.replace('_', ' ')}</Text>
            </View>
          ) : null}
        </View>

        {loadingLatest && !displayResult ? (
          <View style={styles.emptyResult}>
            <ActivityIndicator color={colors.primary} />
            <Text style={styles.emptyResultTitle}>Loading latest proof</Text>
            <Text style={styles.emptyResultText}>
              Pulling in your last saved weekly check-in so this screen reflects the real account state.
            </Text>
          </View>
        ) : displayResult ? (
          <>
            <View style={styles.resultSummaryCard}>
              <View style={styles.resultSummaryHeader}>
              <Text style={styles.resultSummaryLabel}>PROOF READ</Text>
                <View style={styles.resultSummaryPill}>
                  <Text style={styles.resultSummaryPillText}>
                    {Math.round(displayResult.comparison_confidence * 100)}% confidence
                  </Text>
                </View>
              </View>
              <Text style={styles.resultSummary}>
                {displayResult.qualitative_summary[0] ??
                  'A fresh weekly summary will appear here after you run the analysis.'}
              </Text>

              <View style={styles.resultMetricStrip}>
                <View style={styles.resultMetricChip}>
                  <Text style={styles.resultMetricChipLabel}>Goal proximity</Text>
                  <Text style={styles.resultMetricChipValue}>
                    {displayResult.derived_scores.goal_proximity_score.toFixed(1)}
                  </Text>
                </View>
                <View style={styles.resultMetricChip}>
                  <Text style={styles.resultMetricChipLabel}>Body fat</Text>
                  <Text style={styles.resultMetricChipValueSmall}>
                    {displayResult.estimated_ranges.body_fat_percent_min}–{displayResult.estimated_ranges.body_fat_percent_max}%
                  </Text>
                </View>
                <View style={styles.resultMetricChip}>
                  <Text style={styles.resultMetricChipLabel}>Confidence</Text>
                  <Text style={styles.resultMetricChipValue}>{Math.round(displayResult.comparison_confidence * 100)}%</Text>
                </View>
                <View style={styles.resultMetricChip}>
                  <Text style={styles.resultMetricChipLabel}>Highlights</Text>
                  <Text style={styles.resultMetricChipValue}>{regionalHighlights.length}</Text>
                </View>
              </View>
            </View>

            <View style={styles.subsectionHeader}>
              <Text style={styles.subsectionLabel}>REGIONAL NOTES</Text>
              {regionalHighlights.length > 0 ? (
                <Text style={styles.subsectionMeta}>{regionalHighlights.length} regions</Text>
              ) : null}
            </View>
            <View style={styles.highlightGrid}>
              {regionalHighlights.map((item) => (
                <View key={`${item.region}-${item.label}`} style={styles.highlightCard}>
                  <Text style={styles.highlightLabel}>{item.label}</Text>
                  <Text style={styles.highlightValue}>{item.value}</Text>
                  <Text style={styles.highlightNote}>{item.note}</Text>
                </View>
              ))}
            </View>

            <View style={styles.subsectionHeader}>
              <Text style={styles.subsectionLabel}>NEXT STEP</Text>
            </View>
            <View style={styles.resultActionRow}>
              <TouchableOpacity
                style={styles.progressButton}
                onPress={() => navigation.navigate('MainTabs', { screen: 'Progress' })}
              >
                <Text style={styles.progressButtonText}>View progress</Text>
                <Text style={styles.progressButtonHint}>Open the full trend</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryResultButton} onPress={() => setAsset(null)}>
                <Text style={styles.secondaryResultButtonText}>New photo</Text>
                <Text style={styles.secondaryResultButtonHint}>Start another read</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          <View style={styles.emptyResult}>
            <Text style={styles.emptyResultTitle}>No weekly proof yet</Text>
            <Text style={styles.emptyResultText}>
              Once you analyze a full-body photo, your weekly status, confidence, and highlight regions will show up here.
            </Text>
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
    paddingBottom: spacing.xxl,
    gap: spacing.md,
  },
  captureCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
  },
  captureHeader: {
    gap: spacing.xs,
  },
  captureHeaderCopy: {
    flex: 1,
  },
  captureEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  title: {
    ...typography.h3,
    marginBottom: spacing.xs,
    lineHeight: 34,
  },
  subtitle: {
    ...typography.body2,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 18,
  },
  statusPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    backgroundColor: colors.surfaceAlt,
  },
  statusPillText: {
    ...typography.caption,
    fontWeight: '700',
    textTransform: 'capitalize',
  },
  captureStatusPill: {
    alignSelf: 'flex-start',
    marginBottom: spacing.xs,
  },
  captureMetricGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.xs,
  },
  captureMetricCard: {
    width: '48%',
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm,
  },
  captureMetricLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  captureMetricValue: {
    ...typography.h4,
    color: colors.text,
  },
  captureMetricValueSmall: {
    ...typography.button,
    color: colors.text,
  },
  captureMetricHint: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  captureGuideBar: {
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    marginBottom: spacing.xs,
  },
  captureGuideText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  limitCard: {
    backgroundColor: `${colors.warning}14`,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: `${colors.warning}38`,
  },
  limitTitle: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  limitText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  limitButton: {
    alignSelf: 'flex-start',
    marginTop: spacing.md,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.round,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  limitButtonText: {
    ...typography.buttonSmall,
    color: colors.textOnPrimary,
  },
  errorCard: {
    backgroundColor: `${colors.error}12`,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.sm,
    borderWidth: 1,
    borderColor: `${colors.error}30`,
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
  stageCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
  },
  stageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  stageLabel: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: 2,
  },
  stageHeaderTitle: {
    ...typography.button,
    color: colors.text,
  },
  stageStatusPill: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
  },
  stageStatusPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  stageMetaRow: {
    marginBottom: spacing.sm,
  },
  stageMetaText: {
    ...typography.caption,
    color: colors.textLight,
  },
  placeholder: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 168,
    backgroundColor: colors.surface,
  },
  placeholderTitle: {
    ...typography.h5,
    marginBottom: spacing.sm,
  },
  placeholderText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 18,
  },
  previewImage: {
    width: '100%',
    height: 276,
    borderRadius: borderRadius.lg,
  },
  actionsRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    padding: spacing.sm + 2,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
  },
  primaryActionButton: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  actionButtonText: {
    ...typography.button,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  primaryActionButtonText: {
    color: colors.textOnPrimary,
  },
  actionButtonHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  primaryActionButtonHint: {
    color: colors.textOnPrimary,
  },
  analyzeButton: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    padding: spacing.sm + 2,
    alignItems: 'center',
    marginTop: spacing.xs,
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
    padding: spacing.md,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.md,
    marginBottom: spacing.sm,
  },
  resultEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  resultTitle: {
    ...typography.h4,
    color: colors.text,
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
  resultSummary: {
    ...typography.caption,
    color: colors.textSecondary,
    lineHeight: 17,
  },
  resultSummaryCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.sm + 2,
    marginBottom: spacing.xs,
    gap: spacing.xs,
  },
  resultSummaryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  resultSummaryLabel: {
    ...typography.overline,
    color: colors.primary,
  },
  resultSummaryPill: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
  },
  resultSummaryPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  resultMetricStrip: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginTop: spacing.xs,
  },
  resultMetricChip: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs + 6,
  },
  resultMetricChipLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  resultMetricChipValue: {
    ...typography.button,
    color: colors.text,
  },
  resultMetricChipValueSmall: {
    ...typography.caption,
    color: colors.text,
    fontWeight: '700',
  },
  subsectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.xs,
    marginTop: spacing.xs,
  },
  subsectionLabel: {
    ...typography.overline,
    color: colors.primary,
  },
  subsectionMeta: {
    ...typography.caption,
    color: colors.textLight,
  },
  highlightGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginBottom: spacing.xs,
  },
  highlightCard: {
    width: '48%',
    minWidth: 140,
    flexGrow: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
  },
  highlightLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    textTransform: 'uppercase',
  },
  highlightValue: {
    ...typography.h6,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  highlightNote: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 18,
  },
  progressButton: {
    flex: 1.15,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.xl,
    paddingVertical: spacing.sm + 2,
    alignItems: 'center',
  },
  progressButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  progressButtonHint: {
    ...typography.caption,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
    opacity: 0.88,
  },
  resultActionRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  secondaryResultButton: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: spacing.sm + 2,
    alignItems: 'center',
  },
  secondaryResultButtonText: {
    ...typography.button,
    color: colors.text,
  },
  secondaryResultButtonHint: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  emptyResult: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
  },
  emptyResultTitle: {
    ...typography.h5,
    marginBottom: spacing.sm,
  },
  emptyResultText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
});
