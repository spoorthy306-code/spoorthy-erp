import React from 'react';
import { DataTable, Column } from './DataTable';

export interface Invoice {
  invoice_id: string;
  invoice_no: string;
  invoice_date: string;
  buyer_name: string;
  buyer_gstin: string;
  total_amount: number;
  tax_amount: number;
  status: 'ACTIVE' | 'CANCELLED' | 'AMENDED' | 'PAID' | 'OVERDUE';
}

interface InvoiceTableProps {
  invoices: Invoice[];
  loading?: boolean;
  onDownload?: (invoice: Invoice) => void;
}

const STATUS_STYLES: Record<Invoice['status'], string> = {
  ACTIVE:    'bg-blue-100 text-blue-700',
  PAID:      'bg-green-100 text-green-700',
  OVERDUE:   'bg-red-100 text-red-700',
  CANCELLED: 'bg-gray-100 text-gray-500',
  AMENDED:   'bg-yellow-100 text-yellow-700',
};

const formatINR = (v: number): string =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(v);

const columns = (onDownload?: InvoiceTableProps['onDownload']): Column<Invoice>[] => [
  { key: 'invoice_no',   header: 'Invoice #',   className: 'font-mono text-xs' },
  { key: 'invoice_date', header: 'Date',         className: 'whitespace-nowrap' },
  { key: 'buyer_name',   header: 'Buyer' },
  { key: 'buyer_gstin',  header: 'Buyer GSTIN',  className: 'font-mono text-xs' },
  {
    key: 'total_amount',
    header: 'Total (₹)',
    render: (v) => <span className="font-semibold">{formatINR(Number(v))}</span>,
    className: 'text-right',
  },
  {
    key: 'tax_amount',
    header: 'Tax (₹)',
    render: (v) => formatINR(Number(v)),
    className: 'text-right',
  },
  {
    key: 'status',
    header: 'Status',
    render: (v) => {
      const s = v as Invoice['status'];
      return <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_STYLES[s]}`}>{s}</span>;
    },
  },
  {
    key: 'invoice_id',
    header: '',
    sortable: false,
    render: (_v, row) => onDownload ? (
      <button onClick={() => onDownload(row)}
        className="text-xs text-blue-600 hover:underline">PDF ↓</button>
    ) : null,
  },
];

export const InvoiceTable: React.FC<InvoiceTableProps> = ({ invoices, loading, onDownload }) => (
  <DataTable<Invoice>
    columns={columns(onDownload)}
    data={invoices}
    rowKey="invoice_id"
    loading={loading}
    searchKeys={['invoice_no', 'buyer_name', 'buyer_gstin']}
    emptyMessage="No invoices found."
  />
);

export default InvoiceTable;
