import { useQuery } from '@tanstack/react-query';
import { chartOfAccountsService } from '@/services/chartOfAccounts.service';

const STALE = 10 * 60 * 1000;

export function useChartOfAccounts(entityId: string) {
  const flatQuery = useQuery({
    queryKey: ['chart-of-accounts', entityId],
    queryFn: () => chartOfAccountsService.list(entityId),
    enabled: Boolean(entityId),
    staleTime: STALE,
  });

  const hierarchyQuery = useQuery({
    queryKey: ['chart-of-accounts-hierarchy', entityId],
    queryFn: () => chartOfAccountsService.hierarchy(entityId),
    enabled: Boolean(entityId),
    staleTime: STALE,
  });

  return {
    accounts: flatQuery.data ?? [],
    hierarchy: hierarchyQuery.data ?? [],
    isLoading: flatQuery.isLoading || hierarchyQuery.isLoading,
    error: flatQuery.error ?? hierarchyQuery.error,
  };
}
