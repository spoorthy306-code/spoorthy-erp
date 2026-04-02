import React from 'react';
import { useEntityStore } from '../../store/entityStore';

interface EmployeePF {
  emp_id: string;
  name: string;
  basic_salary: number;
  pf_wage: number;
  ee_pf: number;        // Employee PF 12%
  er_pf: number;        // Employer PF 3.67%
  er_eps: number;       // Employer EPS 8.33%
  esic_applicable: boolean;
  ee_esic: number;      // 0.75%
  er_esic: number;      // 3.25%
  pt: number;           // Professional Tax
}

function computePF(emp: Omit<EmployeePF, 'ee_pf' | 'er_pf' | 'er_eps' | 'ee_esic' | 'er_esic' | 'pt'>): EmployeePF {
  const PF_CEILING = 15000;
  const ESIC_CEILING = 21000;

  const pf_wage = Math.min(emp.pf_wage, PF_CEILING);
  const ee_pf   = Math.round(pf_wage * 0.12);
  const er_total_pf = Math.round(pf_wage * 0.12);
  const er_eps  = Math.round(Math.min(pf_wage, PF_CEILING) * 0.0833);
  const er_pf   = er_total_pf - er_eps;

  const esic = emp.basic_salary <= ESIC_CEILING;
  const ee_esic = esic ? Math.round(emp.basic_salary * 0.0075) : 0;
  const er_esic = esic ? Math.round(emp.basic_salary * 0.0325) : 0;

  // Professional Tax (Karnataka slab)
  let pt = 0;
  if (emp.basic_salary > 15000) pt = 200;
  else if (emp.basic_salary > 10000) pt = 150;
  else if (emp.basic_salary > 7500) pt = 100;

  return { ...emp, ee_pf, er_pf, er_eps, esic_applicable: esic, ee_esic, er_esic, pt };
}

const SAMPLE_EMPLOYEES: Omit<EmployeePF, 'ee_pf' | 'er_pf' | 'er_eps' | 'ee_esic' | 'er_esic' | 'pt'>[] = [
  { emp_id: 'E001', name: 'Ramesh Kumar',    basic_salary: 45000, pf_wage: 15000, esic_applicable: false },
  { emp_id: 'E002', name: 'Priya Sharma',    basic_salary: 18000, pf_wage: 15000, esic_applicable: true  },
  { emp_id: 'E003', name: 'Anil Reddy',      basic_salary: 12000, pf_wage: 12000, esic_applicable: true  },
  { emp_id: 'E004', name: 'Sunita Gupta',    basic_salary: 28000, pf_wage: 15000, esic_applicable: false },
];

const fmtINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v);

export const PFPage: React.FC = () => {
  const { selectedEntity } = useEntityStore();
  const employees: EmployeePF[] = SAMPLE_EMPLOYEES.map(computePF);

  const totals = employees.reduce(
    (acc, e) => ({
      ee_pf: acc.ee_pf + e.ee_pf,
      er_pf: acc.er_pf + e.er_pf,
      er_eps: acc.er_eps + e.er_eps,
      ee_esic: acc.ee_esic + e.ee_esic,
      er_esic: acc.er_esic + e.er_esic,
      pt: acc.pt + e.pt,
    }),
    { ee_pf: 0, er_pf: 0, er_eps: 0, ee_esic: 0, er_esic: 0, pt: 0 }
  );

  const totalEmployerLiability = totals.er_pf + totals.er_eps + totals.er_esic;
  const totalEmployeeDeductions = totals.ee_pf + totals.ee_esic + totals.pt;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">PF / ESIC / PT Compliance</h1>
      <p className="text-sm text-gray-500 mb-6">{selectedEntity?.name} · Current Month</p>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          ['Employee PF (12%)',        fmtINR(totals.ee_pf),                'text-blue-700'],
          ['Employer PF + EPS',        fmtINR(totals.er_pf + totals.er_eps), 'text-indigo-700'],
          ['ESIC (Employer 3.25%)',    fmtINR(totals.er_esic),               'text-purple-700'],
          ['Total Employer Liability', fmtINR(totalEmployerLiability),       'text-red-700'],
        ].map(([label, value, cls]) => (
          <div key={label} className="rounded-xl bg-white border border-gray-100 shadow-sm p-4">
            <p className="text-xs text-gray-500 mb-1">{label}</p>
            <p className={`text-lg font-bold ${cls}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-gray-100 shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              {['Employee', 'Basic', 'EE PF 12%', 'ER PF 3.67%', 'EPS 8.33%', 'EE ESIC 0.75%', 'ER ESIC 3.25%', 'PT', 'Total Deduction'].map((h) => (
                <th key={h} className="px-3 py-3 text-right first:text-left font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {employees.map((e) => (
              <tr key={e.emp_id} className="hover:bg-blue-50">
                <td className="px-3 py-2.5 font-medium">{e.name}</td>
                <td className="px-3 py-2.5 text-right">{fmtINR(e.basic_salary)}</td>
                <td className="px-3 py-2.5 text-right text-blue-700">{fmtINR(e.ee_pf)}</td>
                <td className="px-3 py-2.5 text-right text-indigo-700">{fmtINR(e.er_pf)}</td>
                <td className="px-3 py-2.5 text-right text-indigo-700">{fmtINR(e.er_eps)}</td>
                <td className="px-3 py-2.5 text-right">{e.esic_applicable ? fmtINR(e.ee_esic) : '—'}</td>
                <td className="px-3 py-2.5 text-right">{e.esic_applicable ? fmtINR(e.er_esic) : '—'}</td>
                <td className="px-3 py-2.5 text-right">{fmtINR(e.pt)}</td>
                <td className="px-3 py-2.5 text-right font-semibold">
                  {fmtINR(e.ee_pf + e.ee_esic + e.pt)}
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot className="bg-gray-50 text-xs font-semibold">
            <tr>
              <td className="px-3 py-2.5">Totals</td>
              <td />
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.ee_pf)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.er_pf)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.er_eps)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.ee_esic)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.er_esic)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totals.pt)}</td>
              <td className="px-3 py-2.5 text-right">{fmtINR(totalEmployeeDeductions)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
};

export default PFPage;
