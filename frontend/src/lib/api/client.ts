import axios, { AxiosInstance, AxiosError } from 'axios';

// API configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
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
      // Token expired or invalid - trigger session expired event
      if (typeof window !== 'undefined') {
        // Dispatch custom event for AuthContext to handle
        window.dispatchEvent(new Event('session-expired'));
        
        // Clear storage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Don't redirect here - let AuthContext handle the UI
      }
    }
    return Promise.reject(error);
  }
);

export default api;
