export type JournalLineType = 'DEBIT' | 'CREDIT';

export interface JournalEntryLinePayload {
  account_code: string;
  debit: number;
  credit: number;
  description?: string;
}

export interface JournalEntryLineDetail {
  line_id?: string;
  account_code: string;
  debit: number;
  credit: number;
  description?: string | null;
}

export interface JournalEntryLineFormValue {
  id: string;
  accountCode: string;
  type: JournalLineType;
  amount: number;
  description: string;
}

export interface JournalEntry {
  entry_id: string;
  entity_id: string;
  entry_date: string;
  period: string;
  narration?: string | null;
  total_debit: number;
  total_credit: number;
  posted_by?: string | null;
  pqc_signature?: string | null;
  quantum_job_id?: string | null;
  created_at: string;
  lines?: JournalEntryLineDetail[];
}

export interface JournalEntryCreateRequest {
  entity_id: string;
  entry_date: string;
  narration?: string;
  lines: JournalEntryLinePayload[];
}

export interface JournalEntryUpdateRequest {
  entry_date?: string;
  narration?: string;
  lines?: JournalEntryLinePayload[];
}

export interface JournalEntryListParams {
  entityId: string;
  period?: string;
  skip?: number;
  limit?: number;
}

export interface JournalEntryFormValues {
  entityId: string;
  entryDate: string;
  period: string;
  reference: string;
  description: string;
  lines: JournalEntryLineFormValue[];
}

export interface JournalEntryFormInitialState {
  entry?: JournalEntry | null;
  entityId?: string;
}

export interface JournalEntryMutationResult {
  entry: JournalEntry;
  mode: 'create' | 'update';
}

// ── Batch CSV Upload ──────────────────────────────────────────────────────────

export interface BatchEntryCSVRow {
  entry_date: string;
  period: string;
  narration: string;
  account_code: string;
  type: 'DEBIT' | 'CREDIT';
  /** Raw string value from CSV — may be non-numeric if invalid */
  amount: string;
  description: string;
  rowNumber: number;
}

export interface BatchEntryParseError {
  rowNumber: number;
  field: string;
  message: string;
}

export interface BatchEntryGroup {
  key: string;
  entry_date: string;
  period: string;
  narration: string;
  entityId: string;
  lines: JournalEntryLinePayload[];
}

export interface BatchUploadResult {
  created: JournalEntry[];
  failedGroups: string[];
}

// ── Entry List Filters ────────────────────────────────────────────────────────

export type EntrySortField = 'entry_date' | 'total_debit' | 'total_credit';
export type SortDirection = 'asc' | 'desc';

export interface EntryListFilterState {
  period: string;
  narration: string;
  sortField: EntrySortField;
  sortDirection: SortDirection;
}
