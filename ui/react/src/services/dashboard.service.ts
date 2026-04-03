import { api } from '@/services/api';

export interface PnLData {
  entity_id: string;
  period: string;
  revenue: { total_revenue: number; [k: string]: number };
  expenses: { total_expenses: number; [k: string]: number };
  profit_before_tax: number;
  tax: number;
  net_profit: number;
}

export const dashboardService = {
  async getPnL(entityId: string, period: string): Promise<PnLData> {
    const { data } = await api.get<PnLData>(`/api/v1/reports/pnl/${entityId}`, {
      params: { period },
    });
    return data;
  },
};
