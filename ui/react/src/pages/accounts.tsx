import { useState } from 'react';
import { useEntities } from '@/hooks/useEntities';
import { ChartOfAccounts } from '@/components/accounts/ChartOfAccounts';

export default function AccountsPage() {
  const [entityId, setEntityId] = useState('');
  const { entities } = useEntities(0, 200);

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-ink">Chart of Accounts</h1>
        <p className="mt-1 text-sm text-slate-500">
          View and explore the hierarchical chart of accounts for each entity.
        </p>
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
                {ent.name}
              </option>
            ))}
          </select>
        </div>
      </section>

      {entityId ? (
        <ChartOfAccounts entityId={entityId} />
      ) : (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-12 text-center text-sm text-slate-500">
          Select an entity to view its chart of accounts.
        </div>
      )}
    </div>
  );
}
