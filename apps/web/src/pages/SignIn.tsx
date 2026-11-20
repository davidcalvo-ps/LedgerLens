import { type FormEvent, useState } from 'react';
import { Navigate, useSearchParams } from 'react-router';
import { useAuth } from '../auth/context';
import { safeNextPath } from '../auth/session';
import { ApiError } from '../lib/api';

const NOTICES = {
  expired: 'Your session expired. Sign in again to continue.',
  signedOut: 'You have signed out.',
} as const;

export function SignIn() {
  const { state, signIn } = useAuth();
  const [params] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (state.status === 'signedIn') {
    return <Navigate to={safeNextPath(params.get('next'))} replace />;
  }

  const notice =
    state.status === 'signedOut' && state.reason !== 'none' ? NOTICES[state.reason] : null;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setSubmitting(true);
    setError(null);
    try {
      await signIn(String(form.get('email') ?? ''), String(form.get('password') ?? ''));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not reach LedgerLens. Try again.');
      setSubmitting(false);
    }
  }

  return (
    <main className="sign-in" id="main">
      <form
        className="sign-in-card"
        onSubmit={handleSubmit}
        aria-labelledby="sign-in-title"
        noValidate
      >
        <span className="brand">LedgerLens</span>
        <h1 id="sign-in-title">Sign in</h1>
        {notice && (
          <p className="notice" role="status">
            {notice}
          </p>
        )}
        <label>
          Email
          <input name="email" type="email" autoComplete="username" required autoFocus />
        </label>
        <label>
          Password
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
            aria-describedby={error ? 'sign-in-error' : undefined}
          />
        </label>
        {error && (
          <p id="sign-in-error" className="form-error" role="alert">
            {error}
          </p>
        )}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
        <p className="demo-tag">Demo data only — never enter real financial information.</p>
      </form>
    </main>
  );
}
