import { useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { BatchEntryUpload } from '@/components/entries/BatchEntryUpload';
import { EntryDetailModal } from '@/components/entries/EntryDetailModal';
import { EntryListFilters, DEFAULT_FILTER_STATE } from '@/components/entries/EntryListFilters';
import { JournalEntryForm } from '@/components/entries/JournalEntryForm';
import { useJournalEntries } from '@/hooks/useJournalEntries';
import { formatINR } from '@/utils/formatters';
import type { EntryListFilterState } from '@/types/journal.types';

export default function EntriesPage() {
  const queryClient = useQueryClient();
  const [entityId, setEntityId] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  const [selectedEntryId, setSelectedEntryId] = useState<string | null>(null);
  const [filters, setFilters] = useState<EntryListFilterState>(DEFAULT_FILTER_STATE);

  const { entries, isLoading, reconcileEntity, isReconciling } = useJournalEntries({
    entityId,
    period: filters.period || undefined,
    limit: 50,
  });

  const filteredEntries = useMemo(() => {
    let result = [...entries];

    if (filters.narration.trim()) {
      const search = filters.narration.toLowerCase();
      result = result.filter((e) => (e.narration ?? '').toLowerCase().includes(search));
    }

    result.sort((a, b) => {
      let valA: string | number;
      let valB: string | number;

      if (filters.sortField === 'entry_date') {
        valA = a.entry_date;
        valB = b.entry_date;
      } else if (filters.sortField === 'total_debit') {
        valA = Number(a.total_debit);
        valB = Number(b.total_debit);
      } else {
        valA = Number(a.total_credit);
        valB = Number(b.total_credit);
      }

      if (valA < valB) return filters.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return filters.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [entries, filters]);

  const summary = useMemo(
    () => ({
      debit: filteredEntries.reduce((sum, entry) => sum + Number(entry.total_debit), 0),
      credit: filteredEntries.reduce((sum, entry) => sum + Number(entry.total_credit), 0),
    }),
    [filteredEntries]
  );

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-ink">Journal Entries</h1>
            <p className="mt-1 text-sm text-slate-500">
              Create balanced entries, inspect posting totals, and open entry detail without leaving the ledger view.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => {
                setShowCreateForm((c) => !c);
                setShowBatchUpload(false);
              }}
              className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white"
            >
              {showCreateForm ? 'Hide Form' : 'New Entry'}
            </button>
            <button
              type="button"
              onClick={() => {
                setShowBatchUpload((c) => !c);
                setShowCreateForm(false);
              }}
              className="focus-ring rounded-lg border border-brand px-4 py-2 text-sm font-medium text-brand"
            >
              {showBatchUpload ? 'Hide Batch Upload' : 'Batch Upload'}
            </button>
            <button
              type="button"
              onClick={() => void reconcileEntity(entityId)}
              disabled={!entityId || isReconciling}
              className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isReconciling ? 'Reconciling...' : 'Reconcile Entity'}
            </button>
          </div>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-[minmax(0,1fr)_220px_220px]">
          <div>
            <label htmlFor="journal-entity-filter" className="text-sm font-medium text-slate-700">
              Entity ID
            </label>
            <input
              id="journal-entity-filter"
              value={entityId}
              onChange={(event) => setEntityId(event.target.value)}
              className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
              placeholder="Enter an entity UUID to load entries"
            />
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-sm text-slate-500">Debit Total</p>
            <p className="mt-1 text-xl font-semibold text-ink">{formatINR(summary.debit)}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p className="text-sm text-slate-500">Credit Total</p>
            <p className="mt-1 text-xl font-semibold text-ink">{formatINR(summary.credit)}</p>
          </div>
        </div>
      </section>

      {showCreateForm ? (
        <JournalEntryForm
          entityId={entityId}
          onCancel={() => setShowCreateForm(false)}
          onSuccess={({ entry }) => {
            setEntityId(entry.entity_id);
            setSelectedEntryId(entry.entry_id);
            setShowCreateForm(false);
          }}
        />
      ) : null}

      {showBatchUpload ? (
        <BatchEntryUpload
          entityId={entityId}
          onSuccess={() => {
            void queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
            setShowBatchUpload(false);
          }}
        />
      ) : null}

      <EntryListFilters filters={filters} onChange={setFilters} disabled={!entityId} />

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-lg font-semibold text-ink">Journal Entries</h2>
          {filteredEntries.length !== entries.length ? (
            <span className="text-sm text-slate-500">
              {filteredEntries.length} of {entries.length} shown
            </span>
          ) : entries.length > 0 ? (
            <span className="text-sm text-slate-500">
              {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
            </span>
          ) : null}
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Date</th>
              <th className="px-4 py-3">Period</th>
              <th className="px-4 py-3">Narration</th>
              <th className="px-4 py-3 text-right">Debit</th>
              <th className="px-4 py-3 text-right">Credit</th>
            </tr>
          </thead>
          <tbody>
            {filteredEntries.map((entry) => (
              <tr key={entry.entry_id} className="border-t border-slate-200 transition hover:bg-slate-50">
                <td className="px-4 py-3">
                  <button
                    type="button"
                    onClick={() => setSelectedEntryId(entry.entry_id)}
                    className="text-left font-medium text-brand"
                  >
                    {entry.entry_date}
                  </button>
                </td>
                <td className="px-4 py-3 text-slate-600">{entry.period}</td>
                <td className="px-4 py-3 text-slate-700">{entry.narration ?? '-'}</td>
                <td className="px-4 py-3 text-right text-slate-700">{formatINR(Number(entry.total_debit))}</td>
                <td className="px-4 py-3 text-right text-slate-700">{formatINR(Number(entry.total_credit))}</td>
              </tr>
            ))}

            {!filteredEntries.length ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                  {entityId
                    ? isLoading
                      ? 'Loading journal entries...'
                      : filters.narration
                        ? `No entries match "${filters.narration}".`
                        : 'No journal entries were found for this entity yet.'
                    : 'Enter an entity ID to load or create journal entries.'}
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>

      <EntryDetailModal entryId={selectedEntryId} isOpen={Boolean(selectedEntryId)} onClose={() => setSelectedEntryId(null)} />
    </div>
  );
}
