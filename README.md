# LedgerLens

**Cash-flow simulator for independent businesses.** LedgerLens lets freelancers and small agencies rehearse future decisions, like "what if a client pays 18 days late and I buy a laptop next Thursday?", and see the effect on their cash runway before it happens.

> **Status:** early development, following a 12-week roadmap (see below). The project uses synthetic business records and uploaded CSV files only. It does not connect to real bank accounts.

## The problem

A freelancer or small agency can have profitable invoices on paper and still run out of cash before payroll or rent. Typical budgeting apps chart past transactions; they don't help you test a decision before you make it.

LedgerLens keeps deterministic accounting calculations separate from AI explanations: the numbers always come from the ledger and the forecast engine, and AI only explains them.

## Who it's for

- **Owners:** run the business, explore scenarios and approve changes
- **Accountants:** review and correct the ledger
- **Analysts:** read forecasts without changing anything

## Demo workflow

1. Upload a sample bank CSV
2. Review unmatched lines
3. Approve suggested categories
4. Create an invoice
5. Move its expected payment date 18 days later
6. Watch the forecast update
7. Ask "Which bills create the shortfall?" and get a short answer that links to the real invoices and forecast version

## Planned features

- Workspaces with owner, accountant and analyst roles
- Bank statement CSV import with column mapping, reconciliation and traceable source hashes
- Ledger with accounts, transactions, rule-based categories and split transactions
- Invoices and bills with due dates and explicit state transitions
- Dashboard with actual cash, upcoming bills, receivables and runway
- Scenario studio with sliders for payment delays, spending and recurring revenue
- AI category suggestions with a confidence score and reason, which a person approves or rejects
- Cash-flow briefing: plain-language answers grounded in the computed forecast, with citations
- Member management, activity history and CSV export

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript |
| Business API | Django, Django REST Framework |
| AI inference API | FastAPI |
| Database | PostgreSQL with pgvector |
| Background jobs | Redis, Celery |
| Local environment | Docker Compose |
| CI | GitHub Actions |

## Architecture

The Django API is the authoritative source for all business data. A separate FastAPI service handles AI inference and never writes to the ledger directly. Imports and forecasts run as Celery background jobs.

```mermaid
flowchart LR
  User[Owner / accountant] --> Web[React app]
  Web --> API[Django REST API]
  API --> DB[(PostgreSQL + pgvector)]
  API --> Jobs[Celery workers]
  Jobs --> DB
  API --> AI[FastAPI inference service]
  AI -. suggestions only .-> API
```

## Design rules

- Money is stored as integer minor units or exact decimals, never floating point.
- Re-importing the same file never creates duplicate transactions.
- Confirmed imports can't silently change the original transaction.
- Scenarios are independent versions; the real ledger never changes.
- Every AI-proposed change needs a person's approval.
- Every amount in an AI answer comes from server-computed numbers.
- Organization ownership is enforced on every endpoint.

## Roadmap

| Weeks | Focus |
|---|---|
| 1–2 | Product definition, dev environment, identity, tenancy and authorization |
| 3–5 | Ledger and accounting basics, CSV import and reconciliation, bills and invoices |
| 6–8 | Forecast engine and charts, AI categorization with review, background jobs and first staging release |
| 9–10 | AI explanations with citations, reports, performance and reliability |
| 11–12 | Security review and hardening, release and demo |

## Getting started

Setup instructions will be added once the first services are in place.
