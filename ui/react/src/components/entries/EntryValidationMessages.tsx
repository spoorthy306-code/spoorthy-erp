import { getEntryValidation } from '@/hooks/useEntryValidation';
import type { JournalEntryLineFormValue } from '@/types/journal.types';

interface Props {
  lines: JournalEntryLineFormValue[];
}

export function EntryValidationMessages({ lines }: Props) {
  const validation = getEntryValidation(lines);

  if (validation.isBalanced) {
    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
        Entry is balanced. Debits and credits match.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
      Debit and credit totals differ by {validation.difference.toFixed(2)}. Adjust the line items before posting.
    </div>
  );
}
