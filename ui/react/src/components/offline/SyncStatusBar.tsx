import { useEffect, useState } from 'react';
import { getSyncStatus, IS_TAURI, runSyncOnce, type SyncStatus } from '@/offline/tauriBridge';

export function SyncStatusBar() {
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!IS_TAURI) return;

    let active = true;
    const refresh = async () => {
      try {
        const next = await getSyncStatus();
        if (active) {
          setStatus(next);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Sync status unavailable');
        }
      }
    };

    void refresh();
    const interval = window.setInterval(() => {
      void refresh();
    }, 30000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  if (!IS_TAURI) return null;

  const mode = status?.mode ?? 'offline';
  const indicator = mode === 'online' ? '[ONLINE]' : mode === 'configured' ? '[CONFIGURED]' : '[OFFLINE]';

  return (
    <div className="mt-2 flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-600">
      <span>
        {indicator} {mode} | pending {status?.pending_changes ?? 0}
      </span>
      <button
        type="button"
        className="rounded border border-slate-300 px-2 py-1 hover:bg-slate-100"
        onClick={() =>
          void runSyncOnce()
            .then(async () => {
              const refreshed = await getSyncStatus();
              setStatus(refreshed);
            })
            .catch((e) => setError(String(e)))
        }
      >
        Sync now
      </button>
      {error ? <span className="text-danger">{error}</span> : null}
    </div>
  );
}
