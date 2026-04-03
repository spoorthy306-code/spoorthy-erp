import type { KpiItem } from '@/types';
import { formatINR } from '@/utils/formatters';

interface Props {
  items: KpiItem[];
}

export function KPICards({ items }: Props) {
  return (
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <article key={item.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">{item.label}</p>
          <p className="mt-2 font-mono text-2xl font-semibold text-ink">{formatINR(item.value)}</p>
          <p className={`mt-1 text-sm ${item.deltaPct >= 0 ? 'text-success' : 'text-danger'}`}>
            {item.deltaPct >= 0 ? '+' : ''}
            {item.deltaPct.toFixed(1)}% vs last month
          </p>
        </article>
      ))}
    </section>
  );
}
