import { useRef, useState } from 'react';
import { useBatchEntryUpload } from '@/hooks/useBatchEntryUpload';
import { formatINR } from '@/utils/formatters';
import type { JournalEntry } from '@/types/journal.types';

export const SAMPLE_CSV = `entry_date,period,narration,account_code,type,amount,description
2026-04-01,2026-04,April rent,1001,DEBIT,25000,Rent expense
2026-04-01,2026-04,April rent,2001,CREDIT,25000,Cash payment
2026-04-02,2026-04,Salary payment,5001,DEBIT,50000,Salary April
2026-04-02,2026-04,Salary payment,2001,CREDIT,50000,Bank transfer`;

interface BatchEntryUploadProps {
  entityId: string;
  onSuccess?: (entries: JournalEntry[]) => void;
}

export function BatchEntryUpload({ entityId, onSuccess }: BatchEntryUploadProps) {
  const {
    parseCSV,
    parsedRows,
    groupedEntries,
    allErrors,
    submit,
    isSubmitting,
    result,
    submitError,
    reset,
    hasFile,
    canSubmit,
  } = useBatchEntryUpload(entityId);

  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      parseCSV(e.target?.result as string);
    };
    reader.readAsText(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  };

  if (result) {
    return (
      <div className="rounded-2xl border border-green-200 bg-green-50 p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-green-800">Upload Complete</h3>
        <p className="mt-1 text-green-700">
          {result.created.length} journal {result.created.length === 1 ? 'entry' : 'entries'} created
          successfully.
        </p>
        <div className="mt-4 flex gap-3">
          <button
            type="button"
            onClick={() => {
              reset();
              onSuccess?.(result.created);
            }}
            className="focus-ring rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
          >
            Done
          </button>
          <button
            type="button"
            onClick={reset}
            className="focus-ring rounded-lg border border-green-300 px-4 py-2 text-sm font-medium text-green-700 hover:bg-green-100"
          >
            Upload Another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-ink">Batch CSV Upload</h3>
        <a
          href={`data:text/csv;charset=utf-8,${encodeURIComponent(SAMPLE_CSV)}`}
          download="sample_entries.csv"
          className="text-sm text-brand hover:underline"
        >
          Download sample CSV
        </a>
      </div>

      {/* Drop zone */}
      <div
        role="button"
        tabIndex={0}
        data-testid="drop-zone"
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') inputRef.current?.click();
        }}
        className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
          isDragOver ? 'border-brand bg-brand/5' : 'border-slate-300 hover:border-slate-400'
        }`}
      >
        <input
          ref={inputRef}
          data-testid="csv-file-input"
          type="file"
          accept=".csv,text/csv"
          className="hidden"
          onChange={handleInputChange}
        />
        <p className="text-slate-600">
          {isDragOver ? 'Drop your CSV file here' : 'Drag & drop a CSV file, or click to browse'}
        </p>
        <p className="mt-1 text-xs text-slate-400">Accepts .csv files · Required columns: entry_date, period, narration, account_code, type, amount</p>
      </div>

      {/* Errors */}
      {hasFile && allErrors.length > 0 && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4">
          <h4 className="font-semibold text-red-800">
            {allErrors.length} {allErrors.length === 1 ? 'error' : 'errors'} found
          </h4>
          <ul className="mt-2 space-y-1 text-sm text-red-700">
            {allErrors.map((error, idx) => (
              <li key={idx}>{error.message}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Preview */}
      {hasFile && parsedRows.length > 0 && allErrors.length === 0 && (
        <div>
          <p className="font-medium text-slate-700">
            Preview: {groupedEntries.length} {groupedEntries.length === 1 ? 'entry' : 'entries'} (
            {parsedRows.length} lines)
          </p>
          <div className="mt-2 overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">Date</th>
                  <th className="px-3 py-2">Narration</th>
                  <th className="px-3 py-2 text-center">Lines</th>
                  <th className="px-3 py-2 text-right">Debit</th>
                  <th className="px-3 py-2 text-right">Credit</th>
                </tr>
              </thead>
              <tbody>
                {groupedEntries.map((group) => {
                  const totalDebit = group.lines.reduce((s, l) => s + l.debit, 0);
                  const totalCredit = group.lines.reduce((s, l) => s + l.credit, 0);
                  return (
                    <tr key={group.key} className="border-t border-slate-200">
                      <td className="px-3 py-2 text-slate-700">{group.entry_date}</td>
                      <td className="px-3 py-2 font-medium text-ink">{group.narration || '—'}</td>
                      <td className="px-3 py-2 text-center text-slate-500">{group.lines.length}</td>
                      <td className="px-3 py-2 text-right text-slate-700">{formatINR(totalDebit)}</td>
                      <td className="px-3 py-2 text-right text-slate-700">{formatINR(totalCredit)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {submitError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {submitError}
        </div>
      )}

      {/* Actions */}
      {hasFile && (
        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={reset}
            className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Clear
          </button>
          <button
            type="button"
            onClick={() => void submit()}
            disabled={!canSubmit}
            className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting
              ? 'Uploading...'
              : `Upload ${groupedEntries.length} ${groupedEntries.length === 1 ? 'Entry' : 'Entries'}`}
          </button>
        </div>
      )}
    </div>
  );
}
