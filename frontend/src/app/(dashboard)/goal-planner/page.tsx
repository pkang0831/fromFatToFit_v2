'use client';

import { useState, useCallback, useEffect } from 'react';
import toast from 'react-hot-toast';
import { Target, ArrowLeft, ArrowRight, Check, ChevronRight, RefreshCw, Utensils, Download, RotateCcw, Flame, Dumbbell, Clock } from 'lucide-react';
import { Card, CardContent, Button } from '@/components/ui';
import { goalPlanApi, authApi, bodyApi } from '@/lib/api/services';
import { trackRetentionEvent } from '@/lib/analytics';
import { TierComparison } from '@/components/features/goal-planner/TierComparison';
import { MacroSlider } from '@/components/features/goal-planner/MacroSlider';
import { ExerciseRoutine } from '@/components/features/goal-planner/ExerciseRoutine';
import { CardioPlan } from '@/components/features/goal-planner/CardioPlan';

const STEPS = [
  { label: 'Goals', icon: '1' },
  { label: 'Calorie Tier', icon: '2' },
  { label: 'Macros', icon: '3' },
  { label: 'Meal Plan', icon: '4' },
  { label: 'Exercise', icon: '5' },
  { label: 'Cardio', icon: '6' },
  { label: 'Summary', icon: '7' },
];

export default function GoalPlannerPage() {
  useEffect(() => {
    trackRetentionEvent('history_viewed', {
      surface: 'goal_planner_page',
      target: 'planner',
    });
  }, []);

  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [savingPlan, setSavingPlan] = useState(false);
  const [loadingRemotePlan, setLoadingRemotePlan] = useState(false);
  const [remoteSavedAt, setRemoteSavedAt] = useState<string | null>(null);
  const [profileLoaded, setProfileLoaded] = useState(false);

  // Step 0: Goals
  const [currentWeight, setCurrentWeight] = useState('');
  const [currentBf, setCurrentBf] = useState('');
  const [targetBf, setTargetBf] = useState('');
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [age, setAge] = useState('');
  const [heightCm, setHeightCm] = useState('');
  const [activityLevel, setActivityLevel] = useState('moderate');

  useEffect(() => {
    async function loadProfile() {
      try {
        const [profileRes, gapRes] = await Promise.all([
          authApi.getProfile(),
          bodyApi.getGapToGoal().catch(() => null),
        ]);
        const p = profileRes.data;
        if (p.weight_kg) setCurrentWeight(String(p.weight_kg));
        if (p.height_cm) setHeightCm(String(p.height_cm));
        if (p.age) setAge(String(p.age));
        if (p.gender) setGender(p.gender);
        if (p.activity_level) setActivityLevel(p.activity_level);

        const gap = gapRes?.data;
        if (gap?.current_bf) setCurrentBf(String(gap.current_bf));
        if (gap?.target_bf) setTargetBf(String(gap.target_bf));
      } catch {
        // fields stay empty — user fills manually
      } finally {
        setProfileLoaded(true);
      }
    }
    loadProfile();
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const p = new URLSearchParams(window.location.search);
    const cbf = p.get('cbf');
    const tbf = p.get('tbf');
    const cw = p.get('cw');
    const age = p.get('age');
    const hcm = p.get('hcm');
    const act = p.get('act');
    const g = p.get('g');
    if (cbf) setCurrentBf(cbf);
    if (tbf) setTargetBf(tbf);
    if (cw) setCurrentWeight(cw);
    if (age) setAge(age);
    if (hcm) setHeightCm(hcm);
    if (act) setActivityLevel(act);
    if (g === 'male' || g === 'female') setGender(g);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await goalPlanApi.getSavedPlan();
        if (!cancelled && res.data?.updated_at) setRemoteSavedAt(res.data.updated_at);
      } catch {
        // 404 — no saved plan
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Step 1: Tier data
  const [tierData, setTierData] = useState<any>(null);
  const [selectedTier, setSelectedTier] = useState<number | null>(null);

  // Step 2: Macro data
  const [macroData, setMacroData] = useState<any>(null);

  // Step 3: Auto meal plan
  const [mealPlan, setMealPlan] = useState<any>(null);
  const [mealsPerDay, setMealsPerDay] = useState(3);

  // Step 4: Exercise data
  const [exerciseData, setExerciseData] = useState<any>(null);
  const [exerciseMode, setExerciseMode] = useState('cut');
  const [experience, setExperience] = useState('intermediate');

  // Step 5: Cardio data
  const [cardioData, setCardioData] = useState<any>(null);
  const [cardioTarget, setCardioTarget] = useState('300');

  // ── Step handlers ─────────────────────────────────────────────────────────

  const handleGoalSubmit = useCallback(async () => {
    if (!currentWeight || !currentBf || !targetBf || !age || !heightCm) {
      toast.error('Please fill all fields');
      return;
    }
    setLoading(true);
    try {
      const res = await goalPlanApi.compareTiers({
        current_weight_kg: Number(currentWeight),
        current_bf_pct: Number(currentBf),
        target_bf_pct: Number(targetBf),
        gender,
        age: Number(age),
        height_cm: Number(heightCm),
        activity_level: activityLevel,
      });
      setTierData(res.data);
      setStep(1);
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to calculate tiers');
    } finally {
      setLoading(false);
    }
  }, [currentWeight, currentBf, targetBf, gender, age, heightCm, activityLevel]);

  const handleTierSelect = useCallback((index: number) => {
    setSelectedTier(index);
  }, []);

  const handleTierConfirm = useCallback(async () => {
    if (selectedTier === null || !tierData) return;
    const tier = tierData.tiers[selectedTier];
    setLoading(true);
    try {
      const res = await goalPlanApi.getMacros({
        daily_calories: tier.daily_calories,
        weight_kg: Number(currentWeight),
        preset: 'balanced',
      });
      setMacroData(res.data);
      setStep(2);
    } catch {
      toast.error('Failed to calculate macros');
    } finally {
      setLoading(false);
    }
  }, [selectedTier, tierData, currentWeight]);

  const handleMacroPreset = useCallback(async (preset: string) => {
    if (selectedTier === null || !tierData) return;
    const tier = tierData.tiers[selectedTier];
    setLoading(true);
    try {
      const res = await goalPlanApi.getMacros({
        daily_calories: tier.daily_calories,
        weight_kg: Number(currentWeight),
        preset,
      });
      setMacroData(res.data);
    } catch {
      toast.error('Failed to update macros');
    } finally {
      setLoading(false);
    }
  }, [selectedTier, tierData, currentWeight]);

  const handleMacroCustom = useCallback(async (c: number, p: number, f: number) => {
    if (selectedTier === null || !tierData) return;
    const tier = tierData.tiers[selectedTier];
    try {
      const res = await goalPlanApi.getMacros({
        daily_calories: tier.daily_calories,
        weight_kg: Number(currentWeight),
        carb_pct: c,
        protein_pct: p,
        fat_pct: f,
      });
      setMacroData(res.data);
    } catch {
      // silent
    }
  }, [selectedTier, tierData, currentWeight]);

  const fetchMealPlan = useCallback(async (meals?: number) => {
    if (!macroData?.breakdown || selectedTier === null || !tierData) return;
    const tier = tierData.tiers[selectedTier];
    setLoading(true);
    try {
      const res = await goalPlanApi.recommendMeals({
        daily_calories: tier.daily_calories,
        protein_g: macroData.breakdown.protein_g,
        carb_g: macroData.breakdown.carb_g,
        fat_g: macroData.breakdown.fat_g,
        meals_per_day: meals ?? mealsPerDay,
      });
      setMealPlan(res.data);
    } catch {
      toast.error('Failed to generate meal plan');
    } finally {
      setLoading(false);
    }
  }, [macroData, selectedTier, tierData, mealsPerDay]);

  const handleMacroConfirm = useCallback(async () => {
    await fetchMealPlan();
    setStep(3);
  }, [fetchMealPlan]);

  const handleMealPlanConfirm = useCallback(async () => {
    const direction = tierData?.direction || 'deficit';
    const mode = direction === 'deficit' ? 'cut' : 'lean_bulk';
    setExerciseMode(mode);
    setLoading(true);
    try {
      const res = await goalPlanApi.getExerciseRoutine({ mode, gender, experience });
      setExerciseData(res.data);
      setStep(4);
    } catch {
      toast.error('Failed to generate exercise routine');
    } finally {
      setLoading(false);
    }
  }, [tierData, gender, experience]);

  const handleExerciseConfirm = useCallback(async () => {
    setLoading(true);
    try {
      const res = await goalPlanApi.getCardioPlan({
        weight_kg: Number(currentWeight),
        gender,
        height_cm: Number(heightCm),
        age: Number(age),
        target_calories: Number(cardioTarget),
      });
      setCardioData(res.data);
      setStep(5);
    } catch {
      toast.error('Failed to calculate cardio plan');
    } finally {
      setLoading(false);
    }
  }, [currentWeight, gender, heightCm, age, cardioTarget]);

  const handleSavePlan = useCallback(async () => {
    const plan = {
      version: 1 as const,
      savedAt: new Date().toISOString(),
      goals: {
        currentWeight,
        currentBf,
        targetBf,
        gender,
        age,
        heightCm,
        activityLevel,
      },
      tierData,
      selectedTier,
      macroData,
      mealPlan,
      mealsPerDay,
      exerciseData,
      exerciseMode,
      experience,
      cardioData,
      cardioTarget,
    };
    setSavingPlan(true);
    try {
      const res = await goalPlanApi.savePlan({ plan });
      setRemoteSavedAt(res.data.updated_at);
      toast.success('Plan saved to your account.');
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Failed to save plan');
    } finally {
      setSavingPlan(false);
    }
  }, [
    currentWeight,
    currentBf,
    targetBf,
    gender,
    age,
    heightCm,
    activityLevel,
    tierData,
    selectedTier,
    macroData,
    mealPlan,
    mealsPerDay,
    exerciseData,
    exerciseMode,
    experience,
    cardioData,
    cardioTarget,
  ]);

  const handleLoadSavedPlan = useCallback(async () => {
    setLoadingRemotePlan(true);
    try {
      const res = await goalPlanApi.getSavedPlan();
      const plan = res.data.plan;
      if (plan.version !== 1) {
        toast.error('Unsupported saved plan version');
        return;
      }
      const g = plan.goals as Record<string, unknown> | undefined;
      if (g) {
        if (g.currentWeight != null) setCurrentWeight(String(g.currentWeight));
        if (g.currentBf != null) setCurrentBf(String(g.currentBf));
        if (g.targetBf != null) setTargetBf(String(g.targetBf));
        if (g.age != null) setAge(String(g.age));
        if (g.heightCm != null) setHeightCm(String(g.heightCm));
        if (typeof g.activityLevel === 'string') setActivityLevel(g.activityLevel);
        if (g.gender === 'male' || g.gender === 'female') setGender(g.gender);
      }
      if (plan.tierData) setTierData(plan.tierData);
      if (plan.selectedTier != null) setSelectedTier(plan.selectedTier as number);
      if (plan.macroData) setMacroData(plan.macroData);
      if (plan.mealPlan) setMealPlan(plan.mealPlan);
      if (plan.mealsPerDay != null) setMealsPerDay(Number(plan.mealsPerDay));
      if (plan.exerciseData) setExerciseData(plan.exerciseData);
      if (typeof plan.exerciseMode === 'string') setExerciseMode(plan.exerciseMode);
      if (typeof plan.experience === 'string') setExperience(plan.experience);
      if (plan.cardioData) setCardioData(plan.cardioData);
      if (plan.cardioTarget != null) setCardioTarget(String(plan.cardioTarget));
      setRemoteSavedAt(res.data.updated_at);
      setStep(6);
      toast.success('Saved plan loaded.');
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } };
      toast.error(err?.response?.data?.detail || 'Could not load saved plan');
    } finally {
      setLoadingRemotePlan(false);
    }
  }, []);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
            <Target className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-text">Goal Planner</h1>
            <p className="text-sm text-text-secondary">Interactive step-by-step plan builder</p>
          </div>
        </div>
        {remoteSavedAt && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleLoadSavedPlan}
            disabled={loadingRemotePlan}
            isLoading={loadingRemotePlan}
            className="shrink-0 self-start sm:self-center"
          >
            Load saved plan
          </Button>
        )}
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-1 overflow-x-auto pb-2">
        {STEPS.map((s, i) => (
          <div key={i} className="flex items-center">
            <button
              onClick={() => i < step && setStep(i)}
              disabled={i > step}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                i === step
                  ? 'bg-primary text-white'
                  : i < step
                  ? 'bg-primary/20 text-primary cursor-pointer hover:bg-primary/30'
                  : 'bg-surfaceAlt text-text-light cursor-not-allowed'
              }`}
            >
              {i < step ? <Check className="h-3 w-3" /> : <span>{s.icon}</span>}
              {s.label}
            </button>
            {i < STEPS.length - 1 && <ChevronRight className="h-3 w-3 text-text-light mx-0.5 flex-shrink-0" />}
          </div>
        ))}
      </div>

      {/* Step content */}
      <Card>
        <CardContent className="p-6">
          {/* Step 0: Goals */}
          {step === 0 && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-text">Set Your Goals</h2>
              {profileLoaded && currentWeight && (
                <div className="bg-primary/5 border border-primary/20 rounded-xl px-4 py-2.5 text-sm text-primary">
                  Profile data loaded. Confirm your target body fat and adjust anything if needed.
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Current Weight (kg)</label>
                  <input type="number" value={currentWeight} onChange={(e) => setCurrentWeight(e.target.value)}
                    className="w-full px-3 py-2.5 bg-surfaceAlt border border-border rounded-xl text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="80" />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Current Body Fat (%)</label>
                  <input type="number" value={currentBf} onChange={(e) => setCurrentBf(e.target.value)}
                    className="w-full px-3 py-2.5 bg-surfaceAlt border border-border rounded-xl text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="22" />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Target Body Fat (%)</label>
                  <input type="number" value={targetBf} onChange={(e) => setTargetBf(e.target.value)}
                    className="w-full px-3 py-2.5 bg-surfaceAlt border border-border rounded-xl text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="15" />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Age</label>
                  <input type="number" value={age} onChange={(e) => setAge(e.target.value)}
                    className="w-full px-3 py-2.5 bg-surfaceAlt border border-border rounded-xl text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="30" />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Height (cm)</label>
                  <input type="number" value={heightCm} onChange={(e) => setHeightCm(e.target.value)}
                    className="w-full px-3 py-2.5 bg-surfaceAlt border border-border rounded-xl text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                    placeholder="175" />
                </div>
                <div>
                  <label className="block text-sm text-text-secondary mb-1">Gender</label>
                  <div className="flex gap-2">
                    {(['male', 'female'] as const).map((g) => (
                      <button key={g} onClick={() => setGender(g)}
                        className={`flex-1 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                          gender === g ? 'bg-primary text-white' : 'bg-surfaceAlt text-text-secondary hover:text-text border border-border'
                        }`}
                      >{g === 'male' ? 'Male' : 'Female'}</button>
                    ))}
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm text-text-secondary mb-1">Activity Level</label>
                <div className="flex gap-1 flex-wrap">
                  {[
                    { key: 'sedentary', label: 'Sedentary' },
                    { key: 'light', label: 'Light' },
                    { key: 'moderate', label: 'Moderate' },
                    { key: 'active', label: 'Active' },
                    { key: 'very_active', label: 'Very Active' },
                  ].map((a) => (
                    <button key={a.key} onClick={() => setActivityLevel(a.key)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                        activityLevel === a.key ? 'bg-primary text-white' : 'bg-surfaceAlt text-text-secondary hover:text-text'
                      }`}
                    >{a.label}</button>
                  ))}
                </div>
              </div>
              <Button onClick={handleGoalSubmit} disabled={loading} className="w-full">
                {loading ? 'Calculating...' : 'Compare Calorie Tiers'} <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          )}

          {/* Step 1: Tier comparison */}
          {step === 1 && tierData && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-text">Choose Your Calorie Tier</h2>
              <TierComparison
                tiers={tierData.tiers}
                direction={tierData.direction}
                tdee={tierData.tdee}
                bmr={tierData.bmr}
                selectedIndex={selectedTier}
                onSelect={handleTierSelect}
              />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(0)}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>
                <Button onClick={handleTierConfirm} disabled={selectedTier === null || loading} className="flex-1">
                  {loading ? 'Loading...' : 'Set Macros'} <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Macros */}
          {step === 2 && macroData && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-text">Adjust Macro Ratios</h2>
              <MacroSlider
                dailyCalories={tierData?.tiers?.[selectedTier ?? 0]?.daily_calories || 2000}
                weightKg={Number(currentWeight)}
                breakdown={macroData.breakdown}
                onPresetSelect={handleMacroPreset}
                onCustomChange={handleMacroCustom}
              />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(1)}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>
                <Button onClick={handleMacroConfirm} disabled={loading} className="flex-1">
                  {loading ? 'Generating meal plan...' : 'Get Meal Plan'} <Utensils className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Auto-recommended Meal Plan */}
          {step === 3 && mealPlan && (
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-text">Recommended Meal Plan</h2>
                <button
                  onClick={() => fetchMealPlan()}
                  disabled={loading}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-surfaceAlt text-text-secondary hover:text-text transition-all"
                >
                  <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
                  Shuffle
                </button>
              </div>

              {/* Meals per day selector */}
              <div className="flex items-center gap-3">
                <span className="text-sm text-text-secondary">Meals per day:</span>
                <div className="flex gap-1">
                  {[2, 3, 4, 5].map((n) => (
                    <button
                      key={n}
                      onClick={() => { setMealsPerDay(n); fetchMealPlan(n); }}
                      className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${
                        mealsPerDay === n
                          ? 'bg-primary text-white'
                          : 'bg-surfaceAlt text-text-secondary hover:text-text'
                      }`}
                    >{n}</button>
                  ))}
                </div>
              </div>

              {/* Meal cards */}
              <div className="space-y-3">
                {mealPlan.meals.map((meal: any, i: number) => (
                  <div key={i} className="bg-surfaceAlt rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-semibold text-text">{meal.meal_label}</h4>
                      <span className="font-number text-sm text-primary">{Math.round(meal.total_calories)} kcal</span>
                    </div>
                    <div className="space-y-1.5">
                      {meal.ingredients.map((ing: any, j: number) => (
                        <div key={j} className="flex justify-between text-sm">
                          <span className="text-text">{ing.food_name} <span className="text-text-light">({ing.amount_g}g)</span></span>
                          <span className="font-number text-text-secondary text-xs">
                            P:{ing.protein_g}g · C:{ing.carb_g}g · F:{ing.fat_g}g
                          </span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-2 pt-2 border-t border-border/50 flex gap-4 text-xs font-number">
                      <span className="text-green-400">P: {meal.total_protein_g}g</span>
                      <span className="text-blue-400">C: {meal.total_carb_g}g</span>
                      <span className="text-yellow-400">F: {meal.total_fat_g}g</span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Day totals */}
              <div className="bg-surface border border-border rounded-xl p-4">
                <h4 className="text-sm font-semibold text-text mb-3">Day Total</h4>
                <div className="grid grid-cols-4 gap-2 text-center">
                  <div>
                    <div className="text-lg font-bold font-number text-text">{Math.round(mealPlan.day_total_calories)}</div>
                    <div className="text-xs text-text-light">kcal</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold font-number text-green-400">{Math.round(mealPlan.day_total_protein_g)}g</div>
                    <div className="text-xs text-text-light">Protein</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold font-number text-blue-400">{Math.round(mealPlan.day_total_carb_g)}g</div>
                    <div className="text-xs text-text-light">Carbs</div>
                  </div>
                  <div>
                    <div className="text-lg font-bold font-number text-yellow-400">{Math.round(mealPlan.day_total_fat_g)}g</div>
                    <div className="text-xs text-text-light">Fat</div>
                  </div>
                </div>
                {mealPlan.target_diff && (
                  <div className="mt-3 pt-2 border-t border-border flex justify-center gap-4 text-xs">
                    <span className="text-text-light">vs target:</span>
                    {(['calories', 'protein_g', 'carb_g', 'fat_g'] as const).map((k) => {
                      const v = mealPlan.target_diff[k];
                      if (v == null) return null;
                      const label = k === 'calories' ? 'kcal' : k.replace('_g', '');
                      return (
                        <span key={k} className={Math.abs(v) < 30 ? 'text-green-400' : v > 0 ? 'text-red-400' : 'text-yellow-400'}>
                          {v > 0 ? '+' : ''}{Math.round(v)} {label}
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(2)}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>
                <Button onClick={handleMealPlanConfirm} disabled={loading} className="flex-1">
                  {loading ? 'Loading...' : 'Exercise Routine'} <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 4: Exercise */}
          {step === 4 && exerciseData && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-text">Exercise Routine</h2>
              <div className="flex gap-2 mb-2">
                <label className="text-sm text-text-secondary self-center">Experience:</label>
                {['beginner', 'intermediate', 'advanced'].map((e) => (
                  <button key={e} onClick={async () => {
                    setExperience(e);
                    try {
                      const res = await goalPlanApi.getExerciseRoutine({ mode: exerciseMode, gender, experience: e });
                      setExerciseData(res.data);
                    } catch { /* silent */ }
                  }} className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    experience === e ? 'bg-primary text-white' : 'bg-surfaceAlt text-text-secondary'
                  }`}>{e}</button>
                ))}
              </div>
              <ExerciseRoutine
                splitType={exerciseData.split_type}
                sessionsPerWeek={exerciseData.sessions_per_week}
                days={exerciseData.days}
                progressionScheme={exerciseData.progression_scheme}
                deloadNote={exerciseData.deload_note}
              />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(3)}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>
                <div className="flex items-center gap-2 flex-1">
                  <label className="text-sm text-text-secondary whitespace-nowrap">Target burn:</label>
                  <input type="number" value={cardioTarget} onChange={(e) => setCardioTarget(e.target.value)}
                    className="w-20 px-2 py-1.5 bg-surfaceAlt border border-border rounded-lg text-sm text-text font-number text-center" />
                  <span className="text-xs text-text-light">kcal</span>
                </div>
                <Button onClick={handleExerciseConfirm} disabled={loading}>
                  {loading ? 'Loading...' : 'Cardio Plan'} <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 5: Cardio */}
          {step === 5 && cardioData && (
            <div className="space-y-5">
              <h2 className="text-lg font-semibold text-text">Cardio Plan</h2>
              <CardioPlan
                targetCalories={cardioData.target_calories}
                options={cardioData.options}
              />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(4)}><ArrowLeft className="h-4 w-4 mr-2" /> Back</Button>
                <Button onClick={() => setStep(6)} className="flex-1">
                  <Check className="h-4 w-4 mr-2" /> View Full Plan
                </Button>
              </div>
            </div>
          )}

          {/* Step 6: Summary */}
          {step === 6 && (
            <div className="space-y-6">
              <div className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-gradient-primary flex items-center justify-center mx-auto mb-3">
                  <Check className="h-7 w-7 text-white" />
                </div>
                <h2 className="text-xl font-bold text-text">Your Complete Plan</h2>
                <p className="text-sm text-text-secondary mt-1">
                  {Number(currentWeight)}kg · {Number(currentBf)}% BF → {Number(targetBf)}% BF
                </p>
              </div>

              {/* Calorie & Timeline overview */}
              {tierData && selectedTier !== null && (
                <div className="bg-surfaceAlt rounded-xl p-4">
                  <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Calorie Target</h3>
                  <div className="grid grid-cols-4 gap-3 text-center">
                    <div>
                      <div className="text-2xl font-bold font-number text-text">{tierData.tiers[selectedTier].daily_calories}</div>
                      <div className="text-xs text-text-light">kcal / day</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-number text-red-400">{Math.abs(tierData.tiers[selectedTier].deficit_or_surplus)}</div>
                      <div className="text-xs text-text-light">cal {tierData.direction}</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-number text-primary">{tierData.tiers[selectedTier].weeks_to_goal}</div>
                      <div className="text-xs text-text-light">weeks</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-number text-text">{Math.abs(tierData.tiers[selectedTier].weekly_change_kg)}</div>
                      <div className="text-xs text-text-light">kg / week</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Macros */}
              {macroData?.breakdown && (
                <div className="bg-surfaceAlt rounded-xl p-4">
                  <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">Daily Macros</h3>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div>
                      <div className="text-2xl font-bold font-number text-blue-400">{macroData.breakdown.carb_g}g</div>
                      <div className="text-xs text-text-light">Carbs ({macroData.breakdown.carb_pct}%)</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-number text-green-400">{macroData.breakdown.protein_g}g</div>
                      <div className="text-xs text-text-light">Protein ({macroData.breakdown.protein_pct}%)</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-number text-yellow-400">{macroData.breakdown.fat_g}g</div>
                      <div className="text-xs text-text-light">Fat ({macroData.breakdown.fat_pct}%)</div>
                    </div>
                  </div>
                  <div className="h-3 rounded-full overflow-hidden flex mt-3 bg-surface">
                    <div className="bg-blue-500" style={{ width: `${macroData.breakdown.carb_pct}%` }} />
                    <div className="bg-green-500" style={{ width: `${macroData.breakdown.protein_pct}%` }} />
                    <div className="bg-yellow-500" style={{ width: `${macroData.breakdown.fat_pct}%` }} />
                  </div>
                </div>
              )}

              {/* Meal Plan */}
              {mealPlan && (
                <div className="bg-surfaceAlt rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Utensils className="h-4 w-4 text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Meal Plan ({mealPlan.meals.length} meals)</h3>
                  </div>
                  <div className="space-y-2">
                    {mealPlan.meals.map((meal: any, i: number) => (
                      <div key={i} className="bg-surface rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-semibold text-text">{meal.meal_label}</span>
                          <span className="text-xs font-number text-primary">{Math.round(meal.total_calories)} kcal</span>
                        </div>
                        <div className="text-xs text-text-light">
                          {meal.ingredients.map((ing: any) => `${ing.food_name} (${ing.amount_g}g)`).join(' · ')}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-2 pt-2 border-t border-border/50 text-center text-xs font-number text-text-secondary">
                    Total: {Math.round(mealPlan.day_total_calories)} kcal · P:{Math.round(mealPlan.day_total_protein_g)}g · C:{Math.round(mealPlan.day_total_carb_g)}g · F:{Math.round(mealPlan.day_total_fat_g)}g
                  </div>
                </div>
              )}

              {/* Exercise Routine */}
              {exerciseData && (
                <div className="bg-surfaceAlt rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Dumbbell className="h-4 w-4 text-text-secondary" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Exercise — {exerciseData.split_type} · {exerciseData.sessions_per_week}x / week
                    </h3>
                  </div>
                  <div className="space-y-2">
                    {exerciseData.days.map((day: any, i: number) => (
                      <div key={i} className="bg-surface rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-sm font-semibold text-text">{day.day_label}</span>
                          <span className="text-xs text-text-light flex items-center gap-1">
                            <Clock className="h-3 w-3" /> ~{day.estimated_duration_min}min
                          </span>
                        </div>
                        <div className="text-xs text-text-light">
                          {day.exercises.map((ex: any) => `${ex.name} ${ex.sets}×${ex.reps_min}-${ex.reps_max}`).join(' · ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Cardio */}
              {cardioData && (
                <div className="bg-surfaceAlt rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <Flame className="h-4 w-4 text-orange-400" />
                    <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
                      Cardio — {cardioData.target_calories} kcal target
                    </h3>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {cardioData.options.slice(0, 6).map((opt: any) => (
                      <div key={opt.activity} className="bg-surface rounded-lg p-3 text-center">
                        <div className="text-lg font-bold font-number text-primary">{opt.duration_minutes}min</div>
                        <div className="text-xs text-text-light capitalize">{opt.activity.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => setStep(0)} className="flex-1">
                  <RotateCcw className="h-4 w-4 mr-2" /> Start Over
                </Button>
                <Button
                  type="button"
                  onClick={handleSavePlan}
                  disabled={savingPlan}
                  isLoading={savingPlan}
                  className="flex-1"
                >
                  <Download className="h-4 w-4 mr-2" /> Save Plan
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
