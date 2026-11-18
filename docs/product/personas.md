# Personas

All personas are fictional and used to drive acceptance criteria.

## Owner: Lucía, runs a three-person design studio

- Sends 4–8 invoices a month; two clients routinely pay late.
- Checks cash on her phone between meetings; wants to know "can I afford this?"
- **Needs:** runway at a glance, scenarios for late payments and big purchases,
  inviting her accountant.
- **Can:** everything in her workspace, including members and roles.

## Accountant: Martín, external bookkeeper for several small businesses

- Works across many workspaces; must never see one client's data in another's.
- Imports monthly statements and fixes categories in bulk.
- **Needs:** idempotent CSV import, a clear duplicate/conflict queue, fast category
  review with keyboard support, an audit trail of who changed what.
- **Can:** import, categorize, reconcile, manage invoices and bills; approve or
  reject AI suggestions. Cannot manage members.

## Analyst: Sara, part-time finance advisor

- Reviews the forecast before monthly planning calls.
- **Needs:** read-only forecasts and scenarios, exports, and briefings that show
  where each number came from.
- **Can:** read dashboards, forecasts and scenarios. Cannot change the ledger.

## Role summary

| Capability | Owner | Accountant | Analyst |
|---|:-:|:-:|:-:|
| View dashboard, ledger, forecasts | ✓ | ✓ | ✓ |
| Create scenarios | ✓ | ✓ | ✓ |
| Import CSV, edit transactions | ✓ | ✓ | |
| Manage invoices and bills | ✓ | ✓ | |
| Approve AI suggestions | ✓ | ✓ | |
| Manage members and roles | ✓ | | |
