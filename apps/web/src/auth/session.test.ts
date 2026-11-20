import { describe, expect, it } from 'vitest';
import { type Membership, pickWorkspace, safeNextPath, signInPath } from './session';

const membership = (orgId: string, name: string, role: Membership['role']): Membership => ({
  id: `m-${orgId}`,
  role,
  organization: { id: orgId, name, slug: name.toLowerCase(), base_currency: 'EUR' },
});

const both = [membership('a', 'Harbor', 'accountant'), membership('b', 'Lumen', 'analyst')];

describe('pickWorkspace', () => {
  it('reopens the remembered workspace', () => {
    expect(pickWorkspace(both, 'b')?.organization.id).toBe('b');
  });

  it('falls back to the first workspace when the remembered one is gone', () => {
    expect(pickWorkspace(both, 'removed')?.organization.id).toBe('a');
    expect(pickWorkspace(both, null)?.organization.id).toBe('a');
  });

  it('returns null for people without any workspace', () => {
    expect(pickWorkspace([], 'a')).toBeNull();
  });
});

describe('safeNextPath', () => {
  it('keeps in-app paths with their query', () => {
    expect(safeNextPath('/transactions?page=2')).toBe('/transactions?page=2');
  });

  it.each([null, '', 'https://evil.example', '//evil.example', '/\\evil.example', 'transactions'])(
    'rejects %j',
    (next) => {
      expect(safeNextPath(next)).toBe('/');
    },
  );

  it('does not loop back to the sign-in page', () => {
    expect(safeNextPath('/sign-in')).toBe('/');
    expect(safeNextPath('/sign-in?next=/x')).toBe('/');
  });
});

describe('signInPath', () => {
  it('carries the page the person was on', () => {
    expect(signInPath('/imports?step=2')).toBe('/sign-in?next=%2Fimports%3Fstep%3D2');
    expect(signInPath('/')).toBe('/sign-in');
  });
});
