import { useCallback, useMemo, useState } from 'react';
import { journalEntriesService } from '@/services/journalEntries.service';
import type {
  BatchEntryCSVRow,
  BatchEntryGroup,
  BatchEntryParseError,
  BatchUploadResult,
  JournalEntryCreateRequest,
} from '@/types/journal.types';

const REQUIRED_HEADERS = ['entry_date', 'period', 'narration', 'account_code', 'type', 'amount'] as const;

/** Minimal CSV line parser that respects double-quoted fields. */
function parseCSVLine(line: string): string[] {
  const values: string[] = [];
  let current = '';
  let inQuotes = false;

  for (const char of line) {
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      values.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  values.push(current.trim());
  return values;
}

export function useBatchEntryUpload(entityId: string) {
  const [parsedRows, setParsedRows] = useState<BatchEntryCSVRow[]>([]);
  const [parseErrors, setParseErrors] = useState<BatchEntryParseError[]>([]);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<BatchUploadResult | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [hasFile, setHasFile] = useState(false);

  const parseCSV = useCallback((csvText: string) => {
    const rawLines = csvText
      .trim()
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);

    if (rawLines.length < 2) {
      setParseErrors([
        { rowNumber: 0, field: 'file', message: 'CSV must have a header row and at least one data row.' },
      ]);
      setParsedRows([]);
      setHasFile(true);
      return;
    }

    const headers = parseCSVLine(rawLines[0]).map((h) => h.toLowerCase().trim());
    const missingHeaders = REQUIRED_HEADERS.filter((h) => !headers.includes(h));

    if (missingHeaders.length > 0) {
      setParseErrors([
        {
          rowNumber: 0,
          field: 'headers',
          message: `Missing required columns: ${missingHeaders.join(', ')}`,
        },
      ]);
      setParsedRows([]);
      setHasFile(true);
      return;
    }

    const rows: BatchEntryCSVRow[] = [];
    const errors: BatchEntryParseError[] = [];

    for (let i = 1; i < rawLines.length; i++) {
      const values = parseCSVLine(rawLines[i]);
      const row: Record<string, string> = {};
      headers.forEach((h, idx) => {
        row[h] = values[idx] ?? '';
      });

      const rowNumber = i + 1;

      if (!/^\d{4}-\d{2}-\d{2}$/.test(row['entry_date'] ?? '')) {
        errors.push({
          rowNumber,
          field: 'entry_date',
          message: `Row ${rowNumber}: entry_date must be YYYY-MM-DD, got "${row['entry_date']}"`,
        });
      }

      if (!/^\d{4}-\d{2}$/.test(row['period'] ?? '')) {
        errors.push({
          rowNumber,
          field: 'period',
          message: `Row ${rowNumber}: period must be YYYY-MM, got "${row['period']}"`,
        });
      }

      if (!row['account_code']?.trim()) {
        errors.push({
          rowNumber,
          field: 'account_code',
          message: `Row ${rowNumber}: account_code is required`,
        });
      }

      const rawType = row['type']?.toUpperCase().trim();
      if (rawType !== 'DEBIT' && rawType !== 'CREDIT') {
        errors.push({
          rowNumber,
          field: 'type',
          message: `Row ${rowNumber}: type must be DEBIT or CREDIT, got "${row['type']}"`,
        });
      }

      const amount = parseFloat(row['amount'] ?? '');
      if (isNaN(amount) || amount <= 0) {
        errors.push({
          rowNumber,
          field: 'amount',
          message: `Row ${rowNumber}: amount must be a positive number, got "${row['amount']}"`,
        });
      }

      rows.push({
        entry_date: row['entry_date'] ?? '',
        period: row['period'] ?? '',
        narration: row['narration'] ?? '',
        account_code: row['account_code'] ?? '',
        type: rawType === 'CREDIT' ? 'CREDIT' : 'DEBIT',
        amount: row['amount'] ?? '',
        description: row['description'] ?? '',
        rowNumber,
      });
    }

    setParsedRows(rows);
    setParseErrors(errors);
    setHasFile(true);
  }, []);

  const groupedEntries = useMemo((): BatchEntryGroup[] => {
    if (!entityId || parsedRows.length === 0) return [];

    const groups = new Map<string, BatchEntryGroup>();

    for (const row of parsedRows) {
      const key = `${row.entry_date}::${row.narration}`;
      if (!groups.has(key)) {
        groups.set(key, {
          key,
          entry_date: row.entry_date,
          period: row.period,
          narration: row.narration,
          entityId,
          lines: [],
        });
      }
      const group = groups.get(key)!;
      const amount = parseFloat(row.amount);
      const safeAmount = isNaN(amount) ? 0 : amount;
      group.lines.push({
        account_code: row.account_code,
        debit: row.type === 'DEBIT' ? safeAmount : 0,
        credit: row.type === 'CREDIT' ? safeAmount : 0,
        description: row.description || undefined,
      });
    }

    return Array.from(groups.values());
  }, [parsedRows, entityId]);

  const balanceErrors = useMemo((): BatchEntryParseError[] => {
    return groupedEntries.flatMap((group) => {
      const totalDebit = group.lines.reduce((sum, l) => sum + l.debit, 0);
      const totalCredit = group.lines.reduce((sum, l) => sum + l.credit, 0);
      if (Math.abs(totalDebit - totalCredit) >= 0.01) {
        return [
          {
            rowNumber: 0,
            field: 'balance',
            message: `Entry "${group.narration || group.entry_date}" (${group.entry_date}) is not balanced — debit ₹${totalDebit.toFixed(2)} vs credit ₹${totalCredit.toFixed(2)}.`,
          },
        ];
      }
      return [];
    });
  }, [groupedEntries]);

  const allErrors = useMemo(() => [...parseErrors, ...balanceErrors], [parseErrors, balanceErrors]);

  const canSubmit =
    hasFile && allErrors.length === 0 && parsedRows.length > 0 && Boolean(entityId) && !isSubmitting;

  const submit = useCallback(async () => {
    if (!canSubmit) return;

    const payloads: JournalEntryCreateRequest[] = groupedEntries.map((group) => ({
      entity_id: group.entityId,
      entry_date: group.entry_date,
      narration: group.narration,
      lines: group.lines,
    }));

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const created = await journalEntriesService.batchCreate(payloads);
      setResult({ created, failedGroups: [] });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Batch upload failed.';
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  }, [canSubmit, groupedEntries]);

  const reset = useCallback(() => {
    setParsedRows([]);
    setParseErrors([]);
    setSubmitError(null);
    setResult(null);
    setIsSubmitting(false);
    setHasFile(false);
  }, []);

  return {
    parseCSV,
    parsedRows,
    groupedEntries,
    parseErrors,
    balanceErrors,
    allErrors,
    submit,
    isSubmitting,
    result,
    submitError,
    reset,
    hasFile,
    canSubmit,
  };
}
