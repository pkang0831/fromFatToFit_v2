'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';

interface MacroBreakdown {
  carb_pct: number;
  protein_pct: number;
  fat_pct: number;
  carb_g: number;
  protein_g: number;
  fat_g: number;
  calories_check: number;
}

interface Props {
  dailyCalories: number;
  weightKg: number;
  breakdown: MacroBreakdown | null;
  onPresetSelect: (preset: string) => void;
  onCustomChange: (carb: number, protein: number, fat: number) => void;
}

const PRESETS = [
  { key: 'balanced', label: 'Balanced', desc: '40/30/30' },
  { key: 'high_protein', label: 'High Protein', desc: '30/40/30' },
  { key: 'keto', label: 'Keto', desc: '10/30/60' },
  { key: 'low_fat', label: 'Low Fat', desc: '55/25/20' },
];

const MACRO_COLORS = {
  carb: 'bg-blue-500',
  protein: 'bg-green-500',
  fat: 'bg-yellow-500',
};

export function MacroSlider({ dailyCalories, weightKg, breakdown, onPresetSelect, onCustomChange }: Props) {
  const [activePreset, setActivePreset] = useState<string>('balanced');
  const [customCarb, setCustomCarb] = useState(40);
  const [customProtein, setCustomProtein] = useState(30);
  const [customFat, setCustomFat] = useState(30);
  const [isCustom, setIsCustom] = useState(false);

  const handlePreset = (key: string) => {
    setActivePreset(key);
    setIsCustom(false);
    onPresetSelect(key);
  };

  const handleSliderChange = (macro: 'carb' | 'protein' | 'fat', value: number) => {
    let c = customCarb, p = customProtein, f = customFat;
    if (macro === 'carb') c = value;
    else if (macro === 'protein') p = value;
    else f = value;

    const total = c + p + f;
    if (total > 0) {
      c = Math.round(c / total * 100);
      p = Math.round(p / total * 100);
      f = 100 - c - p;
    }
    setCustomCarb(c);
    setCustomProtein(p);
    setCustomFat(f);
    setIsCustom(true);
    setActivePreset('');
    onCustomChange(c, p, f);
  };

  useEffect(() => {
    if (breakdown && !isCustom) {
      setCustomCarb(Math.round(breakdown.carb_pct));
      setCustomProtein(Math.round(breakdown.protein_pct));
      setCustomFat(Math.round(breakdown.fat_pct));
    }
  }, [breakdown, isCustom]);

  return (
    <div className="space-y-6">
      {/* Preset buttons */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.key}
            onClick={() => handlePreset(p.key)}
            className={`px-3 py-3 rounded-xl border-2 text-center transition-all ${
              activePreset === p.key
                ? 'border-primary bg-primary/10 text-text'
                : 'border-border bg-surface text-text-secondary hover:border-primary/30'
            }`}
          >
            <div className="text-sm font-semibold">{p.label}</div>
            <div className="text-xs text-text-light mt-0.5">C/P/F: {p.desc}</div>
          </button>
        ))}
      </div>

      {/* Visual bar */}
      <div className="h-4 rounded-full overflow-hidden flex bg-surfaceAlt">
        <div className={`${MACRO_COLORS.carb} transition-all`} style={{ width: `${customCarb}%` }} />
        <div className={`${MACRO_COLORS.protein} transition-all`} style={{ width: `${customProtein}%` }} />
        <div className={`${MACRO_COLORS.fat} transition-all`} style={{ width: `${customFat}%` }} />
      </div>

      {/* Sliders */}
      <div className="space-y-4">
        {([
          { key: 'carb' as const, label: 'Carbs', value: customCarb, color: 'accent-blue-500' },
          { key: 'protein' as const, label: 'Protein', value: customProtein, color: 'accent-green-500' },
          { key: 'fat' as const, label: 'Fat', value: customFat, color: 'accent-yellow-500' },
        ]).map((m) => (
          <div key={m.key} className="flex items-center gap-4">
            <span className="w-16 text-sm text-text-secondary">{m.label}</span>
            <input
              type="range"
              min={0}
              max={100}
              value={m.value}
              onChange={(e) => handleSliderChange(m.key, Number(e.target.value))}
              className={`flex-1 h-2 rounded-full appearance-none bg-surfaceAlt cursor-pointer ${m.color}`}
            />
            <span className="w-12 text-right font-number text-sm text-text">{m.value}%</span>
          </div>
        ))}
      </div>

      {/* Gram results */}
      {breakdown && (
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Carbs', g: breakdown.carb_g, color: 'text-blue-400' },
            { label: 'Protein', g: breakdown.protein_g, color: 'text-green-400' },
            { label: 'Fat', g: breakdown.fat_g, color: 'text-yellow-400' },
          ].map((m) => (
            <div key={m.label} className="bg-surfaceAlt rounded-xl p-3 text-center">
              <div className={`text-2xl font-bold font-number ${m.color}`}>{m.g}g</div>
              <div className="text-xs text-text-light mt-1">{m.label}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
