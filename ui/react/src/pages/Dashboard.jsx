// SPOORTHY QUANTUM OS — Dashboard Page
// React + TypeScript + Tailwind CSS

import React, { useState, useEffect } from 'react';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

export const Dashboard = () => {
  const [kpis, setKpis] = useState({
    revenueMTD: 1250000,
    pnlYTD: 250000,
    cashPosition: 500000,
    workingCapital: 800000,
    var95: 0.15,
    openReconciliations: 45
  });

  const [selectedEntity, setSelectedEntity] = useState('27AABCS1234C1Z1');

  const revenueExpenseData = {
    labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
    datasets: [
      {
        label: 'Revenue',
        data: [1000000, 1100000, 1050000, 1200000, 1150000, 1300000, 1250000, 1400000, 1350000, 1500000, 1450000, 1600000],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Expenses',
        data: [750000, 800000, 780000, 850000, 820000, 900000, 880000, 950000, 920000, 1000000, 980000, 1050000],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const portfolioData = {
    labels: ['NIFTY', 'INFY', 'TCS', 'HDFC', 'Others'],
    datasets: [
      {
        data: [40, 25, 20, 10, 5],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(156, 163, 175, 0.8)',
        ],
      },
    ],
  };

  const complianceData = [
    { month: 'Apr', status: 'Filed', color: 'green' },
    { month: 'May', status: 'Filed', color: 'green' },
    { month: 'Jun', status: 'Filed', color: 'green' },
    { month: 'Jul', status: 'Due in 3 days', color: 'yellow' },
    { month: 'Aug', status: 'Pending', color: 'red' },
  ];

  const quantumJobs = [
    { id: 'QJ001', module: 'Reconciliation', status: 'Running', progress: 75 },
    { id: 'QJ002', module: 'Portfolio Optimization', status: 'Completed', progress: 100 },
    { id: 'QJ003', module: 'VaR Calculation', status: 'Queued', progress: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Entity Selector */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <select
          value={selectedEntity}
          onChange={(e) => setSelectedEntity(e.target.value)}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="27AABCS1234C1Z1">Spoorthy Technologies Pvt Ltd</option>
          <option value="UK_ENTITY">Spoorthy UK Ltd</option>
          <option value="SG_ENTITY">Spoorthy Singapore Pte</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <KPICard title="Revenue MTD" value={`₹${kpis.revenueMTD.toLocaleString()}`} change="+12%" />
        <KPICard title="P&L YTD" value={`₹${kpis.pnlYTD.toLocaleString()}`} change="+8%" />
        <KPICard title="Cash Position" value={`₹${kpis.cashPosition.toLocaleString()}`} change="-5%" />
        <KPICard title="Working Capital" value={`₹${kpis.workingCapital.toLocaleString()}`} change="+15%" />
        <KPICard title="VaR 95%" value={`${(kpis.var95 * 100).toFixed(1)}%`} change="-2%" />
        <KPICard title="Open Reconciliations" value={kpis.openReconciliations.toString()} change="-10%" />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Revenue vs Expense Chart */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue vs Expenses (12 Months)</h3>
          <Line
            data={revenueExpenseData}
            options={{
              responsive: true,
              plugins: {
                legend: { position: 'top' },
                title: { display: false },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: (value) => `₹${(value / 100000).toFixed(0)}L`,
                  },
                },
              },
            }}
          />
        </div>

        {/* Portfolio Allocation */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Allocation</h3>
          <Doughnut
            data={portfolioData}
            options={{
              responsive: true,
              plugins: {
                legend: { position: 'right' },
                title: { display: false },
              },
            }}
          />
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {/* Compliance Calendar */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Compliance Calendar</h3>
          <div className="space-y-3">
            {complianceData.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <span className="text-sm font-medium text-gray-900">{item.month} 2024</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  item.color === 'green' ? 'bg-green-100 text-green-800' :
                  item.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quantum Job Queue */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quantum Job Queue</h3>
          <div className="space-y-3">
            {quantumJobs.map((job) => (
              <div key={job.id} className="p-3 bg-gray-50 rounded-md">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{job.module}</span>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    job.status === 'Completed' ? 'bg-green-100 text-green-800' :
                    job.status === 'Running' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {job.status}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${job.progress}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">{job.progress}% complete</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const KPICard = ({ title, value, change }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">{value}</dd>
          </dl>
        </div>
        <div className="flex-shrink-0">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            change.startsWith('+') ? 'bg-green-100 text-green-800' :
            change.startsWith('-') ? 'bg-red-100 text-red-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {change}
          </span>
        </div>
      </div>
    </div>
  </div>
);