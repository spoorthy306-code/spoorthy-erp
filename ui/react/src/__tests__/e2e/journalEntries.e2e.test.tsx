/**
 * Journal Entries E2E Tests
 *
 * These tests render EntriesPage directly (without auth wrapper) and mock the
 * service layer to simulate real user workflows end-to-end through the React
 * component tree. Each test exercises a critical user journey.
 */
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import EntriesPage from '@/pages/entries';
import type { JournalEntry } from '@/types/journal.types';

// ── Service mocks ──────────────────────────────────────────────────────────────
const { mockList, mockCreate, mockGetById, mockBatchCreate, mockReconcile } = vi.hoisted(() => ({
  mockList: vi.fn(),
  mockCreate: vi.fn(),
  mockGetById: vi.fn(),
  mockBatchCreate: vi.fn(),
  mockReconcile: vi.fn(),
}));

vi.mock('@/services/journalEntries.service', () => ({
  journalEntriesService: {
    list: mockList,
    create: mockCreate,
    getById: mockGetById,
    batchCreate: mockBatchCreate,
    reconcile: mockReconcile,
    update: vi.fn().mockRejectedValue(new Error('Update not available')),
    delete: vi.fn().mockRejectedValue(new Error('Delete not available')),
  },
}));

// ── Fixtures ───────────────────────────────────────────────────────────────────
const MOCK_ENTRY: JournalEntry = {
  entry_id: 'e-123',
  entity_id: 'entity-1',
  entry_date: '2026-04-01',
  period: '2026-04',
  narration: 'April rent payment',
  total_debit: 25000,
  total_credit: 25000,
  created_at: '2026-04-01T10:00:00',
};

const MOCK_ENTRY_2: JournalEntry = {
  entry_id: 'e-456',
  entity_id: 'entity-1',
  entry_date: '2026-04-02',
  period: '2026-04',
  narration: 'Salary disbursement',
  total_debit: 50000,
  total_credit: 50000,
  created_at: '2026-04-02T10:00:00',
};

// ── Test helpers ───────────────────────────────────────────────────────────────
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

function renderEntriesPage() {
  return render(
    <QueryClientProvider client={makeQueryClient()}>
      <EntriesPage />
    </QueryClientProvider>
  );
}

function typeEntityId(value: string) {
  fireEvent.change(screen.getByPlaceholderText(/enter an entity uuid/i), {
    target: { value },
  });
}

// ── Test suite ─────────────────────────────────────────────────────────────────
describe('Journal Entries E2E', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockList.mockResolvedValue([MOCK_ENTRY]);
    mockGetById.mockResolvedValue(MOCK_ENTRY);
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ── 1. Full create workflow ────────────────────────────────────────────────
  it('full create workflow: form fills, submits, createEntry called with correct payload', async () => {
    const newEntry: JournalEntry = {
      ...MOCK_ENTRY,
      entry_id: 'e-new',
      narration: 'Supplier payment for goods',
    };
    mockCreate.mockResolvedValueOnce(newEntry);
    mockGetById.mockResolvedValue(newEntry);
    mockList.mockResolvedValue([newEntry]);

    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(mockList).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /new entry/i }));
    expect(screen.getByText('New Journal Entry')).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/description/i, { selector: 'textarea' }), {
      target: { value: 'Supplier payment for goods' },
    });

    const accountInputs = screen.getAllByLabelText(/account code/i);
    fireEvent.change(accountInputs[0], { target: { value: '6001' } });
    fireEvent.change(accountInputs[1], { target: { value: '2001' } });

    const amountInputs = screen.getAllByLabelText(/^amount$/i);
    fireEvent.change(amountInputs[0], { target: { value: '15000' } });
    fireEvent.change(amountInputs[1], { target: { value: '15000' } });

    const submitBtn = screen.getByRole('button', { name: 'Save Entry' });
    await waitFor(() => expect(submitBtn).toBeEnabled(), { timeout: 3000 });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalledWith(
        expect.objectContaining({
          entity_id: 'entity-1',
          narration: 'Supplier payment for goods',
          lines: expect.arrayContaining([
            expect.objectContaining({ account_code: '6001', debit: 15000, credit: 0 }),
            expect.objectContaining({ account_code: '2001', debit: 0, credit: 15000 }),
          ]),
        })
      );
    });
  });

  // ── 2. Batch upload — valid CSV shows preview ─────────────────────────────
  it('batch upload: valid CSV parses and shows entry preview', async () => {
    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(mockList).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /batch upload/i }));
    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();

    const csv = [
      'entry_date,period,narration,account_code,type,amount,description',
      '2026-04-01,2026-04,Office supplies,5001,DEBIT,8000,Stationery',
      '2026-04-01,2026-04,Office supplies,2001,CREDIT,8000,Cash out',
    ].join('\n');
    const file = new File([csv], 'entries.csv', { type: 'text/csv' });
    fireEvent.change(screen.getByTestId('csv-file-input'), { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/preview.*1 entry/i)).toBeInTheDocument();
    });
    expect(screen.getByText('Office supplies')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload 1 entry/i })).toBeEnabled();
  });

  // ── 3. Batch upload — invalid CSV shows errors ────────────────────────────
  it('batch upload: CSV with bad entry_date shows a parse error', async () => {
    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(mockList).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /batch upload/i }));

    const csv = [
      'entry_date,period,narration,account_code,type,amount,description',
      'not-a-date,2026-04,Test,1001,DEBIT,1000,',
    ].join('\n');
    const file = new File([csv], 'bad.csv', { type: 'text/csv' });
    fireEvent.change(screen.getByTestId('csv-file-input'), { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByText(/error[s]? found/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/entry_date must be YYYY-MM-DD/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload 1 entry/i })).toBeDisabled();
  });

  // ── 4. Filter workflow — narration search ────────────────────────────────
  it('filter workflow: narration search hides non-matching entries', async () => {
    mockList.mockResolvedValue([MOCK_ENTRY, MOCK_ENTRY_2]);
    renderEntriesPage();
    typeEntityId('entity-1');

    await waitFor(() => {
      expect(screen.getByText('April rent payment')).toBeInTheDocument();
    });
    expect(screen.getByText('Salary disbursement')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText(/filter by narration/i), {
      target: { value: 'salary' },
    });

    await waitFor(() => {
      expect(screen.queryByText('April rent payment')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Salary disbursement')).toBeInTheDocument();
    expect(screen.getByText(/1 of 2 shown/i)).toBeInTheDocument();
  });

  // ── 5. Sort toggle ────────────────────────────────────────────────────────
  it('sort toggle: clicking direction button switches between asc and desc', async () => {
    mockList.mockResolvedValue([MOCK_ENTRY, MOCK_ENTRY_2]);
    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(screen.getByText('April rent payment')).toBeInTheDocument());

    const sortBtn = screen.getByRole('button', { name: /sort ascending.*click to toggle/i });
    expect(sortBtn).toHaveTextContent('↓ Desc');
    fireEvent.click(sortBtn);
    expect(screen.getByRole('button', { name: /sort descending.*click to toggle/i })).toHaveTextContent('↑ Asc');
  });

  // ── 6. Detail modal — open and close with ESC ─────────────────────────────
  it('detail modal: click entry date opens modal, ESC key closes it', async () => {
    renderEntriesPage();
    typeEntityId('entity-1');

    await waitFor(() => {
      expect(screen.getByText('April rent payment')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '2026-04-01' }));
    await waitFor(() => {
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    fireEvent.keyDown(window, { key: 'Escape', code: 'Escape' });
    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
  });

  // ── 7. Unbalanced entry — blocked submit ─────────────────────────────────
  it('prevents submission and shows balance error when entry is unbalanced', async () => {
    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(mockList).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /new entry/i }));

    fireEvent.change(screen.getByLabelText(/description/i, { selector: 'textarea' }), {
      target: { value: 'Test unbalanced entry' },
    });

    const accountInputs = screen.getAllByLabelText(/account code/i);
    fireEvent.change(accountInputs[0], { target: { value: '1001' } });
    fireEvent.change(accountInputs[1], { target: { value: '2001' } });

    const amountInputs = screen.getAllByLabelText(/^amount$/i);
    fireEvent.change(amountInputs[0], { target: { value: '5000' } });
    fireEvent.change(amountInputs[1], { target: { value: '3000' } });

    await waitFor(() => {
      expect(screen.getByText(/debit and credit totals differ/i)).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: 'Save Entry' })).toBeDisabled();
    expect(mockCreate).not.toHaveBeenCalled();
  });

  // ── 8. Empty CSV edge case ────────────────────────────────────────────────
  it('batch upload: CSV with only a header row shows an error', async () => {
    renderEntriesPage();
    typeEntityId('entity-1');
    await waitFor(() => expect(mockList).toHaveBeenCalled());

    fireEvent.click(screen.getByRole('button', { name: /batch upload/i }));

    const file = new File(
      ['entry_date,period,narration,account_code,type,amount,description'],
      'empty.csv',
      { type: 'text/csv' }
    );
    fireEvent.change(screen.getByTestId('csv-file-input'), { target: { files: [file] } });

    await waitFor(() => {
      expect(
        screen.getByText(/must have a header row and at least one data row/i)
      ).toBeInTheDocument();
    });
  });
});
