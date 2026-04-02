import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface GaugeChartProps {
  value: number;       // 0–100
  min?: number;
  max?: number;
  label: string;
  unit?: string;
  thresholds?: { warn: number; danger: number };
  height?: number;
}

export const GaugeChart: React.FC<GaugeChartProps> = ({
  value,
  min = 0,
  max = 100,
  label,
  unit = '%',
  thresholds = { warn: 60, danger: 80 },
  height = 200,
}) => {
  const normalised = Math.min(Math.max(((value - min) / (max - min)) * 100, 0), 100);
  const filled = normalised / 2;       // half-donut = 180°
  const empty = 50 - filled;

  const color =
    normalised >= thresholds.danger ? '#ef4444' :
    normalised >= thresholds.warn   ? '#f59e0b' :
                                      '#10b981';

  const gaugeData = [
    { value: filled, color },
    { value: empty,  color: '#e5e7eb' },
    { value: 50,     color: 'transparent' },   // bottom half hidden
  ];

  return (
    <div className="bg-white rounded-xl shadow p-4 flex flex-col items-center">
      <h3 className="text-sm font-semibold text-gray-600 mb-1">{label}</h3>
      <div style={{ position: 'relative', height }}>
        <ResponsiveContainer width={height * 1.5} height={height}>
          <PieChart>
            <Pie
              data={gaugeData}
              cx="50%"
              cy="75%"
              startAngle={180}
              endAngle={0}
              innerRadius="60%"
              outerRadius="80%"
              paddingAngle={0}
              dataKey="value"
              isAnimationActive
            >
              {gaugeData.map((entry, i) => (
                <Cell key={i} fill={entry.color} stroke="none" />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div
          style={{ position: 'absolute', bottom: '28%', left: '50%', transform: 'translateX(-50%)', textAlign: 'center' }}
        >
          <span className="text-2xl font-bold" style={{ color }}>{value.toFixed(1)}{unit}</span>
        </div>
      </div>
    </div>
  );
};

export default GaugeChart;
