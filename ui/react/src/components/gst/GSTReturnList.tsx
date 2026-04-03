import { useState } from 'react';
import { useGSTReturns } from '@/hooks/useGST';
import type { GSTReturn } from '@/types/gst.types';

interface Props {
  entityId: string;
  period?: string;
}

export function GSTReturnList({ entityId, period }: Props) {
  const { returns, isLoading, fileReturn, isFiling, deleteReturn, isDeleting } = useGSTReturns(entityId, period);
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [filingId, setFilingId] = useState<string | null>(null);

  const handleFile = async (ret: GSTReturn) => {
    setFilingId(ret.return_id);
    try {
      await fileReturn(ret.return_id);
    } finally {
      setFilingId(null);
    }
  };

  const handleDelete = async (returnId: string) => {
    await deleteReturn(returnId);
    setConfirmDeleteId(null);
  };

  if (isLoading) return <p className="py-8 text-center text-sm text-slate-500">Loading GST returns…</p>;

  if (!returns.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-10 text-center text-sm text-slate-500">
        No GST returns found for this entity.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Period</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">ARN</th>
            <th className="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          {returns.map((ret) => (
            <tr key={ret.return_id} className="border-t border-slate-200 hover:bg-slate-50 transition">
              <td className="px-4 py-3 font-medium text-ink">{ret.return_type}</td>
              <td className="px-4 py-3 text-slate-600">{ret.period}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  ret.status === 'FILED' ? 'bg-success/10 text-success' : 'bg-amber-100 text-amber-700'
                }`}>
                  {ret.status}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-xs text-slate-500">{ret.arn ?? '—'}</td>
              <td className="px-4 py-3 text-right">
                {confirmDeleteId === ret.return_id ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="text-xs text-slate-500">Delete?</span>
                    <button type="button" onClick={() => void handleDelete(ret.return_id)} disabled={isDeleting}
                      className="focus-ring rounded px-2 py-1 text-xs font-medium text-danger hover:underline disabled:opacity-60">Yes</button>
                    <button type="button" onClick={() => setConfirmDeleteId(null)}
                      className="focus-ring rounded px-2 py-1 text-xs font-medium text-slate-600 hover:underline">No</button>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-3">
                    {ret.status !== 'FILED' && (
                      <button type="button" onClick={() => void handleFile(ret)} disabled={isFiling && filingId === ret.return_id}
                        className="focus-ring text-xs font-medium text-brand hover:underline disabled:opacity-60">
                        {isFiling && filingId === ret.return_id ? 'Filing…' : 'File'}
                      </button>
                    )}
                    <button type="button" onClick={() => setConfirmDeleteId(ret.return_id)}
                      className="focus-ring text-xs font-medium text-danger hover:underline">Delete</button>
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
