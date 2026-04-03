import { useMutation, useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { authService } from '@/services/auth.service';
import { useAuthStore } from '@/store/authStore';

export function useAuth() {
  const { user, isAuthenticated, setAuth, clearAuth } = useAuthStore();

  const meQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: authService.me,
    enabled: isAuthenticated,
  });

  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (data) => {
      setAuth(data.user ?? null, data.access_token);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: authService.logout,
    onSettled: () => {
      clearAuth();
    },
  });

  useEffect(() => {
    const initializeDefaultUser = async () => {
      try {
        await authService.createDefaultUser();
      } catch {
        // Ignore errors: user may already exist or endpoint may be disabled.
      }
    };

    void initializeDefaultUser();
  }, []);

  return {
    user: meQuery.data ?? user,
    isAuthenticated,
    isLoading: loginMutation.isPending || meQuery.isFetching,
    error: loginMutation.error,
    login: loginMutation.mutateAsync,
    logout: logoutMutation.mutate,
  };
}
