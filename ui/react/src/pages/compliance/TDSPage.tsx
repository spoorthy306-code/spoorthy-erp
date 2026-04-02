import React, { useState } from 'react';
import { useEntityStore } from '../../store/entityStore';

interface ChallanEntry {
  id: string;
  quarter: string;
  form_type: '24Q' | '26Q';
  total_tds: number;
  deposited: number;
  challan_no: string;
  deposit_date: string;
  bank: string;
  status: 'PAID' | 'PENDING' | 'OVERDUE';
}

const SAMPLE_CHALLANS: ChallanEntry[] = [
  { id: '1', quarter: 'Q3 FY2025-26', form_type: '26Q', total_tds: 185000, deposited: 185000, challan_no: 'CHL20260115001', deposit_date: '2026-01-15', bank: 'HDFC Bank', status: 'PAID' },
  { id: '2', quarter: 'Q3 FY2025-26', form_type: '24Q', total_tds: 95000,  deposited: 95000,  challan_no: 'CHL20260115002', deposit_date: '2026-01-15', bank: 'HDFC Bank', status: 'PAID' },
  { id: '3', quarter: 'Q4 FY2025-26', form_type: '26Q', total_tds: 210000, deposited: 0,      challan_no: '',               deposit_date: '',           bank: '',          status: 'PENDING' },
  { id: '4', quarter: 'Q4 FY2025-26', form_type: '24Q', total_tds: 112000, deposited: 0,      challan_no: '',               deposit_date: '',           bank: '',          status: 'PENDING' },
];

const STATUS_CLS: Record<ChallanEntry['status'], string> = {
  PAID:    'bg-green-100 text-green-700',
  PENDING: 'bg-yellow-100 text-yellow-700',
  OVERDUE: 'bg-red-100 text-red-700',
};

const fmtINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v);

export const TDSPage: React.FC = () => {
  const { selectedEntity } = useEntityStore();
  const [challans] = useState<ChallanEntry[]>(SAMPLE_CHALLANS);
  const [activeForm, setActiveForm] = useState<'24Q' | '26Q'>('26Q');

  const filtered = challans.filter((c) => c.form_type === activeForm);
  const totalTDS = filtered.reduce((s, c) => s + c.total_tds, 0);
  const totalDeposited = filtered.reduce((s, c) => s + c.deposited, 0);
  const totalPending = totalTDS - totalDeposited;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">TDS Compliance</h1>
      <p className="text-sm text-gray-500 mb-6">{selectedEntity?.name} · Form 24Q (Salary) &amp; 26Q (Non-Salary)</p>

      <div className="flex gap-2 mb-6">
        {(['26Q', '24Q'] as const).map((f) => (
          <button key={f} onClick={() => setActiveForm(f)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeForm === f ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}>
            Form {f} {f === '24Q' ? '(Salary)' : '(Non-Salary)'}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          ['Total TDS Deducted', fmtINR(totalTDS), 'text-gray-900'],
          ['Total Deposited',    fmtINR(totalDeposited), 'text-green-700'],
          ['Pending Deposit',    fmtINR(totalPending), totalPending > 0 ? 'text-red-600' : 'text-gray-500'],
        ].map(([label, value, cls]) => (
          <div key={label} className="rounded-xl bg-white border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`text-xl font-bold ${cls}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              {['Quarter', 'Form', 'TDS Deducted', 'Deposited', 'Challan No', 'Deposit Date', 'Bank', 'Status'].map((h) => (
                <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {filtered.map((c) => (
              <tr key={c.id} className="hover:bg-blue-50">
                <td className="px-4 py-2.5">{c.quarter}</td>
                <td className="px-4 py-2.5 font-mono text-xs">{c.form_type}</td>
                <td className="px-4 py-2.5 text-right">{fmtINR(c.total_tds)}</td>
                <td className="px-4 py-2.5 text-right">{c.deposited ? fmtINR(c.deposited) : '—'}</td>
                <td className="px-4 py-2.5 font-mono text-xs">{c.challan_no || '—'}</td>
                <td className="px-4 py-2.5">{c.deposit_date || '—'}</td>
                <td className="px-4 py-2.5">{c.bank || '—'}</td>
                <td className="px-4 py-2.5">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_CLS[c.status]}`}>
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TDSPage;
