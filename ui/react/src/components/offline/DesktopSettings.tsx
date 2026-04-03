import { useEffect, useState } from 'react';
import {
  getSyncConfig,
  getSyncStatus,
  IS_TAURI,
  openDatabaseFolder,
  runSyncOnce,
  setSyncConfig,
  type SyncRunResult,
  type SyncStatus,
} from '@/offline/tauriBridge';

export function DesktopSettings() {
  const [apiUrl, setApiUrl] = useState('');
  const [token, setToken] = useState('');
  const [status, setStatus] = useState<SyncStatus | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [lastRun, setLastRun] = useState<SyncRunResult | null>(null);

  useEffect(() => {
    if (!IS_TAURI) return;

    const load = async () => {
      const cfg = await getSyncConfig();
      const syncStatus = await getSyncStatus();
      setApiUrl(cfg?.api_url ?? '');
      setStatus(syncStatus);
    };

    void load();
  }, []);

  if (!IS_TAURI) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h2 className="text-xl font-semibold text-ink">Desktop Settings</h2>
        <p className="mt-2 text-sm text-slate-600">This section is available only in the desktop app.</p>
      </section>
    );
  }

  const save = async () => {
    setIsSaving(true);
    setMessage(null);
    try {
      const next = await setSyncConfig({ apiUrl, bearerToken: token });
      setStatus(next);
      setMessage('Sync configuration saved.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Failed to save sync config.');
    } finally {
      setIsSaving(false);
    }
  };

  const syncNow = async () => {
    try {
      const run = await runSyncOnce();
      if (!run) {
        setMessage('Desktop runtime is not available.');
        return;
      }

      setLastRun(run);
      const refreshed = await getSyncStatus();
      setStatus(refreshed);
      setMessage(run.message);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Sync failed.');
    }
  };

  const openDb = async () => {
    try {
      const dir = await openDatabaseFolder();
      setMessage(dir ? `Opened database folder: ${dir}` : 'Database folder unavailable.');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Could not open database folder.');
    }
  };

  return (
    <section className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-xl font-semibold text-ink">Desktop Settings</h2>
        <p className="mt-1 text-sm text-slate-500">Configure cloud sync for offline-first desktop mode.</p>
      </div>

      <div className="grid gap-3">
        <label className="text-sm font-medium text-slate-700" htmlFor="desktop-api-url">API URL</label>
        <input
          id="desktop-api-url"
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder="https://api.example.com"
          className="focus-ring rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />

        <label className="text-sm font-medium text-slate-700" htmlFor="desktop-token">Bearer Token</label>
        <input
          id="desktop-token"
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          placeholder="Paste API token"
          className="focus-ring rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void save()}
          disabled={isSaving || !apiUrl || !token}
          className="focus-ring rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {isSaving ? 'Saving...' : 'Save & Connect'}
        </button>
        <button
          type="button"
          onClick={() => void syncNow()}
          className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
        >
          Run Sync Now
        </button>
        <button
          type="button"
          onClick={() => void openDb()}
          className="focus-ring rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700"
        >
          Open Database Folder
        </button>
      </div>

      <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
        <p>Status: {status?.mode ?? 'offline'}</p>
        <p>Pending changes: {status?.pending_changes ?? 0}</p>
        <p>Last sync: {status?.last_sync_at ?? 'never'}</p>
        {lastRun ? (
          <>
            <p>Pushed: {lastRun.pushed}</p>
            <p>Pulled: {lastRun.pulled}</p>
            <p>Conflicts: {lastRun.conflicts}</p>
          </>
        ) : null}
      </div>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </section>
  );
}
