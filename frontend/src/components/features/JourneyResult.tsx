'use client';

import { useState, useCallback } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import {
  ChevronDown, ChevronUp,
  Utensils, Dumbbell, AlertTriangle, Info, Zap,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ShareButtons } from '@/components/ui/ShareButtons';
import { challengeApi } from '@/lib/api/services';
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

export interface JourneyPrefill {
  weightKg?: string;
  age?: string;
  heightCm?: string;
  activityLevel?: string;
  gender?: string;
}

interface Props {
  result: TransformationJourneyResponse;
  originalImage: string;
  onReset: () => void;
  journeyPrefill?: JourneyPrefill;
}

function buildGoalPlannerQuery(
  result: TransformationJourneyResponse,
  prefill?: JourneyPrefill,
): string {
  const p = new URLSearchParams();
  p.set('cbf', String(result.current_bf));
  p.set('tbf', String(result.target_bf));
  p.set('wks', String(result.total_weeks));
  if (prefill?.weightKg) p.set('cw', prefill.weightKg);
  if (prefill?.age) p.set('age', prefill.age);
  if (prefill?.heightCm) p.set('hcm', prefill.heightCm);
  if (prefill?.activityLevel) p.set('act', prefill.activityLevel);
  if (prefill?.gender) p.set('g', prefill.gender);
  return p.toString();
}

export function JourneyResult({ result, originalImage, onReset, journeyPrefill }: Props) {
  const router = useRouter();
  const [showNutrition, setShowNutrition] = useState(false);
  const [showWorkout, setShowWorkout] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [softTimelineOpen, setSoftTimelineOpen] = useState(false);
  const [gateDismissed, setGateDismissed] = useState(false);
  const [startingSeven, setStartingSeven] = useState(false);

  const softWeeks = Math.max(result.total_weeks + 1, Math.ceil(result.total_weeks * 1.45));

  const goToGoalPlanner = useCallback(() => {
    const q = buildGoalPlannerQuery(result, journeyPrefill);
    router.push(`/goal-planner?${q}`);
  }, [result, journeyPrefill, router]);

  const startSevenDay = useCallback(async () => {
    setStartingSeven(true);
    try {
      await challengeApi.startSevenDay({
        ai_weeks_snapshot: result.total_weeks,
        ai_current_bf: result.current_bf,
        ai_target_bf: result.target_bf,
      });
      toast.success('7-day loop started — one quick check-in per day.');
      router.push('/challenge');
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Could not start challenge');
    } finally {
      setStartingSeven(false);
    }
  }, [result, router]);

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

      {/* Decision gate: separate browsers vs executors */}
      {!gateDismissed && (
        <div className="rounded-2xl border border-amber-500/35 bg-gradient-to-br from-amber-950/40 to-surfaceAlt p-5 space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-200/90">
            You saw the vision — now pick a lane
          </p>
          <p className="text-sm text-text leading-relaxed">
            Getting to ~{result.target_bf.toFixed(1)}% body fat from ~{result.current_bf.toFixed(1)}% is not a weekend project.
            At the pace we modeled, you&apos;re looking at about{' '}
            <span className="font-bold text-text">{result.total_weeks} weeks</span> of aligned eating and training — not endless scrolling.
          </p>
          <div className="p-3 rounded-xl bg-black/25 border border-white/10 text-sm text-text-secondary">
            <span className="text-rose-300/90 font-medium">Reality check: </span>
            If nothing changes, you don&apos;t stay still — you drift. The gap between today and that goal image is measured in weeks of execution, not motivation.
          </div>
          <div className="flex flex-col gap-2">
            <Button type="button" variant="primary" className="w-full justify-center" onClick={goToGoalPlanner}>
              Start my {result.total_weeks}-week plan
            </Button>
            <Button
              type="button"
              variant="outline"
              className="w-full justify-center border-primary/40"
              onClick={() => setSoftTimelineOpen((v) => !v)}
            >
              See a more realistic timeline
            </Button>
            {softTimelineOpen && (
              <p className="text-xs text-text-secondary px-1 py-2 border-l-2 border-primary/50">
                Aggressive timelines break people. A sustainable pace often lands closer to{' '}
                <span className="font-semibold text-text">{softWeeks} weeks</span> for the same BF change — same direction, less whiplash.
                You can still start the structured plan and adjust intensity inside Goal Planner.
              </p>
            )}
            <button
              type="button"
              onClick={() => setGateDismissed(true)}
              className="text-center text-xs text-text-light hover:text-text-secondary py-2 transition-colors"
            >
              Not for me right now — I&apos;m just browsing
            </button>
          </div>
          <div className="pt-2 border-t border-white/10">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              className="w-full"
              onClick={startSevenDay}
              disabled={startingSeven}
              isLoading={startingSeven}
            >
              <Zap className="h-4 w-4 mr-2 shrink-0" />
              Lock in 7-day check-ins (daily, ~30s)
            </Button>
            <p className="text-[11px] text-text-light mt-2 text-center">
              Builds the habit loop: one check-in per day so the app becomes a system, not a gallery.
            </p>
          </div>
        </div>
      )}

      {gateDismissed && (
        <p className="text-xs text-center text-text-light">
          Whenever you&apos;re ready: <button type="button" className="text-primary underline" onClick={goToGoalPlanner}>Goal Planner</button>
          {' · '}
          <button type="button" className="text-primary underline" onClick={startSevenDay}>7-day challenge</button>
        </p>
      )}

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
