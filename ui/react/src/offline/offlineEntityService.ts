import { invoke } from '@tauri-apps/api/core';
import { entitiesService } from '@/services/entities.service';
import type { Entity, EntityCreate } from '@/types';
import { IS_TAURI } from './tauriBridge';

interface EntityService {
  list: (skip?: number, limit?: number, search?: string) => Promise<Entity[]>;
  get: (entityId: string) => Promise<Entity>;
  create: (payload: EntityCreate) => Promise<Entity>;
  update: (entityId: string, payload: EntityCreate) => Promise<Entity>;
  delete: (entityId: string) => Promise<void>;
}

const tauriEntityService: EntityService = {
  async list(skip = 0, limit = 100, search) {
    return invoke<Entity[]>('list_entities', { skip, limit, search: search ?? null });
  },

  async get(entityId) {
    const found = await invoke<Entity | null>('get_entity', { entityId });
    if (!found) {
      throw new Error(`Entity ${entityId} not found in local database.`);
    }
    return found;
  },

  async create(payload) {
    return invoke<Entity>('create_entity', { payload });
  },

  async update(entityId, payload) {
    return invoke<Entity>('update_entity', { entityId, payload });
  },

  async delete(entityId) {
    await invoke('delete_entity', { entityId });
  },
};

export function getEntityService(): EntityService {
  return IS_TAURI ? tauriEntityService : entitiesService;
}
