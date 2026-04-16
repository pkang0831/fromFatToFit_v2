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
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

function isStrongPassword(value: string) {
  return (
    value.length >= 8 &&
    /[a-z]/.test(value) &&
    /[A-Z]/.test(value) &&
    /\d/.test(value) &&
    /[^A-Za-z0-9]/.test(value)
  );
}

export default function RegisterScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingConfirmation, setPendingConfirmation] = useState(false);
  const { signUp } = useAuth();

  const handleRegister = async () => {
    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password || !confirmPassword) {
      setErrorMessage('Fill in your email, password, and password confirmation.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match.');
      return;
    }

    if (!isStrongPassword(password)) {
      setErrorMessage('Use 8+ characters with upper and lower case letters, a number, and a symbol.');
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    try {
      const result = await signUp(trimmedEmail, password, fullName.trim() || undefined);
      if (!result.session) {
        setPendingConfirmation(true);
      }
    } catch (error: any) {
      setErrorMessage(error?.message || 'We could not create your account right now. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (pendingConfirmation) {
    return (
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <View style={styles.successContainer}>
          <View style={styles.successCard}>
            <Text style={styles.successEyebrow}>Check your inbox</Text>
            <Text style={styles.successTitle}>Account created</Text>
            <Text style={styles.successText}>
              We sent a confirmation email to <Text style={styles.successEmail}>{email.trim()}</Text>.
              Confirm it, then come back to sign in and keep your tracking history in sync.
            </Text>
            <Text style={styles.successHint}>
              If you do not see it, check spam or promotions.
            </Text>
          </View>

          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('Login')}
            activeOpacity={0.9}
          >
            <Text style={styles.buttonText}>Back to Sign In</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => {
              setPendingConfirmation(false);
              setPassword('');
              setConfirmPassword('');
            }}
            activeOpacity={0.85}
          >
            <Text style={styles.linkText}>
              Use a different email <Text style={styles.linkTextBold}>or try again</Text>
            </Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

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
            <Text style={styles.title}>Create your account</Text>
            <Text style={styles.subtitle}>Start your wellness journey and keep your proof loop on every device.</Text>
            <View style={styles.badgeRow}>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>One account</Text>
              </View>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>Protected history</Text>
              </View>
              <View style={styles.badge}>
                <Text style={styles.badgeText}>Cross-device sync</Text>
              </View>
            </View>
          </View>

          <View style={styles.card}>
            {errorMessage && (
              <View style={styles.errorCard}>
                <Text style={styles.errorTitle}>Could not create account</Text>
                <Text style={styles.errorText}>{errorMessage}</Text>
              </View>
            )}

            <View style={styles.form}>
              <TextInput
                style={styles.input}
                placeholder="Full name (optional)"
                placeholderTextColor={colors.textSecondary}
                value={fullName}
                onChangeText={setFullName}
                autoComplete="name"
                textContentType="name"
                returnKeyType="next"
              />

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
                autoComplete="new-password"
                textContentType="newPassword"
                returnKeyType="next"
              />
              <Text style={styles.passwordHint}>
                8+ chars with uppercase, lowercase, number, and symbol.
              </Text>

              <TextInput
                style={styles.input}
                placeholder="Confirm password"
                placeholderTextColor={colors.textSecondary}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry
                autoComplete="password-new"
                textContentType="newPassword"
                returnKeyType="done"
                onSubmitEditing={handleRegister}
              />

              <TouchableOpacity
                style={[styles.button, loading && styles.buttonDisabled]}
                onPress={handleRegister}
                disabled={loading}
                activeOpacity={0.9}
              >
                {loading ? (
                  <View style={styles.buttonRow}>
                    <ActivityIndicator color={colors.textOnPrimary} />
                    <Text style={styles.buttonText}>Creating account...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>Create Account</Text>
                )}
              </TouchableOpacity>

              <Text style={styles.helperText}>
                We&apos;ll keep your scan limits, profile, and progress synced across mobile and web.
              </Text>

              <TouchableOpacity
                style={styles.linkButton}
                onPress={() => navigation.goBack()}
                disabled={loading}
                activeOpacity={0.85}
              >
                <Text style={styles.linkText}>
                  Already have an account? <Text style={styles.linkTextBold}>Sign In</Text>
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
    marginBottom: spacing.xl,
  },
  title: {
    ...typography.h2,
    color: colors.primary,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: spacing.sm,
    marginTop: spacing.lg,
  },
  badge: {
    paddingHorizontal: spacing.md,
    paddingVertical: 6,
    borderRadius: borderRadius.round,
    backgroundColor: colors.surfaceAlt,
    borderWidth: 1,
    borderColor: colors.border,
  },
  badgeText: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '600',
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
  form: {
    marginTop: 0,
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
  },
  passwordHint: {
    ...typography.caption,
    color: colors.textLight,
    marginTop: -spacing.xs,
    marginBottom: spacing.md,
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
    marginTop: spacing.lg,
    lineHeight: 18,
  },
  linkButton: {
    marginTop: spacing.md,
    alignItems: 'center',
  },
  linkText: {
    ...typography.body2,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  linkTextBold: {
    ...typography.button,
    color: colors.primary,
  },
  successContainer: {
    flex: 1,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  successCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    padding: spacing.xl,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border,
    ...shadows.medium,
  },
  successEyebrow: {
    ...typography.overline,
    color: colors.primary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  successTitle: {
    ...typography.h2,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  successText: {
    ...typography.body1,
    textAlign: 'center',
    color: colors.text,
    lineHeight: 22,
  },
  successEmail: {
    ...typography.button,
    color: colors.primary,
  },
  successHint: {
    ...typography.caption,
    textAlign: 'center',
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
});
