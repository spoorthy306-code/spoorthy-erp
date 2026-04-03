import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getEntityService } from '@/offline/offlineEntityService';
import type { Entity, EntityCreate } from '@/types';

export function useEntities(skip = 0, limit = 100, search?: string) {
  const entitiesService = getEntityService();
  const queryClient = useQueryClient();

  const entitiesQuery = useQuery({
    queryKey: ['entities', skip, limit, search],
    queryFn: () => entitiesService.list(skip, limit, search),
  });

  const createMutation = useMutation({
    mutationFn: (payload: EntityCreate) => entitiesService.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['entities'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ entityId, payload }: { entityId: string; payload: EntityCreate }) =>
      entitiesService.update(entityId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['entities'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (entityId: string) => entitiesService.delete(entityId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['entities'] });
    },
  });

  return {
    entities: entitiesQuery.data ?? [] as Entity[],
    isLoading: entitiesQuery.isLoading,
    error: entitiesQuery.error,
    createEntity: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateEntity: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteEntity: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
