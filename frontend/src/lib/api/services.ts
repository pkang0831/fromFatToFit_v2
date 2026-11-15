import api from './client';
import type {
  UserRegister,
  UserLogin,
  TokenResponse,
  User,
  FoodLogCreate,
  FoodLog,
  BeautyAnalyzeRequest,
  BeautyAnalyzeResponse,
  FashionRecommendRequest,
  FashionRecommendResponse,
  DailySummaryResponse,
  TrendResponse,
  RecentFoodsResponse,
  ExerciseLibraryItem,
  WorkoutLogCreate,
  WorkoutLog,
  WorkoutTrendResponse,
  BodyScanRequest,
  BodyPhotoQualityRequest,
  BodyPhotoQualityResponse,
  PercentileResponse,
  TransformationJourneyResponse,
  AccountDeletionResponse,
  CreateCheckoutSessionRequest,
  CheckoutSessionResponse,
  SubscriptionResponse,
  BillingPortalSessionResponse,
  UsageLimitsResponse,
  CalorieBalanceTrendResponse,
  WeightLogCreate,
  WeightLog,
  GoalUpdate,
  GoalProjectionResponse,
  HomeSummaryResponse,
  ReminderStatusResponse,
  ProgressPhoto,
  ProgressPhotoCompareResponse,
  ProofShareResponse,
  WeeklyCheckinAnalysisResponse,
  WeeklyCheckinCreateRequest,
} from '@/types/api';

// Guest API (no auth required)
export const guestApi = {
  bodyScan: (data: {
    image_base64: string;
    gender: string;
    age: number;
    ownership_confirmed?: boolean;
    adult_confirmed?: boolean;
    framing?: 'upper_body' | 'full_body';
  }) =>
    api.post<{ body_fat_percentage: number; confidence: string; category: string; insight: string }>('/guest/body-scan', data),

  validatePhoto: (data: BodyPhotoQualityRequest) =>
    api.post<BodyPhotoQualityResponse>('/guest/validate-photo', data),
};

// Auth API
export const authApi = {
  register: (data: UserRegister) =>
    api.post<TokenResponse>('/auth/register', data),

  login: (data: UserLogin) =>
    api.post<TokenResponse>('/auth/login', data),

  logout: () =>
    api.post('/auth/logout'),

  getProfile: () =>
    api.get<User>('/auth/me'),

  updateProfile: (data: Partial<User>) =>
    api.put<User>('/auth/profile', data),

  deleteAccount: () =>
    api.delete<AccountDeletionResponse>('/auth/account'),
};

// Food API
export const foodApi = {
  logFood: (data: FoodLogCreate) =>
    api.post<FoodLog>('/food/log', data),

  updateLog: (logId: string, data: FoodLogCreate) =>
    api.put<FoodLog>(`/food/log/${logId}`, data),

  getDailyFood: (date: string) =>
    api.get<DailySummaryResponse>(`/food/daily/${date}`),

  getTrends: (days: number = 7) =>
    api.get<TrendResponse>('/food/trends', { params: { days } }),

  getRecentFoods: (days: number = 7, limit: number = 10) =>
    api.get<RecentFoodsResponse>('/food/recent', { params: { days, limit } }),

  deleteLog: (logId: string) =>
    api.delete(`/food/log/${logId}`),
};

// Workout API
export const workoutApi = {
  getExerciseLibrary: (category?: string) =>
    api.get<ExerciseLibraryItem[]>('/workout/exercises/library', {
      params: category ? { category } : undefined,
    }),

  logWorkout: (data: WorkoutLogCreate) =>
    api.post<WorkoutLog>('/workout/log', data),

  getWorkoutLogs: (date: string) =>
    api.get<WorkoutLog[]>(`/workout/logs/${date}`),

  // Bulk API: Get logs for date range (10x faster than individual calls)
  getWorkoutLogsRange: (startDate: string, endDate: string) =>
    api.get<WorkoutLog[]>('/workout/logs-range', {
      params: { start_date: startDate, end_date: endDate },
    }),

  getTrends: (days: number = 30) =>
    api.get<WorkoutTrendResponse>('/workout/trends', { params: { days } }),

  deleteLog: (logId: string) =>
    api.delete(`/workout/log/${logId}`),
};

// Body API
export const bodyApi = {
  validatePhoto: (data: BodyPhotoQualityRequest) =>
    api.post<BodyPhotoQualityResponse>('/body/validate-photo', data),

  calculatePercentile: (data: BodyScanRequest) =>
    api.post<PercentileResponse>('/body/percentile', data),

  generateTransformation: (data: BodyScanRequest) =>
    api.post<TransformationJourneyResponse>('/body/transformation', data),

  getGapToGoal: () =>
    api.get<import('@/types/api').GapToGoalResponse>('/body/gap-to-goal'),
};

// Payment API
export const paymentApi = {
  createCheckoutSession: (data: CreateCheckoutSessionRequest) =>
    api.post<CheckoutSessionResponse>('/payments/create-checkout-session', data),

  getSubscriptionStatus: () =>
    api.get<SubscriptionResponse>('/payments/subscription'),

  createBillingPortalSession: (returnUrl: string) =>
    api.post<BillingPortalSessionResponse>('/payments/billing-portal', { return_url: returnUrl }),

  getUsageLimits: () =>
    api.get<UsageLimitsResponse>('/payments/usage-limits'),

  getCreditBalance: () =>
    api.get('/payments/credits'),

  buyCreditPack: (data: { pack_size: number; success_url: string; cancel_url: string }) =>
    api.post<CheckoutSessionResponse>('/payments/buy-credits', data),
};

// Dashboard API
export const dashboardApi = {
  getCalorieBalanceTrend: (days: number = 7) =>
    api.get<CalorieBalanceTrendResponse>('/dashboard/calorie-balance-trend', {
      params: { days }
    }),
};

export const homeApi = {
  getSummary: (source?: string) =>
    api.get<HomeSummaryResponse>('/home/summary', {
      params: source ? { source } : undefined,
    }),
};

export const weeklyCheckinsApi = {
  analyze: (data: WeeklyCheckinCreateRequest) =>
    api.post<WeeklyCheckinAnalysisResponse>('/weekly-checkins/analyze', data),
};

export const analyticsApi = {
  captureRetentionEvent: (data: {
    event_name:
      | 'scan_success'
      | 'reengagement_session'
      | 'history_viewed'
      | 'notification_sent'
      | 'notification_opened'
      | 'progress_proof_started'
      | 'progress_proof_completed'
      | 'proof_upload_failed'
      | 'progress_compare_viewed'
      | 'progress_checkin_started'
      | 'progress_checkin_completed'
      | 'progress_checkin_failed'
      | 'share_created'
      | 'share_viewed'
      | 'share_revoked'
      | 'referred_try_started'
      | 'register_completed'
      | 'purchase_completed';
    surface: string;
    properties?: Record<string, string | number | boolean | null>;
  }) => api.post('/analytics/retention', data),
};

// Food Database API
export const foodDatabaseApi = {
  searchFoods: (query: string, limit: number = 10, category?: string) =>
    api.get('/food-database/search', { 
      params: { q: query, limit, category } 
    }),

  lookupBarcode: (barcode: string) =>
    api.get(`/food-database/barcode/${barcode}`),

  searchExternal: (query: string, limit?: number) =>
    api.get('/food-database/search-external', { params: { q: query, limit: limit || 10 } }),
};

// Food Decision API (AI-powered food decisions and recommendations)
export const foodDecisionApi = {
  shouldIEat: (imageBase64: string) =>
    api.post('/food-decision/should-i-eat', {
      image_base64: imageBase64,
    }),

  recommendFoods: (mealType: string, justAteFoodId?: string) =>
    api.post('/food-decision/recommend', {
      meal_type: mealType,
      just_ate_food_id: justAteFoodId,
    }),

  getPreferences: () =>
    api.get('/food-decision/preferences'),

  updatePreferences: <T extends object>(preferences: T) =>
    api.put('/food-decision/preferences', preferences),
};

// Notification API
export const notificationApi = {
  getPreferences: () =>
    api.get('/notifications/preferences'),

  getReminderStatus: () =>
    api.get<ReminderStatusResponse>('/notifications/reminder-status'),

  updatePreferences: <T extends object>(data: T) =>
    api.put('/notifications/preferences', data),

  subscribePush: (subscription: PushSubscriptionJSON) =>
    api.post('/notifications/push/subscribe', subscription),

  unsubscribePush: (endpoint: string) =>
    api.post('/notifications/push/unsubscribe', { endpoint }),
};

// Weight Tracking API
export const weightApi = {
  createLog: (data: WeightLogCreate) =>
    api.post<WeightLog>('/weight/log', data),

  updateGoals: (goals: GoalUpdate) =>
    api.patch('/weight/goals', goals),

  getProjection: (daysHistory: number = 30, targetDeficit?: number) =>
    api.get<GoalProjectionResponse>('/weight/projection', {
      params: { 
        days_history: daysHistory,
        ...(targetDeficit !== undefined && { target_deficit: targetDeficit }),
      },
    }),
};

// Chat API (AI Coach)
export const chatApi = {
  sendMessage: (message: string) =>
    api.post<{ answer: string; sources: string[]; messages_today: number; daily_limit: number }>('/chat/message', { message }),

  getHistory: (limit: number = 50) =>
    api.get<{ id: string; role: string; content: string; sources: string[]; created_at: string }[]>('/chat/history', {
      params: { limit },
    }),

  clearHistory: () =>
    api.delete('/chat/history'),

  getStatus: () =>
    api.get<{ messages_today: number; daily_limit: number; remaining: number }>('/chat/status'),
};

// Progress Photos API
export const progressPhotoApi = {
  upload: (imageBase64: string, notes?: string, weightKg?: number, bodyFatPct?: number) =>
    api.post<ProgressPhoto>('/progress-photos', { image_base64: imageBase64, notes, weight_kg: weightKg, body_fat_pct: bodyFatPct }),
  getAll: () => api.get<ProgressPhoto[]>('/progress-photos'),
  getOne: (id: string) => api.get<ProgressPhoto>(`/progress-photos/${id}`),
  delete: (id: string) => api.delete(`/progress-photos/${id}`),
  compare: (id1: string, id2: string) => api.get<ProgressPhotoCompareResponse>(`/progress-photos/compare/${id1}/${id2}`),
};

export const proofShareApi = {
  create: (
    progressPhotoId: string,
    weekMarker?: number,
    context?: {
      sessionId?: string;
      source?: string;
      reentryState?: string;
      surfaceState?: string;
      reminderEventId?: string;
    },
  ) =>
    api.post<ProofShareResponse>('/proof-shares', {
      progress_photo_id: progressPhotoId,
      week_marker: weekMarker,
      session_id: context?.sessionId,
      source: context?.source,
      reentry_state: context?.reentryState,
      surface_state: context?.surfaceState,
      reminder_event_id: context?.reminderEventId,
    }),
  getAll: (progressPhotoId?: string) =>
    api.get<ProofShareResponse[]>('/proof-shares', {
      params: progressPhotoId ? { progress_photo_id: progressPhotoId } : undefined,
    }),
  revoke: (shareId: string) => api.delete<{ message: string }>(`/proof-shares/${shareId}`),
};

// Fasting API
export const fastingApi = {
  getCurrent: () => api.get('/fasting/current'),
  startFast: (protocol: string, targetHours?: number) =>
    api.post('/fasting/start', { protocol, target_hours: targetHours }),
  endFast: (notes?: string) => api.post('/fasting/end', { notes }),
  getHistory: (days?: number) => api.get('/fasting/history', { params: { days: days || 30 } }),
};

// Beauty API
export const beautyApi = {
  analyze: (data: BeautyAnalyzeRequest) =>
    api.post<BeautyAnalyzeResponse>('/beauty/analyze', data),
};

// Fashion API
export const fashionApi = {
  recommend: (data: FashionRecommendRequest) =>
    api.post<FashionRecommendResponse>('/fashion/recommend', data),
};

// Goal Planner API (interactive wizard)
export const goalPlanApi = {
  compareTiers: (data: {
    current_weight_kg: number;
    current_bf_pct: number;
    target_weight_kg?: number;
    target_bf_pct: number;
    gender: 'male' | 'female';
    age: number;
    height_cm: number;
    activity_level: string;
  }) => api.post('/goal-plan/tiers', data),

  getMacros: (data: {
    daily_calories: number;
    weight_kg: number;
    preset?: string;
    carb_pct?: number;
    protein_pct?: number;
    fat_pct?: number;
  }) => api.post('/goal-plan/macros', data),

  recommendMeals: (data: {
    daily_calories: number;
    protein_g: number;
    carb_g: number;
    fat_g: number;
    meals_per_day?: number;
  }) => api.post('/goal-plan/recommend-meals', data),

  getExerciseRoutine: (data: {
    mode: string;
    gender: 'male' | 'female';
    experience?: string;
    available_equipment?: string[];
    sessions_per_week?: number;
  }) => api.post('/goal-plan/exercise', data),

  getCardioPlan: (data: {
    weight_kg: number;
    gender: 'male' | 'female';
    height_cm: number;
    age: number;
    target_calories: number;
    preferred_activities?: string[];
  }) => api.post('/goal-plan/cardio', data),

  savePlan: (data: { plan: Record<string, unknown> }) =>
    api.post<{ status: 'ok'; updated_at: string }>('/goal-plan/saved-plan', data),

  getSavedPlan: () =>
    api.get<{ plan: Record<string, unknown>; updated_at: string }>('/goal-plan/saved-plan'),
};

export const challengeApi = {
  startSevenDay: (data?: {
    ai_weeks_snapshot?: number;
    ai_current_bf?: number;
    ai_target_bf?: number;
  }) => api.post<{ challenge: Record<string, unknown> }>('/challenge/seven-day/start', data ?? {}),

  getSevenDay: () =>
    api.get<{
      challenge: Record<string, unknown> | null;
      checkins: Array<{
        calendar_date: string;
        weight_kg?: number | null;
        body_fat_pct?: number | null;
        checked_at: string;
      }>;
      day_index: number;
      identity_message: string | null;
      week_one_compare: Record<string, unknown> | null;
    }>('/challenge/seven-day'),

  checkinSevenDay: (data?: { weight_kg?: number; body_fat_pct?: number }) =>
    api.post<{ ok: boolean; duplicate?: boolean; message?: string }>(
      '/challenge/seven-day/checkin',
      data ?? {},
    ),
};
