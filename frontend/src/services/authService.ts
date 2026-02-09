// Authentication API service
import axios from 'axios';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const API_URL = 'http://localhost:8001/api/auth';

export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
  confirm_password: string;
}

class AuthService {
  async login(request: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(`${API_URL}/login`, request);
      
      // Store token
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      throw new Error(message);
    }
  }

  async register(request: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>(`${API_URL}/register`, request);
      
      // Store token
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      return response.data;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed';
      throw new Error(message);
    }
  }

  async logout(): Promise<void> {
    // Get token BEFORE clearing localStorage
    const token = this.getToken();
    
    try {
      // Send token to blacklist it on server
      await axios.post(
        `${API_URL}/logout`,
        {},
        {
          headers: token ? { Authorization: `Bearer ${token}` } : {}
        }
      );
    } catch (error) {
      // Ignore logout errors
    } finally {
      // Always clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  getUser(): User | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const authService = new AuthService();

// Zustand store for auth state
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await authService.login({ email, password });
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (email: string, name: string, password: string, confirmPassword: string) => {
        set({ isLoading: true });
        try {
          const response = await authService.register({
            email,
            name,
            password,
            confirm_password: confirmPassword
          });
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        await authService.logout();
        set({ user: null, token: null, isAuthenticated: false });
      },

      checkAuth: () => {
        const token = authService.getToken();
        const user = authService.getUser();
        set({
          token,
          user,
          isAuthenticated: !!token && !!user
        });
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

// Axios interceptor for adding auth token
axios.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling 401 errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
