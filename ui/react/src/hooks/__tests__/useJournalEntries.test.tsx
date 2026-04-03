import React, { PropsWithChildren } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { useJournalEntries } from '@/hooks/useJournalEntries';
import { journalEntriesService } from '@/services/journalEntries.service';

vi.mock('@/services/journalEntries.service', () => ({
  journalEntriesService: {
    list: vi.fn(),
    getById: vi.fn(),
    create: vi.fn(),
    reconcile: vi.fn(),
  },
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });

  return function Wrapper({ children }: PropsWithChildren) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe('useJournalEntries', () => {
  it('loads entries for a selected entity', async () => {
    vi.mocked(journalEntriesService.list).mockResolvedValueOnce([
      {
        entry_id: 'entry-1',
        entity_id: 'entity-1',
        entry_date: '2026-04-03',
        period: '2026-04',
        narration: 'Opening balance',
        total_debit: 100,
        total_credit: 100,
        created_at: '2026-04-03T00:00:00Z',
      },
    ] as any);

    const { result } = renderHook(
      () => useJournalEntries({ entityId: 'entity-1', limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.entries).toHaveLength(1));
    expect(journalEntriesService.list).toHaveBeenCalledWith({ entityId: 'entity-1', limit: 10 });
  });

  it('creates a journal entry and exposes the mutation', async () => {
    vi.mocked(journalEntriesService.list).mockResolvedValue([] as any);
    vi.mocked(journalEntriesService.create).mockResolvedValueOnce({
      entry_id: 'entry-2',
      entity_id: 'entity-1',
      entry_date: '2026-04-03',
      period: '2026-04',
      narration: 'Sales entry',
      total_debit: 250,
      total_credit: 250,
      created_at: '2026-04-03T00:00:00Z',
    } as any);

    const { result } = renderHook(
      () => useJournalEntries({ entityId: 'entity-1', limit: 10 }),
      { wrapper: createWrapper() }
    );

    await result.current.createEntry({
      entity_id: 'entity-1',
      entry_date: '2026-04-03',
      narration: 'Sales entry',
      lines: [
        { account_code: '1001', debit: 250, credit: 0 },
        { account_code: '4001', debit: 0, credit: 250 },
      ],
    });

    expect(journalEntriesService.create).toHaveBeenCalledTimes(1);
  });
});
