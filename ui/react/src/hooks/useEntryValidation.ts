import type { JournalEntryLineFormValue } from '@/types/journal.types';

export interface EntryValidationResult {
  totalDebit: number;
  totalCredit: number;
  isBalanced: boolean;
  difference: number;
}

export function getEntryValidation(lines: JournalEntryLineFormValue[]): EntryValidationResult {
  const totals = lines.reduce(
    (acc, line) => {
      if (line.type === 'DEBIT') {
        acc.totalDebit += line.amount;
      } else {
        acc.totalCredit += line.amount;
      }
      return acc;
    },
    { totalDebit: 0, totalCredit: 0 }
  );

  const difference = Number((totals.totalDebit - totals.totalCredit).toFixed(2));

  return {
    totalDebit: totals.totalDebit,
    totalCredit: totals.totalCredit,
    isBalanced: Math.abs(difference) < 0.01,
    difference,
  };
}
