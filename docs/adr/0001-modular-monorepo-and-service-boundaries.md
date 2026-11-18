# ADR 0001: Modular monorepo with a Django core and a separate AI service

- Status: accepted
- Date: 2026-11-18

## Context

LedgerLens handles money, tenant data and AI output. The finance logic must be exact
and authorized in one place, while AI inference has different dependencies, latency
and failure modes. One developer maintains the project, so the setup has to stay
small enough to run locally with one command.

## Decision

- **One repository** with `apps/web` (React + TypeScript, Vite), `services/core-api`
  (Django + DRF), `services/ai-api` (FastAPI) and `services/worker` (Celery).
  Shared contracts live in `packages/`.
- **Django is the only source of truth** for organizations, ledger, invoices,
  forecasts and audit events. It is a modular monolith: one module per domain
  (`accounts`, `imports`, `ledger`, `invoices`, `forecast`, `audit`) with no
  cross-module database writes, so modules can be extracted later if needed.
- **The browser talks only to Django.** FastAPI is internal: it receives a minimal,
  organization-scoped set of facts after Django has authorized the request, returns
  validated structured output, and never writes financial records.
- **Celery on Redis** runs imports, forecast snapshots and AI jobs outside web requests.
- **PostgreSQL with pgvector** for business data and, later, policy document search.
- **pnpm** for the TypeScript workspace; each Python service locks its own
  dependencies.

## Consequences

- Authorization and money rules are tested in one service.
- An AI outage degrades suggestions and briefings only; the dashboard and forecast
  keep working.
- Two languages and two Python services add setup cost, which Docker Compose and a
  single startup guide have to absorb.
- Internal calls to FastAPI need service authentication and timeouts (week 6).

## Alternatives considered

- **Microservices per domain:** rejected; distributed transactions across ledger and
  invoices are not worth it at this size.
- **AI inside Django:** rejected; it would mix model dependencies and slow calls into
  the authoritative API and widen what AI code can touch.
