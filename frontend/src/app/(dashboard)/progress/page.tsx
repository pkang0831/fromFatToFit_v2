'use client';

import React, { useState } from 'react';
import GoalProjectionChart from '@/components/features/GoalProjectionChart';
import WeightLogForm from '@/components/features/WeightLogForm';
import GoalSettingForm from '@/components/features/GoalSettingForm';
import { Modal } from '@/components/ui/Modal';

export default function ProgressPage() {
  const [showWeightLogModal, setShowWeightLogModal] = useState(false);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleWeightLogSuccess = () => {
    setShowWeightLogModal(false);
    setRefreshKey(prev => prev + 1);
  };

  const handleGoalSuccess = () => {
    setShowGoalModal(false);
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Goal Progress Tracking</h1>
          <p className="text-gray-600 mt-1">
            Log your weight and body fat percentage to see your estimated goal date
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => setShowGoalModal(true)}
            className="px-4 py-2 bg-white border-2 border-emerald-600 text-emerald-600 rounded-lg hover:bg-emerald-50 transition-colors font-medium"
          >
            🎯 Set Goal
          </button>
          <button
            onClick={() => setShowWeightLogModal(true)}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
          >
            ⚖️ Log Weight
          </button>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-4xl">📊</div>
          <div>
            <h3 className="font-semibold text-emerald-800 mb-2">
              3-Day Moving Average Based Prediction
            </h3>
            <p className="text-sm text-emerald-700">
              Averages weight changes over the last 3 days to calculate daily rate of change, 
              and provides an estimated goal date considering your current calorie deficit.
            </p>
            <p className="text-xs text-emerald-600 mt-2">
              💡 Tip: Weighing at the same time each day enables more accurate predictions.
            </p>
          </div>
        </div>
      </div>

      {/* Goal Projection Chart */}
      <GoalProjectionChart key={refreshKey} daysHistory={30} />

      {/* Weight Log Modal */}
      <Modal
        isOpen={showWeightLogModal}
        onClose={() => setShowWeightLogModal(false)}
        title="Log Weight"
      >
        <WeightLogForm
          onSuccess={handleWeightLogSuccess}
          onCancel={() => setShowWeightLogModal(false)}
        />
      </Modal>

      {/* Goal Setting Modal */}
      <Modal
        isOpen={showGoalModal}
        onClose={() => setShowGoalModal(false)}
        title="Set Goal"
      >
        <GoalSettingForm
          onSuccess={handleGoalSuccess}
          onCancel={() => setShowGoalModal(false)}
        />
      </Modal>
    </div>
  );
}
