import { useJournalEntries } from '@/hooks/useJournalEntries';
import { formatINR } from '@/utils/formatters';

interface Props {
  entityId: string;
}

export function RecentActivity({ entityId }: Props) {
  const { entries, isLoading } = useJournalEntries({ entityId, limit: 5 });

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="text-lg font-semibold text-ink">Recent Activity</h3>
      <div className="mt-3 space-y-2">
        {isLoading && (
          <p className="text-sm text-slate-500">Loading…</p>
        )}
        {!isLoading && !entityId && (
          <p className="text-sm text-slate-500">Select an entity to see recent journal entries.</p>
        )}
        {!isLoading && entityId && entries.length === 0 && (
          <p className="text-sm text-slate-500">No journal entries found.</p>
        )}
        {entries.map((entry) => (
          <div
            key={entry.entry_id}
            className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2"
          >
            <div>
              <p className="text-sm font-medium text-ink">{entry.entry_date}</p>
              <p className="text-xs text-slate-500">{entry.narration ?? entry.period}</p>
            </div>
            <div className="text-right">
              <p className="font-mono text-sm text-ink">{formatINR(Number(entry.total_debit))}</p>
              <p className="text-xs text-slate-500">Dr</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
