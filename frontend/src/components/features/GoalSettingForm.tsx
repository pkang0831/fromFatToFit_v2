'use client';

import React, { useState } from 'react';
import { weightApi, authApi } from '@/lib/api/services';
import type { GoalUpdate } from '@/types/api';

interface GoalSettingFormProps {
  currentTargetWeight?: number;
  currentTargetBodyFat?: number;
  onSuccess?: () => void;
  onCancel?: () => void;
}

const GoalSettingForm: React.FC<GoalSettingFormProps> = ({
  currentTargetWeight,
  currentTargetBodyFat,
  onSuccess,
  onCancel
}) => {
  const [formData, setFormData] = useState<GoalUpdate>({
    target_weight_kg: currentTargetWeight,
    target_body_fat_percentage: currentTargetBodyFat
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.target_weight_kg && !formData.target_body_fat_percentage) {
      setError('Please set at least one goal');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await weightApi.updateGoals(formData);
      onSuccess?.();
    } catch (err: any) {
      console.error('Error updating goals:', err);
      setError(err.response?.data?.detail || 'Failed to set goal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Target Weight (kg)
        </label>
        <input
          type="number"
          step="0.1"
          value={formData.target_weight_kg || ''}
          onChange={(e) => setFormData({ 
            ...formData, 
            target_weight_kg: e.target.value ? parseFloat(e.target.value) : undefined 
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="65.0"
        />
        <p className="text-xs text-gray-500 mt-1">
          Enter your target weight (e.g., 65kg)
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Target Body Fat % (optional)
        </label>
        <input
          type="number"
          step="0.1"
          value={formData.target_body_fat_percentage || ''}
          onChange={(e) => setFormData({ 
            ...formData, 
            target_body_fat_percentage: e.target.value ? parseFloat(e.target.value) : undefined 
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="12.0"
        />
        <p className="text-xs text-gray-500 mt-1">
          Enter your target body fat % (e.g., 12%)
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="flex gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          className="flex-1 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Saving...' : 'Set Goal'}
        </button>
      </div>
    </form>
  );
};

export default GoalSettingForm;
