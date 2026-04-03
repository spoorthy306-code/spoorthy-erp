import { NavLink } from 'react-router-dom';
import { IS_TAURI } from '@/offline/tauriBridge';

const links = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/entities',  label: 'Entities' },
  { to: '/entries',   label: 'Entries' },
  { to: '/invoices',  label: 'Invoices' },
  { to: '/accounts',  label: 'Accounts' },
  { to: '/reports',   label: 'Reports' },
  { to: '/gst',       label: 'GST' },
  { to: '/settings',  label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="w-full border-b border-slate-200 bg-white px-4 py-3 md:h-[calc(100vh-4rem)] md:w-64 md:border-b-0 md:border-r">
      <nav className="flex gap-2 overflow-x-auto md:flex-col">
        {links.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `focus-ring rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive ? 'bg-brand text-white' : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
        {IS_TAURI ? (
          <NavLink
            to="/settings/desktop"
            className={({ isActive }) =>
              `focus-ring rounded-lg px-3 py-2 text-sm font-medium transition ${
                isActive ? 'bg-brand text-white' : 'text-slate-700 hover:bg-slate-100'
              }`
            }
          >
            Desktop Settings
          </NavLink>
        ) : null}
      </nav>
    </aside>
  );
}
