import { useState, useEffect, useCallback } from 'react';

export interface Entity {
  entity_id: string;
  name: string;
  gstin: string | null;
  pan: string | null;
  currency: string;
  reporting_currency: string;
  created_at: string;
}

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';
const STORAGE_KEY = 'spoorthy_selected_entity_id';

export function useEntityData(): {
  entities: Entity[];
  selectedEntity: Entity | null;
  setSelectedEntity: (entity: Entity) => void;
  loading: boolean;
  error: string | null;
  refresh: () => void;
} {
  const [entities, setEntities]               = useState<Entity[]>([]);
  const [selectedEntity, _setSelectedEntity]  = useState<Entity | null>(null);
  const [loading, setLoading]                 = useState(false);
  const [error, setError]                     = useState<string | null>(null);

  const fetchEntities = useCallback(async (): Promise<void> => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${API_BASE}/entities/`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as Entity[];
      setEntities(data);

      // Restore persisted selection or default to first
      const savedId = localStorage.getItem(STORAGE_KEY);
      const saved = data.find((e) => e.entity_id === savedId);
      _setSelectedEntity(saved ?? data[0] ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load entities');
    } finally {
      setLoading(false);
    }
  }, []);

  const setSelectedEntity = useCallback((entity: Entity): void => {
    _setSelectedEntity(entity);
    localStorage.setItem(STORAGE_KEY, entity.entity_id);
  }, []);

  useEffect(() => { void fetchEntities(); }, [fetchEntities]);

  return { entities, selectedEntity, setSelectedEntity, loading, error, refresh: fetchEntities };
}
