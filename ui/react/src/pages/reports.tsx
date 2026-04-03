import { useState } from 'react';
import { useEntities } from '@/hooks/useEntities';
import { TrialBalance } from '@/components/reports/TrialBalance';
import { ProfitLoss } from '@/components/reports/ProfitLoss';
import { BalanceSheet } from '@/components/reports/BalanceSheet';
import { CashFlow } from '@/components/reports/CashFlow';

type Tab = 'trial-balance' | 'pnl' | 'balance-sheet' | 'cash-flow';

const TABS: { id: Tab; label: string }[] = [
  { id: 'trial-balance', label: 'Trial Balance' },
  { id: 'pnl', label: 'Profit & Loss' },
  { id: 'balance-sheet', label: 'Balance Sheet' },
  { id: 'cash-flow', label: 'Cash Flow' },
];

function currentPeriod() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function firstOfPeriod(period: string) {
  return `${period}-01`;
}

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('trial-balance');
  const [entityId, setEntityId] = useState('');
  const [period, setPeriod] = useState(currentPeriod());
  const [asOfDate, setAsOfDate] = useState(todayISO());

  const { entities } = useEntities(0, 200);

  const ready = Boolean(entityId);

  return (
    <div className="space-y-6">
      {/* Header + filters */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold text-ink">Financial Reports</h1>
        <p className="mt-1 text-sm text-slate-500">Trial Balance, P&L, Balance Sheet, and Cash Flow.</p>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
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
                  {ent.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Period (YYYY-MM)</label>
            <input
              type="month"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">As-of Date</label>
            <input
              type="date"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
              className="focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
        </div>
      </section>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto rounded-xl border border-slate-200 bg-slate-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`focus-ring whitespace-nowrap rounded-lg px-4 py-2 text-sm font-medium transition ${
              activeTab === tab.id
                ? 'bg-white text-ink shadow-sm'
                : 'text-slate-600 hover:text-ink'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Report content */}
      {!ready ? (
        <div className="rounded-xl border border-slate-200 bg-white px-4 py-12 text-center text-sm text-slate-500">
          Select an entity above to generate reports.
        </div>
      ) : (
        <>
          {activeTab === 'trial-balance' && <TrialBalance entityId={entityId} period={period} />}
          {activeTab === 'pnl' && <ProfitLoss entityId={entityId} period={period} />}
          {activeTab === 'balance-sheet' && <BalanceSheet entityId={entityId} asOfDate={asOfDate} />}
          {activeTab === 'cash-flow' && (
            <CashFlow entityId={entityId} startDate={firstOfPeriod(period)} endDate={asOfDate} />
          )}
        </>
      )}
    </div>
  );
}
