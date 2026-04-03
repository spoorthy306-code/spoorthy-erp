export type InvoiceStatus = 'ACTIVE' | 'CANCELLED';

export interface Invoice {
  invoice_id: string;
  entity_id: string;
  invoice_no?: string | null;
  invoice_date?: string | null;
  buyer_gstin?: string | null;
  buyer_name?: string | null;
  total_amount?: number | null;
  tax_amount?: number | null;
  irn?: string | null;
  qr_code?: string | null;
  status: InvoiceStatus | string;
  created_at: string;
}

export interface InvoiceCreate {
  entity_id: string;
  invoice_no: string;
  invoice_date: string;
  buyer_gstin?: string;
  buyer_name: string;
  total_amount: number;
  tax_amount: number;
}
