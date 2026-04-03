import { useEffect, useState } from 'react';
import { api } from '@/services/api';

export function useDefaultAdmin() {
  const [initialized, setInitialized] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initAdmin = async () => {
      try {
        await api.post('/api/v1/auth/init-default-admin');
        setInitialized(true);
      } catch (err: unknown) {
        if (typeof err === 'object' && err !== null && 'response' in err) {
          const maybeResponse = err as { response?: { status?: number } };
          if (maybeResponse.response?.status === 401) {
            setInitialized(true);
            return;
          }
        }

        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('Failed to initialize default admin');
        }
      }
    };

    void initAdmin();
  }, []);

  return {
    initialized,
    error,
    defaultCredentials: {
      username: 'admin',
      password: 'admin123',
    },
  };
}
