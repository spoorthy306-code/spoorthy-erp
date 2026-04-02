// SPOORTHY QUANTUM OS — GST Compliance Page
// React + TypeScript + Tailwind CSS

import React, { useState } from 'react';

export const GSTCompliance = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('MAR2024');
  const [selectedReturn, setSelectedReturn] = useState('gstr1');
  const [isGenerating, setIsGenerating] = useState(false);
  const [returnData, setReturnData] = useState(null);

  const generateReturn = async () => {
    setIsGenerating(true);

    // Simulate GST return generation
    setTimeout(() => {
      setReturnData({
        gstr1: {
          gstin: '27AABCS1234C1Z1',
          period: 'Mar-2024',
          summary: {
            totalInvoices: 145,
            totalValue: 12500000,
            taxableValue: 11800000,
            igst: 180000,
            cgst: 135000,
            sgst: 135000,
            totalTax: 450000
          },
          b2b: [
            { gstin: '29AAAAA0000A1Z5', invoiceNo: 'INV001', date: '2024-03-15', value: 500000, rate: 18, tax: 90000 },
            { gstin: '33BBBBB0000B1Z6', invoiceNo: 'INV002', date: '2024-03-20', value: 750000, rate: 18, tax: 135000 },
            { gstin: '36CCCCC0000C1Z7', invoiceNo: 'INV003', date: '2024-03-25', value: 300000, rate: 12, tax: 36000 },
          ],
          b2c: {
            small: { count: 25, value: 1500000, tax: 225000 },
            large: { count: 12, value: 2800000, tax: 420000 }
          },
          exports: {
            count: 8,
            value: 2000000,
            tax: 0
          }
        },
        gstr3b: {
          gstin: '27AABCS1234C1Z1',
          period: 'Mar-2024',
          outward: {
            taxable: 11800000,
            exempted: 700000,
            total: 12500000
          },
          inward: {
            taxable: 8500000,
            exempted: 500000,
            total: 9000000
          },
          itc: {
            igst: 180000,
            cgst: 135000,
            sgst: 135000,
            total: 450000
          },
          taxPayable: {
            igst: 180000,
            cgst: 135000,
            sgst: 135000,
            total: 450000
          }
        },
        compliance: {
          status: 'Compliant',
          lastFiled: '2024-04-15',
          nextDue: '2024-05-20',
          penalties: 0,
          notices: 0,
          refunds: 25000
        }
      });
      setIsGenerating(false);
    }, 2500);
  };

  const fileReturn = () => {
    // Simulate GST return filing
    alert('GST Return filed successfully with GSTN!');
  };

  const renderReturn = () => {
    if (!returnData) return null;

    switch (selectedReturn) {
      case 'gstr1':
        return <GSTR1 data={returnData.gstr1} />;
      case 'gstr3b':
        return <GSTR3B data={returnData.gstr3b} />;
      default:
        return null;
    }
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
                <option value="MAR2024">March 2024</option>
                <option value="FEB2024">February 2024</option>
                <option value="JAN2024">January 2024</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Return Type</label>
              <select
                value={selectedReturn}
                onChange={(e) => setSelectedReturn(e.target.value)}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="gstr1">GSTR-1</option>
                <option value="gstr3b">GSTR-3B</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={generateReturn}
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
                  'Generate Return'
                )}
              </button>
            </div>

            <div className="flex items-end">
              <button
                onClick={fileReturn}
                disabled={!returnData}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                File with GSTN
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Status */}
      {returnData && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Compliance Status
            </h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
              <StatusCard
                title="Status"
                value={returnData.compliance.status}
                color={returnData.compliance.status === 'Compliant' ? 'green' : 'red'}
              />
              <StatusCard
                title="Last Filed"
                value={returnData.compliance.lastFiled}
                color="blue"
              />
              <StatusCard
                title="Next Due"
                value={returnData.compliance.nextDue}
                color="yellow"
              />
              <StatusCard
                title="Pending Refunds"
                value={`₹${returnData.compliance.refunds.toLocaleString()}`}
                color="green"
              />
            </div>
          </div>
        </div>
      )}

      {/* Return Display */}
      {returnData && renderReturn()}

      {/* GST Rate Summary */}
      {returnData && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              GST Rate-wise Summary
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      GST Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Taxable Value
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IGST
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CGST
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      SGST
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Tax
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">18%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹8,500,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹765,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹765,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹765,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">₹2,295,000</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">12%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹2,500,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹150,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹150,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹150,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">₹450,000</td>
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">5%</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹750,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹18,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹18,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₹18,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">₹56,250</td>
                  </tr>
                  <tr className="bg-gray-50 font-bold">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">Total</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">₹11,750,000</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">₹933,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">₹933,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">₹933,750</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">₹2,801,250</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StatusCard = ({ title, value, color }) => {
  const colorClasses = {
    green: 'bg-green-50 border-green-200 text-green-800',
    red: 'bg-red-50 border-red-200 text-red-800',
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800'
  };

  return (
    <div className={`border rounded-lg p-4 ${colorClasses[color]}`}>
      <div className="text-sm font-medium text-gray-500">{title}</div>
      <div className="text-lg font-bold">{value}</div>
    </div>
  );
};

const GSTR1 = ({ data }) => (
  <div className="space-y-6">
    {/* Summary */}
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          GSTR-1 Summary - {data.period}
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <SummaryCard title="Total Invoices" value={data.summary.totalInvoices} />
          <SummaryCard title="Total Value" value={`₹${data.summary.totalValue.toLocaleString()}`} />
          <SummaryCard title="Total Tax" value={`₹${data.summary.totalTax.toLocaleString()}`} />
        </div>
      </div>
    </div>

    {/* B2B Invoices */}
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          B2B Invoices
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  GSTIN
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice No
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tax
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data.b2b.map((invoice, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {invoice.gstin}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {invoice.invoiceNo}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {invoice.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ₹{invoice.value.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {invoice.rate}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ₹{invoice.tax.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    {/* B2C Summary */}
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          B2C Summary
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Small Invoices (≤₹2.5L)</h4>
            <p className="text-lg font-bold text-gray-900">{data.b2c.small.count} invoices</p>
            <p className="text-sm text-gray-600">Value: ₹{data.b2c.small.value.toLocaleString()}</p>
            <p className="text-sm text-gray-600">Tax: ₹{data.b2c.small.tax.toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Large Invoices (>₹2.5L)</h4>
            <p className="text-lg font-bold text-gray-900">{data.b2c.large.count} invoices</p>
            <p className="text-sm text-gray-600">Value: ₹{data.b2c.large.value.toLocaleString()}</p>
            <p className="text-sm text-gray-600">Tax: ₹{data.b2c.large.tax.toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const GSTR3B = ({ data }) => (
  <div className="space-y-6">
    {/* Summary */}
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          GSTR-3B Summary - {data.period}
        </h3>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Outward Supplies</h4>
            <div className="space-y-2">
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Taxable</span>
                <span className="text-sm font-medium text-gray-900">₹{data.outward.taxable.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Exempted</span>
                <span className="text-sm font-medium text-gray-900">₹{data.outward.exempted.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2 font-bold border-t border-gray-300">
                <span className="text-sm">Total</span>
                <span className="text-sm">₹{data.outward.total.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-md font-medium text-gray-900 mb-3">Inward Supplies</h4>
            <div className="space-y-2">
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Taxable</span>
                <span className="text-sm font-medium text-gray-900">₹{data.inward.taxable.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-sm text-gray-600">Exempted</span>
                <span className="text-sm font-medium text-gray-900">₹{data.inward.exempted.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2 font-bold border-t border-gray-300">
                <span className="text-sm">Total</span>
                <span className="text-sm">₹{data.inward.total.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* ITC and Tax Payable */}
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Input Tax Credit
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">IGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.itc.igst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">CGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.itc.cgst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">SGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.itc.sgst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2 font-bold border-t border-gray-300">
              <span className="text-sm">Total ITC</span>
              <span className="text-sm">₹{data.itc.total.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Tax Payable
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">IGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.taxPayable.igst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">CGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.taxPayable.cgst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-sm text-gray-600">SGST</span>
              <span className="text-sm font-medium text-gray-900">₹{data.taxPayable.sgst.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2 font-bold border-t border-gray-300">
              <span className="text-sm">Total Payable</span>
              <span className="text-sm">₹{data.taxPayable.total.toLocaleString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const SummaryCard = ({ title, value }) => (
  <div className="bg-gray-50 p-4 rounded-lg">
    <div className="text-sm font-medium text-gray-500">{title}</div>
    <div className="text-2xl font-bold text-gray-900">{value}</div>
  </div>
);