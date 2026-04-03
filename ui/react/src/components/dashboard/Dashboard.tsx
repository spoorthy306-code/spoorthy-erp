import { Suspense, lazy, useState } from 'react';
import { KPICards } from '@/components/dashboard/KPICards';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { useDashboard } from '@/hooks/useDashboard';
import { useEntities } from '@/hooks/useEntities';
import type { KpiItem, TrendPoint } from '@/types';

const Charts = lazy(() =>
  import('@/components/dashboard/Charts').then((module) => ({ default: module.Charts }))
);

function currentPeriod() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
}

function buildKpis(pnl: { revenue: { total_revenue: number }; expenses: { total_expenses: number }; net_profit: number } | undefined): KpiItem[] {
  if (!pnl) {
    return [
      { label: 'Revenue', value: 0, deltaPct: 0, currency: 'INR' },
      { label: 'Expenses', value: 0, deltaPct: 0, currency: 'INR' },
      { label: 'Net Profit', value: 0, deltaPct: 0, currency: 'INR' },
      { label: 'Tax', value: 0, deltaPct: 0, currency: 'INR' },
    ];
  }
  return [
    { label: 'Revenue', value: pnl.revenue.total_revenue, deltaPct: 0, currency: 'INR' },
    { label: 'Expenses', value: pnl.expenses.total_expenses, deltaPct: 0, currency: 'INR' },
    { label: 'Net Profit', value: pnl.net_profit, deltaPct: 0, currency: 'INR' },
    { label: 'Tax', value: (pnl as unknown as Record<string, number>)['tax'] ?? 0, deltaPct: 0, currency: 'INR' },
  ];
}

const PLACEHOLDER_TREND: TrendPoint[] = [
  { month: 'Sep', income: 0, expense: 0 },
  { month: 'Oct', income: 0, expense: 0 },
  { month: 'Nov', income: 0, expense: 0 },
  { month: 'Dec', income: 0, expense: 0 },
  { month: 'Jan', income: 0, expense: 0 },
  { month: 'Feb', income: 0, expense: 0 },
  { month: 'Mar', income: 0, expense: 0 },
  { month: 'Apr', income: 0, expense: 0 },
];

function buildTrend(pnl: { revenue: { total_revenue: number }; expenses: { total_expenses: number } } | undefined, period: string): TrendPoint[] {
  if (!pnl) return PLACEHOLDER_TREND;
  const monthLabel = new Date(period + '-01').toLocaleString('en-IN', { month: 'short' });
  const base = PLACEHOLDER_TREND.map((p) => ({ ...p }));
  base[base.length - 1] = {
    month: monthLabel,
    income: Math.round(pnl.revenue.total_revenue / 1000),
    expense: Math.round(pnl.expenses.total_expenses / 1000),
  };
  return base;
}

export function Dashboard() {
  const [entityId, setEntityId] = useState('');
  const period = currentPeriod();

  const { entities } = useEntities(0, 200);
  const { pnl, isLoading } = useDashboard(entityId, period);

  const kpis = buildKpis(pnl);
  const trend = buildTrend(pnl, period);

  return (
    <div className="space-y-4">
      {/* Entity selector */}
      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-ink">Dashboard</h1>
            <p className="mt-0.5 text-sm text-slate-500">
              {period} · {entityId ? 'Live data' : 'Select an entity to load metrics'}
            </p>
          </div>
          <select
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            className="focus-ring rounded-lg border border-slate-300 px-3 py-2 text-sm"
          >
            <option value="">— Select entity —</option>
            {entities.map((ent) => (
              <option key={ent.entity_id} value={ent.entity_id}>
                {ent.name} {ent.gstin ? `· ${ent.gstin}` : ''}
              </option>
            ))}
          </select>
        </div>
        {isLoading && <p className="mt-2 text-xs text-slate-400">Loading metrics…</p>}
      </section>

      <KPICards items={kpis} />

      <div className="grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <Suspense
            fallback={
              <div className="flex h-80 items-center justify-center rounded-xl border border-slate-200 bg-white">
                <LoadingSpinner />
              </div>
            }
          >
            <Charts data={trend} />
          </Suspense>
        </div>
        <RecentActivity entityId={entityId} />
      </div>
    </div>
  );
}
