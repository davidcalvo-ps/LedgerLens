export type Role = 'owner' | 'accountant' | 'analyst';

export type RouteId =
  | 'dashboard'
  | 'transactions'
  | 'imports'
  | 'invoices'
  | 'scenarios'
  | 'aiReview'
  | 'settings';

export interface AppRoute {
  id: RouteId;
  path: `/${string}`;
  label: string;
  /** Roles that see this section in the navigation. The API enforces access on its own. */
  roles: readonly Role[];
  /** Week of the roadmap in which the section gets real behavior. */
  plannedWeek: number;
  summary: string;
}

const ALL: readonly Role[] = ['owner', 'accountant', 'analyst'];

export const routes: readonly AppRoute[] = [
  {
    id: 'dashboard',
    path: '/',
    label: 'Dashboard',
    roles: ALL,
    plannedWeek: 5,
    summary: 'Actual cash, bills due soon, receivables and runway.',
  },
  {
    id: 'transactions',
    path: '/transactions',
    label: 'Transactions',
    roles: ALL,
    plannedWeek: 3,
    summary: 'Ledger of accounts, transactions and categories.',
  },
  {
    id: 'imports',
    path: '/imports',
    label: 'Imports',
    roles: ['owner', 'accountant'],
    plannedWeek: 4,
    summary: 'Upload a bank CSV, map columns, preview and commit once.',
  },
  {
    id: 'invoices',
    path: '/invoices',
    label: 'Invoices & bills',
    roles: ['owner', 'accountant'],
    plannedWeek: 4,
    summary: 'Receivables and payables with due dates and explicit states.',
  },
  {
    id: 'scenarios',
    path: '/scenarios',
    label: 'Scenarios',
    roles: ALL,
    plannedWeek: 5,
    summary: 'Try payment delays and one-off costs without touching the ledger.',
  },
  {
    id: 'aiReview',
    path: '/ai-review',
    label: 'Review queue',
    roles: ['owner', 'accountant'],
    plannedWeek: 6,
    summary: 'Suggested categories wait here until a person approves or rejects them.',
  },
  {
    id: 'settings',
    path: '/settings',
    label: 'Workspace',
    roles: ['owner'],
    plannedWeek: 2,
    summary: 'Members, roles and workspace details.',
  },
];

export function routeById(id: RouteId): AppRoute {
  const route = routes.find((r) => r.id === id);
  if (!route) throw new Error(`Unknown route: ${id}`);
  return route;
}

export function pathTo(id: RouteId): AppRoute['path'] {
  return routeById(id).path;
}

export function navigationFor(role: Role): AppRoute[] {
  return routes.filter((r) => r.roles.includes(role));
}
