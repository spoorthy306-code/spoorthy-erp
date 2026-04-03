import { useState } from 'react';
import { useEntities } from '@/hooks/useEntities';
import { useInvoices } from '@/hooks/useInvoices';
import { InvoiceForm } from '@/components/invoices/InvoiceForm';
import { InvoiceList } from '@/components/invoices/InvoiceList';
import type { InvoiceCreate } from '@/types/invoice.types';

export default function InvoicesPage() {
  const [entityId, setEntityId] = useState('');
  const [showForm, setShowForm] = useState(false);

  const { entities } = useEntities(0, 200);
  const { invoices, isLoading, createInvoice, isCreating, generateIRN, isGeneratingIRN } = useInvoices(entityId);

  const handleCreate = async (payload: InvoiceCreate) => {
    await createInvoice(payload);
    setShowForm(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">Invoices</h1>
            <p className="mt-1 text-sm text-slate-500">
              Create and manage GST invoices. Generate IRN for e-invoicing compliance.
            </p>
          </div>
          {entityId && (
            <button
              type="button"
              onClick={() => setShowForm((v) => !v)}
              className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white"
            >
              {showForm ? 'Hide Form' : '+ New Invoice'}
            </button>
          )}
        </div>

        <div className="mt-4">
          <label className="block text-xs font-medium text-slate-600 mb-1">Entity</label>
          <select
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            className="focus-ring w-full max-w-sm rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">— Select entity —</option>
            {entities.map((ent) => (
              <option key={ent.entity_id} value={ent.entity_id}>
                {ent.name} {ent.gstin ? `· ${ent.gstin}` : ''}
              </option>
            ))}
          </select>
        </div>
      </section>

      {/* Create form */}
      {showForm && entityId && (
        <InvoiceForm
          entityId={entityId}
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          isSubmitting={isCreating}
        />
      )}

      {/* Invoice list */}
      {entityId ? (
        <InvoiceList
          invoices={invoices}
          isLoading={isLoading}
          onGenerateIRN={generateIRN}
          isGeneratingIRN={isGeneratingIRN}
        />
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-12 text-center text-sm text-slate-500">
          Select an entity to view invoices.
        </div>
      )}
    </div>
  );
}
