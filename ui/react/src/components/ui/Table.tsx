import type { ReactNode } from 'react';

interface Column<T> {
  key: keyof T;
  header: string;
  render?: (value: T[keyof T], row: T) => ReactNode;
}

interface TableProps<T extends Record<string, unknown>> {
  columns: Array<Column<T>>;
  rows: T[];
  rowKey: (row: T) => string;
}

export function Table<T extends Record<string, unknown>>({ columns, rows, rowKey }: TableProps<T>) {
  return (
    <div className="overflow-hidden rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 bg-white text-sm">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((column) => (
              <th key={String(column.key)} className="px-4 py-2 text-left font-semibold text-slate-600">
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((row) => (
            <tr key={rowKey(row)}>
              {columns.map((column) => {
                const value = row[column.key];
                return (
                  <td key={String(column.key)} className="px-4 py-2 text-slate-700">
                    {column.render ? column.render(value, row) : String(value ?? '')}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
