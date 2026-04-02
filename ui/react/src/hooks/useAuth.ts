import { useState, useCallback, useEffect } from 'react';

export interface AuthUser {
  user_id: string;
  username: string;
  email: string;
  roles: string[];
}

export interface AuthState {
  user: AuthUser | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

function parseJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = atob(parts[1].replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(payload) as Record<string, unknown>;
  } catch {
    return null;
  }
}

function isTokenExpired(token: string): boolean {
  const payload = parseJwtPayload(token);
  if (!payload || typeof payload.exp !== 'number') return true;
  return Date.now() / 1000 > payload.exp;
}

export function useAuth(): AuthState & {
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
} {
  const [user, setUser]       = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  // On mount — restore session from localStorage
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token && !isTokenExpired(token)) {
      const payload = parseJwtPayload(token);
      if (payload) {
        setUser({
          user_id:  String(payload.sub ?? ''),
          username: String(payload.username ?? payload.sub ?? ''),
          email:    String(payload.email ?? ''),
          roles:    Array.isArray(payload.roles) ? (payload.roles as string[]) : [],
        });
      }
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      const body = new URLSearchParams({ username, password });
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body.toString(),
      });

      if (!res.ok) {
        const detail = ((await res.json()) as { detail?: string }).detail ?? 'Login failed';
        setError(detail);
        return false;
      }

      const data = (await res.json()) as {
        access_token: string;
        refresh_token?: string;
        token_type: string;
      };

      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);

      const payload = parseJwtPayload(data.access_token);
      if (payload) {
        setUser({
          user_id:  String(payload.sub ?? ''),
          username: String(payload.username ?? payload.sub ?? ''),
          email:    String(payload.email ?? ''),
          roles:    Array.isArray(payload.roles) ? (payload.roles as string[]) : [],
        });
      }
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login error');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback((): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setError(null);
  }, []);

  return {
    user,
    isAuthenticated: user !== null,
    loading,
    error,
    login,
    logout,
  };
}
