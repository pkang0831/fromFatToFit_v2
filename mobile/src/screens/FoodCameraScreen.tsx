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
import { foodApi } from '../services/api';
import { useSubscription } from '../contexts/SubscriptionContext';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

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
        ]
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

    const picker = source === 'camera'
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
      setError(err?.response?.data?.detail ?? 'Failed to analyze the photo. Try a clearer shot with the meal in frame.');
    } finally {
      setAnalyzing(false);
    }
  };

  const resetSelection = () => {
    setImage(null);
    setResult(null);
    setError(null);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Food photo scan</Text>
      <Text style={styles.subtitle}>
        Capture or upload a meal photo, review the estimate, and decide whether it belongs in your tracker.
      </Text>

      {canScan && !canScan.allowed ? (
        <View style={styles.limitCard}>
          <Text style={styles.limitTitle}>Scan limit reached</Text>
          <Text style={styles.limitText}>
            {canScan.remaining > 0
              ? `You still have ${canScan.remaining} scan${canScan.remaining === 1 ? '' : 's'} left.`
              : 'You have used all of your free food scans.'}
          </Text>
          <TouchableOpacity
            style={styles.upgradeButton}
            onPress={() => navigation.navigate('Paywall')}
          >
            <Text style={styles.upgradeButtonText}>Upgrade</Text>
          </TouchableOpacity>
        </View>
      ) : null}

      {result ? (
        <View style={styles.resultCard}>
          <View style={styles.resultHeader}>
            <View style={styles.resultBadge}>
              <Text style={styles.resultBadgeText}>{result.analysis_confidence.toUpperCase()} confidence</Text>
            </View>
            <Text style={styles.resultRemaining}>
              {result.usage_remaining === 999 ? 'Unlimited scans' : `${result.usage_remaining} scan${result.usage_remaining === 1 ? '' : 's'} left`}
            </Text>
          </View>

          <View style={styles.resultHero}>
            <Text style={styles.resultTitle}>Estimated meal total</Text>
            <Text style={styles.resultHeroValue}>{Math.round(result.total_calories)}</Text>
            <Text style={styles.resultHeroLabel}>calories</Text>
          </View>

          <View style={styles.metricGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{result.total_protein.toFixed(1)}g</Text>
              <Text style={styles.metricLabel}>protein</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{result.total_carbs.toFixed(1)}g</Text>
              <Text style={styles.metricLabel}>carbs</Text>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricValue}>{result.total_fat.toFixed(1)}g</Text>
              <Text style={styles.metricLabel}>fat</Text>
            </View>
          </View>

          <Text style={styles.sectionLabel}>What the scan saw</Text>
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
              We could not break this photo into items, but the macro estimate is still available.
            </Text>
          )}

          <View style={styles.resultActions}>
            <TouchableOpacity style={styles.primaryButton} onPress={() => navigation.goBack()}>
              <Text style={styles.primaryButtonText}>Back to tracker</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection}>
              <Text style={styles.secondaryButtonText}>Scan another photo</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <>
          {image ? (
            <View style={styles.previewCard}>
              <Image source={{ uri: image.uri }} style={styles.image} />
              <View style={styles.previewMeta}>
                <Text style={styles.previewTitle}>Ready to analyze</Text>
                <Text style={styles.previewSubtitle}>
                  {image.source === 'camera' ? 'Camera capture' : 'Library upload'} · result will stay on screen until you dismiss it.
                </Text>
              </View>
              <TouchableOpacity
                style={[styles.primaryButton, analyzing && styles.disabledButton]}
                onPress={analyzeImage}
                disabled={analyzing}
              >
                {analyzing ? (
                  <ActivityIndicator color={colors.textOnPrimary} />
                ) : (
                  <Text style={styles.primaryButtonText}>Analyze food photo</Text>
                )}
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection} disabled={analyzing}>
                <Text style={styles.secondaryButtonText}>Pick a different photo</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.placeholderCard}>
              <Text style={styles.placeholderTitle}>No photo selected</Text>
              <Text style={styles.placeholderText}>
                Take a quick photo or choose one from your library. We will show the estimate directly on this screen.
              </Text>

              <View style={styles.actionStack}>
                <TouchableOpacity
                  style={[styles.primaryButton, analyzing && styles.disabledButton]}
                  onPress={() => void chooseImage('camera')}
                  disabled={analyzing}
                >
                  <Text style={styles.primaryButtonText}>Take photo</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={styles.secondaryButton}
                  onPress={() => void chooseImage('library')}
                  disabled={analyzing}
                >
                  <Text style={styles.secondaryButtonText}>Choose from gallery</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
        </>
      )}

      {error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>Something went wrong</Text>
          <Text style={styles.errorText}>{error}</Text>
          <View style={styles.errorActions}>
            <TouchableOpacity style={styles.secondaryButton} onPress={resetSelection}>
              <Text style={styles.secondaryButtonText}>Try another photo</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.primaryButton} onPress={() => void analyzeImage()} disabled={!image || analyzing}>
              <Text style={styles.primaryButtonText}>Retry analysis</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : null}

      <View style={styles.helperCard}>
        <Text style={styles.helperTitle}>How to get a better scan</Text>
        <Text style={styles.helperText}>Use a clear meal photo, keep the plate in frame, and avoid harsh shadows or motion blur.</Text>
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
  title: {
    ...typography.h2,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
  },
  limitCard: {
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: `${colors.warning}35`,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
  },
  limitTitle: {
    ...typography.h5,
  },
  limitText: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    marginBottom: spacing.sm,
  },
  upgradeButton: {
    backgroundColor: colors.primary,
    alignSelf: 'flex-start',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.sm,
    borderRadius: borderRadius.md,
  },
  upgradeButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  placeholderCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xl,
    alignItems: 'stretch',
    gap: spacing.md,
    ...shadows.small,
  },
  placeholderTitle: {
    ...typography.h4,
    textAlign: 'center',
  },
  placeholderText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  actionStack: {
    gap: spacing.sm,
  },
  previewCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.md,
    ...shadows.small,
  },
  image: {
    width: '100%',
    height: 320,
    borderRadius: borderRadius.lg,
    backgroundColor: colors.background,
  },
  previewMeta: {
    gap: 4,
  },
  previewTitle: {
    ...typography.h4,
  },
  previewSubtitle: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  primaryButton: {
    backgroundColor: colors.primary,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  primaryButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  secondaryButton: {
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.background,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  secondaryButtonText: {
    ...typography.button,
    color: colors.text,
  },
  disabledButton: {
    opacity: 0.7,
  },
  resultCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    gap: spacing.md,
    ...shadows.small,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  resultBadge: {
    backgroundColor: `${colors.success}18`,
    borderWidth: 1,
    borderColor: `${colors.success}40`,
    paddingHorizontal: spacing.sm,
    paddingVertical: 4,
    borderRadius: 999,
  },
  resultBadgeText: {
    ...typography.caption,
    color: colors.success,
    fontWeight: '700',
  },
  resultRemaining: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  resultTitle: {
    ...typography.h4,
  },
  resultHero: {
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.lg,
    alignItems: 'center',
  },
  resultHeroValue: {
    ...typography.number,
    fontSize: 48,
    color: colors.primary,
    marginTop: spacing.xs,
  },
  resultHeroLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: 2,
  },
  metricGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  metricCard: {
    flexBasis: '31%',
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
  },
  metricValue: {
    ...typography.number,
    fontSize: 24,
    color: colors.primary,
  },
  metricLabel: {
    ...typography.body2,
    color: colors.textSecondary,
    marginTop: 2,
    textTransform: 'capitalize',
  },
  sectionLabel: {
    ...typography.body1,
    fontWeight: '700',
    marginTop: spacing.xs,
  },
  itemRow: {
    backgroundColor: colors.background,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    padding: spacing.md,
    gap: 4,
  },
  itemRowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: spacing.sm,
  },
  itemName: {
    ...typography.body1,
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
  },
  emptyText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  resultActions: {
    flexDirection: 'column',
    gap: spacing.sm,
    marginTop: spacing.xs,
  },
  errorCard: {
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: `${colors.error}30`,
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
  errorActions: {
    flexDirection: 'column',
    gap: spacing.sm,
    marginTop: spacing.md,
  },
  helperCard: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    marginTop: spacing.lg,
  },
  helperTitle: {
    ...typography.h5,
    marginBottom: spacing.xs,
  },
  helperText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
});
