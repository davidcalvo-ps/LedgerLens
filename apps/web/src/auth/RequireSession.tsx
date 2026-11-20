import { Navigate, Outlet, useLocation } from 'react-router';
import { useAuth } from './context';
import { signInPath } from './session';

/** Gate for every page that needs a signed-in person. */
export function RequireSession() {
  const { state } = useAuth();
  const location = useLocation();

  if (state.status === 'loading') {
    return (
      <p className="status-page" role="status">
        Loading your workspace…
      </p>
    );
  }
  if (state.status === 'unavailable') {
    return (
      <p className="status-page" role="alert">
        LedgerLens cannot reach the server right now. Check that the API is running and reload
        the page.
      </p>
    );
  }
  if (state.status === 'signedOut') {
    return <Navigate to={signInPath(location.pathname + location.search)} replace />;
  }
  return <Outlet />;
}
