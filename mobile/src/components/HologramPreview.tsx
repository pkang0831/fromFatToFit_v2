import React, { useMemo, useState } from 'react';
import { ActivityIndicator, StyleProp, StyleSheet, Text, View, ViewStyle } from 'react-native';
import { WebView } from 'react-native-webview';

import { colors, typography } from '../theme';

const API_URL = (process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api').replace(/\/$/, '');
const VIEWER_URL = `${API_URL}/assets/human-body-preview`;

interface HologramPreviewProps {
  style?: StyleProp<ViewStyle>;
}

export default function HologramPreview({ style }: HologramPreviewProps) {
  const [loaded, setLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);

  const source = useMemo(() => ({ uri: VIEWER_URL }), []);

  return (
    <View style={[styles.container, style]}>
      <View pointerEvents="none" style={styles.ambientGlow} />
      <View pointerEvents="none" style={styles.focusHalo} />
      <View pointerEvents="none" style={styles.topScrim} />
      <View pointerEvents="none" style={styles.bottomScrim} />
      <View pointerEvents="none" style={styles.gridOverlay} />
      <View pointerEvents="none" style={styles.bottomGlow} />
      <View pointerEvents="none" style={styles.frame}>
        <View style={[styles.corner, styles.cornerTopLeft]} />
        <View style={[styles.corner, styles.cornerTopRight]} />
        <View style={[styles.corner, styles.cornerBottomLeft]} />
        <View style={[styles.corner, styles.cornerBottomRight]} />
      </View>

      <View pointerEvents="none" style={styles.chrome}>
        <View style={styles.chromePill}>
          <Text style={styles.chromePillText}>{loaded ? 'HOLOGRAM LIVE' : 'WEEKLY BODY VIEW'}</Text>
        </View>
        <View style={styles.chromeStatus}>
          <View style={[styles.chromeStatusDot, loaded && styles.chromeStatusDotLive]} />
          <Text style={styles.chromeStatusText}>{loaded ? 'Connected' : 'Syncing'}</Text>
        </View>
      </View>

      <WebView
        source={source}
        onLoadStart={() => {
          setLoaded(false);
          setHasError(false);
        }}
        onMessage={(event) => {
          try {
            const data = JSON.parse(event.nativeEvent.data);
            if (data?.type === 'loaded') {
              setLoaded(true);
              setHasError(false);
            } else if (data?.type === 'error') {
              setHasError(true);
            }
          } catch {
            // Ignore malformed messages from the viewer page.
          }
        }}
        onError={() => {
          setHasError(true);
        }}
        mixedContentMode="always"
        javaScriptEnabled
        domStorageEnabled
        scrollEnabled={false}
        overScrollMode="never"
        bounces={false}
        setSupportMultipleWindows={false}
        originWhitelist={['*']}
        style={styles.webview}
      />

      {!loaded && !hasError ? (
        <View style={styles.overlay}>
          <ActivityIndicator size="small" color={colors.secondary} />
          <Text style={styles.overlayEyebrow}>Preparing body view</Text>
          <Text style={styles.overlayTitle}>Loading the hologram</Text>
          <Text style={styles.overlayText}>Pulling in the same GLB anatomy preview used on web.</Text>
        </View>
      ) : null}

      {hasError ? (
        <View style={styles.overlay}>
          <Text style={styles.errorEyebrow}>Temporary issue</Text>
          <Text style={styles.errorTitle}>3D body view unavailable</Text>
          <Text style={styles.errorBody}>The anatomy model did not load this time. Reload Dashboard and we’ll try again.</Text>
        </View>
      ) : null}

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    borderRadius: 24,
    overflow: 'hidden',
    backgroundColor: '#0B0907',
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.08)',
  },
  ambientGlow: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'transparent',
    shadowColor: '#C9E7FF',
    shadowOpacity: 0.28,
    shadowRadius: 28,
    shadowOffset: { width: 0, height: 8 },
  },
  focusHalo: {
    position: 'absolute',
    left: '15%',
    right: '15%',
    top: '18%',
    height: '48%',
    borderRadius: 999,
    backgroundColor: 'rgba(122, 212, 255, 0.08)',
  },
  topScrim: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '26%',
    backgroundColor: 'rgba(9, 7, 5, 0.12)',
  },
  bottomScrim: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    height: '34%',
    backgroundColor: 'rgba(9, 7, 5, 0.18)',
  },
  gridOverlay: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    height: '42%',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 238, 214, 0.05)',
    backgroundColor: 'rgba(0,0,0,0)',
  },
  bottomGlow: {
    position: 'absolute',
    left: '19%',
    right: '19%',
    bottom: 16,
    height: 28,
    borderRadius: 999,
    backgroundColor: 'rgba(231, 204, 152, 0.14)',
  },
  frame: {
    ...StyleSheet.absoluteFillObject,
  },
  corner: {
    position: 'absolute',
    width: 18,
    height: 18,
    borderColor: 'rgba(255, 238, 214, 0.14)',
  },
  cornerTopLeft: {
    top: 12,
    left: 12,
    borderTopWidth: 1,
    borderLeftWidth: 1,
  },
  cornerTopRight: {
    top: 12,
    right: 12,
    borderTopWidth: 1,
    borderRightWidth: 1,
  },
  cornerBottomLeft: {
    bottom: 12,
    left: 12,
    borderBottomWidth: 1,
    borderLeftWidth: 1,
  },
  cornerBottomRight: {
    bottom: 12,
    right: 12,
    borderBottomWidth: 1,
    borderRightWidth: 1,
  },
  chrome: {
    position: 'absolute',
    top: 10,
    left: 10,
    right: 10,
    zIndex: 2,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  chromePill: {
    borderRadius: 999,
    paddingHorizontal: 9,
    paddingVertical: 5,
    backgroundColor: 'rgba(231, 204, 152, 0.14)',
    borderWidth: 1,
    borderColor: 'rgba(231, 204, 152, 0.32)',
  },
  chromePillText: {
    ...typography.overline,
    color: colors.primaryLight,
    letterSpacing: 1.2,
  },
  chromeStatus: {
    borderRadius: 999,
    paddingHorizontal: 10,
    paddingVertical: 6,
    backgroundColor: 'rgba(9, 7, 5, 0.62)',
    borderWidth: 1,
    borderColor: 'rgba(255, 238, 214, 0.08)',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  chromeStatusDot: {
    width: 6,
    height: 6,
    borderRadius: 999,
    backgroundColor: colors.textLight,
    opacity: 0.7,
  },
  chromeStatusDotLive: {
    backgroundColor: colors.secondary,
    opacity: 1,
  },
  chromeStatusText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  webview: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: 'rgba(9, 7, 5, 0.42)',
    paddingHorizontal: 24,
  },
  overlayEyebrow: {
    ...typography.overline,
    color: colors.secondaryLight,
  },
  overlayTitle: {
    ...typography.h5,
    color: colors.text,
    textAlign: 'center',
  },
  overlayText: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  errorEyebrow: {
    ...typography.overline,
    color: colors.warning,
  },
  errorTitle: {
    ...typography.h6,
    color: colors.text,
    marginBottom: 4,
  },
  errorBody: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
  },
});
