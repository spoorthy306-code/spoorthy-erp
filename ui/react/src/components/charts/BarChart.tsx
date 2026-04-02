import React from 'react';
import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface BarDataPoint {
  month: string;
  revenue: number;
  expense: number;
}

interface BarChartProps {
  data: BarDataPoint[];
  title?: string;
  height?: number;
}

const formatINR = (value: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value);

export const BarChart: React.FC<BarChartProps> = ({ data, title = 'Revenue vs Expense', height = 300 }) => (
  <div className="bg-white rounded-xl shadow p-4">
    {title && <h3 className="text-sm font-semibold text-gray-600 mb-3">{title}</h3>}
    <ResponsiveContainer width="100%" height={height}>
      <ReBarChart data={data} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" tick={{ fontSize: 11 }} />
        <YAxis tickFormatter={(v: number) => `₹${(v / 100000).toFixed(0)}L`} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(value: number) => formatINR(value)} />
        <Legend />
        <Bar dataKey="revenue" fill="#3b82f6" name="Revenue" radius={[3, 3, 0, 0]} />
        <Bar dataKey="expense" fill="#f87171" name="Expense" radius={[3, 3, 0, 0]} />
      </ReBarChart>
    </ResponsiveContainer>
  </div>
);

export default BarChart;
