# Product charter

## Problem

A freelancer or a small agency can have profitable invoices on paper and still run
out of cash before payroll or rent. Budgeting tools chart what already happened; they
don't let an owner try a decision before making it.

## Product

LedgerLens is a cash-flow simulator. An owner imports bank statements as CSV files,
keeps a small ledger of invoices and bills, and rehearses decisions such as "what if
Acme pays 18 days late and I buy a laptop next Thursday?" against a deterministic
forecast.

The numbers always come from the ledger and the forecast engine. AI features only
suggest categories (which a person approves) and explain forecasts that have already
been computed, citing the facts they used.

## Goals for v1

1. Import a bank CSV without duplicates, review it and reconcile it.
2. Keep invoices and bills with due dates and explicit state transitions.
3. Show actual cash, receivables, payables and runway on one dashboard.
4. Let a user build a scenario (payment delays, one-off spend, recurring revenue)
   that never changes the real ledger.
5. Offer AI category suggestions behind a human review queue, and a cash-flow
   briefing that only quotes server-computed numbers.

## Out of scope

- Tax filing, loans, investment advice or any regulated financial advice
- Moving money or connecting to live bank accounts
- Real customer data: the project uses synthetic records and uploaded sample CSVs

## Success targets

These are targets for the demo and its test fixtures, not measured results.

| Target | How it will be checked |
|---|---|
| Seeded examples reconcile exactly | Ledger fixture tests |
| Re-importing a file creates zero duplicate rows | Import replay test |
| Forecast numbers match deterministic fixtures | Forecast unit tests |
| Every AI-proposed change waits for approval | Suggestion workflow tests |
| End-to-end demo fits in five minutes | Scripted demo run |
| P95 read latency under 400 ms at a stated local load | Load test (week 7) |

## Principles

- Money is stored as integer minor units or exact decimals, never floats.
- Organization ownership is checked on every endpoint, not just in the UI.
- Corrections are reversals; confirmed imports are never silently rewritten.
- The browser talks only to the Django API; the AI service never writes records.
