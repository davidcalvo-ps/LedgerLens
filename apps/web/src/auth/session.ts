import type { Role } from '../routes';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  base_currency: string;
}

export interface Membership {
  id: string;
  role: Role;
  organization: Organization;
}

export interface SessionUser {
  id: number;
  email: string;
  display_name: string;
}

export interface Session {
  user: SessionUser;
  memberships: Membership[];
}

/** Remembers the last workspace per browser; holds an organization ID only. */
export const WORKSPACE_STORAGE_KEY = 'ledgerlens.workspace';

/**
 * The workspace to open: the remembered one if the person still belongs to
 * it, otherwise the first membership (sorted by organization name by the API).
 */
export function pickWorkspace(
  memberships: readonly Membership[],
  rememberedOrgId: string | null,
): Membership | null {
  return (
    memberships.find((m) => m.organization.id === rememberedOrgId) ?? memberships[0] ?? null
  );
}

/**
 * Where to go after signing in. Only same-app paths are accepted, so a crafted
 * `?next=` cannot bounce people to another site.
 */
export function safeNextPath(next: string | null): string {
  if (!next || !next.startsWith('/') || next.startsWith('//') || next.includes('\\')) return '/';
  if (next === '/sign-in' || next.startsWith('/sign-in?')) return '/';
  return next;
}

export function signInPath(from: string): string {
  return from === '/' ? '/sign-in' : `/sign-in?next=${encodeURIComponent(from)}`;
}
