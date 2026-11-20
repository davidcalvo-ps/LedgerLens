import { type ReactNode, useCallback, useEffect, useMemo, useState } from 'react';
import { ApiError, api, onUnauthorized } from '../lib/api';
import { AuthContext, type AuthState, type AuthValue } from './context';
import { type Session, WORKSPACE_STORAGE_KEY, pickWorkspace } from './session';

function rememberedWorkspace(): string | null {
  try {
    return localStorage.getItem(WORKSPACE_STORAGE_KEY);
  } catch {
    return null; // storage disabled (private mode, policy): just don't remember
  }
}

function rememberWorkspace(orgId: string): void {
  try {
    localStorage.setItem(WORKSPACE_STORAGE_KEY, orgId);
  } catch {
    // see rememberedWorkspace
  }
}

function signedIn(session: Session): AuthState {
  return {
    status: 'signedIn',
    session,
    workspace: pickWorkspace(session.memberships, rememberedWorkspace()),
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({ status: 'loading' });

  useEffect(() => {
    const controller = new AbortController();
    api<Session>('/auth/session', { signal: controller.signal, quietUnauthorized: true })
      .then((session) => setState(signedIn(session)))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return;
        if (error instanceof ApiError && error.status === 401) {
          setState({ status: 'signedOut', reason: 'none' });
        } else {
          setState({ status: 'unavailable' });
        }
      });
    return () => controller.abort();
  }, []);

  // Any API call that comes back 401 while signed in means the session expired
  // (eight-hour lifetime, sign-out in another tab, or an admin deactivation).
  useEffect(
    () =>
      onUnauthorized(() =>
        setState((current) =>
          current.status === 'signedIn' ? { status: 'signedOut', reason: 'expired' } : current,
        ),
      ),
    [],
  );

  const signIn = useCallback(async (email: string, password: string) => {
    const session = await api<Session>('/auth/login', {
      method: 'POST',
      body: { email, password },
      quietUnauthorized: true,
    });
    setState(signedIn(session));
  }, []);

  const signOut = useCallback(async () => {
    try {
      await api<void>('/auth/logout', { method: 'POST', quietUnauthorized: true });
    } catch (error) {
      if (!(error instanceof ApiError && error.status === 401)) throw error;
    }
    setState({ status: 'signedOut', reason: 'signedOut' });
  }, []);

  const switchWorkspace = useCallback((orgId: string) => {
    setState((current) => {
      if (current.status !== 'signedIn') return current;
      const next = current.session.memberships.find((m) => m.organization.id === orgId);
      if (!next) return current;
      rememberWorkspace(orgId);
      return { ...current, workspace: next };
    });
  }, []);

  const value = useMemo<AuthValue>(
    () => ({ state, signIn, signOut, switchWorkspace }),
    [state, signIn, signOut, switchWorkspace],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
