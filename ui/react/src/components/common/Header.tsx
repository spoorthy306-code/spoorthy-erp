import { useAuth } from '@/hooks/useAuth';
import { SyncStatusBar } from '@/components/offline/SyncStatusBar';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 px-6 py-3 backdrop-blur">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Spoorthy ERP</p>
          <h1 className="text-lg font-semibold text-ink">Finance Operations</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <p className="text-sm font-medium text-ink">{user?.name ?? 'Team Member'}</p>
            <p className="text-xs text-slate-500">{user?.email ?? 'not-signed-in'}</p>
          </div>
          <button className="focus-ring rounded-lg bg-slate-100 px-3 py-2 text-sm hover:bg-slate-200" onClick={() => logout()}>
            Logout
          </button>
        </div>
      </div>
      <SyncStatusBar />
    </header>
  );
}
