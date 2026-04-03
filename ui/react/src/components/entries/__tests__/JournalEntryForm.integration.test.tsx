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

describe('JournalEntryForm', () => {
  beforeEach(() => {
    localStorage.clear();
    mocks.createEntry.mockReset();
    mocks.updateEntry.mockReset();
  });

  it('submits a balanced journal entry and notifies success', async () => {
    mocks.createEntry.mockResolvedValueOnce({
      entry_id: 'entry-101',
      entity_id: 'entity-1',
      entry_date: '2026-04-03',
      period: '2026-04',
      narration: 'Cash received from customer',
      total_debit: 5000,
      total_credit: 5000,
      created_at: '2026-04-03T00:00:00Z',
    });

    const onSuccess = vi.fn();
    render(<JournalEntryForm entityId="entity-1" onSuccess={onSuccess} />);

    fireEvent.change(screen.getByLabelText(/entity id/i), { target: { value: 'entity-1' } });
    fireEvent.change(screen.getByLabelText(/description/i, { selector: 'textarea' }), {
      target: { value: 'Cash received from customer' },
    });
    fireEvent.change(screen.getAllByLabelText(/account code/i)[0], { target: { value: '1000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[0], { target: { value: '5000' } });
    fireEvent.change(screen.getAllByLabelText(/account code/i)[1], { target: { value: '2000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[1], { target: { value: '5000' } });

    const submitButton = screen.getByRole('button', { name: /save entry/i });
    await waitFor(() => expect(submitButton).toBeEnabled());

    fireEvent.click(submitButton);

    await waitFor(() => expect(mocks.createEntry).toHaveBeenCalledTimes(1));
    expect(onSuccess).toHaveBeenCalledWith(
      expect.objectContaining({
        mode: 'create',
        entry: expect.objectContaining({ entry_id: 'entry-101' }),
      })
    );
  });

  it('prevents submission while the entry is unbalanced', async () => {
    render(<JournalEntryForm entityId="entity-1" />);

    fireEvent.change(screen.getByLabelText(/entity id/i), { target: { value: 'entity-1' } });
    fireEvent.change(screen.getByLabelText(/description/i, { selector: 'textarea' }), {
      target: { value: 'Unbalanced test entry' },
    });
    fireEvent.change(screen.getAllByLabelText(/account code/i)[0], { target: { value: '1000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[0], { target: { value: '5000' } });
    fireEvent.change(screen.getAllByLabelText(/account code/i)[1], { target: { value: '2000' } });
    fireEvent.change(screen.getAllByLabelText(/amount/i)[1], { target: { value: '3000' } });

    await waitFor(() => {
      expect(screen.getByText(/debit and credit totals differ by/i)).toBeInTheDocument();
    });
    expect(screen.getByRole('button', { name: /save entry/i })).toBeDisabled();
  });
});