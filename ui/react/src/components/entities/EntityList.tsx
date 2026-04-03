import { useState } from 'react';
import type { Entity } from '@/types';

interface Props {
  items: Entity[];
  onEdit: (entity: Entity) => void;
  onDelete: (entityId: string) => Promise<void>;
  isDeleting?: boolean;
}

export function EntityList({ items, onEdit, onDelete, isDeleting }: Props) {
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const handleDelete = async (entityId: string) => {
    await onDelete(entityId);
    setConfirmDeleteId(null);
  };

  if (!items.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500">
        No entities found. Create one using the form above.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">GSTIN</th>
            <th className="px-4 py-3">PAN</th>
            <th className="px-4 py-3">City / State</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.entity_id} className="border-t border-slate-200 hover:bg-slate-50 transition">
              <td className="px-4 py-3 font-medium text-ink">{item.name}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{item.gstin ?? '—'}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{item.pan ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">
                {[item.address?.city, item.address?.state].filter(Boolean).join(', ') || '—'}
              </td>
              <td className="px-4 py-3 text-right">
                {confirmDeleteId === item.entity_id ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="text-xs text-slate-500">Delete?</span>
                    <button
                      type="button"
                      onClick={() => void handleDelete(item.entity_id)}
                      disabled={isDeleting}
                      className="focus-ring rounded px-2 py-1 text-xs font-medium text-danger hover:underline disabled:opacity-60"
                    >
                      Yes
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmDeleteId(null)}
                      className="focus-ring rounded px-2 py-1 text-xs font-medium text-slate-600 hover:underline"
                    >
                      No
                    </button>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => onEdit(item)}
                      className="focus-ring text-xs font-medium text-brand hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmDeleteId(item.entity_id)}
                      className="focus-ring text-xs font-medium text-danger hover:underline"
                    >
                      Delete
                    </button>
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
