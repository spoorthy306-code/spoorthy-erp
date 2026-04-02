import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { JournalTable } from '../../components/tables/JournalTable';
import type { JournalEntry } from '../../components/tables/JournalTable';
import { useEntityStore } from '../../store/entityStore';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

interface NewLine {
  account_code: string;
  description:  string;
  debit:        string;
  credit:       string;
}

const emptyLine = (): NewLine => ({ account_code: '', description: '', debit: '', credit: '' });

const apiFetch = async <T,>(url: string, options?: RequestInit): Promise<T> => {
  const token = localStorage.getItem('access_token');
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
};

export const JournalPage: React.FC = () => {
  const { selectedEntity } = useEntityStore();
  const queryClient = useQueryClient();

  const [showForm, setShowForm] = useState(false);
  const [narration, setNarration] = useState('');
  const [entryDate, setEntryDate] = useState(new Date().toISOString().slice(0, 10));
  const [lines, setLines] = useState<NewLine[]>([emptyLine(), emptyLine()]);

  const { data: entries = [], isLoading } = useQuery<JournalEntry[]>({
    queryKey: ['journal-entries', selectedEntity?.entity_id],
    queryFn: () =>
      apiFetch(`${API_BASE}/journal-entries/?entity_id=${selectedEntity!.entity_id}&limit=100`),
    enabled: !!selectedEntity,
  });

  const createMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiFetch(`${API_BASE}/journal-entries/`, { method: 'POST', body: JSON.stringify(body) }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
      setShowForm(false);
      setNarration('');
      setLines([emptyLine(), emptyLine()]);
    },
  });

  const totalDebit  = lines.reduce((s, l) => s + (parseFloat(l.debit)  || 0), 0);
  const totalCredit = lines.reduce((s, l) => s + (parseFloat(l.credit) || 0), 0);
  const balanced    = Math.abs(totalDebit - totalCredit) < 0.01;

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (!selectedEntity || !balanced) return;
    createMutation.mutate({
      entity_id:  selectedEntity.entity_id,
      entry_date: entryDate,
      period:     entryDate.slice(0, 7),
      narration,
      lines: lines
        .filter((l) => l.account_code)
        .map((l) => ({
          account_code: l.account_code,
          description:  l.description,
          debit:        parseFloat(l.debit)  || 0,
          credit:       parseFloat(l.credit) || 0,
        })),
    });
  };

  const updateLine = (i: number, field: keyof NewLine, val: string): void =>
    setLines((prev) => prev.map((l, idx) => idx === i ? { ...l, [field]: val } : l));

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Journal Entries</h1>
          <p className="text-sm text-gray-500 mt-0.5">{selectedEntity?.name}</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          {showForm ? '✕ Cancel' : '+ New Entry'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 rounded-xl border border-blue-100 bg-blue-50 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-blue-800 mb-4">New Journal Entry</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Date</label>
              <input type="date" value={entryDate} onChange={(e) => setEntryDate(e.target.value)}
                className="w-full rounded border border-gray-200 px-3 py-1.5 text-sm" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">Narration</label>
              <input type="text" value={narration} onChange={(e) => setNarration(e.target.value)}
                placeholder="Journal narration" required
                className="w-full rounded border border-gray-200 px-3 py-1.5 text-sm" />
            </div>
          </div>

          <table className="w-full text-sm mb-3">
            <thead><tr className="text-xs text-gray-500">
              <th className="text-left pb-2 pr-2">Account Code</th>
              <th className="text-left pb-2 pr-2">Description</th>
              <th className="text-right pb-2 pr-2">Debit (₹)</th>
              <th className="text-right pb-2">Credit (₹)</th>
            </tr></thead>
            <tbody>
              {lines.map((l, i) => (
                <tr key={i}>
                  <td className="pr-2 pb-1.5">
                    <input value={l.account_code} onChange={(e) => updateLine(i, 'account_code', e.target.value)}
                      placeholder="e.g. 1001" className="w-full rounded border border-gray-200 px-2 py-1 text-xs font-mono" />
                  </td>
                  <td className="pr-2 pb-1.5">
                    <input value={l.description} onChange={(e) => updateLine(i, 'description', e.target.value)}
                      placeholder="Description" className="w-full rounded border border-gray-200 px-2 py-1 text-xs" />
                  </td>
                  <td className="pr-2 pb-1.5">
                    <input type="number" min="0" step="0.01" value={l.debit}
                      onChange={(e) => updateLine(i, 'debit', e.target.value)}
                      className="w-full rounded border border-gray-200 px-2 py-1 text-xs text-right" />
                  </td>
                  <td className="pb-1.5">
                    <input type="number" min="0" step="0.01" value={l.credit}
                      onChange={(e) => updateLine(i, 'credit', e.target.value)}
                      className="w-full rounded border border-gray-200 px-2 py-1 text-xs text-right" />
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="text-xs font-semibold border-t border-gray-200">
                <td colSpan={2} className="pt-2 text-right text-gray-500">Totals:</td>
                <td className={`pt-2 pr-2 text-right ${balanced ? 'text-green-700' : 'text-red-600'}`}>
                  ₹{totalDebit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
                <td className={`pt-2 text-right ${balanced ? 'text-green-700' : 'text-red-600'}`}>
                  ₹{totalCredit.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
              </tr>
            </tfoot>
          </table>

          <div className="flex items-center gap-3">
            <button type="button" onClick={() => setLines((l) => [...l, emptyLine()])}
              className="text-xs text-blue-600 hover:underline">+ Add line</button>
            {!balanced && <span className="text-xs text-red-600">Entry not balanced</span>}
            <div className="ml-auto">
              <button type="submit" disabled={!balanced || createMutation.isPending}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-blue-700">
                {createMutation.isPending ? 'Posting…' : 'Post Entry'}
              </button>
            </div>
          </div>
          {createMutation.isError && (
            <p className="mt-2 text-xs text-red-600">Error: {(createMutation.error as Error).message}</p>
          )}
        </form>
      )}

      <JournalTable entries={entries} loading={isLoading} />
    </div>
  );
};

export default JournalPage;
