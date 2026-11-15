'use client';

import { Dumbbell, Clock, RotateCcw } from 'lucide-react';
import { Badge } from '@/components/ui';

interface ExerciseDetail {
  name: string;
  muscle_group: string;
  equipment: string;
  exercise_type: 'compound' | 'isolation';
  sets: number;
  reps_min: number;
  reps_max: number;
  rest_seconds: number;
  tempo?: string;
  notes?: string;
}

interface WorkoutDay {
  day_label: string;
  focus: string;
  exercises: ExerciseDetail[];
  estimated_duration_min: number;
}

interface Props {
  splitType: string;
  sessionsPerWeek: number;
  days: WorkoutDay[];
  progressionScheme: string;
  deloadNote: string;
}

const MUSCLE_COLORS: Record<string, string> = {
  legs: 'bg-purple-500/20 text-purple-300',
  chest: 'bg-red-500/20 text-red-300',
  back: 'bg-blue-500/20 text-blue-300',
  shoulders: 'bg-orange-500/20 text-orange-300',
  arms: 'bg-green-500/20 text-green-300',
  core: 'bg-yellow-500/20 text-yellow-300',
};

export function ExerciseRoutine({ splitType, sessionsPerWeek, days, progressionScheme, deloadNote }: Props) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 flex-wrap">
        <Badge variant="premium">{splitType}</Badge>
        <span className="text-sm text-text-secondary">{sessionsPerWeek}x per week</span>
      </div>

      {/* Days */}
      {days.map((day, di) => (
        <div key={di} className="bg-surfaceAlt rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-border/50 flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-text">{day.day_label}</h4>
              <p className="text-xs text-text-light">{day.focus}</p>
            </div>
            <div className="flex items-center gap-1 text-xs text-text-light">
              <Clock className="h-3.5 w-3.5" />
              ~{day.estimated_duration_min} min
            </div>
          </div>
          <div className="divide-y divide-border/30">
            {day.exercises.map((ex, ei) => (
              <div key={ei} className="px-4 py-3 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-surface flex items-center justify-center flex-shrink-0">
                  <Dumbbell className="h-4 w-4 text-text-light" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-text">{ex.name}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
                      MUSCLE_COLORS[ex.muscle_group] || 'bg-surfaceAlt text-text-light'
                    }`}>
                      {ex.muscle_group}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-text-light mt-0.5">
                    <span className="font-number">{ex.sets} × {ex.reps_min}-{ex.reps_max}</span>
                    <span>{ex.equipment}</span>
                    <span className="flex items-center gap-0.5">
                      <RotateCcw className="h-3 w-3" /> {ex.rest_seconds}s rest
                    </span>
                    {ex.tempo && <span>Tempo: {ex.tempo}</span>}
                  </div>
                  {ex.notes && <p className="text-xs text-text-light mt-0.5 italic">{ex.notes}</p>}
                </div>
                <Badge variant={ex.exercise_type === 'compound' ? 'success' : 'default'}>
                  {ex.exercise_type}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Progression & Deload */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-surfaceAlt rounded-xl p-4">
          <h4 className="text-xs font-semibold text-text-secondary uppercase mb-2">Progression</h4>
          <p className="text-sm text-text-light leading-relaxed">{progressionScheme}</p>
        </div>
        <div className="bg-surfaceAlt rounded-xl p-4">
          <h4 className="text-xs font-semibold text-text-secondary uppercase mb-2">Deload</h4>
          <p className="text-sm text-text-light leading-relaxed">{deloadNote}</p>
        </div>
      </div>
    </div>
  );
}
