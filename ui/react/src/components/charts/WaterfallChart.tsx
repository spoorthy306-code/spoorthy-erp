import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ResponsiveContainer,
} from 'recharts';

interface WaterfallItem {
  name: string;
  value: number;
  isTotal?: boolean;
}

interface WaterfallChartProps {
  data: WaterfallItem[];
  title?: string;
  height?: number;
}

interface WaterfallBarData {
  name: string;
  value: number;
  start: number;
  isTotal: boolean;
  isPositive: boolean;
}

const formatINR = (value: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(Math.abs(value));

const buildWaterfallData = (items: WaterfallItem[]): WaterfallBarData[] => {
  let running = 0;
  return items.map((item) => {
    if (item.isTotal) {
      return { name: item.name, value: running, start: 0, isTotal: true, isPositive: running >= 0 };
    }
    const start = running;
    running += item.value;
    return { name: item.name, value: item.value, start: item.value < 0 ? running : start, isTotal: false, isPositive: item.value >= 0 };
  });
};

export const WaterfallChart: React.FC<WaterfallChartProps> = ({ data, title = 'Cash Flow', height = 320 }) => {
  const chartData = buildWaterfallData(data);

  return (
    <div className="bg-white rounded-xl shadow p-4">
      {title && <h3 className="text-sm font-semibold text-gray-600 mb-3">{title}</h3>}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
          <YAxis tickFormatter={(v: number) => `₹${(v / 100000).toFixed(0)}L`} tick={{ fontSize: 11 }} />
          <Tooltip
            formatter={(value: number, _name: string, props: { payload: WaterfallBarData }) => [
              formatINR(props.payload.value),
              props.payload.name,
            ]}
          />
          {/* Invisible base bar for stacking offset */}
          <Bar dataKey="start" stackId="a" fill="transparent" />
          <Bar dataKey="value" stackId="a" radius={[3, 3, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.isTotal ? '#6366f1' : entry.isPositive ? '#10b981' : '#ef4444'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default WaterfallChart;
