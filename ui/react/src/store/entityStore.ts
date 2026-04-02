import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Entity {
  entity_id: string;
  name: string;
  gstin: string | null;
  pan: string | null;
  currency: string;
  reporting_currency: string;
}

interface EntityStore {
  entities: Entity[];
  selectedEntity: Entity | null;
  loading: boolean;
  setEntities: (entities: Entity[]) => void;
  setSelectedEntity: (entity: Entity) => void;
  setLoading: (loading: boolean) => void;
}

export const useEntityStore = create<EntityStore>()(
  persist(
    (set) => ({
      entities:       [],
      selectedEntity: null,
      loading:        false,
      setEntities:    (entities) => set({ entities }),
      setSelectedEntity: (entity) => set({ selectedEntity: entity }),
      setLoading:     (loading) => set({ loading }),
    }),
    {
      name: 'spoorthy-entity',
      partialize: (state) => ({ selectedEntity: state.selectedEntity }),
    }
  )
);
