'use client';

import { useState } from 'react';
import Image from 'next/image';
import {
  ChevronDown, ChevronUp,
  Utensils, Dumbbell, AlertTriangle, Info,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ShareButtons } from '@/components/ui/ShareButtons';
import type { TransformationJourneyResponse } from '@/types/api';

const MODE_LABELS: Record<string, string> = {
  cut: 'Fat Loss',
  recomp: 'Body Recomposition',
  lean_bulk: 'Lean Bulk',
  mass_gain: 'Weight Gain',
  unsupported: 'Unsupported',
};

const MODE_COLORS: Record<string, string> = {
  cut: 'bg-red-500/20 text-red-300 border-red-500/30',
  recomp: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  lean_bulk: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  mass_gain: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  unsupported: 'bg-gray-500/20 text-gray-300 border-gray-500/30',
};

interface Props {
  result: TransformationJourneyResponse;
  originalImage: string;
  onReset: () => void;
}

export function JourneyResult({ result, originalImage, onReset }: Props) {
  const [showNutrition, setShowNutrition] = useState(false);
  const [showWorkout, setShowWorkout] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const stages = result.stages;
  const finalStage = stages[stages.length - 1];
  const afterImage = finalStage?.image_url;

  return (
    <div className="space-y-6">
      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="p-3 bg-amber-900/20 border border-amber-700/40 rounded-lg space-y-1">
          {result.warnings.map((w, i) => (
            <p key={i} className="text-sm text-amber-200 flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
              {w}
            </p>
          ))}
        </div>
      )}

      {/* Plan summary */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${MODE_COLORS[result.mode] || MODE_COLORS.unsupported}`}>
          {MODE_LABELS[result.mode] || result.mode}
        </span>
        <span className="text-sm text-text-secondary">
          {result.current_bf.toFixed(1)}% → {result.target_bf.toFixed(1)}% body fat
        </span>
        <span className="text-sm text-text-secondary">
          {result.total_weeks} weeks
        </span>
      </div>

      {/* Before / After comparison */}
      <div className="space-y-3">
        <h3 className="font-semibold text-text">Before &amp; After</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-2">
            <p className="text-xs font-medium text-text-secondary text-center">
              Now — {result.current_bf.toFixed(1)}% BF
            </p>
            <Image
              src={originalImage}
              alt="Before"
              width={400}
              height={600}
              className="w-full rounded-lg object-contain max-h-[32rem]"
              unoptimized
            />
          </div>
          <div className="space-y-2">
            <p className="text-xs font-medium text-text-secondary text-center">
              Goal — {result.target_bf.toFixed(1)}% BF
              {result.total_weeks > 0 && ` (${result.total_weeks} wk)`}
            </p>
            {afterImage ? (
              <Image
                src={afterImage}
                alt="After"
                width={400}
                height={600}
                className="w-full rounded-lg object-contain max-h-[32rem]"
                unoptimized
              />
            ) : (
              <div className="w-full aspect-[3/4] bg-surfaceAlt rounded-lg flex items-center justify-center text-text-light text-sm">
                Image unavailable
              </div>
            )}
          </div>
        </div>
        {afterImage && (
          <ShareButtons imageUrl={afterImage} />
        )}
      </div>

      {/* Body composition details */}
      {finalStage && (
        <div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-text transition-colors"
          >
            Body composition details
            {showDetails ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
          {showDetails && (
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-text-secondary">
              {Object.entries(finalStage.body_state).map(([key, val]) => {
                if (key === 'overall') return null;
                return (
                  <div key={key} className="p-2 bg-surfaceAlt rounded-lg">
                    <span className="font-medium capitalize text-text">{key}: </span>
                    {val}
                  </div>
                );
              })}
              {finalStage.weight_kg != null && (
                <div className="p-2 bg-surfaceAlt rounded-lg col-span-2">
                  <span className="font-medium text-text">Est. weight: </span>
                  {finalStage.weight_kg} kg
                  {finalStage.fat_mass_delta_kg !== 0 && (
                    <span className="ml-2 text-text-light">
                      (fat {finalStage.fat_mass_delta_kg > 0 ? '+' : ''}{finalStage.fat_mass_delta_kg.toFixed(1)} kg
                      {finalStage.lean_mass_delta_kg !== 0 &&
                        `, lean ${finalStage.lean_mass_delta_kg > 0 ? '+' : ''}${finalStage.lean_mass_delta_kg.toFixed(1)} kg`
                      })
                    </span>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-surfaceAlt rounded-lg text-center">
          <p className="text-xs text-text-secondary">Mode</p>
          <p className="text-lg font-bold text-text">{MODE_LABELS[result.mode] || result.mode}</p>
        </div>
        <div className="p-3 bg-surfaceAlt rounded-lg text-center">
          <p className="text-xs text-text-secondary">BF Change</p>
          <p className="text-lg font-bold text-text">
            {result.current_bf.toFixed(1)}% → {result.target_bf.toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-surfaceAlt rounded-lg text-center">
          <p className="text-xs text-text-secondary">Timeline</p>
          <p className="text-lg font-bold text-text">{result.total_weeks} weeks</p>
        </div>
      </div>

      {/* Nutrition plan */}
      <div className="border border-border rounded-xl overflow-hidden">
        <button
          onClick={() => setShowNutrition(!showNutrition)}
          className="w-full flex items-center justify-between p-4 bg-surfaceAlt hover:bg-surfaceAlt/80 transition-colors"
        >
          <span className="flex items-center gap-2 font-semibold text-text">
            <Utensils className="h-5 w-5 text-primary" />
            Nutrition Plan
          </span>
          {showNutrition ? <ChevronUp className="h-5 w-5 text-text-secondary" /> : <ChevronDown className="h-5 w-5 text-text-secondary" />}
        </button>
        {showNutrition && (
          <div className="p-4 space-y-4 text-sm text-text-secondary">
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-surface rounded-lg">
                <p className="text-xs text-text-light">Daily Calories</p>
                <p className="text-lg font-bold text-text">{result.nutrition.daily_calories} kcal</p>
              </div>
              <div className="p-3 bg-surface rounded-lg">
                <p className="text-xs text-text-light">Protein</p>
                <p className="text-lg font-bold text-text">{result.nutrition.protein_g} g</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-surface rounded-lg">
                <p className="text-xs text-text-light">Carbs</p>
                <p className="font-semibold text-text">{result.nutrition.carbs_g_min}–{result.nutrition.carbs_g_max} g</p>
              </div>
              <div className="p-3 bg-surface rounded-lg">
                <p className="text-xs text-text-light">Fat</p>
                <p className="font-semibold text-text">{result.nutrition.fat_g_min}–{result.nutrition.fat_g_max} g</p>
              </div>
            </div>

            <div>
              <p className="font-semibold text-text mb-2">Meal Structure</p>
              <ul className="space-y-1 list-disc list-inside text-xs">
                {result.nutrition.meal_structure.map((m, i) => <li key={i}>{m}</li>)}
              </ul>
            </div>

            <p><strong className="text-text">Weekly adjustment:</strong> {result.nutrition.weekly_adjustment}</p>
            <p><strong className="text-text">Check-in cadence:</strong> {result.nutrition.checkin_cadence}</p>

            {Object.keys(result.nutrition.stage_notes).length > 0 && (
              <div>
                <p className="font-semibold text-text mb-1">Stage Notes</p>
                <ul className="space-y-1">
                  {Object.entries(result.nutrition.stage_notes).map(([stage, note]) => (
                    <li key={stage} className="text-xs">
                      <span className="font-medium text-text">Stage {stage}:</span> {note}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.nutrition.assumptions.length > 0 && (
              <div className="p-2 bg-surface rounded-lg">
                <p className="text-xs text-text-light font-medium mb-1">Assumptions</p>
                <ul className="space-y-0.5 text-xs">
                  {result.nutrition.assumptions.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </div>
            )}

            <p className="text-xs text-text-light italic">{result.nutrition.disclaimer}</p>
          </div>
        )}
      </div>

      {/* Workout plan */}
      <div className="border border-border rounded-xl overflow-hidden">
        <button
          onClick={() => setShowWorkout(!showWorkout)}
          className="w-full flex items-center justify-between p-4 bg-surfaceAlt hover:bg-surfaceAlt/80 transition-colors"
        >
          <span className="flex items-center gap-2 font-semibold text-text">
            <Dumbbell className="h-5 w-5 text-primary" />
            Workout Plan
          </span>
          {showWorkout ? <ChevronUp className="h-5 w-5 text-text-secondary" /> : <ChevronDown className="h-5 w-5 text-text-secondary" />}
        </button>
        {showWorkout && (
          <div className="p-4 space-y-4 text-sm text-text-secondary">
            <div className="flex items-center gap-3">
              <Badge variant="info">{result.workout.split_type}</Badge>
              <span>{result.workout.sessions_per_week}x / week</span>
            </div>

            <div className="space-y-2">
              <p className="font-semibold text-text">Exercises</p>
              {result.workout.exercises.map((ex, i) => (
                <div key={i} className="p-2 bg-surface rounded-lg flex items-center gap-2 text-xs">
                  <span className="font-medium text-text">{ex.name}</span>
                  <span className="text-text-light">— {ex.muscle_group}</span>
                  <Badge variant="default" className="text-[10px] ml-auto">{ex.type}</Badge>
                </div>
              ))}
            </div>

            <p><strong className="text-text">Sets & Reps:</strong> {result.workout.sets_reps_guidance}</p>
            <p><strong className="text-text">Progression:</strong> {result.workout.progression_scheme}</p>
            <p><strong className="text-text">Cardio:</strong> {result.workout.cardio_guidance}</p>
            <p><strong className="text-text">Recovery:</strong> {result.workout.recovery_notes}</p>
            <p><strong className="text-text">Deload:</strong> {result.workout.deload_protocol}</p>

            {Object.keys(result.workout.stage_adjustments).length > 0 && (
              <div>
                <p className="font-semibold text-text mb-1">Stage Adjustments</p>
                <ul className="space-y-1">
                  {Object.entries(result.workout.stage_adjustments).map(([stage, adj]) => (
                    <li key={stage} className="text-xs">
                      <span className="font-medium text-text">Stage {stage}:</span> {adj}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="p-3 bg-surfaceAlt rounded-lg flex items-start gap-2">
        <Info className="h-4 w-4 text-text-light mt-0.5 shrink-0" />
        <p className="text-xs text-text-light">{result.disclaimer}</p>
      </div>

      {/* Reset */}
      <div className="text-center">
        <Button variant="secondary" size="sm" onClick={onReset}>
          Start New Journey
        </Button>
      </div>
    </div>
  );
}
