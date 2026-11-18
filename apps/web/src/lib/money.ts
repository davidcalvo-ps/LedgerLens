/**
 * Amounts travel as integer minor units (cents) so the UI never does
 * floating-point arithmetic on money. Formatting is the only conversion.
 */
const MINOR_DIGITS: Record<string, number> = { JPY: 0, KRW: 0, BHD: 3, KWD: 3 };

export function minorDigits(currency: string): number {
  return MINOR_DIGITS[currency] ?? 2;
}

export function formatMinor(amountMinor: number, currency: string, locale = 'en-US'): string {
  if (!Number.isSafeInteger(amountMinor)) {
    throw new RangeError('amountMinor must be a safe integer');
  }
  const digits = minorDigits(currency);
  const negative = amountMinor < 0;
  const abs = Math.abs(amountMinor).toString().padStart(digits + 1, '0');
  const whole = digits ? abs.slice(0, -digits) : abs;
  const fraction = digits ? abs.slice(-digits) : '';
  const parts = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).formatToParts(negative ? -1 : 1);
  return parts
    .map((p) => {
      if (p.type === 'integer') {
        return new Intl.NumberFormat(locale, { useGrouping: true }).format(BigInt(whole));
      }
      if (p.type === 'fraction') return fraction;
      return p.value;
    })
    .join('');
}
