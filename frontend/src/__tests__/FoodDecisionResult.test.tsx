/**
 * Tests for FoodDecisionResult Component
 * 
 * Run with: npm test FoodDecisionResult.test.tsx
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { FoodDecisionResult } from '@/components/features/FoodDecisionResult';

// Mock data
const mockGreenResult = {
  decision: 'green' as const,
  decision_text: 'Good choice! You can eat it 😊',
  food_items: [
    {
      name: 'Grilled Chicken Breast',
      calories: 165,
      protein: 31,
      carbs: 0,
      fat: 3.6,
    },
  ],
  total_calories: 165,
  total_protein: 31,
  total_carbs: 0,
  total_fat: 3.6,
  impact: {
    calories_used_percentage: 20,
    remaining_calories: 1600,
    remaining_protein: 70,
    remaining_carbs: 200,
    remaining_fat: 50,
  },
  reasons: [
    {
      type: 'calorie' as const,
      message: 'Within appropriate calorie range',
      severity: 'info' as const,
    },
    {
      type: 'macro' as const,
      message: 'Rich in protein',
      severity: 'info' as const,
    },
  ],
  ai_advice: 'Perfect choice! High protein, low fat diet helps muscle growth.',
  current_stats: {
    consumed_calories: 400,
    consumed_protein: 30,
    consumed_carbs: 50,
    consumed_fat: 15,
    calorie_goal: 2000,
  },
  confidence: 'high',
};

const mockYellowResult = {
  ...mockGreenResult,
  decision: 'yellow' as const,
  decision_text: 'Needs a bit of caution',
  total_calories: 800,
  impact: {
    ...mockGreenResult.impact,
    calories_used_percentage: 75,
    remaining_calories: 400,
  },
  reasons: [
    {
      type: 'calorie' as const,
      message: 'Uses 75% of remaining calories',
      severity: 'warning' as const,
    },
  ],
  alternatives: [
    {
      food_id: 'salad',
      name: 'Chicken Salad',
      category: 'salads',
      calories: 350,
      protein: 30,
      carbs: 15,
      fat: 18,
      reason: 'Saves 400kcal · High protein',
    },
  ],
};

const mockRedResult = {
  ...mockGreenResult,
  decision: 'red' as const,
  decision_text: 'Better to choose a different food for now',
  total_calories: 1500,
  impact: {
    ...mockGreenResult.impact,
    calories_used_percentage: 100,
    remaining_calories: 0,
  },
  reasons: [
    {
      type: 'calorie' as const,
      message: 'Exceeds remaining calories',
      severity: 'critical' as const,
    },
    {
      type: 'allergy' as const,
      message: 'Allergy warning: peanuts',
      severity: 'critical' as const,
    },
  ],
  alternatives: [
    {
      food_id: 'chicken',
      name: 'Grilled Chicken',
      category: 'meat',
      calories: 200,
      protein: 35,
      carbs: 0,
      fat: 5,
      reason: 'Low calorie · High protein',
    },
  ],
};

describe('FoodDecisionResult Component', () => {
  const mockOnEatAnyway = jest.fn();
  const mockOnFindAlternative = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Green Decision', () => {
    it('renders green decision correctly', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      // Check for green decision title
      expect(screen.getByText(/Good choice/)).toBeInTheDocument();

      // Check food items
      expect(screen.getByText('Grilled Chicken Breast')).toBeInTheDocument();
      expect(screen.getByText(/165 kcal/)).toBeInTheDocument();

      // Check macros
      expect(screen.getByText(/31.0g/)).toBeInTheDocument(); // protein
    });

    it('displays AI advice', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/Perfect choice/)).toBeInTheDocument();
    });

    it('shows "Eat This" button for green decision', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      const eatButton = screen.getByRole('button', { name: /Eat This/ });
      expect(eatButton).toBeInTheDocument();
      expect(eatButton).not.toHaveTextContent('Anyway');
    });

    it('does not show alternatives for green decision', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.queryByText(/How About These Instead/)).not.toBeInTheDocument();
    });
  });

  describe('Yellow Decision', () => {
    it('renders yellow decision with warning', () => {
      render(
        <FoodDecisionResult
          result={mockYellowResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/Use Caution/)).toBeInTheDocument();
    });

    it('shows alternatives for yellow decision', () => {
      render(
        <FoodDecisionResult
          result={mockYellowResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/How About These Instead/)).toBeInTheDocument();
      expect(screen.getByText('Chicken Salad')).toBeInTheDocument();
    });

    it('shows "Eat Anyway" button for yellow decision', () => {
      render(
        <FoodDecisionResult
          result={mockYellowResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByRole('button', { name: /Eat Anyway/ })).toBeInTheDocument();
    });
  });

  describe('Red Decision', () => {
    it('renders red decision with critical warning', () => {
      render(
        <FoodDecisionResult
          result={mockRedResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/Think Again/)).toBeInTheDocument();
    });

    it('shows critical reasons', () => {
      render(
        <FoodDecisionResult
          result={mockRedResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/Exceeds remaining calories/)).toBeInTheDocument();
      expect(screen.getByText(/Allergy warning/)).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('calls onEatAnyway when eat button is clicked', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      const eatButton = screen.getByRole('button', { name: /Eat This/ });
      fireEvent.click(eatButton);

      expect(mockOnEatAnyway).toHaveBeenCalledTimes(1);
    });

    it('calls onFindAlternative when alternative button is clicked', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      const alternativeButton = screen.getByRole('button', { name: /Find Other Food/ });
      fireEvent.click(alternativeButton);

      expect(mockOnFindAlternative).toHaveBeenCalledTimes(1);
    });
  });

  describe('Impact Analysis', () => {
    it('displays calorie usage percentage correctly', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText('20%')).toBeInTheDocument();
    });

    it('displays remaining calories', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/1600 kcal/)).toBeInTheDocument();
    });
  });
});
