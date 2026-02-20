import axios, { AxiosInstance, AxiosError } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

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

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('access_token');
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

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear storage and redirect to login
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user']);
      // You can emit an event here to trigger navigation to login
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

export const foodApi = {
  logFood: (data: any) =>
    api.post('/food/log', data),
  
  analyzePhoto: (imageBase64: string) =>
    api.post('/food/analyze-photo', { image_base64: imageBase64 }),
  
  getDailyFood: (date: string) =>
    api.get(`/food/daily/${date}`),
  
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
