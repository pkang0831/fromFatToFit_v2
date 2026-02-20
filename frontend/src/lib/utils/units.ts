/**
 * Unit conversion utilities for food portions
 */

export type WeightUnit = 'g' | 'kg' | 'oz' | 'lbs';

export interface UnitConversion {
  unit: WeightUnit;
  label: string;
  toGrams: number; // Conversion factor to grams
}

export const WEIGHT_UNITS: Record<WeightUnit, UnitConversion> = {
  g: {
    unit: 'g',
    label: 'grams (g)',
    toGrams: 1,
  },
  kg: {
    unit: 'kg',
    label: 'kilograms (kg)',
    toGrams: 1000,
  },
  oz: {
    unit: 'oz',
    label: 'ounces (oz)',
    toGrams: 28.3495,
  },
  lbs: {
    unit: 'lbs',
    label: 'pounds (lbs)',
    toGrams: 453.592,
  },
};

/**
 * Convert any weight unit to grams
 */
export function convertToGrams(amount: number, unit: WeightUnit): number {
  const conversion = WEIGHT_UNITS[unit];
  if (!conversion) {
    throw new Error(`Unknown unit: ${unit}`);
  }
  return amount * conversion.toGrams;
}

/**
 * Convert grams to any weight unit
 */
export function convertFromGrams(grams: number, targetUnit: WeightUnit): number {
  const conversion = WEIGHT_UNITS[targetUnit];
  if (!conversion) {
    throw new Error(`Unknown unit: ${targetUnit}`);
  }
  return grams / conversion.toGrams;
}

/**
 * Format weight with unit
 */
export function formatWeight(amount: number, unit: WeightUnit): string {
  const rounded = Math.round(amount * 10) / 10; // Round to 1 decimal
  return `${rounded}${unit}`;
}

/**
 * Calculate nutrition based on amount and base nutrition per 100g
 */
export interface NutritionPer100g {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
}

export interface CalculatedNutrition extends NutritionPer100g {
  amount_grams: number;
}

export function calculateNutrition(
  nutritionPer100g: NutritionPer100g,
  amount: number,
  unit: WeightUnit
): CalculatedNutrition {
  const grams = convertToGrams(amount, unit);
  const multiplier = grams / 100;

  return {
    amount_grams: grams,
    calories: Math.round(nutritionPer100g.calories * multiplier * 10) / 10,
    protein: Math.round(nutritionPer100g.protein * multiplier * 10) / 10,
    carbs: Math.round(nutritionPer100g.carbs * multiplier * 10) / 10,
    fat: Math.round(nutritionPer100g.fat * multiplier * 10) / 10,
  };
}

/**
 * Get list of available weight units for dropdown
 */
export function getWeightUnitOptions() {
  return Object.values(WEIGHT_UNITS).map((unit) => ({
    value: unit.unit,
    label: unit.label,
  }));
}
