import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  ActivityIndicator,
  Image,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { signIn, signInWithGoogle } = useAuth();

  const handleLogin = async () => {
    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password) {
      setErrorMessage('Enter your email and password to continue.');
      return;
    }

    setEmailLoading(true);
    setErrorMessage(null);

    try {
      await signIn(trimmedEmail, password);
    } catch (error: any) {
      setErrorMessage(error?.message || 'We could not sign you in right now. Please try again.');
    } finally {
      setEmailLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setGoogleLoading(true);
    setErrorMessage(null);

    try {
      await signInWithGoogle();
    } catch (error: any) {
      setErrorMessage(error?.message || 'Google sign-in did not finish. Please try again.');
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        <View style={styles.content}>
          <View style={styles.hero}>
            <Text style={styles.eyebrow}>DEVENIRA</Text>
            <Image source={require('../../assets/icon.png')} style={styles.logo} />
            <Text style={styles.title}>Continue your weekly proof loop.</Text>
            <Text style={styles.subtitle}>
              Google first, email as fallback. Use the same account you use on web so your scans,
              progress, and premium access stay in one place.
            </Text>
          </View>

          <View style={styles.card}>
            {errorMessage && (
              <View style={styles.errorCard}>
                <Text style={styles.errorTitle}>Sign in needs attention</Text>
                <Text style={styles.errorText}>{errorMessage}</Text>
              </View>
            )}

            <View style={styles.oauthBlock}>
              <Text style={styles.blockEyebrow}>RECOMMENDED</Text>
              <TouchableOpacity
                style={[styles.googleButton, googleLoading && styles.buttonDisabled]}
                onPress={handleGoogleLogin}
                disabled={googleLoading || emailLoading}
                activeOpacity={0.92}
              >
                {googleLoading ? (
                  <View style={styles.buttonRow}>
                    <ActivityIndicator color={colors.text} />
                    <Text style={styles.googleButtonText}>Opening Google…</Text>
                  </View>
                ) : (
                  <View style={styles.googleButtonContent}>
                    <View style={styles.googleIconWrap}>
                      <Ionicons name="logo-google" size={18} color={colors.textOnPrimary} />
                    </View>
                    <View style={styles.googleCopy}>
                      <Text style={styles.googleButtonText}>Continue with Google</Text>
                      <Text style={styles.googleButtonHint}>Fastest way back into your proof history</Text>
                    </View>
                    <Ionicons name="arrow-forward" size={18} color={colors.text} />
                  </View>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.dividerRow}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>OR USE EMAIL</Text>
              <View style={styles.dividerLine} />
            </View>

            <View style={styles.formCard}>
              <Text style={styles.blockEyebrow}>EMAIL FALLBACK</Text>
              <TextInput
                style={styles.input}
                placeholder="Email"
                placeholderTextColor={colors.textSecondary}
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                autoComplete="email"
                keyboardType="email-address"
                textContentType="emailAddress"
                returnKeyType="next"
              />

              <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor={colors.textSecondary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoComplete="password"
                textContentType="password"
                returnKeyType="done"
                onSubmitEditing={handleLogin}
              />

              <TouchableOpacity
                style={[styles.button, (emailLoading || googleLoading) && styles.buttonDisabled]}
                onPress={handleLogin}
                disabled={emailLoading || googleLoading}
                activeOpacity={0.9}
              >
                {emailLoading ? (
                  <View style={styles.buttonRow}>
                    <ActivityIndicator color={colors.textOnPrimary} />
                    <Text style={styles.buttonText}>Signing in...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>Sign In with Email</Text>
                )}
              </TouchableOpacity>

              <Text style={styles.helperText}>
                Best for existing password accounts or if Google is unavailable on this device.
              </Text>

              <TouchableOpacity
                style={styles.linkButton}
                onPress={() => navigation.navigate('Register')}
                disabled={emailLoading || googleLoading}
                activeOpacity={0.85}
              >
                <Text style={styles.linkText}>
                  Don&apos;t have an account yet? <Text style={styles.linkTextBold}>Create one</Text>
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  hero: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  eyebrow: {
    ...typography.overline,
    color: colors.primaryLight,
    marginBottom: spacing.sm,
  },
  logo: {
    width: 72,
    height: 72,
    marginBottom: spacing.lg,
    borderRadius: 20,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.sm,
    maxWidth: 320,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    maxWidth: 340,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.lg,
    ...shadows.medium,
  },
  errorCard: {
    backgroundColor: `${colors.error}14`,
    borderWidth: 1,
    borderColor: `${colors.error}40`,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
  },
  errorTitle: {
    ...typography.button,
    color: colors.error,
    marginBottom: spacing.xs,
  },
  errorText: {
    ...typography.body2,
    color: colors.text,
  },
  oauthBlock: {
    gap: spacing.md,
  },
  blockEyebrow: {
    ...typography.overline,
    color: colors.textLight,
    marginBottom: spacing.xs,
  },
  googleButton: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surfaceAlt,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  googleButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  googleIconWrap: {
    width: 40,
    height: 40,
    borderRadius: 14,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  googleCopy: {
    flex: 1,
  },
  googleButtonText: {
    ...typography.button,
    color: colors.text,
  },
  googleButtonHint: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    marginVertical: spacing.lg,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: colors.border,
  },
  dividerText: {
    ...typography.overline,
    color: colors.textLight,
  },
  formCard: {
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: colors.borderLight,
    backgroundColor: colors.background,
    padding: spacing.md,
  },
  input: {
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
    ...typography.body1,
    color: colors.text,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.md,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  buttonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  helperText: {
    ...typography.caption,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.md,
  },
  linkButton: {
    marginTop: spacing.lg,
    alignItems: 'center',
  },
  linkText: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  linkTextBold: {
    color: colors.primary,
    fontWeight: '700',
  },
});
