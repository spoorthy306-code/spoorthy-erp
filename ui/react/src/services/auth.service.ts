import { api } from '@/services/api';
import type { AuthResponse, LoginRequest, User } from '@/types';

export const DEFAULT_ADMIN = {
  username: 'admin',
  password: 'admin123',
  email: 'spoorthy306@gmail.com',
} as const;

type DefaultUserPayload = {
  username: string;
  password: string;
  email: string;
};

export const authService = {
  async login(payload: LoginRequest): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', payload);
    return data;
  },

  async me(): Promise<User> {
    const { data } = await api.get<User>('/auth/me');
    return data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  async createDefaultUser(payload: DefaultUserPayload = DEFAULT_ADMIN): Promise<void> {
    await api.post('/api/v1/auth/init-default-admin', payload);
  },
};
