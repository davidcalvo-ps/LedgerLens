# Week 01: Product definition & dev environment

- Goal: React shell, Django and FastAPI health endpoints, PostgreSQL and Redis started
  from one documented command; CI running lint and unit tests.
- Delivered so far:
  - Product charter, personas, backlog and ADR 0001
  - pnpm workspace and React + TypeScript (Vite) shell with a typed route table,
    role-aware navigation preview and a dashboard placeholder
  - Money formatting helper that works on integer minor units, with unit tests
  - `services/core-api`: Django + DRF project with split settings, deny-by-default
    permissions and versioned health routes: `/api/v1/health/live` (process only)
    and `/api/v1/health/ready` (PostgreSQL + Redis, 503 when either fails, no error
    details in the response)
  - `services/ai-api`: FastAPI app factory with a typed `/v1/health/live` response;
    OpenAPI docs only when `LEDGERLENS_ENV=local`
  - `compose.yaml`: PostgreSQL 17 with pgvector, Redis 7.4 and both services, with
    healthchecks; `data` and `services` networks keep the AI API away from the
    database and Redis; published ports bind to 127.0.0.1; `.env.example`
- Tests added / CI result: route and money unit tests (Vitest); pytest suites for both
  health APIs (`services/core-api/tests`, `services/ai-api/tests`). CI comes later this week.
- Security or reliability concerns: roles in the web app are a preview switch only;
  real authorization arrives with sign-in in week 2. The AI API has no authentication
  yet and is only reachable inside the Compose `services` network.
- Unfinished work: startup guide, CI workflow.
- Next: one-command local startup guide and a GitHub Actions lint and unit-test workflow.
