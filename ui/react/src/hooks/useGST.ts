import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { gstService } from '@/services/gst.service';
import type { GSTReturnCreate } from '@/types/gst.types';

const STALE = 5 * 60 * 1000;

export function useGSTReturns(entityId: string, period?: string) {
  const queryClient = useQueryClient();

  const returnsQuery = useQuery({
    queryKey: ['gst-returns', entityId, period],
    queryFn: () => gstService.list(entityId, period),
    enabled: Boolean(entityId),
    staleTime: STALE,
  });

  const createMutation = useMutation({
    mutationFn: (payload: GSTReturnCreate) => gstService.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['gst-returns', entityId] });
    },
  });

  const fileMutation = useMutation({
    mutationFn: (returnId: string) => gstService.file(returnId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['gst-returns', entityId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (returnId: string) => gstService.delete(returnId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['gst-returns', entityId] });
    },
  });

  return {
    returns: returnsQuery.data ?? [],
    isLoading: returnsQuery.isLoading,
    error: returnsQuery.error,
    createReturn: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    fileReturn: fileMutation.mutateAsync,
    isFiling: fileMutation.isPending,
    deleteReturn: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}

export function useGSTSummary(entityId: string, period: string) {
  return useQuery({
    queryKey: ['gst-summary', entityId, period],
    queryFn: () => gstService.getGSTSummary(entityId, period),
    enabled: Boolean(entityId) && Boolean(period),
    staleTime: STALE,
  });
}

export function useComplianceStatus(entityId: string) {
  return useQuery({
    queryKey: ['compliance-status', entityId],
    queryFn: () => gstService.getComplianceStatus(entityId),
    enabled: Boolean(entityId),
    staleTime: STALE,
  });
}
