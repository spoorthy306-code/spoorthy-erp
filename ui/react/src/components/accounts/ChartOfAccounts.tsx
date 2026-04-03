import { useState } from 'react';
import { useChartOfAccounts } from '@/hooks/useChartOfAccounts';
import type { Account } from '@/types/account.types';

const TYPE_COLORS: Record<string, string> = {
  Asset: 'bg-blue-100 text-blue-700',
  Liability: 'bg-red-100 text-red-700',
  Equity: 'bg-purple-100 text-purple-700',
  Income: 'bg-green-100 text-green-700',
  Expense: 'bg-amber-100 text-amber-700',
};

function typeColor(type?: string | null) {
  if (!type) return 'bg-slate-100 text-slate-500';
  for (const [key, cls] of Object.entries(TYPE_COLORS)) {
    if (type.toLowerCase().includes(key.toLowerCase())) return cls;
  }
  return 'bg-slate-100 text-slate-500';
}

interface AccountRowProps {
  account: Account;
  depth: number;
}

function AccountRow({ account, depth }: AccountRowProps) {
  return (
    <tr className="border-t border-slate-100 hover:bg-slate-50 transition">
      <td className="px-4 py-2 font-mono text-xs text-slate-500" style={{ paddingLeft: `${16 + depth * 20}px` }}>
        {account.account_code}
      </td>
      <td className="px-4 py-2 text-sm text-ink" style={{ paddingLeft: `${16 + depth * 20}px` }}>
        {account.account_name}
      </td>
      <td className="px-4 py-2">
        {account.account_type && (
          <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${typeColor(account.account_type)}`}>
            {account.account_type}
          </span>
        )}
      </td>
      <td className="px-4 py-2 text-center text-xs text-slate-400">
        {account.level ?? '—'}
      </td>
    </tr>
  );
}

interface Props {
  entityId: string;
}

type ViewMode = 'flat' | 'hierarchy';

export function ChartOfAccounts({ entityId }: Props) {
  const [viewMode, setViewMode] = useState<ViewMode>('hierarchy');
  const [search, setSearch] = useState('');
  const { accounts, hierarchy, isLoading, error } = useChartOfAccounts(entityId);

  const source = viewMode === 'flat' ? accounts : hierarchy;

  const filtered = search
    ? source.filter(
        (a) =>
          a.account_code.toLowerCase().includes(search.toLowerCase()) ||
          a.account_name.toLowerCase().includes(search.toLowerCase())
      )
    : source;

  if (isLoading) return <p className="py-8 text-center text-sm text-slate-500">Loading chart of accounts…</p>;
  if (error) return <p className="py-8 text-center text-sm text-danger">Failed to load accounts.</p>;

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search code or name…"
          className="focus-ring rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <div className="flex rounded-lg border border-slate-300 overflow-hidden">
          {(['flat', 'hierarchy'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setViewMode(mode)}
              className={`px-3 py-2 text-xs font-medium capitalize transition ${
                viewMode === mode ? 'bg-brand text-white' : 'bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-400">{filtered.length} accounts</span>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Account Name</th>
              <th className="px-4 py-3">Type</th>
              <th className="px-4 py-3 text-center">Level</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((acc) => (
              <AccountRow key={acc.account_code} account={acc} depth={(acc.level ?? 1) - 1} />
            ))}
            {!filtered.length && (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-sm text-slate-500">
                  {search ? 'No accounts match your search.' : 'No accounts found.'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
