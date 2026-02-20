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
          <h1 className="text-3xl font-bold text-gray-800">목표 달성 추적</h1>
          <p className="text-gray-600 mt-1">
            체중과 체지방률을 기록하고 목표 달성 예상일을 확인하세요
          </p>
        </div>
        
        <div className="flex gap-3">
          <button
            onClick={() => setShowGoalModal(true)}
            className="px-4 py-2 bg-white border-2 border-emerald-600 text-emerald-600 rounded-lg hover:bg-emerald-50 transition-colors font-medium"
          >
            🎯 목표 설정
          </button>
          <button
            onClick={() => setShowWeightLogModal(true)}
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors font-medium"
          >
            ⚖️ 체중 기록
          </button>
        </div>
      </div>

      {/* Info Card */}
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 rounded-lg p-6">
        <div className="flex items-start gap-4">
          <div className="text-4xl">📊</div>
          <div>
            <h3 className="font-semibold text-emerald-800 mb-2">
              3일 Moving Average 기반 예측
            </h3>
            <p className="text-sm text-emerald-700">
              최근 3일의 체중 변화를 평균하여 일일 변화율을 계산하고, 
              현재 칼로리 deficit을 고려하여 목표 달성 예상일을 제공합니다.
            </p>
            <p className="text-xs text-emerald-600 mt-2">
              💡 Tip: 매일 같은 시간에 체중을 측정하면 더 정확한 예측이 가능합니다.
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
        title="체중 기록"
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
        title="목표 설정"
      >
        <GoalSettingForm
          onSuccess={handleGoalSuccess}
          onCancel={() => setShowGoalModal(false)}
        />
      </Modal>
    </div>
  );
}
