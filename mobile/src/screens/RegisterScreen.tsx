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
import { Ionicons } from '@expo/vector-icons';
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
  const [emailLoading, setEmailLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingConfirmation, setPendingConfirmation] = useState(false);
  const { signUp, signInWithGoogle } = useAuth();

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

    setEmailLoading(true);
    setErrorMessage(null);

    try {
      const result = await signUp(trimmedEmail, password, fullName.trim() || undefined);
      if (!result.session) {
        setPendingConfirmation(true);
      }
    } catch (error: any) {
      setErrorMessage(error?.message || 'We could not create your account right now. Please try again.');
    } finally {
      setEmailLoading(false);
    }
  };

  const handleGoogleRegister = async () => {
    setGoogleLoading(true);
    setErrorMessage(null);

    try {
      await signInWithGoogle();
    } catch (error: any) {
      setErrorMessage(error?.message || 'Google sign-up did not finish. Please try again.');
    } finally {
      setGoogleLoading(false);
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
            <Text style={styles.successEyebrow}>CHECK YOUR INBOX</Text>
            <Text style={styles.successTitle}>Account created</Text>
            <Text style={styles.successText}>
              We sent a confirmation email to <Text style={styles.successEmail}>{email.trim()}</Text>.
              Confirm it, then come back to sign in and keep your proof history in sync.
            </Text>
            <Text style={styles.successHint}>If you do not see it, check spam or promotions.</Text>
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
            <Text style={styles.eyebrow}>DEVENIRA</Text>
            <Text style={styles.title}>Create one account for mobile and web.</Text>
            <Text style={styles.subtitle}>
              Start with Google if you want the cleanest setup. Email registration stays here when you need it.
            </Text>
          </View>

          <View style={styles.card}>
            {errorMessage && (
              <View style={styles.errorCard}>
                <Text style={styles.errorTitle}>Could not create account</Text>
                <Text style={styles.errorText}>{errorMessage}</Text>
              </View>
            )}

            <View style={styles.oauthBlock}>
              <Text style={styles.blockEyebrow}>GOOGLE FIRST</Text>
              <TouchableOpacity
                style={[styles.googleButton, googleLoading && styles.buttonDisabled]}
                onPress={handleGoogleRegister}
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
                      <Text style={styles.googleButtonHint}>Fastest way to set up your account</Text>
                    </View>
                    <Ionicons name="arrow-forward" size={18} color={colors.text} />
                  </View>
                )}
              </TouchableOpacity>
            </View>

            <View style={styles.dividerRow}>
              <View style={styles.dividerLine} />
              <Text style={styles.dividerText}>OR CREATE WITH EMAIL</Text>
              <View style={styles.dividerLine} />
            </View>

            <View style={styles.formCard}>
              <Text style={styles.blockEyebrow}>EMAIL FALLBACK</Text>
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
                style={[styles.button, (emailLoading || googleLoading) && styles.buttonDisabled]}
                onPress={handleRegister}
                disabled={emailLoading || googleLoading}
                activeOpacity={0.9}
              >
                {emailLoading ? (
                  <View style={styles.buttonRow}>
                    <ActivityIndicator color={colors.textOnPrimary} />
                    <Text style={styles.buttonText}>Creating account...</Text>
                  </View>
                ) : (
                  <Text style={styles.buttonText}>Create Account</Text>
                )}
              </TouchableOpacity>

              <Text style={styles.helperText}>
                Best if you prefer a password account or need email confirmation for your setup.
              </Text>

              <TouchableOpacity
                style={styles.linkButton}
                onPress={() => navigation.goBack()}
                disabled={emailLoading || googleLoading}
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
  eyebrow: {
    ...typography.overline,
    color: colors.primaryLight,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    textAlign: 'center',
    marginBottom: spacing.sm,
    maxWidth: 320,
    alignSelf: 'center',
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    maxWidth: 340,
    alignSelf: 'center',
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
  passwordHint: {
    ...typography.caption,
    color: colors.textLight,
    marginTop: -spacing.xs,
    marginBottom: spacing.sm,
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
  successContainer: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    padding: spacing.lg,
  },
  successCard: {
    backgroundColor: colors.surface,
    borderRadius: borderRadius.xl,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.xl,
    ...shadows.medium,
  },
  successEyebrow: {
    ...typography.overline,
    color: colors.primaryDark,
    marginBottom: spacing.sm,
  },
  successTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.sm,
  },
  successText: {
    ...typography.body1,
    color: colors.textSecondary,
  },
  successEmail: {
    color: colors.text,
    fontWeight: '700',
  },
  successHint: {
    ...typography.caption,
    color: colors.textLight,
    marginTop: spacing.md,
  },
});
