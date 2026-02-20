import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Alert, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { foodApi } from '../services/api';
import { useSubscription } from '../contexts/SubscriptionContext';
import { colors, typography, spacing, borderRadius } from '../theme';

export default function FoodCameraScreen({ navigation }: any) {
  const [image, setImage] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const { checkFeatureAccess } = useSubscription();

  const pickImage = async () => {
    const { allowed, remaining } = checkFeatureAccess('food_scan');
    
    if (!allowed) {
      Alert.alert(
        'Usage Limit Reached',
        'You have used all your free food scans. Upgrade to premium for unlimited access.',
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Upgrade', onPress: () => navigation.navigate('Paywall') },
        ]
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const { allowed } = checkFeatureAccess('food_scan');
    
    if (!allowed) {
      Alert.alert('Usage Limit Reached', 'Upgrade to premium for unlimited scans');
      return;
    }

    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission needed', 'Camera permission is required');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });

    if (!result.canceled) {
      setImage(result.assets[0].uri);
    }
  };

  const analyzeImage = async () => {
    if (!image) return;

    setAnalyzing(true);
    try {
      // Convert image to base64
      const response = await fetch(image);
      const blob = await response.blob();
      const reader = new FileReader();
      
      reader.onloadend = async () => {
        const base64 = (reader.result as string).split(',')[1];
        
        try {
          const { data } = await foodApi.analyzePhoto(base64);
          
          Alert.alert(
            'Analysis Complete',
            `Total Calories: ${data.total_calories}\nProtein: ${data.total_protein}g\nRemaining scans: ${data.usage_remaining}`,
            [
              { text: 'OK', onPress: () => navigation.goBack() }
            ]
          );
        } catch (error) {
          Alert.alert('Error', 'Failed to analyze image');
        } finally {
          setAnalyzing(false);
        }
      };
      
      reader.readAsDataURL(blob);
    } catch (error) {
      Alert.alert('Error', 'Failed to process image');
      setAnalyzing(false);
    }
  };

  return (
    <View style={styles.container}>
      {image ? (
        <>
          <Image source={{ uri: image }} style={styles.image} />
          <TouchableOpacity
            style={[styles.button, styles.analyzeButton]}
            onPress={analyzeImage}
            disabled={analyzing}
          >
            <Text style={styles.buttonText}>
              {analyzing ? 'Analyzing...' : '🔍 Analyze Food'}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.button}
            onPress={() => setImage(null)}
          >
            <Text style={styles.buttonText}>Take New Photo</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={styles.title}>Analyze Food Photo</Text>
          <Text style={styles.subtitle}>AI-powered nutritional analysis</Text>
          
          <TouchableOpacity style={[styles.button, styles.cameraButton]} onPress={takePhoto}>
            <Text style={styles.buttonText}>📷 Take Photo</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.button} onPress={pickImage}>
            <Text style={styles.buttonText}>🖼️ Choose from Gallery</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    padding: spacing.lg,
    justifyContent: 'center',
  },
  title: {
    ...typography.h3,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.xl,
  },
  image: {
    width: '100%',
    height: 300,
    borderRadius: borderRadius.lg,
    marginBottom: spacing.lg,
  },
  button: {
    backgroundColor: colors.secondary,
    padding: spacing.lg,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  cameraButton: {
    backgroundColor: colors.primary,
  },
  analyzeButton: {
    backgroundColor: colors.success,
  },
  buttonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
});
