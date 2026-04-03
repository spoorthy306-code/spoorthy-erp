import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';

const ACCESS_TOKEN_KEY = 'access_token';

export const DEFAULT_CREDENTIALS = {
  username: 'admin',
  password: 'admin123',
  email: 'spoorthy306@gmail.com',
} as const;

interface AuthStore {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  defaultCredentials: typeof DEFAULT_CREDENTIALS;
  setAuth: (user: User | null, accessToken: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      defaultCredentials: DEFAULT_CREDENTIALS,

      setAuth: (user, accessToken) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
        set({ user, accessToken, isAuthenticated: true });
      },

      clearAuth: () => {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        set({ user: null, accessToken: null, isAuthenticated: false });
      },
    }),
    {
      name: 'spoorthy-auth',
    }
  )
);
