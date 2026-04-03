export interface Account {
  account_code: string;
  account_name: string;
  account_type?: string | null;
  parent_code?: string | null;
  level?: number | null;
}
