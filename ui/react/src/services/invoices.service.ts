import { api } from '@/services/api';
import type { Invoice, InvoiceCreate } from '@/types/invoice.types';

export const invoicesService = {
  async list(entityId: string, startDate?: string, endDate?: string): Promise<Invoice[]> {
    const params: Record<string, string> = { entity_id: entityId };
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    const { data } = await api.get<Invoice[]>('/api/v1/invoices', { params });
    return data;
  },

  async get(invoiceId: string): Promise<Invoice> {
    const { data } = await api.get<Invoice>(`/api/v1/invoices/${invoiceId}`);
    return data;
  },

  async create(payload: InvoiceCreate): Promise<Invoice> {
    const { data } = await api.post<Invoice>('/api/v1/invoices', payload);
    return data;
  },

  async generateIRN(invoiceId: string): Promise<{ invoice_id: string; irn: string; qr_code: string }> {
    const { data } = await api.post(`/api/v1/invoices/${invoiceId}/generate-irn`);
    return data;
  },
};
