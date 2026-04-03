import { Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { PrivateLayout } from '@/components/auth/PrivateLayout';
import { DesktopSettings } from '@/components/offline/DesktopSettings';
import { lazyLoad, withSuspense } from '@/utils/lazyLoad';
import HomePage from '@/pages/index.tsx';
import LoginPage from '@/pages/login.tsx';

const DashboardPage    = lazyLoad(() => import('@/pages/dashboard.tsx'));
const EntitiesPage     = lazyLoad(() => import('@/pages/entities.tsx'));
const EntriesPage      = lazyLoad(() => import('@/pages/entries.tsx'));
const ReportsPage      = lazyLoad(() => import('@/pages/reports.tsx'));
const GSTPage          = lazyLoad(() => import('@/pages/gst.tsx'));
const InvoicesPage     = lazyLoad(() => import('@/pages/invoices.tsx'));
const AccountsPage     = lazyLoad(() => import('@/pages/accounts.tsx'));
const SettingsPage     = lazyLoad(() => import('@/pages/settings.tsx'));
const NotFoundPage     = lazyLoad(() => import('@/pages/404.tsx'));

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={
          <ProtectedRoute>
            <PrivateLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard"  element={withSuspense(<DashboardPage />)} />
        <Route path="/entities"   element={withSuspense(<EntitiesPage />)} />
        <Route path="/entries"    element={withSuspense(<EntriesPage />)} />
        <Route path="/invoices"   element={withSuspense(<InvoicesPage />)} />
        <Route path="/accounts"   element={withSuspense(<AccountsPage />)} />
        <Route path="/reports"    element={withSuspense(<ReportsPage />)} />
        <Route path="/gst"        element={withSuspense(<GSTPage />)} />
        <Route path="/settings"   element={withSuspense(<SettingsPage />)} />
        <Route path="/settings/desktop" element={<DesktopSettings />} />
      </Route>

      <Route path="/home" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={withSuspense(<NotFoundPage />)} />
    </Routes>
  );
}

export default App;
