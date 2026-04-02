import React from 'react';
import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface LineDataPoint {
  date: string;
  pnl: number;
  benchmark?: number;
}

interface LineChartProps {
  data: LineDataPoint[];
  title?: string;
  height?: number;
}

const formatINR = (value: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

export const LineChart: React.FC<LineChartProps> = ({ data, title = 'Portfolio P&L', height = 300 }) => (
  <div className="bg-white rounded-xl shadow p-4">
    {title && <h3 className="text-sm font-semibold text-gray-600 mb-3">{title}</h3>}
    <ResponsiveContainer width="100%" height={height}>
      <ReLineChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v: number) => `₹${(v / 100000).toFixed(0)}L`} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(value: number) => formatINR(value)} />
        <Legend />
        <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="4 4" />
        <Line type="monotone" dataKey="pnl" stroke="#6366f1" strokeWidth={2} dot={false} name="P&L" />
        {data[0]?.benchmark !== undefined && (
          <Line type="monotone" dataKey="benchmark" stroke="#10b981" strokeWidth={1.5}
            strokeDasharray="5 5" dot={false} name="Benchmark" />
        )}
      </ReLineChart>
    </ResponsiveContainer>
  </div>
);

export default LineChart;
