import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { BatchEntryUpload } from '../BatchEntryUpload';
import type { BatchEntryCSVRow, BatchEntryGroup, BatchEntryParseError } from '@/types/journal.types';

// ── Mock the hook ──────────────────────────────────────────────────────────────

const mockUseBatchEntryUpload = vi.hoisted(() => vi.fn());

vi.mock('@/hooks/useBatchEntryUpload', () => ({
  useBatchEntryUpload: mockUseBatchEntryUpload,
}));

function makeDefaultReturn() {
  return {
    parseCSV: vi.fn(),
    parsedRows: [] as BatchEntryCSVRow[],
    groupedEntries: [] as BatchEntryGroup[],
    parseErrors: [] as BatchEntryParseError[],
    balanceErrors: [] as BatchEntryParseError[],
    allErrors: [] as BatchEntryParseError[],
    submitError: null,
    result: null,
    isSubmitting: false,
    hasFile: false,
    canSubmit: false,
    submit: vi.fn(),
    reset: vi.fn(),
  };
}

describe('BatchEntryUpload', () => {
  beforeEach(() => {
    mockUseBatchEntryUpload.mockReturnValue(makeDefaultReturn());
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the drop zone and sample CSV link initially', () => {
    render(<BatchEntryUpload entityId="entity-1" />);

    expect(screen.getByTestId('drop-zone')).toBeInTheDocument();
    expect(screen.getByText(/drag.*drop/i)).toBeInTheDocument();
    expect(screen.getByText(/download sample csv/i)).toBeInTheDocument();
  });

  it('shows error summary when the CSV has parse errors', () => {
    mockUseBatchEntryUpload.mockReturnValue({
      ...makeDefaultReturn(),
      hasFile: true,
      allErrors: [
        {
          rowNumber: 2,
          field: 'entry_date',
          message: 'Row 2: entry_date must be YYYY-MM-DD, got "not-a-date"',
        },
      ],
    });

    render(<BatchEntryUpload entityId="entity-1" />);

    expect(screen.getByText(/1 error found/i)).toBeInTheDocument();
    expect(screen.getByText(/entry_date must be YYYY-MM-DD/i)).toBeInTheDocument();
  });

  it('shows preview table and enabled submit when CSV is valid', () => {
    const mockGroup: BatchEntryGroup = {
      key: '2026-04-01::April rent',
      entry_date: '2026-04-01',
      narration: 'April rent',
      period: '2026-04',
      entityId: 'entity-1',
      lines: [
        { account_code: '1001', debit: 25000, credit: 0 },
        { account_code: '2001', debit: 0, credit: 25000 },
      ],
    };

    mockUseBatchEntryUpload.mockReturnValue({
      ...makeDefaultReturn(),
      hasFile: true,
      parsedRows: [
        {
          entry_date: '2026-04-01',
          period: '2026-04',
          narration: 'April rent',
          account_code: '1001',
          type: 'DEBIT' as const,
          amount: '25000',
          description: '',
          rowNumber: 2,
        },
      ],
      groupedEntries: [mockGroup],
      allErrors: [],
      canSubmit: true,
    });

    render(<BatchEntryUpload entityId="entity-1" />);

    expect(screen.getByText(/preview.*1 entry/i)).toBeInTheDocument();
    expect(screen.getByText('April rent')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload 1 entry/i })).toBeEnabled();
  });

  it('shows success message after a successful upload', () => {
    mockUseBatchEntryUpload.mockReturnValue({
      ...makeDefaultReturn(),
      result: { created: [{ entry_id: 'e1' } as never, { entry_id: 'e2' } as never], failedGroups: [] },
    });

    render(<BatchEntryUpload entityId="entity-1" />);

    expect(screen.getByText(/upload complete/i)).toBeInTheDocument();
    expect(screen.getByText(/2 journal entries created/i)).toBeInTheDocument();
  });
});
