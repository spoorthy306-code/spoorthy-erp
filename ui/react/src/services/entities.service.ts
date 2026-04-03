import { api } from '@/services/api';
import type { Entity, EntityCreate } from '@/types';

export const entitiesService = {
  async list(skip = 0, limit = 100, search?: string): Promise<Entity[]> {
    const params: Record<string, string | number> = { skip, limit };
    if (search) params.search = search;
    const { data } = await api.get<Entity[]>('/api/v1/entities', { params });
    return data;
  },

  async get(entityId: string): Promise<Entity> {
    const { data } = await api.get<Entity>(`/api/v1/entities/${entityId}`);
    return data;
  },

  async create(entity: EntityCreate): Promise<Entity> {
    const { data } = await api.post<Entity>('/api/v1/entities', entity);
    return data;
  },

  async update(entityId: string, entity: EntityCreate): Promise<Entity> {
    const { data } = await api.put<Entity>(`/api/v1/entities/${entityId}`, entity);
    return data;
  },

  async delete(entityId: string): Promise<void> {
    await api.delete(`/api/v1/entities/${entityId}`);
  },
};
