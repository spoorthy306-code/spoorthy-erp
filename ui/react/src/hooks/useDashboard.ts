import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '@/services/dashboard.service';

export function useDashboard(entityId: string, period: string) {
  const pnlQuery = useQuery({
    queryKey: ['dashboard', 'pnl', entityId, period],
    queryFn: () => dashboardService.getPnL(entityId, period),
    enabled: Boolean(entityId) && Boolean(period),
    staleTime: 5 * 60 * 1000,
  });

  return {
    pnl: pnlQuery.data,
    isLoading: pnlQuery.isLoading,
    error: pnlQuery.error,
  };
}
