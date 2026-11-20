import { createBrowserRouter } from 'react-router';
import { RequireSession } from './auth/RequireSession';
import { AppShell } from './layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { NotFound } from './pages/NotFound';
import { SectionPage } from './pages/SectionPage';
import { SignIn } from './pages/SignIn';
import { routes } from './routes';

export const router = createBrowserRouter([
  { path: '/sign-in', element: <SignIn /> },
  {
    element: <RequireSession />,
    children: [
      {
        path: '/',
        element: <AppShell />,
        children: [
          { index: true, element: <Dashboard /> },
          ...routes
            .filter((r) => r.id !== 'dashboard')
            .map((r) => ({ path: r.path.slice(1), element: <SectionPage route={r} /> })),
          { path: '*', element: <NotFound /> },
        ],
      },
    ],
  },
]);
