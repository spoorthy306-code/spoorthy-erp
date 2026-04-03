import type { ChangeEvent } from 'react';
import type { JournalEntryLineFormValue, JournalLineType } from '@/types/journal.types';

interface EntryLineItemProps {
  line: JournalEntryLineFormValue;
  index: number;
  onChange: (id: string, field: keyof JournalEntryLineFormValue, value: string | number | JournalLineType) => void;
  onRemove?: (id: string) => void;
  disableRemove?: boolean;
}

export function EntryLineItem({ line, index, onChange, onRemove, disableRemove }: EntryLineItemProps) {
  const handleTextChange = (field: 'accountCode' | 'description') => (event: ChangeEvent<HTMLInputElement>) => {
    onChange(line.id, field, event.target.value);
  };

  const handleAmountChange = (event: ChangeEvent<HTMLInputElement>) => {
    onChange(line.id, 'amount', Number(event.target.value));
  };

  const handleTypeChange = (event: ChangeEvent<HTMLSelectElement>) => {
    onChange(line.id, 'type', event.target.value as JournalLineType);
  };

  return (
    <div className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 md:grid-cols-[1.2fr_140px_140px_1fr_auto]">
      <div>
        <label className="text-xs font-medium uppercase tracking-wide text-slate-500" htmlFor={`account-${line.id}`}>
          Account Code
        </label>
        <input
          id={`account-${line.id}`}
          value={line.accountCode}
          onChange={handleTextChange('accountCode')}
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          placeholder="1001"
        />
      </div>
      <div>
        <label className="text-xs font-medium uppercase tracking-wide text-slate-500" htmlFor={`type-${line.id}`}>
          Type
        </label>
        <select
          id={`type-${line.id}`}
          value={line.type}
          onChange={handleTypeChange}
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        >
          <option value="DEBIT">Debit</option>
          <option value="CREDIT">Credit</option>
        </select>
      </div>
      <div>
        <label className="text-xs font-medium uppercase tracking-wide text-slate-500" htmlFor={`amount-${line.id}`}>
          Amount
        </label>
        <input
          id={`amount-${line.id}`}
          value={line.amount}
          onChange={handleAmountChange}
          type="number"
          min="0"
          step="0.01"
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
        />
      </div>
      <div>
        <label className="text-xs font-medium uppercase tracking-wide text-slate-500" htmlFor={`description-${line.id}`}>
          Description
        </label>
        <input
          id={`description-${line.id}`}
          value={line.description ?? ''}
          onChange={handleTextChange('description')}
          className="focus-ring mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
          placeholder={`Line ${index + 1} narration`}
        />
      </div>
      <div className="flex items-end">
        <button
          type="button"
          disabled={disableRemove}
          onClick={() => onRemove?.(line.id)}
          className="focus-ring rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
        >
          Remove
        </button>
      </div>
    </div>
  );
}
