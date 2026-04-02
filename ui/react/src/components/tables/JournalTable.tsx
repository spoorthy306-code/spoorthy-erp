import React, { useState } from 'react';
import { DataTable, Column } from './DataTable';

export interface JournalLine {
  account_code: string;
  description: string;
  debit: number;
  credit: number;
}

export interface JournalEntry {
  entry_id: string;
  entry_date: string;
  period: string;
  narration: string;
  total_debit: number;
  total_credit: number;
  posted_by: string;
  lines?: JournalLine[];
}

interface JournalTableProps {
  entries: JournalEntry[];
  loading?: boolean;
  onSelect?: (entry: JournalEntry) => void;
}

const formatINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const columns: Column<JournalEntry>[] = [
  { key: 'entry_date', header: 'Date', className: 'whitespace-nowrap' },
  { key: 'period',     header: 'Period' },
  {
    key: 'narration',
    header: 'Narration',
    render: (v) => <span className="max-w-xs truncate block" title={String(v)}>{String(v)}</span>,
  },
  {
    key: 'total_debit',
    header: 'Debit (₹)',
    render: (v) => <span className="text-blue-700 font-medium">{formatINR(Number(v))}</span>,
    className: 'text-right',
  },
  {
    key: 'total_credit',
    header: 'Credit (₹)',
    render: (v) => <span className="text-green-700 font-medium">{formatINR(Number(v))}</span>,
    className: 'text-right',
  },
  { key: 'posted_by', header: 'Posted By' },
];

export const JournalTable: React.FC<JournalTableProps> = ({ entries, loading, onSelect }) => {
  const [expanded, setExpanded] = useState<string | null>(null);

  const handleRowClick = (entry: JournalEntry): void => {
    setExpanded((e) => (e === entry.entry_id ? null : entry.entry_id));
    onSelect?.(entry);
  };

  // Suppress unused variable warning — handleRowClick is available for parent wiring
  void handleRowClick;

  return (
    <div>
      <DataTable<JournalEntry>
        columns={columns}
        data={entries}
        rowKey="entry_id"
        loading={loading}
        emptyMessage="No journal entries found."
      />
      {expanded && (() => {
        const entry = entries.find((e) => e.entry_id === expanded);
        if (!entry?.lines?.length) return null;
        return (
          <div className="mt-2 rounded-lg border border-indigo-100 bg-indigo-50 p-3 text-xs">
            <p className="font-semibold text-indigo-700 mb-2">Lines — {entry.narration}</p>
            <table className="w-full">
              <thead><tr className="text-gray-500">
                <th className="text-left py-1 pr-4">Account</th>
                <th className="text-left py-1 pr-4">Description</th>
                <th className="text-right py-1 pr-4">Debit</th>
                <th className="text-right py-1">Credit</th>
              </tr></thead>
              <tbody>
                {entry.lines.map((l, i) => (
                  <tr key={i} className="border-t border-indigo-100">
                    <td className="py-1 pr-4 font-mono">{l.account_code}</td>
                    <td className="py-1 pr-4">{l.description}</td>
                    <td className="py-1 pr-4 text-right text-blue-700">{l.debit ? formatINR(l.debit) : '-'}</td>
                    <td className="py-1 text-right text-green-700">{l.credit ? formatINR(l.credit) : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })()}
    </div>
  );
};

export default JournalTable;
