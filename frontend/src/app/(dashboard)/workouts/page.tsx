'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { Dumbbell, Plus, TrendingUp, Trash2, Flame } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Button, Input, Badge, Modal } from '@/components/ui';
import { workoutApi } from '@/lib/api/services';
import { getTodayString, formatDateLong } from '@/lib/utils/date';
import type { ExerciseLibraryItem, WorkoutLog, WorkoutTrendResponse } from '@/types/api';

interface SetData {
  set_number: number;
  reps: number;
  weight: number;
}

export default function WorkoutsPage() {
  const [exercises, setExercises] = useState<ExerciseLibraryItem[]>([]);
  const [workoutLogs, setWorkoutLogs] = useState<WorkoutLog[]>([]);
  const [trends, setTrends] = useState<WorkoutTrendResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [selectedExercise, setSelectedExercise] = useState<ExerciseLibraryItem | null>(null);
  const [showLogForm, setShowLogForm] = useState(false);
  const [showQuickSelectModal, setShowQuickSelectModal] = useState(false);
  const [showRecentWorkoutsModal, setShowRecentWorkoutsModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'cardio' | 'strength'>('all');
  const [activeLibraryTab, setActiveLibraryTab] = useState<'all' | 'cardio' | 'strength'>('all');
  const [recentWorkouts, setRecentWorkouts] = useState<WorkoutLog[]>([]);
  const [sets, setSets] = useState<SetData[]>([{ set_number: 1, reps: 0, weight: 0 }]);
  const [duration, setDuration] = useState<number>(0);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  // Debug: Log exercise data when loaded
  useEffect(() => {
    if (exercises.length > 0) {
      console.log('📊 Total exercises:', exercises.length);
      console.log('🏃 Cardio:', exercises.filter(ex => (ex as any).exercise_type === 'cardio').length);
      console.log('💪 Strength:', exercises.filter(ex => (ex as any).exercise_type === 'strength').length);
      console.log('❓ No type:', exercises.filter(ex => !(ex as any).exercise_type).length);
      console.log('🔍 First exercise sample:', exercises[0]);
    }
  }, [exercises]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const [exercisesRes, logsRes, trendsRes] = await Promise.all([
        workoutApi.getExerciseLibrary(),
        workoutApi.getWorkoutLogs(getTodayString()),
        workoutApi.getTrends(30),
      ]);
      setExercises(exercisesRes.data);
      setWorkoutLogs(logsRes.data);
      setTrends(trendsRes.data);
    } catch (error) {
      console.error('Failed to load workout data:', error);
    } finally {
      setLoading(false);
      // Load recent workouts in background (don't block main loading)
      loadRecentWorkouts().catch(err => console.error('Failed to load recent workouts:', err));
    }
  }, []);

  const loadRecentWorkouts = async () => {
    try {
      // 🚀 OPTIMIZED: 1 API call instead of 7 (10x faster)
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      
      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];
      
      const logsRes = await workoutApi.getWorkoutLogsRange(startDateStr, endDateStr);
      
      // Get unique exercises (most recent first)
      const recentLogs: WorkoutLog[] = [];
      const uniqueExercises = new Set<string>();
      
      logsRes.data.forEach((log: WorkoutLog) => {
        if (!uniqueExercises.has(log.exercise_name)) {
          uniqueExercises.add(log.exercise_name);
          recentLogs.push(log);
        }
      });
      
      setRecentWorkouts(recentLogs.slice(0, 5)); // Top 5 recent
    } catch (error) {
      console.error('Failed to load recent workouts:', error);
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return <Badge variant="success">Beginner</Badge>;
      case 'intermediate':
        return <Badge variant="warning">Intermediate</Badge>;
      case 'advanced':
        return <Badge variant="error">Advanced</Badge>;
      default:
        return null;
    }
  };

  const handleLogExercise = () => {
    setShowExerciseModal(false);
    setShowLogForm(true);
    setSets([{ set_number: 1, reps: 0, weight: 0 }]);
    setDuration(0);
    setNotes('');
  };

  const addSet = () => {
    setSets([...sets, { set_number: sets.length + 1, reps: 0, weight: 0 }]);
  };

  const updateSet = (index: number, field: keyof SetData, value: number) => {
    const newSets = [...sets];
    newSets[index] = { ...newSets[index], [field]: value };
    setSets(newSets);
  };

  const removeSet = (index: number) => {
    if (sets.length > 1) {
      setSets(sets.filter((_, i) => i !== index));
    }
  };

  const submitWorkout = async () => {
    if (!selectedExercise) return;

    setIsSubmitting(true);
    try {
      await workoutApi.logWorkout({
        date: getTodayString(),
        exercise_id: selectedExercise.id,
        exercise_name: selectedExercise.name,
        sets: sets,
        duration_minutes: duration || undefined,
        notes: notes || undefined,
      });
      
      setShowLogForm(false);
      setSelectedExercise(null);
      await loadData();
    } catch (error) {
      console.error('Failed to log workout:', error);
      alert('Failed to log workout. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const deleteWorkout = async (logId: string, exerciseName: string) => {
    if (!confirm(`"${exerciseName}" 운동 기록을 삭제하시겠습니까?`)) {
      return;
    }

    try {
      await workoutApi.deleteLog(logId);
      await loadData();
    } catch (error) {
      console.error('Failed to delete workout:', error);
      alert('운동 기록 삭제에 실패했습니다.');
    }
  };

  const handleQuickSelect = () => {
    setSearchQuery('');
    setShowQuickSelectModal(true);
  };

  const handleRecentWorkout = () => {
    setShowRecentWorkoutsModal(true);
  };

  const handleSelectFromQuickModal = (exercise: ExerciseLibraryItem) => {
    setSelectedExercise(exercise);
    setShowQuickSelectModal(false);
    setShowLogForm(true);
    setSets([{ set_number: 1, reps: 0, weight: 0 }]);
    setDuration(0);
    setNotes('');
  };

  const handleSelectRecentWorkout = (log: WorkoutLog) => {
    // Find the exercise from library
    const exercise = exercises.find(ex => ex.id === log.exercise_id || ex.name === log.exercise_name);
    if (exercise) {
      setSelectedExercise(exercise);
      setShowRecentWorkoutsModal(false);
      setShowLogForm(true);
      // Pre-fill with previous data, ensuring types match
      const normalizedSets = log.sets ? log.sets.map(s => ({
        set_number: s.set_number,
        reps: s.reps || 0,
        weight: s.weight || 0
      })) : [{ set_number: 1, reps: 0, weight: 0 }];
      setSets(normalizedSets);
      setDuration(log.duration_minutes || 0);
      setNotes(log.notes || '');
    }
  };

  // 🚀 OPTIMIZED: Memoize expensive filter operations
  const filteredExercises = useMemo(() => {
    return exercises.filter(ex => {
      // Search filter
      const matchesSearch = searchQuery === '' || 
        ex.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ex.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ex.muscle_groups.some(m => m.toLowerCase().includes(searchQuery.toLowerCase()));
      
      // Category filter (for library view)
      const matchesCategory = selectedCategory === 'all' || 
        (ex as any).exercise_type === selectedCategory;
      
      return matchesSearch && matchesCategory;
    });
  }, [exercises, searchQuery, selectedCategory]);

  // 🚀 OPTIMIZED: Memoize exercise categorization
  const { cardioExercises, strengthExercises } = useMemo(() => ({
    cardioExercises: exercises.filter(ex => (ex as any).exercise_type === 'cardio'),
    strengthExercises: exercises.filter(ex => (ex as any).exercise_type === 'strength' || !(ex as any).exercise_type)
  }), [exercises]);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text">Workout Tracker</h1>
          <p className="text-text-secondary mt-1">{formatDateLong(getTodayString())}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={handleRecentWorkout} disabled={recentWorkouts.length === 0}>
            <TrendingUp className="h-5 w-5 mr-2" />
            Quick Add
          </Button>
          <Button variant="primary" onClick={handleQuickSelect}>
            <Plus className="h-5 w-5 mr-2" />
            Log Workout
          </Button>
        </div>
      </div>

      {/* Weekly Stats */}
      {trends && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card variant="elevated">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary mb-1">Total Workouts</p>
                  <p className="text-3xl font-bold text-text">{trends.total_workouts}</p>
                </div>
                <div className="p-3 bg-primary/10 rounded-lg">
                  <Dumbbell className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary mb-1">Per Week</p>
                  <p className="text-3xl font-bold text-text">
                    {trends.average_per_week.toFixed(1)}
                  </p>
                </div>
                <div className="p-3 bg-secondary/10 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-secondary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-text-secondary mb-1">Today's Logs</p>
                  <p className="text-3xl font-bold text-text">{workoutLogs.length}</p>
                </div>
                <div className="p-3 bg-accent/30 rounded-lg">
                  <Dumbbell className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Today's Workouts */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Workouts</CardTitle>
        </CardHeader>
        <CardContent>
          {workoutLogs.length === 0 ? (
            <div className="text-center py-16 border-2 border-dashed border-gray-300 rounded-lg">
              <Dumbbell className="h-20 w-20 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                아직 오늘의 운동 기록이 없어요
              </h3>
              <p className="text-gray-500 mb-6">
                첫 운동을 기록하고 건강한 습관을 시작해보세요!
              </p>
              <Button size="lg" onClick={handleQuickSelect}>
                <Plus className="h-5 w-5 mr-2" />
                첫 운동 기록하기
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {workoutLogs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 border border-border rounded-lg hover:shadow-lg hover:-translate-y-1 transition-all relative"
                >
                  <div className="flex items-start justify-between">
                    <h4 className="font-semibold text-text mb-2">{log.exercise_name}</h4>
                    <button
                      onClick={() => deleteWorkout(log.id, log.exercise_name)}
                      className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                      title="운동 기록 삭제"
                    >
                      <Trash2 className="h-5 w-5 text-red-500 hover:text-red-700" />
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <span className="text-text-secondary">Sets:</span>
                      <span className="font-medium text-text ml-1">{log.sets.length}</span>
                    </div>
                    {log.duration_minutes && (
                      <div>
                        <span className="text-text-secondary">Duration:</span>
                        <span className="font-medium text-text ml-1">
                          {log.duration_minutes} min
                        </span>
                      </div>
                    )}
                  </div>
                  {log.calories_burned && log.calories_burned > 0 && (
                    <div className="flex items-center gap-2 mt-3 p-3 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border-2 border-orange-200">
                      <Flame className="h-5 w-5 text-orange-500" />
                      <span className="text-lg font-bold text-orange-600">
                        {Math.round(log.calories_burned)} kcal 소모
                      </span>
                    </div>
                  )}
                  {log.notes && (
                    <p className="text-sm text-text-secondary mt-2">{log.notes}</p>
                  )}
                </div>
                ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Exercise Library with Tabs */}
      <Card id="exercise-library">
        <CardHeader>
          <CardTitle>운동 라이브러리</CardTitle>
          <div className="flex gap-2 mt-4 border-b-2 border-gray-200">
            <button
              onClick={() => setActiveLibraryTab('all')}
              className={`pb-3 px-6 font-semibold transition-all relative ${
                activeLibraryTab === 'all'
                  ? 'text-primary'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              전체 ({exercises.length})
              {activeLibraryTab === 'all' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary rounded-t-full" />
              )}
            </button>
            <button
              onClick={() => setActiveLibraryTab('cardio')}
              className={`pb-3 px-6 font-semibold transition-all relative ${
                activeLibraryTab === 'cardio'
                  ? 'text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              🏃 유산소 ({cardioExercises.length})
              {activeLibraryTab === 'cardio' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-500 rounded-t-full" />
              )}
            </button>
            <button
              onClick={() => setActiveLibraryTab('strength')}
              className={`pb-3 px-6 font-semibold transition-all relative ${
                activeLibraryTab === 'strength'
                  ? 'text-orange-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              💪 무산소 ({strengthExercises.length})
              {activeLibraryTab === 'strength' && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-orange-500 rounded-t-full" />
              )}
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-surfaceAlt animate-pulse rounded-lg" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(activeLibraryTab === 'all' ? exercises : 
                activeLibraryTab === 'cardio' ? cardioExercises : 
                strengthExercises).map((exercise) => {
                const isCardio = (exercise as any).exercise_type === 'cardio';
                return (
                  <div
                    key={exercise.id}
                    className={`p-4 border-2 rounded-lg hover:shadow-lg hover:-translate-y-1 transition-all cursor-pointer ${
                      isCardio 
                        ? 'border-blue-200 bg-blue-50 hover:border-blue-400' 
                        : 'border-orange-200 bg-orange-50 hover:border-orange-400'
                    }`}
                    onClick={() => {
                      setSelectedExercise(exercise);
                      setShowExerciseModal(true);
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-text">{exercise.name}</h4>
                      {getDifficultyBadge(exercise.difficulty)}
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge 
                        variant={isCardio ? 'info' : 'warning'} 
                        className="text-xs"
                      >
                        {isCardio ? '🏃 유산소' : '💪 무산소'}
                      </Badge>
                      {(exercise as any).met_value && (
                        <span className="text-xs text-gray-600 font-medium">
                          MET {(exercise as any).met_value}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {exercise.muscle_groups.slice(0, 3).map((muscle) => (
                        <Badge 
                          key={muscle} 
                          variant="default" 
                          className={`text-xs ${isCardio ? 'bg-blue-100' : 'bg-orange-100'}`}
                        >
                          {muscle}
                        </Badge>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Exercise Detail Modal */}
      {selectedExercise && (
        <Modal
          isOpen={showExerciseModal}
          onClose={() => setShowExerciseModal(false)}
          title={selectedExercise.name}
          size="lg"
        >
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              {getDifficultyBadge(selectedExercise.difficulty)}
              <Badge variant="info" className="capitalize">
                {selectedExercise.category}
              </Badge>
            </div>

            <div>
              <h4 className="font-semibold text-text mb-2">Muscle Groups</h4>
              <div className="flex flex-wrap gap-2">
                {selectedExercise.muscle_groups.map((muscle) => (
                  <Badge key={muscle} variant="default">
                    {muscle}
                  </Badge>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-text mb-2">Form Instructions</h4>
              <p className="text-text-secondary whitespace-pre-line">
                {selectedExercise.form_instructions}
              </p>
            </div>

            <Button variant="primary" className="w-full" onClick={handleLogExercise}>
              <Plus className="h-5 w-5 mr-2" />
              Log This Exercise
            </Button>
          </div>
        </Modal>
      )}

      {/* Quick Select Modal (Option 1) */}
      <Modal
        isOpen={showQuickSelectModal}
        onClose={() => {
          setShowQuickSelectModal(false);
          setSelectedCategory('all');
          setSearchQuery('');
        }}
        title="운동 선택"
        size="lg"
      >
        <div className="space-y-4">
          {/* Search Bar */}
          <Input
            type="text"
            placeholder="운동 검색..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full"
          />

          {/* Category Tabs */}
          <div className="flex gap-2 border-b border-border pb-2">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedCategory === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              전체 ({exercises.length})
            </button>
            <button
              onClick={() => setSelectedCategory('cardio')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedCategory === 'cardio'
                  ? 'bg-blue-500 text-white'
                  : 'bg-blue-50 text-blue-700 hover:bg-blue-100'
              }`}
            >
              🏃 유산소 ({cardioExercises.length})
            </button>
            <button
              onClick={() => setSelectedCategory('strength')}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                selectedCategory === 'strength'
                  ? 'bg-orange-500 text-white'
                  : 'bg-orange-50 text-orange-700 hover:bg-orange-100'
              }`}
            >
              💪 무산소 ({strengthExercises.length})
            </button>
          </div>

          {/* Exercise List */}
          <div className="max-h-96 overflow-y-auto space-y-2">
            {filteredExercises.length === 0 ? (
              <p className="text-center text-text-secondary py-8">검색 결과가 없습니다</p>
            ) : (
              filteredExercises.map((exercise) => {
                const isCardio = (exercise as any).exercise_type === 'cardio';
                return (
                  <button
                    key={exercise.id}
                    onClick={() => handleSelectFromQuickModal(exercise)}
                    className={`w-full text-left p-4 border-2 rounded-lg hover:shadow-md transition ${
                      isCardio 
                        ? 'border-blue-200 bg-blue-50 hover:border-blue-400' 
                        : 'border-orange-200 bg-orange-50 hover:border-orange-400'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-text">{exercise.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge 
                            variant={isCardio ? 'info' : 'warning'} 
                            className="text-xs"
                          >
                            {isCardio ? '🏃 유산소' : '💪 무산소'}
                          </Badge>
                          {(exercise as any).met_value && (
                            <span className="text-xs text-gray-600 font-medium">
                              MET {(exercise as any).met_value}
                            </span>
                          )}
                        </div>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {exercise.muscle_groups.slice(0, 3).map((muscle) => (
                            <Badge 
                              key={muscle} 
                              variant="default" 
                              className={`text-xs ${isCardio ? 'bg-blue-100' : 'bg-orange-100'}`}
                            >
                              {muscle}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      {getDifficultyBadge(exercise.difficulty)}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>
      </Modal>

      {/* Recent Workouts Modal (Option 2) */}
      <Modal
        isOpen={showRecentWorkoutsModal}
        onClose={() => setShowRecentWorkoutsModal(false)}
        title="Recent Workouts"
        size="lg"
      >
        <div className="space-y-3">
          {recentWorkouts.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-text-secondary">No recent workouts found</p>
              <Button
                variant="primary"
                onClick={() => {
                  setShowRecentWorkoutsModal(false);
                  handleQuickSelect();
                }}
                className="mt-4"
              >
                <Plus className="h-5 w-5 mr-2" />
                Log New Workout
              </Button>
            </div>
          ) : (
            recentWorkouts.map((log) => (
              <button
                key={log.id}
                onClick={() => handleSelectRecentWorkout(log)}
                className="w-full text-left p-4 border border-border rounded-lg hover:bg-surfaceAlt transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-text mb-2">{log.exercise_name}</h4>
                    <div className="flex gap-4 text-sm text-text-secondary">
                      <span>{log.sets.length} sets</span>
                      {log.duration_minutes && <span>{log.duration_minutes} min</span>}
                      {log.sets[0] && (
                        <span>
                          Last: {log.sets[0].reps} reps × {log.sets[0].weight}kg
                        </span>
                      )}
                    </div>
                  </div>
                  <Badge variant="info">Repeat</Badge>
                </div>
              </button>
            ))
          )}
        </div>
      </Modal>

      {/* Workout Log Form Modal */}
      {selectedExercise && (
        <Modal
          isOpen={showLogForm}
          onClose={() => setShowLogForm(false)}
          title={`${selectedExercise.name} 기록하기`}
          size="lg"
        >
          <div className="space-y-6">
            {/* Exercise Type Badge */}
            <div className="flex items-center gap-2">
              <Badge 
                variant={(selectedExercise as any).exercise_type === 'cardio' ? 'info' : 'warning'}
                className="text-base px-4 py-2"
              >
                {(selectedExercise as any).exercise_type === 'cardio' ? '🏃 유산소 운동' : '💪 무산소 운동'}
              </Badge>
              {(selectedExercise as any).met_value && (
                <span className="text-sm text-gray-600">
                  칼로리 소모: MET {(selectedExercise as any).met_value}
                </span>
              )}
            </div>

            {/* Duration (Required for Cardio, Optional for Strength) */}
            {(selectedExercise as any).exercise_type === 'cardio' ? (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-text mb-2 flex items-center gap-2">
                  ⏱️ 운동 시간 (필수)
                </h4>
                <Input
                  type="number"
                  placeholder="분 (예: 30)"
                  value={duration || ''}
                  onChange={(e) => setDuration(parseInt(e.target.value) || 0)}
                  className="text-lg"
                />
                {duration > 0 && (selectedExercise as any).met_value && (
                  <p className="text-sm text-blue-700 mt-2">
                    💡 예상 칼로리 소모: 약 {Math.round((selectedExercise as any).met_value * 70 * (duration / 60))} kcal (70kg 기준)
                  </p>
                )}
              </div>
            ) : (
              <>
                {/* Sets (for Strength) */}
                <div>
                  <h4 className="font-semibold text-text mb-3">세트</h4>
              <div className="space-y-3">
                {sets.map((set, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <span className="text-sm font-medium text-text-secondary w-12">
                      Set {set.set_number}
                    </span>
                    <Input
                      type="number"
                      placeholder="Reps"
                      value={set.reps || ''}
                      onChange={(e) => updateSet(index, 'reps', parseInt(e.target.value) || 0)}
                      className="flex-1"
                    />
                    <Input
                      type="number"
                      placeholder="Weight (kg)"
                      value={set.weight || ''}
                      onChange={(e) => updateSet(index, 'weight', parseFloat(e.target.value) || 0)}
                      className="flex-1"
                    />
                    {sets.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeSet(index)}
                        className="text-error"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                ))}
              </div>
              <Button variant="outline" size="sm" onClick={addSet} className="mt-3">
                <Plus className="h-4 w-4 mr-1" />
                세트 추가
              </Button>
            </div>

            {/* Duration (optional for strength) */}
            <div>
              <h4 className="font-semibold text-text mb-2">운동 시간 (선택)</h4>
              <Input
                type="number"
                placeholder="분 (선택사항)"
                value={duration || ''}
                onChange={(e) => setDuration(parseInt(e.target.value) || 0)}
              />
              <p className="text-xs text-gray-500 mt-1">
                입력하지 않으면 자동으로 추정됩니다
              </p>
            </div>
            </>
            )}

            {/* Notes */}
            <div>
              <h4 className="font-semibold text-text mb-2">메모 (선택)</h4>
              <textarea
                className="w-full px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                rows={3}
                placeholder="운동에 대한 메모를 남겨보세요..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-3">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowLogForm(false)}
                disabled={isSubmitting}
              >
                취소
              </Button>
              <Button
                variant="primary"
                className="flex-1"
                onClick={submitWorkout}
                isLoading={isSubmitting}
              >
                운동 저장
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
