import { describe, expect, it } from 'vitest';
import { errorMessage, readCookie } from './api';

describe('readCookie', () => {
  const cookies = 'theme=dark; ledgerlens_csrftoken=abc%3D123; other=x=y';

  it('finds a cookie by exact name and decodes it', () => {
    expect(readCookie(cookies, 'ledgerlens_csrftoken')).toBe('abc=123');
    expect(readCookie(cookies, 'other')).toBe('x=y');
  });

  it('returns null when the cookie is missing', () => {
    expect(readCookie(cookies, 'csrftoken')).toBeNull();
    expect(readCookie('', 'ledgerlens_csrftoken')).toBeNull();
  });
});

describe('errorMessage', () => {
  it('uses the DRF detail message', () => {
    expect(errorMessage(400, { detail: 'Invalid email or password.' })).toBe(
      'Invalid email or password.',
    );
  });

  it('uses the first field error', () => {
    expect(errorMessage(400, { email: ['Enter a valid email address.'] })).toBe(
      'Enter a valid email address.',
    );
  });

  it('never shows raw server errors', () => {
    expect(errorMessage(502, '<html>Bad gateway</html>')).toBe(
      'The server had a problem. Please try again.',
    );
  });
});
