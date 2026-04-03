import type { Invoice } from '@/types/invoice.types';
import { formatINR } from '@/utils/formatters';

interface Props {
  invoices: Invoice[];
  isLoading?: boolean;
  onGenerateIRN: (invoiceId: string) => Promise<unknown>;
  isGeneratingIRN?: boolean;
}

export function InvoiceList({ invoices, isLoading, onGenerateIRN, isGeneratingIRN }: Props) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500">
        Loading invoices…
      </div>
    );
  }

  if (!invoices.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500">
        No invoices found. Create one using the form above.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Invoice No</th>
            <th className="px-4 py-3">Date</th>
            <th className="px-4 py-3">Buyer</th>
            <th className="px-4 py-3 text-right">Amount</th>
            <th className="px-4 py-3 text-right">Tax</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">IRN</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((inv) => (
            <tr key={inv.invoice_id} className="border-t border-slate-200 hover:bg-slate-50 transition">
              <td className="px-4 py-3 font-medium text-ink">{inv.invoice_no ?? '—'}</td>
              <td className="px-4 py-3 text-slate-600">{inv.invoice_date ?? '—'}</td>
              <td className="px-4 py-3 text-slate-700">
                <div>{inv.buyer_name ?? '—'}</div>
                {inv.buyer_gstin && (
                  <div className="font-mono text-xs text-slate-400">{inv.buyer_gstin}</div>
                )}
              </td>
              <td className="px-4 py-3 text-right font-mono">
                {inv.total_amount != null ? formatINR(inv.total_amount) : '—'}
              </td>
              <td className="px-4 py-3 text-right font-mono text-slate-600">
                {inv.tax_amount != null ? formatINR(inv.tax_amount) : '—'}
              </td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  inv.status === 'ACTIVE' ? 'bg-success/10 text-success' : 'bg-slate-100 text-slate-500'
                }`}>
                  {inv.status}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-xs text-slate-500">
                {inv.irn ? inv.irn.slice(0, 16) + '…' : '—'}
              </td>
              <td className="px-4 py-3 text-right">
                {!inv.irn && (
                  <button
                    type="button"
                    onClick={() => void onGenerateIRN(inv.invoice_id)}
                    disabled={isGeneratingIRN}
                    className="focus-ring text-xs font-medium text-brand hover:underline disabled:opacity-60"
                  >
                    Generate IRN
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
