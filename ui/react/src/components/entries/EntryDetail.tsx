import { useMemo, useState } from 'react';
import { JournalEntryForm } from '@/components/entries/JournalEntryForm';
import { useJournalEntries } from '@/hooks/useJournalEntries';
import { formatINR } from '@/utils/formatters';

interface EntryDetailProps {
  entryId: string;
  onClose?: () => void;
}

export function EntryDetail({ entryId, onClose }: EntryDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const { selectedEntry, isFetchingDetail, error } = useJournalEntries({}, entryId);
  const totals = useMemo(
    () => ({
      debit: selectedEntry?.lines?.reduce((sum, line) => sum + Number(line.debit || 0), 0) ?? selectedEntry?.total_debit ?? 0,
      credit: selectedEntry?.lines?.reduce((sum, line) => sum + Number(line.credit || 0), 0) ?? selectedEntry?.total_credit ?? 0,
    }),
    [selectedEntry]
  );

  if (isFetchingDetail) {
    return <div className="p-6 text-sm text-slate-500">Loading journal entry details...</div>;
  }

  if (error) {
    return <div className="p-6 text-sm text-rose-600">Unable to load journal entry details.</div>;
  }

  if (!selectedEntry) {
    return <div className="p-6 text-sm text-rose-600">Journal entry not found.</div>;
  }

  if (isEditing) {
    return (
      <JournalEntryForm
        entry={selectedEntry}
        onCancel={() => setIsEditing(false)}
        onSuccess={() => {
          setIsEditing(false);
          onClose?.();
        }}
      />
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-ink">Journal Entry Detail</h2>
          <p className="mt-1 text-sm text-slate-500">Entry ID: {selectedEntry.entry_id}</p>
        </div>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setIsEditing(true)}
            disabled={!selectedEntry.lines?.length}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={onClose}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
          >
            Close
          </button>
        </div>
      </div>

      <section className="grid gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-2">
        <div>
          <p className="text-sm text-slate-500">Entry Date</p>
          <p className="mt-1 font-medium text-ink">{selectedEntry.entry_date}</p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Period</p>
          <p className="mt-1 font-medium text-ink">{selectedEntry.period}</p>
        </div>
        <div className="md:col-span-2">
          <p className="text-sm text-slate-500">Narration</p>
          <p className="mt-1 font-medium text-ink">{selectedEntry.narration || 'No narration provided.'}</p>
        </div>
      </section>

      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="text-lg font-semibold text-ink">Line Items</h3>
        </div>
        {selectedEntry.lines?.length ? (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Account</th>
                <th className="px-4 py-3 text-right">Debit</th>
                <th className="px-4 py-3 text-right">Credit</th>
                <th className="px-4 py-3">Description</th>
              </tr>
            </thead>
            <tbody>
              {selectedEntry.lines.map((line) => (
                <tr key={line.line_id ?? `${line.account_code}-${line.debit}-${line.credit}`} className="border-t border-slate-200">
                  <td className="px-4 py-3 font-mono text-xs text-slate-700">{line.account_code}</td>
                  <td className="px-4 py-3 text-right text-slate-700">{line.debit ? formatINR(Number(line.debit)) : '-'}</td>
                  <td className="px-4 py-3 text-right text-slate-700">{line.credit ? formatINR(Number(line.credit)) : '-'}</td>
                  <td className="px-4 py-3 text-slate-600">{line.description || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="px-4 py-5 text-sm text-amber-700">
            The current backend detail schema does not expose journal lines yet, so only header and audit data are available here.
          </div>
        )}
      </section>

      <section className="grid gap-4 rounded-xl border border-slate-200 bg-slate-50 p-4 md:grid-cols-2">
        <div>
          <p className="text-sm text-slate-500">Total Debit</p>
          <p className="mt-1 text-xl font-semibold text-ink">{formatINR(Number(totals.debit))}</p>
        </div>
        <div>
          <p className="text-sm text-slate-500">Total Credit</p>
          <p className="mt-1 text-xl font-semibold text-ink">{formatINR(Number(totals.credit))}</p>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
        <p>Created at: {new Date(selectedEntry.created_at).toLocaleString()}</p>
        <p className="mt-2">Posted by: {selectedEntry.posted_by || 'System'}</p>
        <p className="mt-2">PQC signature: {selectedEntry.pqc_signature || 'Pending'}</p>
      </section>
    </div>
  );
}