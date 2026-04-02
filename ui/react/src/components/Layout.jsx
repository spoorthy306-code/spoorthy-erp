// SPOORTHY QUANTUM OS — Layout Components
// React + TypeScript + Tailwind CSS

import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
      <div className="lg:pl-64">
        <Header setSidebarOpen={setSidebarOpen} darkMode={darkMode} setDarkMode={setDarkMode} />
        <main className="py-6">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Accounting', href: '/accounting', icon: '📈', children: [
      { name: 'Journal Entries', href: '/accounting/journal' },
      { name: 'Reconciliation', href: '/accounting/reconcile' },
      { name: 'Financial Statements', href: '/accounting/statements' },
      { name: 'Payroll', href: '/accounting/payroll' },
      { name: 'Fixed Assets', href: '/accounting/assets' },
      { name: 'Inventory', href: '/accounting/inventory' },
    ]},
    { name: 'Financial Services', href: '/financial', icon: '💰', children: [
      { name: 'Portfolio', href: '/financial/portfolio' },
      { name: 'Risk Management', href: '/financial/risk' },
      { name: 'Treasury', href: '/financial/treasury' },
      { name: 'Credit Scoring', href: '/financial/credit' },
    ]},
    { name: 'Compliance', href: '/compliance', icon: '⚖️', children: [
      { name: 'GST Returns', href: '/compliance/gst' },
      { name: 'TDS', href: '/compliance/tds' },
      { name: 'Regulatory', href: '/compliance/regulatory' },
    ]},
    { name: 'Reports', href: '/reports', icon: '📋' },
    { name: 'Admin', href: '/admin', icon: '⚙️' },
  ];

  return (
    <>
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-white">
          <SidebarContent navigation={navigation} location={location} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-grow flex-col overflow-y-auto bg-white pt-5 pb-4">
          <SidebarContent navigation={navigation} location={location} />
        </div>
      </div>
    </>
  );
};

const SidebarContent = ({ navigation, location }) => (
  <div className="flex flex-1 flex-col">
    <div className="flex flex-shrink-0 items-center px-4">
      <h1 className="text-xl font-bold text-gray-900">Spoorthy Quantum OS</h1>
    </div>
    <nav className="mt-5 flex-1 space-y-1 px-2">
      {navigation.map((item) => (
        <div key={item.name}>
          <Link
            to={item.href}
            className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
              location.pathname === item.href
                ? 'bg-gray-100 text-gray-900'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <span className="mr-3">{item.icon}</span>
            {item.name}
          </Link>
          {item.children && (
            <div className="ml-6 mt-1 space-y-1">
              {item.children.map((child) => (
                <Link
                  key={child.name}
                  to={child.href}
                  className={`group flex items-center px-2 py-1 text-xs font-medium rounded-md ${
                    location.pathname === child.href
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-500 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  {child.name}
                </Link>
              ))}
            </div>
          )}
        </div>
      ))}
    </nav>
  </div>
);

const Header = ({ setSidebarOpen, darkMode, setDarkMode }) => (
  <div className="sticky top-0 z-10 flex h-16 flex-shrink-0 border-b border-gray-200 bg-white">
    <button
      type="button"
      className="border-r border-gray-200 px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
      onClick={() => setSidebarOpen(true)}
    >
      <span className="sr-only">Open sidebar</span>
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
      </svg>
    </button>
    <div className="flex flex-1 justify-between px-4">
      <div className="flex flex-1">
        <div className="flex w-full md:ml-0">
          <label htmlFor="search-field" className="sr-only">Search</label>
          <div className="relative w-full text-gray-400 focus-within:text-gray-600">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center">
              <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
              </svg>
            </div>
            <input
              id="search-field"
              className="block h-full w-full border-0 py-2 pl-8 pr-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-0 sm:text-sm"
              placeholder="Search..."
              type="search"
              name="search"
            />
          </div>
        </div>
      </div>
      <div className="ml-4 flex items-center md:ml-6">
        <button
          type="button"
          className="rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          onClick={() => setDarkMode(!darkMode)}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>
        <div className="relative ml-3">
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-700">admin</span>
            <button className="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
              <img className="h-8 w-8 rounded-full" src="https://via.placeholder.com/32" alt="User" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
);