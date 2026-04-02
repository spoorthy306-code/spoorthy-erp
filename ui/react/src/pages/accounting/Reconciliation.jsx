// SPOORTHY QUANTUM OS — Reconciliation Page
// React + TypeScript + Tailwind CSS

import React, { useState, useRef } from 'react';

export const Reconciliation = () => {
  const [bankFile, setBankFile] = useState(null);
  const [itemsFile, setItemsFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const bankFileRef = useRef();
  const itemsFileRef = useRef();

  const handleFileUpload = (event, type) => {
    const file = event.target.files[0];
    if (type === 'bank') {
      setBankFile(file);
    } else {
      setItemsFile(file);
    }
  };

  const runReconciliation = async () => {
    if (!bankFile || !itemsFile) {
      alert('Please upload both bank statement and open items files');
      return;
    }

    setIsProcessing(true);

    // Simulate quantum reconciliation process
    setTimeout(() => {
      setResults({
        totalBankItems: 150,
        totalOpenItems: 200,
        matchedItems: 142,
        matchRate: 94.7,
        unmatchedBank: 8,
        unmatchedItems: 58,
        energy: -45.67,
        solveTime: 1200,
        matches: [
          { bankRef: 'TXN001', itemRef: 'INV001', amount: 118000, confidence: 0.98 },
          { bankRef: 'TXN002', itemRef: 'INV002', amount: 85000, confidence: 0.95 },
          { bankRef: 'TXN003', itemRef: 'INV003', amount: 67500, confidence: 0.92 },
        ],
        unmatchedBankItems: [
          { ref: 'TXN008', amount: 25000, date: '2024-04-15' },
          { ref: 'TXN012', amount: 15000, date: '2024-04-16' },
        ],
        unmatchedOpenItems: [
          { ref: 'INV015', amount: 30000, dueDate: '2024-04-20' },
          { ref: 'INV018', amount: 45000, dueDate: '2024-04-22' },
        ]
      });
      setIsProcessing(false);
    }, 3000);
  };

  const postToLedger = () => {
    // Simulate posting matched items to ledger
    alert('Matched items posted to general ledger successfully!');
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Bank Reconciliation
          </h3>

          {/* File Upload Section */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Bank Statement (CSV)
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label htmlFor="bank-file" className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                      <span>Upload bank statement</span>
                      <input
                        id="bank-file"
                        name="bank-file"
                        type="file"
                        accept=".csv"
                        className="sr-only"
                        ref={bankFileRef}
                        onChange={(e) => handleFileUpload(e, 'bank')}
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">
                    {bankFile ? bankFile.name : 'CSV up to 10MB'}
                  </p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Open Items (CSV)
              </label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <div className="flex text-sm text-gray-600">
                    <label htmlFor="items-file" className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500">
                      <span>Upload open items</span>
                      <input
                        id="items-file"
                        name="items-file"
                        type="file"
                        accept=".csv"
                        className="sr-only"
                        ref={itemsFileRef}
                        onChange={(e) => handleFileUpload(e, 'items')}
                      />
                    </label>
                  </div>
                  <p className="text-xs text-gray-500">
                    {itemsFile ? itemsFile.name : 'CSV up to 10MB'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Run Reconciliation Button */}
          <div className="mt-6">
            <button
              onClick={runReconciliation}
              disabled={!bankFile || !itemsFile || isProcessing}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                !bankFile || !itemsFile || isProcessing
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Quantum Reconciliation...
                </>
              ) : (
                <>
                  ⚛️ Run Quantum Reconciliation
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {results && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <ResultCard title="Match Rate" value={`${results.matchRate}%`} color="green" />
            <ResultCard title="Matched Items" value={results.matchedItems} color="blue" />
            <ResultCard title="Unmatched Bank" value={results.unmatchedBank} color="yellow" />
            <ResultCard title="Unmatched Items" value={results.unmatchedItems} color="red" />
          </div>

          {/* Quantum Metrics */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Quantum Solve Metrics
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-500">Energy</div>
                  <div className="text-2xl font-bold text-gray-900">{results.energy}</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-500">Solve Time</div>
                  <div className="text-2xl font-bold text-gray-900">{results.solveTime}ms</div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm text-gray-500">QUBO Size</div>
                  <div className="text-2xl font-bold text-gray-900">{results.totalBankItems + results.totalOpenItems}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Matched Items Table */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Matched Items
                </h3>
                <button
                  onClick={postToLedger}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Post to Ledger
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Bank Reference
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Item Reference
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confidence
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.matches.map((match, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {match.bankRef}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {match.itemRef}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          ₹{match.amount.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            {(match.confidence * 100).toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Unmatched Items */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <UnmatchedTable title="Unmatched Bank Items" items={results.unmatchedBankItems} type="bank" />
            <UnmatchedTable title="Unmatched Open Items" items={results.unmatchedOpenItems} type="items" />
          </div>
        </div>
      )}
    </div>
  );
};

const ResultCard = ({ title, value, color }) => {
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

const UnmatchedTable = ({ title, items, type }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">{title}</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Reference
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {type === 'bank' ? 'Date' : 'Due Date'}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {item.ref}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  ₹{item.amount.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {item.date || item.dueDate}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);