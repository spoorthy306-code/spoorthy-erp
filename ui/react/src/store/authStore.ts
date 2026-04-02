import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface AuthUser {
  user_id: string;
  username: string;
  email: string;
  roles: string[];
}

interface AuthStore {
  user: AuthUser | null;
  token: string | null;
  refreshToken: string | null;
  permissions: string[];
  setAuth: (user: AuthUser, token: string, refreshToken?: string) => void;
  clearAuth: () => void;
  hasRole: (role: string) => boolean;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user:         null,
      token:        null,
      refreshToken: null,
      permissions:  [],

      setAuth: (user, token, refreshToken) =>
        set({ user, token, refreshToken: refreshToken ?? null, permissions: user.roles }),

      clearAuth: () =>
        set({ user: null, token: null, refreshToken: null, permissions: [] }),

      hasRole: (role) => get().permissions.includes(role),
    }),
    {
      name: 'spoorthy-auth',
      partialize: (state) => ({
        user:         state.user,
        token:        state.token,
        refreshToken: state.refreshToken,
        permissions:  state.permissions,
      }),
    }
  )
);
