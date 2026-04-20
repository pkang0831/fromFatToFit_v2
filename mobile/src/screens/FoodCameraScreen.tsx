import React, { useMemo, useState } from 'react';
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
import { foodApi } from '../services/api';
import { borderRadius, colors, shadows, spacing, typography } from '../theme';

type FoodAnalysisItem = {
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  serving_size?: string | null;
};

type FoodAnalysisResult = {
  items: FoodAnalysisItem[];
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  analysis_confidence: 'low' | 'medium' | 'high' | string;
  usage_remaining: number;
};

type PickedImage = {
  uri: string;
  base64: string;
  source: 'camera' | 'library';
};

export default function FoodCameraScreen({ navigation }: any) {
  const [image, setImage] = useState<PickedImage | null>(null);
  const [result, setResult] = useState<FoodAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { checkFeatureAccess, loading: subscriptionLoading } = useSubscription();

  const canScan = useMemo(() => {
    if (subscriptionLoading) return null;
    return checkFeatureAccess('food_scan');
  }, [checkFeatureAccess, subscriptionLoading]);

  const chooseImage = async (source: 'camera' | 'library') => {
    const access = checkFeatureAccess('food_scan');
    if (!access.allowed) {
      Alert.alert(
        'Usage limit reached',
        'You have used all your free food scans. Upgrade to premium for unlimited access.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Upgrade', onPress: () => navigation.navigate('Paywall') },
        ],
      );
      return;
    }

    if (source === 'camera') {
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert('Camera access needed', 'Please allow camera access to capture a food photo.');
        return;
      }
    }

    const picker =
      source === 'camera'
        ? ImagePicker.launchCameraAsync({
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
            base64: true,
          })
        : ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 0.8,
            base64: true,
          });

    const response = await picker;
    if (!response.canceled) {
      const asset = response.assets[0];
      if (!asset.base64) {
        setError('We could not read that image. Please try another photo.');
        return;
      }

      setImage({
        uri: asset.uri,
        base64: asset.base64,
        source,
      });
      setResult(null);
      setError(null);
    }
  };

  const analyzeImage = async () => {
    if (!image?.base64) {
      setError('Pick a photo before analyzing.');
      return;
    }

    setAnalyzing(true);
    setError(null);
    try {
      const { data } = await foodApi.analyzePhoto(image.base64);
      setResult(data as FoodAnalysisResult);
    } catch (err: any) {
      console.error('Food analysis failed:', err);
      setError(
        err?.response?.data?.detail ??
          'Failed to analyze the photo. Try a clearer shot with the meal in frame.',
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const resetSelection = () => {
    setImage(null);
    setResult(null);
    setError(null);
  };

  const accessLabel =
    canScan == null ? 'Checking' : canScan.allowed ? (canScan.remaining >= 999 ? 'Unlimited' : 'Open') : 'Locked';
  const remainingLabel =
    result != null
      ? result.usage_remaining >= 999
        ? 'Unlimited'
        : `${result.usage_remaining} left`
      : canScan == null
        ? '...'
        : canScan.remaining >= 999
          ? 'Unlimited'
          : `${canScan.remaining} left`;
  const sourceLabel = image ? (image.source === 'camera' ? 'Camera' : 'Gallery') : 'Awaiting';
  const outputLabel = result ? 'Macros ready' : image ? 'Ready to scan' : 'Need one photo';
  const confidenceTone =
    result?.analysis_confidence === 'high'
      ? colors.success
      : result?.analysis_confidence === 'medium'
        ? colors.primary
        : colors.warning;

  const macroCards = result
    ? [
        { key: 'protein', label: 'Protein', value: `${result.total_protein.toFixed(1)}g` },
        { key: 'carbs', label: 'Carbs', value: `${result.total_carbs.toFixed(1)}g` },
        { key: 'fat', label: 'Fat', value: `${result.total_fat.toFixed(1)}g` },
      ]
    : [];

  const helperPills = ['Keep the plate in frame', 'Use one meal at a time', 'Avoid motion blur'];

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.heroCard}>
        <View style={styles.heroHeader}>
          <View style={styles.heroCopy}>
            <Text style={styles.eyebrow}>FOOD CAMERA</Text>
            <Text style={styles.heroTitle}>Read one meal fast.</Text>
            <Text style={styles.heroBody}>
              Capture one clear plate photo, review the estimate, and decide what belongs in your tracker.
            </Text>
          </View>
          <View style={[styles.statusPill, canScan != null && !canScan.allowed && styles.statusPillWarning]}>
            <Text style={[styles.statusPillText, canScan != null && !canScan.allowed && styles.statusPillWarningText]}>
              {canScan != null && !canScan.allowed ? 'Limit reached' : analyzing ? 'Scanning' : 'Ready'}
            </Text>
          </View>
        </View>

        <View style={styles.metricGrid}>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Access</Text>
            <Text style={styles.metricValue}>{accessLabel}</Text>
            <Text style={styles.metricHint}>food scans</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Remaining</Text>
            <Text style={styles.metricValue}>{remainingLabel}</Text>
            <Text style={styles.metricHint}>this account</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Source</Text>
            <Text style={styles.metricValue}>{sourceLabel}</Text>
            <Text style={styles.metricHint}>current stage</Text>
          </View>
          <View style={styles.metricCard}>
            <Text style={styles.metricLabel}>Output</Text>
            <Text style={styles.metricValueSmall}>{outputLabel}</Text>
            <Text style={styles.metricHint}>scan state</Text>
          </View>
        </View>
      </View>

      {canScan && !canScan.allowed ? (
        <View style={styles.bannerCard}>
          <Text style={styles.bannerTitle}>Free scans are used up.</Text>
          <Text style={styles.bannerText}>
            Upgrade when you want food scans to stay open without weekly interruption.
          </Text>
          <TouchableOpacity style={styles.bannerButton} onPress={() => navigation.navigate('Paywall')}>
            <Text style={styles.bannerButtonText}>View premium</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {result ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionEyebrow}>SCAN RESULT</Text>
          <View style={styles.resultHeader}>
            <View>
              <Text style={styles.sectionTitle}>Meal estimate</Text>
              <Text style={styles.sectionBody}>Review the macro split and decide if this belongs in today’s log.</Text>
            </View>
            <View style={[styles.resultBadge, { backgroundColor: `${confidenceTone}16`, borderColor: `${confidenceTone}55` }]}>
              <Text style={[styles.resultBadgeText, { color: confidenceTone }]}>
                {result.analysis_confidence.toUpperCase()}
              </Text>
            </View>
          </View>

          <View style={styles.resultHero}>
            <Text style={styles.resultHeroLabel}>Estimated total</Text>
            <Text style={styles.resultHeroValue}>{Math.round(result.total_calories)}</Text>
            <Text style={styles.resultHeroHint}>calories</Text>
          </View>

          <View style={styles.metricGrid}>
            {macroCards.map((card) => (
              <View key={card.key} style={styles.metricCardCompact}>
                <Text style={styles.metricValue}>{card.value}</Text>
                <Text style={styles.metricLabel}>{card.label}</Text>
              </View>
            ))}
          </View>

          <View style={styles.listSection}>
            <Text style={styles.listLabel}>What the scan saw</Text>
            {result.items.length > 0 ? (
              result.items.map((item, index) => (
                <View key={`${item.name}-${index}`} style={styles.itemRow}>
                  <View style={styles.itemRowHeader}>
                    <Text style={styles.itemName}>{item.name}</Text>
                    <Text style={styles.itemCalories}>{Math.round(item.calories)} cal</Text>
                  </View>
                  <Text style={styles.itemMeta}>
                    {item.serving_size ? `${item.serving_size} · ` : ''}
                    {item.protein.toFixed(1)}g protein · {item.carbs.toFixed(1)}g carbs · {item.fat.toFixed(1)}g fat
                  </Text>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>
                We could not split the plate into separate items, but the full macro estimate is still available.
              </Text>
            )}
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.primaryButton} onPress={() => navigation.goBack()}>
              <Text style={styles.primaryButtonText}>Back to tracker</Text>
              <Text style={styles.primaryButtonHint}>Keep today’s flow moving</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection}>
              <Text style={styles.secondaryButtonText}>Scan another</Text>
              <Text style={styles.secondaryButtonHint}>Choose a new photo</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : image ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionEyebrow}>PHOTO STAGE</Text>
          <Text style={styles.sectionTitle}>Ready to analyze</Text>
          <Text style={styles.sectionBody}>
            {image.source === 'camera' ? 'Camera capture' : 'Gallery upload'} is set. Run the scan when the framing looks clean.
          </Text>

          <Image source={{ uri: image.uri }} style={styles.image} />

          <View style={styles.pillRow}>
            <View style={styles.helperPill}>
              <Text style={styles.helperPillText}>{image.source === 'camera' ? 'Fresh capture' : 'Library upload'}</Text>
            </View>
            <View style={styles.helperPill}>
              <Text style={styles.helperPillText}>Result stays on screen</Text>
            </View>
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[styles.primaryButton, analyzing && styles.buttonDisabled]}
              onPress={analyzeImage}
              disabled={analyzing}
            >
              {analyzing ? (
                <View style={styles.inlineLoader}>
                  <ActivityIndicator color={colors.textOnPrimary} />
                  <Text style={styles.primaryButtonText}>Analyzing...</Text>
                </View>
              ) : (
                <>
                  <Text style={styles.primaryButtonText}>Analyze photo</Text>
                  <Text style={styles.primaryButtonHint}>Estimate calories + macros</Text>
                </>
              )}
            </TouchableOpacity>

            <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection} disabled={analyzing}>
              <Text style={styles.secondaryButtonText}>Pick another</Text>
              <Text style={styles.secondaryButtonHint}>Reset this stage</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionEyebrow}>PHOTO STAGE</Text>
          <Text style={styles.sectionTitle}>Start with one clear meal shot.</Text>
          <Text style={styles.sectionBody}>
            Keep one plate in frame, avoid blur, and let the scan give you a fast read before you log it.
          </Text>

          <View style={styles.placeholderStage}>
            <Text style={styles.placeholderTitle}>No photo selected</Text>
            <Text style={styles.placeholderBody}>Take a fresh picture or pull one from your gallery.</Text>
          </View>

          <View style={styles.actionRow}>
            <TouchableOpacity
              style={[styles.primaryButton, analyzing && styles.buttonDisabled]}
              onPress={() => void chooseImage('camera')}
              disabled={analyzing}
            >
              <Text style={styles.primaryButtonText}>Take photo</Text>
              <Text style={styles.primaryButtonHint}>Open camera</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.secondaryButton} onPress={() => void chooseImage('library')} disabled={analyzing}>
              <Text style={styles.secondaryButtonText}>Choose from gallery</Text>
              <Text style={styles.secondaryButtonHint}>Use an existing shot</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.pillRow}>
            {helperPills.map((pill) => (
              <View key={pill} style={styles.helperPill}>
                <Text style={styles.helperPillText}>{pill}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Scan needs another pass.</Text>
          <Text style={styles.errorText}>{error}</Text>
          <View style={styles.actionRow}>
            <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection}>
              <Text style={styles.secondaryButtonText}>Try another photo</Text>
              <Text style={styles.secondaryButtonHint}>Reset this scan</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.primaryButton, (!image || analyzing) && styles.buttonDisabled]}
              onPress={() => void analyzeImage()}
              disabled={!image || analyzing}
            >
              <Text style={styles.primaryButtonText}>Retry analysis</Text>
              <Text style={styles.primaryButtonHint}>Run the estimate again</Text>
            </TouchableOpacity>
          </View>
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
    paddingBottom: spacing.xxl,
    gap: spacing.lg,
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
    alignItems: 'flex-start',
    gap: spacing.md,
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
    ...typography.body1,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  statusPill: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  statusPillWarning: {
    backgroundColor: `${colors.warning}14`,
    borderColor: `${colors.warning}45`,
  },
  statusPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  statusPillWarningText: {
    color: colors.warning,
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
  metricCardCompact: {
    width: '31%',
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
    marginTop: spacing.xs,
  },
  metricValue: {
    ...typography.h3,
    color: colors.text,
  },
  metricValueSmall: {
    ...typography.button,
    color: colors.text,
  },
  metricHint: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  bannerCard: {
    backgroundColor: `${colors.warning}10`,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: `${colors.warning}40`,
    padding: spacing.lg,
    gap: spacing.sm,
  },
  bannerTitle: {
    ...typography.h4,
    color: colors.text,
  },
  bannerText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  bannerButton: {
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.primary,
  },
  bannerButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
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
  },
  placeholderStage: {
    marginTop: spacing.lg,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xl,
    minHeight: 180,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholderTitle: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  placeholderBody: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: borderRadius.xl,
    backgroundColor: colors.surfaceAlt,
    marginTop: spacing.lg,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  resultBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: borderRadius.round,
    borderWidth: 1,
  },
  resultBadgeText: {
    ...typography.caption,
    fontWeight: '700',
  },
  resultHero: {
    marginTop: spacing.lg,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xl,
    alignItems: 'center',
  },
  resultHeroLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
    marginBottom: spacing.xs,
  },
  resultHeroValue: {
    ...typography.number,
    fontSize: 48,
    color: colors.primary,
  },
  resultHeroHint: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  listSection: {
    marginTop: spacing.lg,
    gap: spacing.sm,
  },
  listLabel: {
    ...typography.button,
    color: colors.text,
  },
  itemRow: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
  },
  itemRowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  itemName: {
    ...typography.body1,
    color: colors.text,
    fontWeight: '700',
    flex: 1,
  },
  itemCalories: {
    ...typography.body2,
    color: colors.primary,
    fontWeight: '700',
  },
  itemMeta: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  helperPill: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.round,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  helperPillText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '700',
  },
  actionRow: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  primaryButton: {
    flex: 1.15,
    backgroundColor: colors.primary,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
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
    opacity: 0.9,
  },
  secondaryButton: {
    flex: 1,
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
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
    alignItems: 'center',
    gap: spacing.sm,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  errorCard: {
    backgroundColor: `${colors.error}10`,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: `${colors.error}35`,
    padding: spacing.lg,
  },
  errorTitle: {
    ...typography.h4,
    color: colors.text,
    marginBottom: spacing.xs,
  },
  errorText: {
    ...typography.body2,
    color: colors.textSecondary,
    lineHeight: 20,
  },
});
