import { api } from '@/services/api';
import type { TrialBalanceReport, PnLReport, BalanceSheetReport, CashFlowReport } from '@/types/report.types';

export const reportsService = {
  async getTrialBalance(entityId: string, period: string): Promise<TrialBalanceReport> {
    const { data } = await api.get<TrialBalanceReport>(`/api/v1/reports/trial-balance/${entityId}`, {
      params: { period },
    });
    return data;
  },

  async getPnL(entityId: string, period: string): Promise<PnLReport> {
    const { data } = await api.get<PnLReport>(`/api/v1/reports/pnl/${entityId}`, {
      params: { period },
    });
    return data;
  },

  async getBalanceSheet(entityId: string, asOfDate: string): Promise<BalanceSheetReport> {
    const { data } = await api.get<BalanceSheetReport>(`/api/v1/reports/balance-sheet/${entityId}`, {
      params: { as_of_date: asOfDate },
    });
    return data;
  },

  async getCashFlow(entityId: string, startDate: string, endDate: string): Promise<CashFlowReport> {
    const { data } = await api.get<CashFlowReport>(`/api/v1/reports/cash-flow/${entityId}`, {
      params: { start_date: startDate, end_date: endDate },
    });
    return data;
  },
};
