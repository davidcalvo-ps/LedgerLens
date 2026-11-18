import { describe, expect, it } from 'vitest';
import { formatMinor, minorDigits } from './money';

describe('formatMinor', () => {
  it('formats cents without floating-point conversion', () => {
    expect(formatMinor(123456, 'USD')).toBe('$1,234.56');
    expect(formatMinor(5, 'USD')).toBe('$0.05');
    expect(formatMinor(0, 'USD')).toBe('$0.00');
  });

  it('keeps the sign for outflows', () => {
    expect(formatMinor(-1999, 'USD')).toBe('-$19.99');
  });

  it('respects currencies without minor units', () => {
    expect(minorDigits('JPY')).toBe(0);
    expect(formatMinor(1500, 'JPY')).toBe('¥1,500');
  });

  it('formats amounts where float math would drift', () => {
    expect(formatMinor(900719925474099, 'USD')).toBe('$9,007,199,254,740.99');
  });

  it('rejects non-integer amounts', () => {
    expect(() => formatMinor(10.5, 'USD')).toThrow(RangeError);
  });
});
