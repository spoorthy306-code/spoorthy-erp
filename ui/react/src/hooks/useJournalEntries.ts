import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getJournalService } from '@/offline/offlineJournalService';
import type {
  JournalEntryCreateRequest,
  JournalEntryListParams,
  JournalEntryUpdateRequest,
} from '@/types/journal.types';

interface UseJournalEntriesParams extends Partial<JournalEntryListParams> {
  entityId?: string;
}

export function useJournalEntries(params: UseJournalEntriesParams = {}, selectedEntryId?: string) {
  const journalEntriesService = getJournalService();
  const queryClient = useQueryClient();
  const normalizedParams: JournalEntryListParams = {
    entityId: params.entityId ?? '',
    period: params.period,
    skip: params.skip,
    limit: params.limit,
  };

  const listQuery = useQuery({
    queryKey: ['journal-entries', normalizedParams],
    queryFn: () => journalEntriesService.list(normalizedParams),
    enabled: Boolean(normalizedParams.entityId),
  });

  const detailQuery = useQuery({
    queryKey: ['journal-entry', selectedEntryId],
    queryFn: () => journalEntriesService.getById(selectedEntryId as string),
    enabled: Boolean(selectedEntryId),
  });

  const createMutation = useMutation({
    mutationFn: (payload: JournalEntryCreateRequest) => journalEntriesService.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ entryId, payload }: { entryId: string; payload: JournalEntryUpdateRequest }) =>
      journalEntriesService.update(entryId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
      queryClient.invalidateQueries({ queryKey: ['journal-entry', variables.entryId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (entryId: string) => journalEntriesService.delete(entryId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
    },
  });

  const reconcileMutation = useMutation({
    mutationFn: (entityId: string) => journalEntriesService.reconcile(entityId),
  });

  return {
    entries: listQuery.data ?? [],
    selectedEntry: detailQuery.data ?? null,
    isLoading: listQuery.isLoading,
    isFetchingDetail: detailQuery.isFetching,
    error: listQuery.error ?? detailQuery.error ?? createMutation.error ?? null,
    createEntry: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateEntry: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteEntry: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
    reconcileEntity: reconcileMutation.mutateAsync,
    isReconciling: reconcileMutation.isPending,
  };
}
