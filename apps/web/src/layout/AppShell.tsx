import { useState } from 'react';
import { NavLink, Outlet } from 'react-router';
import { useAuth } from '../auth/context';
import { navigationFor } from '../routes';

export function AppShell() {
  const { state, signOut, switchWorkspace } = useAuth();
  const [signingOut, setSigningOut] = useState(false);

  // RequireSession only renders the shell for signed-in people.
  if (state.status !== 'signedIn') return null;
  const { session, workspace } = state;

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await signOut();
    } catch {
      // Still signed in (network or server error); the button can be used again.
      setSigningOut(false);
    }
  }

  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <span className="brand">LedgerLens</span>
        <span className="demo-tag">Demo data only</span>
        {workspace && (
          <div className="workspace">
            {session.memberships.length > 1 ? (
              <label>
                Workspace
                <select
                  value={workspace.organization.id}
                  onChange={(e) => switchWorkspace(e.target.value)}
                >
                  {session.memberships.map((m) => (
                    <option key={m.organization.id} value={m.organization.id}>
                      {m.organization.name}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <span className="workspace-name">{workspace.organization.name}</span>
            )}
            <span className="role-badge">{workspace.role}</span>
          </div>
        )}
        <span className="user" title={session.user.email}>
          {session.user.display_name}
        </span>
        <button
          type="button"
          className="link-button"
          onClick={handleSignOut}
          disabled={signingOut}
        >
          Sign out
        </button>
      </header>
      <nav className="sidebar" aria-label="Main">
        {workspace && (
          <ul>
            {navigationFor(workspace.role).map((r) => (
              <li key={r.id}>
                <NavLink to={r.path} end={r.path === '/'}>
                  {r.label}
                </NavLink>
              </li>
            ))}
          </ul>
        )}
      </nav>
      <main id="main" className="content" tabIndex={-1}>
        {workspace ? (
          // Keyed by organization so no page state leaks between workspaces.
          <Outlet key={workspace.organization.id} />
        ) : (
          <section aria-labelledby="no-workspace-title">
            <h1 id="no-workspace-title">No workspace yet</h1>
            <p className="empty">
              Your account is not a member of any organization. Ask a workspace owner to invite
              you.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
