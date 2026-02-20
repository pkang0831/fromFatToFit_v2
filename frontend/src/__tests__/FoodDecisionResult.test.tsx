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
  decision_text: '좋은 선택이에요! 드셔도 됩니다 😊',
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
      message: '적절한 칼로리 범위입니다',
      severity: 'info' as const,
    },
    {
      type: 'macro' as const,
      message: '단백질이 풍부합니다',
      severity: 'info' as const,
    },
  ],
  ai_advice: '완벽한 선택입니다! 고단백 저지방 식단으로 근육 성장에 도움이 됩니다.',
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
  decision_text: '조금 주의가 필요해요',
  total_calories: 800,
  impact: {
    ...mockGreenResult.impact,
    calories_used_percentage: 75,
    remaining_calories: 400,
  },
  reasons: [
    {
      type: 'calorie' as const,
      message: '남은 칼로리의 75%를 사용합니다',
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
      reason: '400kcal 절약 · 고단백',
    },
  ],
};

const mockRedResult = {
  ...mockGreenResult,
  decision: 'red' as const,
  decision_text: '지금은 다른 음식을 선택하는 게 좋겠어요',
  total_calories: 1500,
  impact: {
    ...mockGreenResult.impact,
    calories_used_percentage: 100,
    remaining_calories: 0,
  },
  reasons: [
    {
      type: 'calorie' as const,
      message: '남은 칼로리를 초과합니다',
      severity: 'critical' as const,
    },
    {
      type: 'allergy' as const,
      message: '알레르기 경고: peanuts',
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
      reason: '저칼로리 · 고단백',
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
      expect(screen.getByText(/좋은 선택이에요/)).toBeInTheDocument();

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

      expect(screen.getByText(/완벽한 선택입니다/)).toBeInTheDocument();
    });

    it('shows "먹기" button for green decision', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      const eatButton = screen.getByRole('button', { name: /먹기/ });
      expect(eatButton).toBeInTheDocument();
      expect(eatButton).not.toHaveTextContent('그래도');
    });

    it('does not show alternatives for green decision', () => {
      render(
        <FoodDecisionResult
          result={mockGreenResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.queryByText(/대신 이건 어때요/)).not.toBeInTheDocument();
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

      expect(screen.getByText(/주의하세요/)).toBeInTheDocument();
    });

    it('shows alternatives for yellow decision', () => {
      render(
        <FoodDecisionResult
          result={mockYellowResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/대신 이건 어때요/)).toBeInTheDocument();
      expect(screen.getByText('Chicken Salad')).toBeInTheDocument();
    });

    it('shows "그래도 먹기" button for yellow decision', () => {
      render(
        <FoodDecisionResult
          result={mockYellowResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByRole('button', { name: /그래도 먹기/ })).toBeInTheDocument();
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

      expect(screen.getByText(/다시 생각해보세요/)).toBeInTheDocument();
    });

    it('shows critical reasons', () => {
      render(
        <FoodDecisionResult
          result={mockRedResult}
          onEatAnyway={mockOnEatAnyway}
          onFindAlternative={mockOnFindAlternative}
        />
      );

      expect(screen.getByText(/남은 칼로리를 초과합니다/)).toBeInTheDocument();
      expect(screen.getByText(/알레르기 경고/)).toBeInTheDocument();
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

      const eatButton = screen.getByRole('button', { name: /먹기/ });
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

      const alternativeButton = screen.getByRole('button', { name: /다른 음식 찾기/ });
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
