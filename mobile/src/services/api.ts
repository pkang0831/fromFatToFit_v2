import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { supabase } from './auth';

// API configuration
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/** Prefer Supabase session JWT (auto-refreshed); fallback to legacy AsyncStorage key. */
async function getBearerToken(): Promise<string | null> {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      return session.access_token;
    }
  } catch (e) {
    console.error('getSession failed:', e);
  }
  return AsyncStorage.getItem('access_token');
}

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await getBearerToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - refresh once on 401, then clear session if still unauthorized
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined;
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      try {
        const { data: { session }, error: refreshErr } = await supabase.auth.refreshSession();
        if (!refreshErr && session?.access_token) {
          await AsyncStorage.setItem('access_token', session.access_token);
          if (session.refresh_token) {
            await AsyncStorage.setItem('refresh_token', session.refresh_token);
          }
          original.headers = original.headers ?? {};
          original.headers.Authorization = `Bearer ${session.access_token}`;
          return api.request(original);
        }
      } catch {
        // fall through to logout
      }
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      await supabase.auth.signOut();
    }
    return Promise.reject(error);
  }
);

// API service methods
export const authApi = {
  register: (email: string, password: string, fullName?: string) =>
    api.post('/auth/register', { email, password, full_name: fullName }),
  
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  
  logout: () =>
    api.post('/auth/logout'),
  
  getProfile: () =>
    api.get('/auth/me'),
  
  updateProfile: (data: any) =>
    api.put('/auth/profile', data),
};

export interface FoodLog {
  id: string;
  user_id: string;
  date: string;
  meal_type: string;
  food_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  serving_size?: string | null;
  source: string;
  image_url?: string | null;
  created_at: string;
}

export interface FoodDailySummary {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  calorie_goal?: number | null;
  meals: FoodLog[];
}

export interface FoodPhotoAnalysis {
  items: Array<{
    name: string;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    serving_size?: string | null;
  }>;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  analysis_confidence: string;
  usage_remaining: number;
}

export const foodApi = {
  logFood: (data: any) =>
    api.post('/food/log', data),
  
  analyzePhoto: (imageBase64: string) =>
    api.post<FoodPhotoAnalysis>('/food/analyze-photo', { image_base64: imageBase64 }),
  
  getDailyFood: (date: string) =>
    api.get<FoodDailySummary>(`/food/daily/${date}`),
  
  getTrends: (days: number = 7) =>
    api.get('/food/trends', { params: { days } }),
  
  deleteLog: (logId: string) =>
    api.delete(`/food/log/${logId}`),
};

export const workoutApi = {
  getExerciseLibrary: (category?: string) =>
    api.get('/workout/exercises/library', { params: { category } }),
  
  logWorkout: (data: any) =>
    api.post('/workout/log', data),
  
  getWorkoutLogs: (date: string) =>
    api.get(`/workout/logs/${date}`),
  
  getTrends: (days: number = 30) =>
    api.get('/workout/trends', { params: { days } }),
  
  analyzeForm: (videoBase64: string, exerciseName: string) =>
    api.post('/workout/analyze-form', { video_base64: videoBase64, exercise_name: exerciseName }),
  
  deleteLog: (logId: string) =>
    api.delete(`/workout/log/${logId}`),
};

export interface WeightLog {
  id: string;
  user_id: string;
  date: string;
  weight_kg: number;
  body_fat_percentage?: number | null;
  notes?: string | null;
  created_at: string;
}

export interface ProjectionPoint {
  date: string;
  projected_weight: number;
  projected_body_fat?: number | null;
  is_goal_reached: boolean;
}

export interface MovingAveragePoint {
  date: string;
  weight_kg: number;
  body_fat_percentage?: number | null;
  moving_avg_weight: number;
  moving_avg_body_fat?: number | null;
}

export interface GoalProjectionResponse {
  current_weight: number;
  current_body_fat?: number | null;
  target_weight?: number | null;
  target_body_fat?: number | null;
  moving_avg_weight: number;
  moving_avg_body_fat?: number | null;
  daily_weight_change: number;
  daily_body_fat_change?: number | null;
  avg_daily_deficit: number;
  target_deficit?: number | null;
  estimated_days_to_goal?: number | null;
  estimated_goal_date?: string | null;
  historical_data: MovingAveragePoint[];
  projection_data: ProjectionPoint[];
  actual_projection_data: ProjectionPoint[];
  on_track: boolean;
  message: string;
}

export const weightApi = {
  getLogs: (days: number = 30) =>
    api.get<WeightLog[]>('/weight/logs', { params: { days } }),

  createLog: (payload: {
    date: string;
    weight_kg: number;
    body_fat_percentage?: number;
    notes?: string;
  }) =>
    api.post<WeightLog>('/weight/log', payload),

  deleteLog: (logId: string) =>
    api.delete(`/weight/log/${logId}`),

  getProjection: (params?: { days_history?: number; target_deficit?: number | null }) =>
    api.get<GoalProjectionResponse>('/weight/projection', { params }),

  updateGoals: (payload: {
    target_weight_kg?: number;
    target_body_fat_percentage?: number;
  }) =>
    api.patch('/weight/goals', payload),
};

export const bodyApi = {
  estimateBodyFat: (data: any) =>
    api.post('/body/estimate-bodyfat', data),
  
  calculatePercentile: (data: any) =>
    api.post('/body/percentile', data),
  
  generateTransformation: (data: any) =>
    api.post('/body/transformation', data),
  
  getScanHistory: () =>
    api.get('/body/scans/history'),
};

export interface HomeSummary {
  primary_cta: {
    state: string;
    href: string;
    label: string;
    title: string;
    description: string;
  };
  latest_weekly_checkin?: WeeklyCheckinAnalysis | null;
  goal_summary: {
    current_bf?: number | null;
    target_bf?: number | null;
    gap?: number | null;
    has_saved_plan: boolean;
  };
  progress_summary: {
    photo_count: number;
    latest_photo_date?: string | null;
    compare_ready: boolean;
  };
  scan_summary: {
    scan_count: number;
    prompt_state: string;
    last_scan_date?: string | null;
    next_check_in_label?: string | null;
  };
}

export interface WeeklyCheckinAnalysis {
  id: string;
  taken_at: string;
  weekly_status: 'improved' | 'stable' | 'regressed' | 'low_confidence';
  comparison_confidence: number;
  is_first_checkin: boolean;
  qualitative_summary: string[];
  regional_visualization: Array<{
    region: string;
    label: string;
    value: string;
    note: string;
    status: string;
    intensity: number;
  }>;
  derived_scores: {
    goal_proximity_score: number;
    leanness_score: number;
    definition_score: number;
    proportion_score: number;
  };
  estimated_ranges: {
    body_fat_percent_min: number;
    body_fat_percent_max: number;
    body_fat_confidence: number;
  };
}

export const homeApi = {
  getSummary: () =>
    api.get<HomeSummary>('/home/summary'),
};

export const weeklyCheckinsApi = {
  getLatest: () =>
    api.get<WeeklyCheckinAnalysis>('/weekly-checkins/latest'),

  analyze: (payload: {
    image_base64: string;
    ownership_confirmed: boolean;
    notes?: string;
    weight_kg?: number;
  }) =>
    api.post<WeeklyCheckinAnalysis>('/weekly-checkins/analyze', payload),
};

export const paymentApi = {
  createCheckoutSession: (priceId: string, successUrl: string, cancelUrl: string) =>
    api.post('/payments/create-checkout-session', { price_id: priceId, success_url: successUrl, cancel_url: cancelUrl }),
  
  verifyPurchase: (receiptToken: string, platform: 'ios' | 'android') =>
    api.post('/payments/verify-purchase', { receipt_token: receiptToken, platform }),
  
  getSubscriptionStatus: () =>
    api.get('/payments/subscription'),
  
  getUsageLimits: () =>
    api.get('/payments/usage-limits'),
};

export const dashboardApi = {
  getDashboard: () =>
    api.get('/dashboard'),
  
  getQuickStats: () =>
    api.get('/dashboard/quick-stats'),
};

export default api;
