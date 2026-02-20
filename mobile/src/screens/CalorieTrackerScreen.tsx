import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';
import { foodApi } from '../services/api';
import { colors, typography, spacing, borderRadius, shadows } from '../theme';

export default function CalorieTrackerScreen({ navigation }: any) {
  const [meals, setMeals] = useState<any[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [foodName, setFoodName] = useState('');
  const [calories, setCalories] = useState('');
  const [protein, setProtein] = useState('');

  useEffect(() => {
    loadTodaysMeals();
  }, []);

  const loadTodaysMeals = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const { data } = await foodApi.getDailyFood(today);
      setMeals(data.meals || []);
    } catch (error) {
      console.error('Error loading meals:', error);
    }
  };

  const handleAddFood = async () => {
    if (!foodName || !calories) {
      Alert.alert('Error', 'Please enter food name and calories');
      return;
    }

    try {
      await foodApi.logFood({
        date: new Date().toISOString().split('T')[0],
        meal_type: 'snack',
        food_name: foodName,
        calories: parseFloat(calories),
        protein: protein ? parseFloat(protein) : 0,
        carbs: 0,
        fat: 0,
      });

      setFoodName('');
      setCalories('');
      setProtein('');
      setShowAddForm(false);
      loadTodaysMeals();
      Alert.alert('Success', 'Food logged successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to log food');
    }
  };

  const totalCalories = meals.reduce((sum, meal) => sum + meal.calories, 0);
  const totalProtein = meals.reduce((sum, meal) => sum + meal.protein, 0);

  return (
    <View style={styles.container}>
      <ScrollView>
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Today's Total</Text>
          <Text style={styles.summaryCalories}>{totalCalories.toFixed(0)}</Text>
          <Text style={styles.summaryLabel}>calories</Text>
          <Text style={styles.summaryProtein}>{totalProtein.toFixed(1)}g protein</Text>
        </View>

        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => setShowAddForm(!showAddForm)}
          >
            <Text style={styles.actionButtonText}>
              {showAddForm ? 'Cancel' : '+ Add Food'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.cameraButton]}
            onPress={() => navigation.navigate('FoodCamera')}
          >
            <Text style={styles.actionButtonText}>📸 AI Scan</Text>
          </TouchableOpacity>
        </View>

        {showAddForm && (
          <View style={styles.addForm}>
            <Text style={styles.formTitle}>Add Food Manually</Text>
            <TextInput
              style={styles.input}
              placeholder="Food name"
              value={foodName}
              onChangeText={setFoodName}
            />
            <TextInput
              style={styles.input}
              placeholder="Calories"
              value={calories}
              onChangeText={setCalories}
              keyboardType="numeric"
            />
            <TextInput
              style={styles.input}
              placeholder="Protein (g) - optional"
              value={protein}
              onChangeText={setProtein}
              keyboardType="numeric"
            />
            <TouchableOpacity style={styles.submitButton} onPress={handleAddFood}>
              <Text style={styles.submitButtonText}>Log Food</Text>
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.mealsList}>
          <Text style={styles.mealsTitle}>Today's Meals</Text>
          {meals.map((meal, index) => (
            <View key={index} style={styles.mealCard}>
              <Text style={styles.mealName}>{meal.food_name}</Text>
              <View style={styles.mealStats}>
                <Text style={styles.mealCalories}>{meal.calories} cal</Text>
                <Text style={styles.mealProtein}>{meal.protein}g protein</Text>
              </View>
            </View>
          ))}
          {meals.length === 0 && (
            <Text style={styles.emptyText}>No meals logged today</Text>
          )}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  summaryCard: {
    backgroundColor: colors.primary,
    padding: spacing.xl,
    alignItems: 'center',
  },
  summaryTitle: {
    ...typography.body1,
    color: colors.textOnPrimary,
  },
  summaryCalories: {
    ...typography.number,
    fontSize: 48,
    color: colors.textOnPrimary,
    marginVertical: spacing.sm,
  },
  summaryLabel: {
    ...typography.body1,
    color: colors.textOnPrimary,
  },
  summaryProtein: {
    ...typography.body2,
    color: colors.textOnPrimary,
    marginTop: spacing.xs,
  },
  actions: {
    flexDirection: 'row',
    padding: spacing.md,
    gap: spacing.sm,
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.secondary,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
  },
  cameraButton: {
    backgroundColor: colors.primary,
  },
  actionButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  addForm: {
    backgroundColor: colors.surface,
    margin: spacing.md,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
    ...shadows.medium,
  },
  formTitle: {
    ...typography.h5,
    marginBottom: spacing.md,
  },
  input: {
    backgroundColor: colors.background,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    marginBottom: spacing.sm,
    ...typography.body1,
  },
  submitButton: {
    backgroundColor: colors.primary,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    alignItems: 'center',
    marginTop: spacing.sm,
  },
  submitButtonText: {
    ...typography.button,
    color: colors.textOnPrimary,
  },
  mealsList: {
    padding: spacing.md,
  },
  mealsTitle: {
    ...typography.h5,
    marginBottom: spacing.md,
  },
  mealCard: {
    backgroundColor: colors.surface,
    padding: spacing.md,
    borderRadius: borderRadius.md,
    marginBottom: spacing.sm,
    ...shadows.small,
  },
  mealName: {
    ...typography.body1,
    fontWeight: '600',
    marginBottom: spacing.xs,
  },
  mealStats: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  mealCalories: {
    ...typography.body2,
    color: colors.primary,
  },
  mealProtein: {
    ...typography.body2,
    color: colors.textSecondary,
  },
  emptyText: {
    ...typography.body1,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xl,
  },
});
