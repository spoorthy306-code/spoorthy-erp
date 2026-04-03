import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useJournalEntryForm } from '@/hooks/useJournalEntryForm';

const mocks = vi.hoisted(() => ({
  createEntry: vi.fn(),
  updateEntry: vi.fn(),
}));

vi.mock('@/hooks/useJournalEntries', () => ({
  useJournalEntries: () => ({
    createEntry: mocks.createEntry,
    updateEntry: mocks.updateEntry,
    isCreating: false,
    isUpdating: false,
  }),
}));

describe('useJournalEntryForm', () => {
  beforeEach(() => {
    localStorage.clear();
    mocks.createEntry.mockReset();
    mocks.updateEntry.mockReset();
  });

  it('initializes with the expected default values', () => {
    const { result } = renderHook(() => useJournalEntryForm({ entityId: 'entity-1' }));

    expect(result.current.form.getValues()).toEqual({
      entityId: 'entity-1',
      entryDate: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      period: expect.stringMatching(/^\d{4}-\d{2}$/),
      reference: '',
      description: '',
      lines: [
        {
          id: expect.any(String),
          accountCode: '',
          type: 'DEBIT',
          amount: 0,
          description: '',
        },
        {
          id: expect.any(String),
          accountCode: '',
          type: 'CREDIT',
          amount: 0,
          description: '',
        },
      ],
    });
  });

  it('auto-saves drafts to localStorage when the form changes', async () => {
    const { result } = renderHook(() => useJournalEntryForm({ entityId: 'entity-1' }));

    await act(async () => {
      result.current.form.setValue('description', 'Drafted journal entry', { shouldDirty: true });
    });

    await waitFor(() => {
      expect(JSON.parse(localStorage.getItem('journal-entry-draft') ?? '{}').description).toBe('Drafted journal entry');
    });
  });

  it('adds and removes line items while protecting the minimum pair', () => {
    const { result } = renderHook(() => useJournalEntryForm({ entityId: 'entity-1' }));

    expect(result.current.fields).toHaveLength(2);

    act(() => {
      result.current.appendLine();
    });

    expect(result.current.form.getValues('lines')).toHaveLength(3);

    act(() => {
      result.current.removeLine(2);
      result.current.removeLine(1);
    });

    expect(result.current.form.getValues('lines')).toHaveLength(2);
  });

  it('submits a balanced create payload and clears the draft', async () => {
    mocks.createEntry.mockResolvedValueOnce({
      entry_id: 'entry-1',
      entity_id: 'entity-1',
      entry_date: '2026-04-03',
      period: '2026-04',
      narration: 'Cash sale',
      total_debit: 500,
      total_credit: 500,
      created_at: '2026-04-03T00:00:00Z',
    });

    const onSuccess = vi.fn();
    const { result } = renderHook(() => useJournalEntryForm({ entityId: 'entity-1', onSuccess }));

    await act(async () => {
      result.current.form.setValue('description', 'Cash sale', { shouldDirty: true, shouldValidate: true });
      result.current.form.setValue('lines.0.accountCode', '1001', { shouldDirty: true, shouldValidate: true });
      result.current.form.setValue('lines.0.amount', 500, { shouldDirty: true, shouldValidate: true });
      result.current.form.setValue('lines.1.accountCode', '4001', { shouldDirty: true, shouldValidate: true });
      result.current.form.setValue('lines.1.amount', 500, { shouldDirty: true, shouldValidate: true });
    });

    await act(async () => {
      await result.current.submit();
    });

    expect(mocks.createEntry).toHaveBeenCalledWith({
      entity_id: 'entity-1',
      entry_date: result.current.form.getValues('entryDate'),
      narration: 'Cash sale',
      lines: [
        { account_code: '1001', debit: 500, credit: 0, description: undefined },
        { account_code: '4001', debit: 0, credit: 500, description: undefined },
      ],
    });
    expect(localStorage.getItem('journal-entry-draft')).toBeNull();
    expect(onSuccess).toHaveBeenCalled();
  });
});