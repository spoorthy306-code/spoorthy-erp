import { useQuery } from '@tanstack/react-query';
import { reportsService } from '@/services/reports.service';

const STALE = 5 * 60 * 1000;

export function useTrialBalance(entityId: string, period: string) {
  return useQuery({
    queryKey: ['reports', 'trial-balance', entityId, period],
    queryFn: () => reportsService.getTrialBalance(entityId, period),
    enabled: Boolean(entityId) && Boolean(period),
    staleTime: STALE,
  });
}

export function usePnL(entityId: string, period: string) {
  return useQuery({
    queryKey: ['reports', 'pnl', entityId, period],
    queryFn: () => reportsService.getPnL(entityId, period),
    enabled: Boolean(entityId) && Boolean(period),
    staleTime: STALE,
  });
}

export function useBalanceSheet(entityId: string, asOfDate: string) {
  return useQuery({
    queryKey: ['reports', 'balance-sheet', entityId, asOfDate],
    queryFn: () => reportsService.getBalanceSheet(entityId, asOfDate),
    enabled: Boolean(entityId) && Boolean(asOfDate),
    staleTime: STALE,
  });
}

export function useCashFlow(entityId: string, startDate: string, endDate: string) {
  return useQuery({
    queryKey: ['reports', 'cash-flow', entityId, startDate, endDate],
    queryFn: () => reportsService.getCashFlow(entityId, startDate, endDate),
    enabled: Boolean(entityId) && Boolean(startDate) && Boolean(endDate),
    staleTime: STALE,
  });
}
