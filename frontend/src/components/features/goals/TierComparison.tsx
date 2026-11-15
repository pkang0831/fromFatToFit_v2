'use client';

import { Card, CardContent, Badge } from '@/components/ui';

interface MonthMilestone {
  month: number;
  projected_weight_kg: number;
  projected_bf_pct: number;
  fat_lost_kg: number;
}

interface TierInfo {
  deficit_or_surplus: number;
  daily_calories: number;
  weekly_change_kg: number;
  weeks_to_goal: number;
  monthly_milestones: MonthMilestone[];
  safety_note: string;
}

interface Props {
  tiers: TierInfo[];
  direction: 'deficit' | 'surplus';
  tdee: number;
  bmr: number;
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

const TIER_COLORS = [
  'border-green-500/40 hover:border-green-400',
  'border-blue-500/40 hover:border-blue-400',
  'border-yellow-500/40 hover:border-yellow-400',
  'border-red-500/40 hover:border-red-400',
];

const TIER_LABELS = ['Conservative', 'Moderate', 'Aggressive', 'Very Aggressive'];

export function TierComparison({ tiers, direction, tdee, bmr, selectedIndex, onSelect }: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4 text-sm text-text-secondary">
        <span>TDEE: <strong className="text-text font-number">{tdee}</strong> kcal</span>
        <span>BMR: <strong className="text-text font-number">{bmr}</strong> kcal</span>
        <Badge variant={direction === 'deficit' ? 'warning' : 'success'}>
          {direction === 'deficit' ? 'Fat Loss' : 'Weight Gain'}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {tiers.map((tier, i) => {
          const isSelected = selectedIndex === i;
          return (
            <button
              key={i}
              onClick={() => onSelect(i)}
              className={`text-left transition-all duration-200 rounded-xl border-2 p-4 ${
                isSelected
                  ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                  : `border-border bg-surface ${TIER_COLORS[i]}`
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-text-light">
                  {TIER_LABELS[i]}
                </span>
                <Badge variant={i < 2 ? 'success' : i === 2 ? 'warning' : 'error'}>
                  {Math.abs(tier.deficit_or_surplus)} cal {direction}
                </Badge>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-text-secondary text-sm">Daily calories</span>
                  <span className="font-number font-bold text-text">{tier.daily_calories} kcal</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary text-sm">Weekly change</span>
                  <span className="font-number font-medium text-text">
                    {tier.weekly_change_kg > 0 ? '+' : ''}{tier.weekly_change_kg} kg
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-secondary text-sm">Weeks to goal</span>
                  <span className="font-number font-bold text-primary">{tier.weeks_to_goal} weeks</span>
                </div>
              </div>

              {tier.safety_note && (
                <p className="mt-3 text-xs text-text-light leading-relaxed">{tier.safety_note}</p>
              )}

              {isSelected && tier.monthly_milestones.length > 0 && (
                <div className="mt-4 pt-3 border-t border-border">
                  <p className="text-xs font-semibold text-text-secondary mb-2">Monthly Projection</p>
                  <div className="space-y-1">
                    {tier.monthly_milestones.slice(0, 4).map((m) => (
                      <div key={m.month} className="flex justify-between text-xs">
                        <span className="text-text-light">Month {m.month}</span>
                        <span className="font-number text-text-secondary">
                          {m.projected_weight_kg} kg · {m.projected_bf_pct}% BF · -{m.fat_lost_kg} kg fat
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
