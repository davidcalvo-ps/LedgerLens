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
  - `scripts/dev.sh up` starts the whole stack with one command (generates `.env` with
    random secrets on first run, waits for every healthcheck); `web`, `check`, `down`
    and `reset` subcommands; [getting started guide](../setup/getting-started.md)
  - ESLint 9 flat config for the web app (typescript-eslint, React hooks rules)
- Tests added / CI result: route and money unit tests (Vitest); pytest suites for both
  health APIs (`services/core-api/tests`, `services/ai-api/tests`). GitHub Actions CI
  (`.github/workflows/ci.yml`): web lint, typecheck, Vitest and build; ruff and pytest for
  core-api and ai-api; `docker compose config` against `.env.example`.
- Security or reliability concerns: roles in the web app are a preview switch only;
  real authorization arrives with sign-in in week 2. The AI API has no authentication
  yet and is only reachable inside the Compose `services` network.
- Unfinished work: first demo screenshot and walkthrough, to be added once the stack
  has been started from a clean clone.
- Next: week 2, organizations, memberships, sign-in and tenant isolation.
