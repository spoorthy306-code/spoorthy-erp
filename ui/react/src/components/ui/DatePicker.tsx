import type { InputHTMLAttributes } from 'react';

export interface DatePickerProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
}

export function DatePicker({ id, label, className = '', ...rest }: DatePickerProps) {
  return (
    <div className="space-y-1">
      {label ? (
        <label htmlFor={id} className="block text-sm font-medium text-slate-700">
          {label}
        </label>
      ) : null}
      <input
        id={id}
        type="date"
        className={`focus-ring w-full rounded-lg border border-slate-300 px-3 py-2 text-sm ${className}`}
        {...rest}
      />
    </div>
  );
}
