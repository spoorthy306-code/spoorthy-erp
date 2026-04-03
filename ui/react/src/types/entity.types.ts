export interface EntityAddress {
  street?: string;
  city?: string;
  state?: string;
  postal?: string;
  country?: string;
  email?: string;
  phone?: string;
}

export interface Entity {
  entity_id: string;
  name: string;
  gstin?: string | null;
  pan?: string | null;
  tan?: string | null;
  address?: EntityAddress | null;
  currency: string;
  reporting_currency: string;
  created_at: string;
  updated_at: string;
}

export interface EntityCreate {
  name: string;
  gstin?: string;
  pan?: string;
  tan?: string;
  address?: EntityAddress;
  currency?: string;
  reporting_currency?: string;
}
