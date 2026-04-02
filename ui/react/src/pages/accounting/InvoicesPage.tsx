import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { InvoiceTable } from '../../components/tables/InvoiceTable';
import type { Invoice } from '../../components/tables/InvoiceTable';
import { useEntityStore } from '../../store/entityStore';

const API_BASE = import.meta.env.VITE_API_URL ?? '/api/v1';

const apiFetch = async <T,>(url: string, options?: RequestInit): Promise<T> => {
  const token = localStorage.getItem('access_token');
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
};

interface NewInvoiceForm {
  invoice_no:    string;
  invoice_date:  string;
  buyer_name:    string;
  buyer_gstin:   string;
  total_amount:  string;
  tax_amount:    string;
}

const emptyForm = (): NewInvoiceForm => ({
  invoice_no:   '',
  invoice_date: new Date().toISOString().slice(0, 10),
  buyer_name:   '',
  buyer_gstin:  '',
  total_amount: '',
  tax_amount:   '',
});

export const InvoicesPage: React.FC = () => {
  const { selectedEntity } = useEntityStore();
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<NewInvoiceForm>(emptyForm());
  const [qrData, setQrData] = useState<string | null>(null);

  const { data: invoices = [], isLoading } = useQuery<Invoice[]>({
    queryKey: ['invoices', selectedEntity?.entity_id],
    queryFn: () =>
      apiFetch(`${API_BASE}/invoices/?entity_id=${selectedEntity!.entity_id}&limit=100`),
    enabled: !!selectedEntity,
  });

  const createMutation = useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      apiFetch<{ invoice_id: string; irn?: string; qr_code?: string }>(
        `${API_BASE}/invoices/`, { method: 'POST', body: JSON.stringify(body) }
      ),
    onSuccess: (data) => {
      void queryClient.invalidateQueries({ queryKey: ['invoices'] });
      if (data.qr_code) setQrData(data.qr_code);
      setShowForm(false);
      setForm(emptyForm());
    },
  });

  const handleSubmit = (e: React.FormEvent): void => {
    e.preventDefault();
    if (!selectedEntity) return;
    createMutation.mutate({
      entity_id:    selectedEntity.entity_id,
      invoice_no:   form.invoice_no,
      invoice_date: form.invoice_date,
      buyer_name:   form.buyer_name,
      buyer_gstin:  form.buyer_gstin,
      total_amount: parseFloat(form.total_amount) || 0,
      tax_amount:   parseFloat(form.tax_amount)   || 0,
      status:       'ACTIVE',
    });
  };

  const field = (key: keyof NewInvoiceForm): React.InputHTMLAttributes<HTMLInputElement> & { value: string } => ({
    value: form[key],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [key]: e.target.value })),
  });

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Invoices</h1>
          <p className="text-sm text-gray-500 mt-0.5">{selectedEntity?.name}</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? '✕ Cancel' : '+ New Invoice'}
        </button>
      </div>

      {qrData && (
        <div className="mb-4 rounded-lg border border-green-200 bg-green-50 p-4 text-sm">
          <p className="font-semibold text-green-700 mb-2">e-Invoice generated — IRN &amp; QR code</p>
          <pre className="text-xs text-green-800 whitespace-pre-wrap break-all">{qrData}</pre>
          <button onClick={() => setQrData(null)} className="mt-2 text-xs text-green-600 hover:underline">Dismiss</button>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 rounded-xl border border-blue-100 bg-blue-50 p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-blue-800 mb-4">New Invoice</h2>
          <div className="grid grid-cols-3 gap-4">
            {([
              ['Invoice No',    'invoice_no',    'text',   'e.g. INV2025-001'],
              ['Invoice Date',  'invoice_date',  'date',   ''],
              ['Buyer Name',    'buyer_name',    'text',   'Customer name'],
              ['Buyer GSTIN',   'buyer_gstin',   'text',   '29AAAAA0000A1Z5'],
              ['Total Amount',  'total_amount',  'number', '118000'],
              ['Tax Amount',    'tax_amount',    'number', '18000'],
            ] as [string, keyof NewInvoiceForm, string, string][]).map(([label, key, type, placeholder]) => (
              <div key={key}>
                <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
                <input type={type} placeholder={placeholder} required {...field(key)}
                  className="w-full rounded border border-gray-200 px-3 py-1.5 text-sm" />
              </div>
            ))}
          </div>
          <div className="mt-4 flex justify-end">
            <button type="submit" disabled={createMutation.isPending}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-blue-700">
              {createMutation.isPending ? 'Creating…' : 'Create Invoice'}
            </button>
          </div>
          {createMutation.isError && (
            <p className="mt-2 text-xs text-red-600">Error: {(createMutation.error as Error).message}</p>
          )}
        </form>
      )}

      <InvoiceTable invoices={invoices} loading={isLoading} />
    </div>
  );
};

export default InvoicesPage;
