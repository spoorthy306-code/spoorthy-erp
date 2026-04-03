import { describe, expect, it } from 'vitest';
import { formatINR, formatIndianNumber } from '@/utils/formatters';

describe('formatters', () => {
  it('formats INR values with symbol and separators', () => {
    expect(formatINR(1000000)).toContain('10,00,000');
  });

  it('formats indian number grouping', () => {
    expect(formatIndianNumber(12500000)).toBe('1,25,00,000');
  });
});
