import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ScrollView,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { colors, typography, spacing, borderRadius } from '../theme';

export default function RegisterScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const { signUp } = useAuth();

  const handleRegister = async () => {
    if (!email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    setLoading(true);
    try {
      await signUp(email, password, fullName);
      Alert.alert('Success', 'Account created successfully!');
    } catch (error: any) {
      Alert.alert('Registration Failed', error.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Start your wellness journey today</Text>

          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Full Name (optional)"
              placeholderTextColor={colors.textSecondary}
              value={fullName}
              onChangeText={setFullName}
            />

            <TextInput
              style={styles.input}
              placeholder="Email *"
              placeholderTextColor={colors.textSecondary}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
            />

            <TextInput
              style={styles.input}
              placeholder="Password (min 8 characters) *"
              placeholderTextColor={colors.textSecondary}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
            />

            <TextInput
              style={styles.input}
              placeholder="Confirm Password *"
              placeholderTextColor={colors.textSecondary}
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              secureTextEntry
            />

            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleRegister}
              disabled={loading}
            >
              <Text style={styles.buttonText}>
                {loading ? 'Creating Account...' : 'Create Account'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.goBack()}
            >
              <Text style={styles.linkText}>
                Already have an account? <Text style={styles.linkTextBold}>Sign In</Text>
              </Text>
            </TouchableOpacity>
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
    marginBottom: spacing.xl,
  },
  form: {
    marginTop: spacing.lg,
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.md,
    ...typography.body1,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    alignItems: 'center',
    marginTop: spacing.md,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    ...typography.button,
    color: colors.textOnPrimary,
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
    ...typography.button,
    color: colors.primary,
  },
});
