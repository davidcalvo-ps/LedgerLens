import { createBrowserRouter } from 'react-router';
import { AppShell } from './layout/AppShell';
import { Dashboard } from './pages/Dashboard';
import { NotFound } from './pages/NotFound';
import { SectionPage } from './pages/SectionPage';
import { routes } from './routes';

export const router = createBrowserRouter([
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
]);
