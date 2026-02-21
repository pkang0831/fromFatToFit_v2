'use client';

import React, { useState } from 'react';
import { weightApi } from '@/lib/api/services';
import type { WeightLogCreate } from '@/types/api';

interface WeightLogFormProps {
  onSuccess?: () => void;
  onCancel?: () => void;
}

const WeightLogForm: React.FC<WeightLogFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState<WeightLogCreate>({
    date: new Date().toISOString().split('T')[0],
    weight_kg: 0,
    body_fat_percentage: undefined,
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.weight_kg <= 0) {
      setError('Please enter your weight');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await weightApi.createLog(formData);
      onSuccess?.();
    } catch (err: any) {
      console.error('Error logging weight:', err);
      setError(err.response?.data?.detail || 'Failed to log weight');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Date
        </label>
        <input
          type="date"
          value={formData.date}
          onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Weight (kg) *
        </label>
        <input
          type="number"
          step="0.1"
          value={formData.weight_kg || ''}
          onChange={(e) => setFormData({ ...formData, weight_kg: parseFloat(e.target.value) || 0 })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="70.5"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Body Fat % (optional)
        </label>
        <input
          type="number"
          step="0.1"
          value={formData.body_fat_percentage || ''}
          onChange={(e) => setFormData({ 
            ...formData, 
            body_fat_percentage: e.target.value ? parseFloat(e.target.value) : undefined 
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          placeholder="15.5"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Notes (optional)
        </label>
        <textarea
          value={formData.notes || ''}
          onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          rows={3}
          placeholder="Record today's condition or notes..."
        />
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
          {loading ? 'Saving...' : 'Save'}
        </button>
      </div>
    </form>
  );
};

export default WeightLogForm;
