import { createContext, useContext } from 'react';
import type { Membership, Session } from './session';

export type AuthState =
  | { status: 'loading' }
  | { status: 'unavailable' }
  | { status: 'signedOut'; reason: 'none' | 'expired' | 'signedOut' }
  | { status: 'signedIn'; session: Session; workspace: Membership | null };

export interface AuthValue {
  state: AuthState;
  signIn(email: string, password: string): Promise<void>;
  signOut(): Promise<void>;
  switchWorkspace(orgId: string): void;
}

export const AuthContext = createContext<AuthValue | null>(null);

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used inside <AuthProvider>');
  return value;
}
