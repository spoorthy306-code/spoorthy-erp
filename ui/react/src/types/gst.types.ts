export type GSTReturnType = 'GSTR1' | 'GSTR3B' | 'GSTR9';
export type GSTReturnStatus = 'DRAFT' | 'FILED';

export interface GSTReturn {
  return_id: string;
  entity_id: string;
  return_type: GSTReturnType | string;
  period: string;
  json_payload?: Record<string, unknown> | null;
  status: GSTReturnStatus | string;
  arn?: string | null;
  filed_at: string;
}

export interface GSTReturnCreate {
  entity_id: string;
  return_type: string;
  period: string;
  json_payload?: Record<string, unknown>;
}
