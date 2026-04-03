import { useState } from 'react';
import { useEntities } from '@/hooks/useEntities';
import { useGSTReturns, useGSTSummary } from '@/hooks/useGST';
import { GSTReturnList } from '@/components/gst/GSTReturnList';
import { GSTReturnForm } from '@/components/gst/GSTReturnForm';
import { formatINR } from '@/utils/formatters';
import type { GSTReturnCreate } from '@/types/gst.types';

function currentPeriod() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

export default function GSTPage() {
  const [entityId, setEntityId] = useState('');
  const [period, setPeriod] = useState(currentPeriod());
  const [showForm, setShowForm] = useState(false);

  const { entities } = useEntities(0, 200);
  const { createReturn, isCreating } = useGSTReturns(entityId, period);
  const { data: summary, isLoading: summaryLoading } = useGSTSummary(entityId, period);

  const handleCreate = async (payload: GSTReturnCreate) => {
    await createReturn(payload);
    setShowForm(false);
  };

  const gstSummary = summary as Record<string, unknown> | undefined;

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">GST Compliance</h1>
            <p className="mt-1 text-sm text-slate-500">
              Manage GSTR-1, GSTR-3B, and annual returns. File directly from this screen.
            </p>
          </div>
          {entityId && (
            <button
              type="button"
              onClick={() => setShowForm((v) => !v)}
              className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white"
            >
              {showForm ? 'Hide Form' : '+ New Return'}
            </button>
          )}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Entity</label>
            <select
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option value="">— Select entity —</option>
              {entities.map((ent) => (
                <option key={ent.entity_id} value={ent.entity_id}>
                  {ent.name} {ent.gstin ? `· ${ent.gstin}` : ''}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Period</label>
            <input
              type="month"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
      </section>

      {/* GST Summary KPIs */}
      {entityId && (
        <section>
          {summaryLoading ? (
            <p className="text-sm text-slate-500">Loading GST summary…</p>
          ) : gstSummary ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {(['total_taxable_value', 'total_igst', 'total_cgst', 'total_sgst'] as const).map((key) => {
                const val = typeof gstSummary[key] === 'number' ? (gstSummary[key] as number) : 0;
                const label = key.replace('total_', '').replace(/_/g, ' ').toUpperCase();
                return (
                  <article key={key} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                    <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
                    <p className="mt-2 font-mono text-2xl font-semibold text-ink">{formatINR(val)}</p>
                  </article>
                );
              })}
            </div>
          ) : null}
        </section>
      )}

      {/* Create form */}
      {showForm && entityId && (
        <GSTReturnForm
          entityId={entityId}
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          isSubmitting={isCreating}
        />
      )}

      {/* Returns list */}
      {entityId ? (
        <GSTReturnList entityId={entityId} period={period} />
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-12 text-center text-sm text-slate-500">
          Select an entity to view GST returns.
        </div>
      )}
    </div>
  );
}
