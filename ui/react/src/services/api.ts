import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, API_TIMEOUT } from '@/utils/constants';

const ACCESS_TOKEN_KEY = 'access_token';
let isRefreshing = false;
let waitingQueue: Array<(token: string | null) => void> = [];

function resolveQueue(token: string | null) {
  waitingQueue.forEach((cb) => cb(token));
  waitingQueue = [];
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  withCredentials: true,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers['Content-Type'] = 'application/json';
  config.headers['X-Request-ID'] = crypto.randomUUID();
  return config;
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    console.error('[API Error]', {
      url: original?.url,
      method: original?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
    });

    if (error.response?.status !== 401 || original?._retry) {
      if (error.response?.status === 500 && typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('api:server-error'));
      }
      return Promise.reject(error);
    }

    original._retry = true;

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        waitingQueue.push((newToken) => {
          if (!newToken) {
            reject(error);
            return;
          }
          original.headers.Authorization = `Bearer ${newToken}`;
          resolve(api(original));
        });
      });
    }

    isRefreshing = true;

    try {
      const refresh = await axios.post(
        `${API_BASE_URL}/auth/refresh`,
        {},
        { withCredentials: true }
      );
      const newToken = refresh.data?.access_token as string;
      localStorage.setItem(ACCESS_TOKEN_KEY, newToken);
      resolveQueue(newToken);
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (refreshError) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      resolveQueue(null);
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);
