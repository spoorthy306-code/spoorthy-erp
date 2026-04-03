import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { EntryLineItem } from '@/components/entries/EntryLineItem';

const sampleLine = {
  id: 'line-1',
  accountCode: '1001',
  type: 'DEBIT' as const,
  amount: 500,
  description: 'Cash received',
};

describe('EntryLineItem', () => {
  it('renders the provided line values', () => {
    render(<EntryLineItem line={sampleLine} index={0} onChange={vi.fn()} />);

    expect(screen.getByDisplayValue('1001')).toBeInTheDocument();
    expect(screen.getByDisplayValue('500')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Cash received')).toBeInTheDocument();
  });

  it('emits remove events when requested', () => {
    const onRemove = vi.fn();

    render(<EntryLineItem line={sampleLine} index={0} onChange={vi.fn()} onRemove={onRemove} />);

    fireEvent.click(screen.getByRole('button', { name: 'Remove' }));
    expect(onRemove).toHaveBeenCalledWith('line-1');
  });
});
