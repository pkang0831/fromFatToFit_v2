import api from './client';
import type {
  UserRegister,
  UserLogin,
  TokenResponse,
  User,
  FoodLogCreate,
  FoodLog,
  FoodAnalysisRequest,
  FoodAnalysisResponse,
  DailySummaryResponse,
  TrendResponse,
  RecentFoodsResponse,
  ExerciseLibraryItem,
  WorkoutLogCreate,
  WorkoutLog,
  WorkoutTrendResponse,
  BodyScanRequest,
  BodyFatEstimateResponse,
  PercentileResponse,
  TransformationResponse,
  EnhancementResponse,
  BodyScanHistoryItem,
  CreateCheckoutSessionRequest,
  CheckoutSessionResponse,
  SubscriptionResponse,
  UsageLimitsResponse,
  QuickStatsResponse,
  CalorieBalanceTrendResponse,
  WeightLogCreate,
  WeightLogUpdate,
  WeightLog,
  GoalUpdate,
  GoalProjectionResponse,
} from '@/types/api';

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

  resetPassword: (email: string) =>
    api.post('/auth/reset-password', { email }),
};

// Food API
export const foodApi = {
  logFood: (data: FoodLogCreate) =>
    api.post<FoodLog>('/food/log', data),

  updateLog: (logId: string, data: FoodLogCreate) =>
    api.put<FoodLog>(`/food/log/${logId}`, data),

  analyzePhoto: (data: FoodAnalysisRequest) =>
    api.post<FoodAnalysisResponse>('/food/analyze-photo', data),

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

  analyzeForm: (videoBase64: string, exerciseName: string) =>
    api.post('/workout/analyze-form', {
      video_base64: videoBase64,
      exercise_name: exerciseName,
    }),

  deleteLog: (logId: string) =>
    api.delete(`/workout/log/${logId}`),
};

// Body API
export const bodyApi = {
  estimateBodyFat: (data: BodyScanRequest) =>
    api.post<BodyFatEstimateResponse>('/body/estimate-bodyfat', data),

  calculatePercentile: (data: BodyScanRequest) =>
    api.post<PercentileResponse>('/body/percentile', data),

  generateTransformation: (data: BodyScanRequest) =>
    api.post<TransformationResponse>('/body/transformation', data),

  generateEnhancement: (data: BodyScanRequest) =>
    api.post<EnhancementResponse>('/body/enhancement', data),

  getScanHistory: () =>
    api.get<BodyScanHistoryItem[]>('/body/scans/history'),
};

// Payment API
export const paymentApi = {
  createCheckoutSession: (data: CreateCheckoutSessionRequest) =>
    api.post<CheckoutSessionResponse>('/payments/create-checkout-session', data),

  verifyPurchase: (receiptToken: string, platform: 'ios' | 'android') =>
    api.post('/payments/verify-purchase', { receipt_token: receiptToken, platform }),

  getSubscriptionStatus: () =>
    api.get<SubscriptionResponse>('/payments/subscription'),

  getUsageLimits: () =>
    api.get<UsageLimitsResponse>('/payments/usage-limits'),
};

// Dashboard API
export const dashboardApi = {
  getDashboard: () =>
    api.get('/dashboard'),

  getQuickStats: () =>
    api.get<QuickStatsResponse>('/dashboard/quick-stats'),

  getCalorieBalanceTrend: (days: number = 7) =>
    api.get<CalorieBalanceTrendResponse>('/dashboard/calorie-balance-trend', {
      params: { days }
    }),
};

// Food Database API
export const foodDatabaseApi = {
  searchFoods: (query: string, limit: number = 10, category?: string) =>
    api.get('/food-database/search', { 
      params: { q: query, limit, category } 
    }),

  getFoodDetails: (foodId: string) =>
    api.get(`/food-database/${foodId}`),

  getCategories: () =>
    api.get('/food-database/categories'),

  calculateNutrition: (foodId: string, amountGrams: number) =>
    api.post('/food-database/calculate', { 
      food_id: foodId, 
      amount_grams: amountGrams 
    }),

  getDatabaseStats: () =>
    api.get('/food-database/stats/overview'),
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

  updatePreferences: (preferences: any) =>
    api.put('/food-decision/preferences', preferences),
};

// Weight Tracking API
export const weightApi = {
  createLog: (data: WeightLogCreate) =>
    api.post<WeightLog>('/weight/log', data),

  getLogs: (days: number = 30) =>
    api.get<WeightLog[]>('/weight/logs', { params: { days } }),

  updateLog: (logId: string, data: WeightLogUpdate) =>
    api.patch<WeightLog>(`/weight/log/${logId}`, data),

  deleteLog: (logId: string) =>
    api.delete(`/weight/log/${logId}`),

  updateGoals: (goals: GoalUpdate) =>
    api.patch('/weight/goals', goals),

  getProjection: (daysHistory: number = 30) =>
    api.get<GoalProjectionResponse>('/weight/projection', {
      params: { 
        days_history: daysHistory,
        _t: Date.now()  // Cache buster
      },
    }),
};
