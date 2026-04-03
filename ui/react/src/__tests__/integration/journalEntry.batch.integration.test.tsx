import { renderHook, act } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useBatchEntryUpload } from '@/hooks/useBatchEntryUpload';
import type { JournalEntry } from '@/types/journal.types';

// Mock only the service — the hook and its logic run for real
const mockBatchCreate = vi.hoisted(() => vi.fn());

vi.mock('@/services/journalEntries.service', () => ({
  journalEntriesService: { batchCreate: mockBatchCreate },
}));

const MULTI_ENTRY_CSV = `entry_date,period,narration,account_code,type,amount,description
2026-04-01,2026-04,April rent,1001,DEBIT,25000,Rent expense
2026-04-01,2026-04,April rent,2001,CREDIT,25000,Cash payment
2026-04-02,2026-04,Salary payment,5001,DEBIT,50000,Salary April
2026-04-02,2026-04,Salary payment,2001,CREDIT,50000,Bank transfer`;

describe('Batch Journal Entry Upload — Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('parses multi-entry CSV, groups correctly, and submits batch successfully', async () => {
    const mockCreated: JournalEntry[] = [
      {
        entry_id: 'e1',
        entity_id: 'entity-1',
        entry_date: '2026-04-01',
        period: '2026-04',
        total_debit: 25000,
        total_credit: 25000,
        created_at: '2026-04-01T00:00:00',
      },
      {
        entry_id: 'e2',
        entity_id: 'entity-1',
        entry_date: '2026-04-02',
        period: '2026-04',
        total_debit: 50000,
        total_credit: 50000,
        created_at: '2026-04-02T00:00:00',
      },
    ];

    mockBatchCreate.mockResolvedValueOnce(mockCreated);

    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    // Step 1: Parse
    act(() => {
      result.current.parseCSV(MULTI_ENTRY_CSV);
    });

    expect(result.current.parsedRows).toHaveLength(4);
    expect(result.current.groupedEntries).toHaveLength(2);
    expect(result.current.allErrors).toHaveLength(0);
    expect(result.current.canSubmit).toBe(true);

    // Step 2: Submit
    await act(async () => {
      await result.current.submit();
    });

    expect(mockBatchCreate).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({ entity_id: 'entity-1', entry_date: '2026-04-01', narration: 'April rent' }),
        expect.objectContaining({ entity_id: 'entity-1', entry_date: '2026-04-02', narration: 'Salary payment' }),
      ])
    );
    expect(result.current.result?.created).toHaveLength(2);
    expect(result.current.submitError).toBeNull();
    expect(result.current.isSubmitting).toBe(false);
  });

  it('stores a submit error and leaves result null when batchCreate throws', async () => {
    mockBatchCreate.mockRejectedValueOnce(
      new Error('Batch journal entry creation is not available until the backend exposes POST /api/v1/journal-entries/batch.')
    );

    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV(MULTI_ENTRY_CSV);
    });

    await act(async () => {
      await result.current.submit();
    });

    expect(result.current.submitError).toMatch(/batch journal entry creation is not available/i);
    expect(result.current.result).toBeNull();
    expect(result.current.isSubmitting).toBe(false);
  });
});
