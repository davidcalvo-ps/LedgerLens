import { describe, expect, it } from 'vitest';
import { navigationFor, pathTo, routes } from './routes';

describe('routes', () => {
  it('has unique ids and paths', () => {
    expect(new Set(routes.map((r) => r.id)).size).toBe(routes.length);
    expect(new Set(routes.map((r) => r.path)).size).toBe(routes.length);
  });

  it('builds paths from route ids', () => {
    expect(pathTo('dashboard')).toBe('/');
    expect(pathTo('aiReview')).toBe('/ai-review');
  });

  it('gives every role the dashboard', () => {
    for (const role of ['owner', 'accountant', 'analyst'] as const) {
      expect(navigationFor(role).map((r) => r.id)).toContain('dashboard');
    }
  });

  it('keeps analysts read-only', () => {
    const ids = navigationFor('analyst').map((r) => r.id);
    expect(ids).not.toContain('imports');
    expect(ids).not.toContain('invoices');
    expect(ids).not.toContain('aiReview');
    expect(ids).not.toContain('settings');
  });

  it('shows workspace settings to owners only', () => {
    expect(navigationFor('owner').map((r) => r.id)).toContain('settings');
    expect(navigationFor('accountant').map((r) => r.id)).not.toContain('settings');
  });
});
