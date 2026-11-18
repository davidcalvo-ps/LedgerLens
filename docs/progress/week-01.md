# Week 01: Product definition & dev environment

- Goal: React shell, Django and FastAPI health endpoints, PostgreSQL and Redis started
  from one documented command; CI running lint and unit tests.
- Delivered so far:
  - Product charter, personas, backlog and ADR 0001
  - pnpm workspace and React + TypeScript (Vite) shell with a typed route table,
    role-aware navigation preview and a dashboard placeholder
  - Money formatting helper that works on integer minor units, with unit tests
- Tests added / CI result: route and money unit tests (Vitest); CI comes later this week.
- Security or reliability concerns: roles in the web app are a preview switch only;
  real authorization arrives with sign-in in week 2.
- Unfinished work: Django and FastAPI services, Compose stack, startup guide, CI.
- Next: bootstrap the Django REST and FastAPI health services with Compose.
