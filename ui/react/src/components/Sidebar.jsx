import { NavLink } from 'react-router-dom';

const navClass = ({ isActive }) =>
  `block px-4 py-3 rounded mb-2 ${isActive ? 'bg-blue-600 text-white' : 'text-slate-700 hover:bg-slate-200'}`;

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r h-screen p-4">
      <h3 className="text-lg font-bold mb-4">Spoorthy ERP</h3>
      <NavLink className={navClass} to="/app">Inventory Products</NavLink>
      <NavLink className={navClass} to="/app">Sales Dashboard</NavLink>
      <NavLink className={navClass} to="/app">Ledger</NavLink>
    </aside>
  );
}
