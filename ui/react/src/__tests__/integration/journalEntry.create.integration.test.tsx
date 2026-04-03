import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { JournalEntryForm } from '@/components/entries/JournalEntryForm';

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

describe('journal entry create integration', () => {
  beforeEach(() => {
    localStorage.clear();
    mocks.createEntry.mockReset();
    mocks.updateEntry.mockReset();
  });

  it('persists draft changes and clears the draft after a successful submit', async () => {
    mocks.createEntry.mockResolvedValueOnce({
      entry_id: 'entry-500',
      entity_id: 'entity-1',
      entry_date: '2026-04-03',
      period: '2026-04',
      narration: 'Customer receipt',
      total_debit: 1200,
      total_credit: 1200,
      created_at: '2026-04-03T00:00:00Z',
    });

    render(<JournalEntryForm entityId="entity-1" />);

    fireEvent.change(screen.getByLabelText(/entity id/i), { target: { value: 'entity-1' } });
    fireEvent.change(screen.getByLabelText(/description/i, { selector: 'textarea' }), {
      target: { value: 'Customer receipt' },
    });

    await waitFor(() => {
      expect(JSON.parse(localStorage.getItem('journal-entry-draft') ?? '{}').description).toBe('Customer receipt');
    });

    fireEvent.change(screen.getAllByLabelText(/account code/i)[0], { target: { value: '1000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[0], { target: { value: '1200' } });
    fireEvent.change(screen.getAllByLabelText(/account code/i)[1], { target: { value: '4000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[1], { target: { value: '1200' } });

    const submitButton = screen.getByRole('button', { name: /save entry/i });
    await waitFor(() => expect(submitButton).toBeEnabled());
    fireEvent.click(submitButton);

    await waitFor(() => expect(mocks.createEntry).toHaveBeenCalledTimes(1));
    await waitFor(() => expect(localStorage.getItem('journal-entry-draft')).toBeNull());
  });
});