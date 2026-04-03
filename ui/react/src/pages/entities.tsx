import { useState, useMemo } from 'react';
import { EntityForm } from '@/components/entities/EntityForm';
import { EntityList } from '@/components/entities/EntityList';
import { useEntities } from '@/hooks/useEntities';
import type { Entity, EntityCreate } from '@/types';

export default function EntitiesPage() {
  const [search, setSearch] = useState('');
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null);
  const [showForm, setShowForm] = useState(false);

  const { entities, isLoading, createEntity, isCreating, updateEntity, isUpdating, deleteEntity, isDeleting } =
    useEntities(0, 100, search || undefined);

  const debouncedSearch = useMemo(() => search, [search]);
  void debouncedSearch;

  const handleCreate = async (payload: EntityCreate) => {
    await createEntity(payload);
    setShowForm(false);
  };

  const handleUpdate = async (payload: EntityCreate) => {
    if (!editingEntity) return;
    await updateEntity({ entityId: editingEntity.entity_id, payload });
    setEditingEntity(null);
  };

  const handleEdit = (entity: Entity) => {
    setEditingEntity(entity);
    setShowForm(false);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingEntity(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">Entities</h1>
            <p className="mt-1 text-sm text-slate-500">
              Manage customers, vendors, and business entities.
            </p>
          </div>
          <button
            type="button"
            onClick={() => { setShowForm((v) => !v); setEditingEntity(null); }}
            className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white"
          >
            {showForm ? 'Hide Form' : '+ New Entity'}
          </button>
        </div>

        {/* Search */}
        <div className="mt-4">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, GSTIN, or PAN…"
            className="focus-ring w-full max-w-sm rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
      </section>

      {/* Create form */}
      {showForm && (
        <EntityForm
          onSubmit={handleCreate}
          onCancel={handleCancelForm}
          isSubmitting={isCreating}
        />
      )}

      {/* Edit form */}
      {editingEntity && (
        <EntityForm
          entity={editingEntity}
          onSubmit={handleUpdate}
          onCancel={handleCancelForm}
          isSubmitting={isUpdating}
        />
      )}

      {/* List */}
      {isLoading ? (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500">
          Loading entities…
        </div>
      ) : (
        <EntityList
          items={entities}
          onEdit={handleEdit}
          onDelete={deleteEntity}
          isDeleting={isDeleting}
        />
      )}
    </div>
  );
}
