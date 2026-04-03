import { api } from '@/services/api';
import type { Account } from '@/types/account.types';

export const chartOfAccountsService = {
  async list(entityId: string, activeOnly = true): Promise<Account[]> {
    const { data } = await api.get<Account[]>(`/api/v1/chart-of-accounts/${entityId}`, {
      params: { active_only: activeOnly },
    });
    return data;
  },

  async hierarchy(entityId: string): Promise<Account[]> {
    const { data } = await api.get<Account[]>(`/api/v1/chart-of-accounts/${entityId}/hierarchy`);
    return data;
  },
};
