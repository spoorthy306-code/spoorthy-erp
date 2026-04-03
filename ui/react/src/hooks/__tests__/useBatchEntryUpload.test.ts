import { renderHook, act } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useBatchEntryUpload } from '../useBatchEntryUpload';

const { mockBatchCreate } = vi.hoisted(() => ({
  mockBatchCreate: vi.fn(),
}));

vi.mock('@/services/journalEntries.service', () => ({
  journalEntriesService: { batchCreate: mockBatchCreate },
}));

const VALID_CSV = `entry_date,period,narration,account_code,type,amount,description
2026-04-01,2026-04,April rent,1001,DEBIT,25000,Rent expense
2026-04-01,2026-04,April rent,2001,CREDIT,25000,Cash payment`;

describe('useBatchEntryUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('parses a valid CSV into rows and groups', () => {
    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV(VALID_CSV);
    });

    expect(result.current.parsedRows).toHaveLength(2);
    expect(result.current.groupedEntries).toHaveLength(1);
    expect(result.current.groupedEntries[0].narration).toBe('April rent');
    expect(result.current.allErrors).toHaveLength(0);
    expect(result.current.canSubmit).toBe(true);
  });

  it('returns a parse error for missing required headers', () => {
    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV('entry_date,narration\n2026-04-01,Test');
    });

    expect(result.current.parseErrors).toHaveLength(1);
    expect(result.current.parseErrors[0].message).toMatch(/missing required columns/i);
    expect(result.current.canSubmit).toBe(false);
  });

  it('returns a parse error for an invalid entry_date', () => {
    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV(
        `entry_date,period,narration,account_code,type,amount,description\nnot-a-date,2026-04,Test,1001,DEBIT,1000,`
      );
    });

    expect(result.current.allErrors.some((e) => e.field === 'entry_date')).toBe(true);
    expect(result.current.canSubmit).toBe(false);
  });

  it('returns a balance error for an unbalanced entry', () => {
    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV(
        `entry_date,period,narration,account_code,type,amount,description
2026-04-01,2026-04,Test,1001,DEBIT,1000,
2026-04-01,2026-04,Test,2001,CREDIT,500,`
      );
    });

    expect(result.current.balanceErrors).toHaveLength(1);
    expect(result.current.balanceErrors[0].message).toMatch(/not balanced/i);
    expect(result.current.canSubmit).toBe(false);
  });

  it('resets all state when reset() is called', () => {
    const { result } = renderHook(() => useBatchEntryUpload('entity-1'));

    act(() => {
      result.current.parseCSV(VALID_CSV);
    });

    expect(result.current.parsedRows).toHaveLength(2);

    act(() => {
      result.current.reset();
    });

    expect(result.current.parsedRows).toHaveLength(0);
    expect(result.current.groupedEntries).toHaveLength(0);
    expect(result.current.hasFile).toBe(false);
    expect(result.current.canSubmit).toBe(false);
  });
});
