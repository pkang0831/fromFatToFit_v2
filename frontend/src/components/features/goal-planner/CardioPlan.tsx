'use client';

import { Timer, Flame, Zap } from 'lucide-react';
import { Badge } from '@/components/ui';

interface CardioOption {
  activity: string;
  met_value: number;
  duration_minutes: number;
  calories_burned: number;
  intensity: string;
}

interface Props {
  targetCalories: number;
  options: CardioOption[];
}

const INTENSITY_BADGE: Record<string, 'success' | 'warning' | 'error' | 'default'> = {
  low: 'success',
  'low-moderate': 'success',
  moderate: 'warning',
  high: 'error',
  'very high': 'error',
};

const ACTIVITY_LABELS: Record<string, string> = {
  walking: 'Walking (Brisk)',
  jogging: 'Jogging',
  running: 'Running',
  cycling: 'Cycling',
  stationary_bike: 'Stationary Bike',
  swimming: 'Swimming Laps',
  elliptical: 'Elliptical',
  rowing: 'Rowing Machine',
  stair_climber: 'Stair Climber',
  jump_rope: 'Jump Rope',
  hiking: 'Hiking',
};

export function CardioPlan({ targetCalories, options }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <Flame className="h-4 w-4 text-orange-400" />
        Target burn: <strong className="text-text font-number">{targetCalories} kcal</strong>
      </div>

      <div className="space-y-2">
        {options.map((opt) => (
          <div
            key={opt.activity}
            className="flex items-center gap-4 bg-surfaceAlt rounded-xl px-4 py-3 hover:bg-surface transition-colors"
          >
            <div className="w-10 h-10 rounded-xl bg-surface flex items-center justify-center flex-shrink-0">
              <Timer className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-text">
                  {ACTIVITY_LABELS[opt.activity] || opt.activity}
                </span>
                <Badge variant={INTENSITY_BADGE[opt.intensity] || 'default'}>
                  {opt.intensity}
                </Badge>
              </div>
              <div className="text-xs text-text-light mt-0.5">
                MET {opt.met_value} · {opt.calories_burned} kcal actual burn
              </div>
            </div>
            <div className="text-right flex-shrink-0">
              <div className="text-xl font-bold font-number text-primary">{opt.duration_minutes}</div>
              <div className="text-xs text-text-light">minutes</div>
            </div>
          </div>
        ))}
      </div>

      {options.length === 0 && (
        <div className="text-center py-8 text-text-light text-sm">
          No cardio options available.
        </div>
      )}
    </div>
  );
}
