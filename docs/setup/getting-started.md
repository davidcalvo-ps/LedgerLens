# Getting started

LedgerLens runs locally as four containers (PostgreSQL with pgvector, Redis, the Django
core API and the internal FastAPI AI service) plus the React dev server on your machine.
All data is synthetic; never load real bank statements into a development stack.

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Docker with the Compose plugin | Compose v2.20+ (`--wait`) | PostgreSQL, Redis, core-api, ai-api |
| Node.js | 22 (see `.nvmrc`) | React web app |
| pnpm | 10 (`corepack enable`) | web dependencies and scripts |
| Python | 3.12 | only for running the service tests outside Docker |

## One-command start

```bash
scripts/dev.sh up
```

On the first run this copies `.env.example` to `.env` and replaces the placeholder
PostgreSQL password and Django secret key with random values (`.env` is git-ignored and
created with mode 600). It then builds both service images, starts the stack and waits
until every healthcheck passes, and finally prints the core API readiness response.

Then start the web app in a second terminal:

```bash
scripts/dev.sh web
```

Open <http://localhost:5173>. The dev server proxies `/api` to the core API.

## What runs where

| Service | URL from your machine | Notes |
|---|---|---|
| Web (Vite) | <http://localhost:5173> | role switch in the header is a preview only until sign-in lands in week 2 |
| core-api | <http://127.0.0.1:8000/api/v1/health/live> | process liveness |
| | <http://127.0.0.1:8000/api/v1/health/ready> | checks PostgreSQL and Redis; 503 when either is down |
| ai-api | not published | reachable only from core-api on the internal `services` network |
| PostgreSQL | `127.0.0.1:5432` | database `ledgerlens` |
| Redis | `127.0.0.1:6379` | append-only persistence |

Published ports bind to `127.0.0.1` only. Change them in `.env` if they clash with
something already running.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_DB`, `POSTGRES_USER` | `ledgerlens` | database name and role |
| `POSTGRES_PASSWORD` | random on first run | required; Compose refuses to start without it |
| `POSTGRES_PORT`, `REDIS_PORT`, `CORE_API_PORT` | 5432, 6379, 8000 | host ports |
| `DJANGO_SECRET_KEY` | random on first run | required |
| `DJANGO_DEBUG` | `true` | local only; production settings arrive with staging in week 6 |

## Everyday commands

```bash
scripts/dev.sh check   # lint + unit tests for web, core-api and ai-api (same as CI)
scripts/dev.sh down    # stop the stack, keep data
scripts/dev.sh reset   # delete the PostgreSQL and Redis volumes (asks first)
docker compose logs -f core-api
```

`check` creates a `.venv` inside each service on first use; the unit tests use SQLite in
memory and stubbed health probes, so they do not need the stack to be running.

## Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and on pull requests:

- **web**: `pnpm lint`, `pnpm typecheck`, `pnpm test` (Vitest), `pnpm build`
- **core-api** and **ai-api**: `ruff check` and `pytest`
- **compose**: `docker compose config` against `.env.example`

## Troubleshooting

- `set POSTGRES_PASSWORD in .env`: `.env` is missing a value; delete it and rerun
  `scripts/dev.sh up` to regenerate it.
- `/health/ready` returns 503: PostgreSQL or Redis is not healthy yet; check
  `docker compose ps`.
- Port already in use: change the matching `*_PORT` value in `.env` and rerun `up`.
