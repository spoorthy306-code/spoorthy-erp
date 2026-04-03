import fs from 'node:fs';
import path from 'node:path';

const REQUIRED_COMPONENTS = [
  'src/components/common/Header.tsx',
  'src/components/common/Sidebar.tsx',
  'src/components/common/Footer.tsx',
  'src/components/common/LoadingSpinner.tsx',
  'src/components/common/ErrorBoundary.tsx',
  'src/components/auth/LoginForm.tsx',
  'src/components/auth/ProtectedRoute.tsx',
  'src/components/entities/EntityList.tsx',
  'src/components/entities/EntityForm.tsx',
  'src/components/accounts/ChartOfAccounts.tsx',
  'src/components/entries/JournalEntryForm.tsx',
  'src/components/entries/BatchEntryUpload.tsx',
  'src/components/entries/EntryListFilters.tsx',
  'src/components/invoices/InvoiceForm.tsx',
  'src/components/invoices/InvoiceList.tsx',
  'src/components/reports/TrialBalance.tsx',
  'src/components/reports/ProfitLoss.tsx',
  'src/components/reports/BalanceSheet.tsx',
  'src/components/gst/GSTReturnForm.tsx',
  'src/components/offline/SyncStatusBar.tsx',
  'src/components/offline/DesktopSettings.tsx',
  'src/components/ui/Modal.tsx',
  'src/components/ui/Table.tsx',
  'src/components/ui/Button.tsx',
  'src/components/ui/Input.tsx',
  'src/components/ui/Select.tsx',
  'src/components/ui/DatePicker.tsx',
];

const results = REQUIRED_COMPONENTS.map((relPath) => {
  const exists = fs.existsSync(path.resolve(process.cwd(), relPath));
  return { component: relPath, exists };
});

const missing = results.filter((item) => !item.exists);

console.log('Component inventory complete.');
console.log(`Total required: ${results.length}`);
console.log(`Missing: ${missing.length}`);

for (const row of results) {
  console.log(`${row.exists ? 'OK' : 'MISSING'} ${row.component}`);
}

if (missing.length > 0) {
  process.exitCode = 1;
}
