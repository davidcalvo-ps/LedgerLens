import { useState } from 'react';
import { NavLink, Outlet } from 'react-router';
import { navigationFor, type Role } from '../routes';

const ROLES: readonly Role[] = ['owner', 'accountant', 'analyst'];

export function AppShell() {
  // Until sign-in lands (week 2) the role is a local preview switch only.
  const [role, setRole] = useState<Role>('owner');

  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <span className="brand">LedgerLens</span>
        <span className="demo-tag">Demo data only</span>
        <label className="role-switch">
          Preview as
          <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>
      </header>
      <nav className="sidebar" aria-label="Main">
        <ul>
          {navigationFor(role).map((r) => (
            <li key={r.id}>
              <NavLink to={r.path} end={r.path === '/'}>
                {r.label}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <main id="main" className="content" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
