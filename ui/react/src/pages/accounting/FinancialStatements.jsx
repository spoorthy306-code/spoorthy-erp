// SPOORTHY QUANTUM OS — Financial Statements Page
// React + TypeScript + Tailwind CSS

import React, { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
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
  Title,
  Tooltip,
  Legend
);

export const FinancialStatements = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('FY2024');
  const [selectedStatement, setSelectedStatement] = useState('pnl');
  const [isGenerating, setIsGenerating] = useState(false);
  const [statementData, setStatementData] = useState(null);

  const generateStatement = async () => {
    setIsGenerating(true);

    // Simulate statement generation
    setTimeout(() => {
      setStatementData({
        pnl: {
          revenue: 12500000,
          costOfSales: 7500000,
          grossProfit: 5000000,
          operatingExpenses: 2800000,
          operatingProfit: 2200000,
          interestExpense: 150000,
          profitBeforeTax: 2050000,
          taxExpense: 615000,
          netProfit: 1435000,
          items: [
            { account: 'Revenue', amount: 12500000, type: 'revenue' },
            { account: 'Cost of Sales', amount: -7500000, type: 'expense' },
            { account: 'Gross Profit', amount: 5000000, type: 'subtotal' },
            { account: 'Operating Expenses', amount: -2800000, type: 'expense' },
            { account: 'Operating Profit', amount: 2200000, type: 'subtotal' },
            { account: 'Interest Expense', amount: -150000, type: 'expense' },
            { account: 'Profit Before Tax', amount: 2050000, type: 'subtotal' },
            { account: 'Tax Expense', amount: -615000, type: 'expense' },
            { account: 'Net Profit', amount: 1435000, type: 'total' },
          ]
        },
        balanceSheet: {
          assets: {
            currentAssets: 8500000,
            fixedAssets: 12000000,
            totalAssets: 20500000,
            items: [
              { account: 'Cash & Bank', amount: 2500000 },
              { account: 'Accounts Receivable', amount: 3500000 },
              { account: 'Inventory', amount: 2500000 },
              { account: 'Fixed Assets', amount: 12000000 },
            ]
          },
          liabilities: {
            currentLiabilities: 4500000,
            longTermLiabilities: 3500000,
            equity: 12500000,
            totalLiabilitiesEquity: 20500000,
            items: [
              { account: 'Accounts Payable', amount: 2500000 },
              { account: 'Short-term Loans', amount: 2000000 },
              { account: 'Long-term Loans', amount: 3500000 },
              { account: 'Share Capital', amount: 5000000 },
              { account: 'Retained Earnings', amount: 7500000 },
            ]
          }
        },
        cashFlow: {
          operatingCashFlow: 2800000,
          investingCashFlow: -1500000,
          financingCashFlow: -800000,
          netCashFlow: 500000,
          items: [
            { category: 'Operating Activities', amount: 2800000 },
            { category: 'Investing Activities', amount: -1500000 },
            { category: 'Financing Activities', amount: -800000 },
            { category: 'Net Cash Flow', amount: 500000 },
          ]
        },
        trends: {
          labels: ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
          revenue: [950000, 1050000, 1100000, 1150000, 1200000, 1250000, 1300000, 1350000, 1400000, 1450000, 1500000, 1550000],
          expenses: [650000, 700000, 750000, 800000, 850000, 900000, 950000, 1000000, 1050000, 1100000, 1150000, 1200000],
          profit: [300000, 350000, 350000, 350000, 350000, 350000, 350000, 350000, 350000, 350000, 350000, 350000]
        }
      });
      setIsGenerating(false);
    }, 2000);
  };

  const exportStatement = (format) => {
    // Simulate export
    alert(`Exporting ${selectedStatement.toUpperCase()} as ${format.toUpperCase()}`);
  };

  const renderStatement = () => {
    if (!statementData) return null;

    switch (selectedStatement) {
      case 'pnl':
        return <ProfitLossStatement data={statementData.pnl} />;
      case 'balance':
        return <BalanceSheet data={statementData.balanceSheet} />;
      case 'cashflow':
        return <CashFlowStatement data={statementData.cashFlow} />;
      default:
        return null;
    }
  };

  const renderChart = () => {
    if (!statementData || !statementData.trends) return null;

    const data = {
      labels: statementData.trends.labels,
      datasets: [
        {
          label: 'Revenue',
          data: statementData.trends.revenue,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Expenses',
          data: statementData.trends.expenses,
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Profit',
          data: statementData.trends.profit,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Financial Performance Trends',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '₹' + (value / 100000).toFixed(0) + 'L';
            }
          }
        }
      }
    };

    return <Line data={data} options={options} />;
  };

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Period</label>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="FY2024">FY 2023-24</option>
                <option value="FY2023">FY 2022-23</option>
                <option value="FY2022">FY 2021-22</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Statement</label>
              <select
                value={selectedStatement}
                onChange={(e) => setSelectedStatement(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="pnl">Profit & Loss</option>
                <option value="balance">Balance Sheet</option>
                <option value="cashflow">Cash Flow</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={generateStatement}
                disabled={isGenerating}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                  isGenerating
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                }`}
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  'Generate Statement'
                )}
              </button>
            </div>

            <div className="flex items-end space-x-2">
              <button
                onClick={() => exportStatement('pdf')}
                disabled={!statementData}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                PDF
              </button>
              <button
                onClick={() => exportStatement('excel')}
                disabled={!statementData}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                Excel
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Statement Display */}
      {statementData && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {renderStatement()}
          </div>
          <div className="space-y-6">
            {/* Key Metrics */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Key Metrics
                </h3>
                <div className="space-y-4">
                  <MetricCard
                    title="Revenue"
                    value={`₹${statementData.pnl.revenue.toLocaleString()}`}
                    change="+12.5%"
                    changeType="positive"
                  />
                  <MetricCard
                    title="Net Profit"
                    value={`₹${statementData.pnl.netProfit.toLocaleString()}`}
                    change="+8.3%"
                    changeType="positive"
                  />
                  <MetricCard
                    title="Gross Margin"
                    value={`${((statementData.pnl.grossProfit / statementData.pnl.revenue) * 100).toFixed(1)}%`}
                    change="+2.1%"
                    changeType="positive"
                  />
                  <MetricCard
                    title="Current Ratio"
                    value="1.89:1"
                    change="-0.1"
                    changeType="negative"
                  />
                </div>
              </div>
            </div>

            {/* Compliance Status */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Compliance Status
                </h3>
                <div className="space-y-3">
                  <ComplianceItem title="GST Returns" status="Filed" dueDate="15th Apr" />
                  <ComplianceItem title="ITR Filing" status="Pending" dueDate="31st Jul" />
                  <ComplianceItem title="MCA Filing" status="Filed" dueDate="30th Sep" />
                  <ComplianceItem title="TDS Returns" status="Filed" dueDate="31st Mar" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trends Chart */}
      {statementData && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Financial Trends
            </h3>
            <div className="h-80">
              {renderChart()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const ProfitLossStatement = ({ data }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
        Profit & Loss Statement - FY 2023-24
      </h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Account
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount (₹)
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.items.map((item, index) => (
              <tr key={index} className={item.type === 'total' ? 'bg-gray-50 font-bold' : item.type === 'subtotal' ? 'bg-gray-25 font-semibold' : ''}>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${item.type === 'total' ? 'font-bold' : item.type === 'subtotal' ? 'font-semibold' : 'text-gray-900'}`}>
                  {item.account}
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${item.amount < 0 ? 'text-red-600' : 'text-gray-900'} ${item.type === 'total' ? 'font-bold' : item.type === 'subtotal' ? 'font-semibold' : ''}`}>
                  {item.amount < 0 ? '(' : ''}₹{Math.abs(item.amount).toLocaleString()}{item.amount < 0 ? ')' : ''}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

const BalanceSheet = ({ data }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
        Balance Sheet - As on 31st March 2024
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Assets</h4>
          <div className="space-y-2">
            {data.assets.items.map((item, index) => (
              <div key={index} className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">{item.account}</span>
                <span className="text-sm font-medium text-gray-900">₹{item.amount.toLocaleString()}</span>
              </div>
            ))}
            <div className="flex justify-between py-2 font-bold border-t border-gray-300">
              <span className="text-sm">Total Assets</span>
              <span className="text-sm">₹{data.assets.totalAssets.toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-md font-medium text-gray-900 mb-3">Liabilities & Equity</h4>
          <div className="space-y-2">
            {data.liabilities.items.map((item, index) => (
              <div key={index} className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-sm text-gray-600">{item.account}</span>
                <span className="text-sm font-medium text-gray-900">₹{item.amount.toLocaleString()}</span>
              </div>
            ))}
            <div className="flex justify-between py-2 font-bold border-t border-gray-300">
              <span className="text-sm">Total Liabilities & Equity</span>
              <span className="text-sm">₹{data.liabilities.totalLiabilitiesEquity.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const CashFlowStatement = ({ data }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
        Cash Flow Statement - FY 2023-24
      </h3>
      <div className="space-y-4">
        {data.items.map((item, index) => (
          <div key={index} className={`flex justify-between py-3 px-4 rounded-lg ${item.category === 'Net Cash Flow' ? 'bg-indigo-50 border border-indigo-200' : 'bg-gray-50'}`}>
            <span className={`text-sm ${item.category === 'Net Cash Flow' ? 'font-bold text-indigo-900' : 'text-gray-600'}`}>
              {item.category}
            </span>
            <span className={`text-sm font-medium ${item.amount < 0 ? 'text-red-600' : item.category === 'Net Cash Flow' ? 'text-indigo-900 font-bold' : 'text-gray-900'}`}>
              {item.amount < 0 ? '(' : ''}₹{Math.abs(item.amount).toLocaleString()}{item.amount < 0 ? ')' : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const MetricCard = ({ title, value, change, changeType }) => (
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-gray-600">{title}</p>
      <p className="text-lg font-semibold text-gray-900">{value}</p>
    </div>
    <div className={`text-sm font-medium ${changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
      {change}
    </div>
  </div>
);

const ComplianceItem = ({ title, status, dueDate }) => (
  <div className="flex items-center justify-between py-2">
    <div>
      <p className="text-sm font-medium text-gray-900">{title}</p>
      <p className="text-xs text-gray-500">Due: {dueDate}</p>
    </div>
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
      status === 'Filed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
    }`}>
      {status}
    </span>
  </div>
);