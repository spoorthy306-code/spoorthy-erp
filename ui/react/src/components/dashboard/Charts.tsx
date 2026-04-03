import type { TrendPoint } from '@/types';

interface Props {
  data: TrendPoint[];
}

export function Charts({ data }: Props) {
  const chartHeight = 220;
  const chartWidth = 720;
  const padding = 24;
  const maxValue = Math.max(...data.flatMap((point) => [point.income, point.expense]), 1);
  const xStep = (chartWidth - padding * 2) / Math.max(data.length - 1, 1);
  const barWidth = 20;

  const yForValue = (value: number) => {
    const normalized = value / maxValue;
    return chartHeight - padding - normalized * (chartHeight - padding * 2);
  };

  const incomePoints = data
    .map((point, index) => `${padding + index * xStep},${yForValue(point.income)}`)
    .join(' ');

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold text-ink">Cash Flow Trend (12M)</h3>
        <div className="flex items-center gap-4 text-xs text-slate-500">
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-growth" />
            Income
          </span>
          <span className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-danger" />
            Expense
          </span>
        </div>
      </div>
      <div className="mt-4 overflow-x-auto">
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="h-80 w-full min-w-[680px]"
          role="img"
          aria-label="Income line and expense bar chart for the last twelve months"
        >
          {[0.25, 0.5, 0.75, 1].map((step) => {
            const y = chartHeight - padding - step * (chartHeight - padding * 2);
            return (
              <line
                key={step}
                x1={padding}
                y1={y}
                x2={chartWidth - padding}
                y2={y}
                stroke="#E2E8F0"
                strokeDasharray="4 4"
              />
            );
          })}

          <polyline
            fill="none"
            stroke="#059669"
            strokeWidth="3"
            strokeLinejoin="round"
            strokeLinecap="round"
            points={incomePoints}
          />

          {data.map((point, index) => {
            const x = padding + index * xStep;
            const expenseY = yForValue(point.expense);
            const height = chartHeight - padding - expenseY;
            return (
              <g key={point.month}>
                <rect
                  x={x - barWidth / 2}
                  y={expenseY}
                  width={barWidth}
                  height={height}
                  rx="5"
                  fill="#DC2626"
                  opacity="0.82"
                />
                <circle cx={x} cy={yForValue(point.income)} r="4" fill="#059669" />
                <text x={x} y={chartHeight - 6} textAnchor="middle" fontSize="11" fill="#64748B">
                  {point.month}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </section>
  );
}
