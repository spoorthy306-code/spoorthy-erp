// SPOORTHY QUANTUM OS — Portfolio & Risk Page
// React + TypeScript + Tailwind CSS

import React, { useState } from 'react';
import { Pie, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
} from 'chart.js';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement
);

export const PortfolioRisk = () => {
  const [selectedPortfolio, setSelectedPortfolio] = useState('conservative');
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);

  const runOptimization = async () => {
    setIsOptimizing(true);

    // Simulate quantum portfolio optimization
    setTimeout(() => {
      setOptimizationResult({
        conservative: {
          expectedReturn: 8.5,
          volatility: 12.3,
          sharpeRatio: 0.69,
          maxDrawdown: -8.2,
          allocation: [
            { asset: 'Government Bonds', weight: 0.40, return: 6.2, risk: 8.1 },
            { asset: 'Corporate Bonds', weight: 0.30, return: 7.8, risk: 10.5 },
            { asset: 'Large Cap Stocks', weight: 0.20, return: 12.5, risk: 18.2 },
            { asset: 'Gold ETF', weight: 0.10, return: 8.9, risk: 15.3 }
          ],
          quantumMetrics: {
            solveTime: 850,
            qubits: 512,
            energy: -125.67,
            confidence: 0.94
          }
        },
        balanced: {
          expectedReturn: 11.2,
          volatility: 15.8,
          sharpeRatio: 0.71,
          maxDrawdown: -12.5,
          allocation: [
            { asset: 'Large Cap Stocks', weight: 0.35, return: 12.5, risk: 18.2 },
            { asset: 'Mid Cap Stocks', weight: 0.25, return: 14.2, risk: 22.1 },
            { asset: 'Corporate Bonds', weight: 0.25, return: 7.8, risk: 10.5 },
            { asset: 'International Funds', weight: 0.15, return: 9.8, risk: 16.7 }
          ],
          quantumMetrics: {
            solveTime: 920,
            qubits: 512,
            energy: -118.34,
            confidence: 0.91
          }
        },
        aggressive: {
          expectedReturn: 15.8,
          volatility: 22.4,
          sharpeRatio: 0.71,
          maxDrawdown: -18.7,
          allocation: [
            { asset: 'Large Cap Stocks', weight: 0.40, return: 12.5, risk: 18.2 },
            { asset: 'Mid Cap Stocks', weight: 0.30, return: 14.2, risk: 22.1 },
            { asset: 'Small Cap Stocks', weight: 0.20, return: 16.8, risk: 28.5 },
            { asset: 'Sector Funds', weight: 0.10, return: 18.5, risk: 32.1 }
          ],
          quantumMetrics: {
            solveTime: 1050,
            qubits: 512,
            energy: -95.23,
            confidence: 0.87
          }
        },
        riskMetrics: {
          var95: -185000,
          cvar95: -245000,
          beta: 0.85,
          alpha: 0.023,
          trackingError: 0.045
        },
        stressTests: [
          { scenario: 'Market Crash (-30%)', loss: -425000, probability: 0.05 },
          { scenario: 'Recession (-15%)', loss: -210000, probability: 0.15 },
          { scenario: 'Inflation Spike (+8%)', loss: -95000, probability: 0.10 },
          { scenario: 'Interest Rate Hike (+2%)', loss: -135000, probability: 0.20 }
        ],
        performance: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          portfolio: [100, 102.5, 98.7, 105.2, 108.9, 112.4, 115.8, 118.3, 121.7, 119.5, 124.2, 127.8],
          benchmark: [100, 101.8, 97.2, 103.5, 106.8, 109.9, 113.2, 115.1, 117.8, 116.4, 120.9, 123.5]
        }
      });
      setIsOptimizing(false);
    }, 3000);
  };

  const renderAllocationChart = () => {
    if (!optimizationResult || !optimizationResult[selectedPortfolio]) return null;

    const data = {
      labels: optimizationResult[selectedPortfolio].allocation.map(item => item.asset),
      datasets: [{
        data: optimizationResult[selectedPortfolio].allocation.map(item => item.weight * 100),
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(249, 115, 22, 0.8)',
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(168, 85, 247, 1)',
          'rgba(249, 115, 22, 1)',
        ],
        borderWidth: 1,
      }],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'right' as const,
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.label}: ${context.parsed.toFixed(1)}%`;
            }
          }
        }
      }
    };

    return <Pie data={data} options={options} />;
  };

  const renderPerformanceChart = () => {
    if (!optimizationResult || !optimizationResult.performance) return null;

    const data = {
      labels: optimizationResult.performance.labels,
      datasets: [
        {
          label: 'Portfolio',
          data: optimizationResult.performance.portfolio,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Benchmark',
          data: optimizationResult.performance.benchmark,
          borderColor: 'rgb(156, 163, 175)',
          backgroundColor: 'rgba(156, 163, 175, 0.1)',
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
          text: 'Portfolio Performance vs Benchmark',
        },
      },
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: function(value) {
              return value.toFixed(1);
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
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-sm font-medium text-gray-700">Portfolio Type</label>
              <select
                value={selectedPortfolio}
                onChange={(e) => setSelectedPortfolio(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="conservative">Conservative</option>
                <option value="balanced">Balanced</option>
                <option value="aggressive">Aggressive</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={runOptimization}
                disabled={isOptimizing}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                  isOptimizing
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                }`}
              >
                {isOptimizing ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Running Quantum Optimization...
                  </>
                ) : (
                  <>
                    ⚛️ Run Quantum Optimization
                  </>
                )}
              </button>
            </div>

            <div className="flex items-end">
              <button
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Export Report
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      {optimizationResult && optimizationResult[selectedPortfolio] && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            title="Expected Return"
            value={`${optimizationResult[selectedPortfolio].expectedReturn}%`}
            color="green"
          />
          <MetricCard
            title="Volatility"
            value={`${optimizationResult[selectedPortfolio].volatility}%`}
            color="yellow"
          />
          <MetricCard
            title="Sharpe Ratio"
            value={optimizationResult[selectedPortfolio].sharpeRatio.toFixed(2)}
            color="blue"
          />
          <MetricCard
            title="Max Drawdown"
            value={`${optimizationResult[selectedPortfolio].maxDrawdown}%`}
            color="red"
          />
        </div>
      )}

      {/* Charts Section */}
      {optimizationResult && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Allocation Chart */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Asset Allocation
              </h3>
              <div className="h-80">
                {renderAllocationChart()}
              </div>
            </div>
          </div>

          {/* Performance Chart */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Performance vs Benchmark
              </h3>
              <div className="h-80">
                {renderPerformanceChart()}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Allocation Details */}
      {optimizationResult && optimizationResult[selectedPortfolio] && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Asset Allocation Details
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Asset
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Weight
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Expected Return
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Risk (Volatility)
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {optimizationResult[selectedPortfolio].allocation.map((asset, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {asset.asset}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {(asset.weight * 100).toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {asset.return}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {asset.risk}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Risk Analysis */}
      {optimizationResult && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Metrics */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Risk Metrics
              </h3>
              <div className="space-y-4">
                <RiskMetric
                  title="VaR (95% Confidence)"
                  value={`₹${Math.abs(optimizationResult.riskMetrics.var95).toLocaleString()}`}
                  type="loss"
                />
                <RiskMetric
                  title="CVaR (95% Confidence)"
                  value={`₹${Math.abs(optimizationResult.riskMetrics.cvar95).toLocaleString()}`}
                  type="loss"
                />
                <RiskMetric
                  title="Beta"
                  value={optimizationResult.riskMetrics.beta.toFixed(2)}
                  type="neutral"
                />
                <RiskMetric
                  title="Alpha"
                  value={`${(optimizationResult.riskMetrics.alpha * 100).toFixed(2)}%`}
                  type="positive"
                />
                <RiskMetric
                  title="Tracking Error"
                  value={`${(optimizationResult.riskMetrics.trackingError * 100).toFixed(2)}%`}
                  type="neutral"
                />
              </div>
            </div>
          </div>

          {/* Stress Tests */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Stress Test Scenarios
              </h3>
              <div className="space-y-3">
                {optimizationResult.stressTests.map((test, index) => (
                  <div key={index} className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{test.scenario}</p>
                      <p className="text-xs text-gray-500">Probability: {(test.probability * 100).toFixed(1)}%</p>
                    </div>
                    <span className="text-sm font-medium text-red-600">
                      -₹{Math.abs(test.loss).toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quantum Metrics */}
      {optimizationResult && optimizationResult[selectedPortfolio] && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Quantum Solve Metrics
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
              <QuantumMetric
                title="Solve Time"
                value={`${optimizationResult[selectedPortfolio].quantumMetrics.solveTime}ms`}
              />
              <QuantumMetric
                title="Qubits Used"
                value={optimizationResult[selectedPortfolio].quantumMetrics.qubits}
              />
              <QuantumMetric
                title="Ground Energy"
                value={optimizationResult[selectedPortfolio].quantumMetrics.energy.toFixed(2)}
              />
              <QuantumMetric
                title="Confidence"
                value={`${(optimizationResult[selectedPortfolio].quantumMetrics.confidence * 100).toFixed(1)}%`}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MetricCard = ({ title, value, color }) => {
  const colorClasses = {
    green: 'bg-green-50 border-green-200',
    blue: 'bg-blue-50 border-blue-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    red: 'bg-red-50 border-red-200'
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color]}`}>
      <div className="text-sm font-medium text-gray-500">{title}</div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
};

const RiskMetric = ({ title, value, type }) => {
  const typeClasses = {
    positive: 'text-green-600',
    negative: 'text-red-600',
    neutral: 'text-gray-900',
    loss: 'text-red-600'
  };

  return (
    <div className="flex justify-between items-center py-2">
      <span className="text-sm text-gray-600">{title}</span>
      <span className={`text-sm font-medium ${typeClasses[type]}`}>{value}</span>
    </div>
  );
};

const QuantumMetric = ({ title, value }) => (
  <div className="bg-gray-50 p-4 rounded-lg">
    <div className="text-sm font-medium text-gray-500">{title}</div>
    <div className="text-lg font-bold text-gray-900">{value}</div>
  </div>
);