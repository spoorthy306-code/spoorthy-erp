export interface KpiItem {
  label: string;
  value: number;
  deltaPct: number;
  currency?: 'INR';
}

export interface TrendPoint {
  month: string;
  income: number;
  expense: number;
}

// Trial Balance
export interface TrialBalanceAccount {
  code: string;
  name: string;
  debit: number;
  credit: number;
  balance: number;
}

export interface TrialBalanceReport {
  entity_id: string;
  period: string;
  accounts: TrialBalanceAccount[];
  total_debit: number;
  total_credit: number;
  difference: number;
}

// Profit & Loss
export interface PnLReport {
  entity_id: string;
  period: string;
  revenue: Record<string, number> & { total_revenue: number };
  expenses: Record<string, number> & { total_expenses: number };
  profit_before_tax: number;
  tax: number;
  net_profit: number;
}

// Balance Sheet
export interface BalanceSheetAssets {
  current_assets: Record<string, number> & { total_current_assets: number };
  fixed_assets: Record<string, number> & { net_fixed_assets: number };
  total_assets: number;
}

export interface BalanceSheetLiabilities {
  current_liabilities: Record<string, number> & { total_current_liabilities: number };
  long_term_liabilities: Record<string, number> & { total_long_term_liabilities: number };
  total_liabilities: number;
}

export interface BalanceSheetReport {
  entity_id: string;
  as_of_date: string;
  assets: BalanceSheetAssets;
  liabilities: BalanceSheetLiabilities;
  equity: Record<string, number> & { total_equity: number };
  total_liabilities_equity: number;
}

// Cash Flow
export interface CashFlowReport {
  entity_id: string;
  start_date: string;
  end_date: string;
  operating_activities: Record<string, number> & { net_operating: number };
  investing_activities: Record<string, number> & { net_investing: number };
  financing_activities: Record<string, number> & { net_financing: number };
  net_cash_change: number;
  opening_balance: number;
  closing_balance: number;
}
