# Backlog

The roadmap is eight weeks. Each week ends with something that runs and is tested;
anything unfinished moves to the next week instead of being marked done.

| Week | Theme | Done when |
|---|---|---|
| 1 | Product definition & dev environment | React shell, Django and FastAPI health endpoints, PostgreSQL and Redis start from one documented command; CI runs lint and unit tests |
| 2 | Identity, tenancy & authorization | Organizations, memberships and sessions; sign-in and workspace switcher; cross-tenant reads and writes are denied and tested |
| 3 | Ledger & accounting primitives | Accounts, categories, transactions, balanced journal posting; paginated ledger API and table; three months of seeded data with deterministic balances |
| 4 | CSV import, reconciliation, bills & invoices | Mapped CSV import that is idempotent on replay; duplicate/conflict review; invoices and bills with explicit state transitions |
| 5 | Forecast engine & scenarios | Deterministic daily cash projection; scenario overlays for delays and one-off costs; base snapshot stays untouched |
| 6 | AI categorization, background jobs & staging | Suggestion schema with mock provider and review queue; idempotent Celery jobs; first staging deploy |
| 7 | Cited briefings, reports & reliability | Facts envelope and structured briefing with verified citations; monthly reports; metrics and traces |
| 8 | Security hardening & release | Authorization review on every endpoint, abuse tests for uploads and prompt injection, tagged release and demo |

## Module acceptance criteria

| Module | Acceptance criteria |
|---|---|
| Tenant onboarding | Organization ownership enforced on every endpoint |
| Data ingestion | Import is idempotent per organization, file and row signature |
| Ledger | Amounts are integer minor units or exact decimals; journal entries balance |
| Reconciliation | A confirmed import cannot silently change the original transaction |
| Invoices / bills | Explicit state transitions, each with an audit event |
| Dashboard | Derived totals reconcile with journal fixtures |
| Scenario studio | Each scenario is an independent version; the ledger never changes |
| AI review | Suggestions are stored apart from ledger changes until approved |
| AI briefing | Every quoted amount comes from server-generated facts |
| Admin / reports | Role filtering, traceable exports, audit history |
