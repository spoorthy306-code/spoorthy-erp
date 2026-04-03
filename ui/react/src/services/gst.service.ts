import { api } from '@/services/api';
import type { GSTReturn, GSTReturnCreate } from '@/types/gst.types';

export const gstService = {
  async list(entityId: string, period?: string, returnType?: string): Promise<GSTReturn[]> {
    const params: Record<string, string> = { entity_id: entityId };
    if (period) params.period = period;
    if (returnType) params.return_type = returnType;
    const { data } = await api.get<GSTReturn[]>('/api/v1/gst-returns', { params });
    return data;
  },

  async get(returnId: string): Promise<GSTReturn> {
    const { data } = await api.get<GSTReturn>(`/api/v1/gst-returns/${returnId}`);
    return data;
  },

  async create(payload: GSTReturnCreate): Promise<GSTReturn> {
    const { data } = await api.post<GSTReturn>('/api/v1/gst-returns', payload);
    return data;
  },

  async file(returnId: string): Promise<{ return_id: string; status: string; arn: string }> {
    const { data } = await api.post(`/api/v1/gst-returns/${returnId}/file`);
    return data;
  },

  async delete(returnId: string): Promise<void> {
    await api.delete(`/api/v1/gst-returns/${returnId}`);
  },

  async getGSTSummary(entityId: string, period: string): Promise<Record<string, unknown>> {
    const { data } = await api.get(`/api/v1/reports/gst-summary/${entityId}`, {
      params: { period },
    });
    return data;
  },

  async generateGSTR1(entityId: string): Promise<Record<string, unknown>> {
    const { data } = await api.post(`/api/v1/compliance/gst/generate-gstr1/${entityId}`);
    return data;
  },

  async getComplianceStatus(entityId: string): Promise<Record<string, unknown>> {
    const { data } = await api.get(`/api/v1/compliance/compliance-status/${entityId}`);
    return data;
  },
};
