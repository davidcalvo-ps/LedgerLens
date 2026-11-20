# Week 02: Identity, tenancy & authorization

- Goal: people sign in, belong to one or more organizations with a role, and can never
  read or change another organization's data.
- Delivered:
  - `modules/accounts`: `Organization` (random UUID IDs, ISO 4217 base currency) and
    `Membership` (owner / accountant / analyst, one per person and organization) with
    database constraints and migration `0001`
  - Session sign-in, sign-out, CSRF and current-session endpoints; HttpOnly, SameSite=Lax,
    Secure session cookie; scrypt password hashing and password validators
  - `IsOrganizationMember` / `OrganizationScopedView`: 401 signed out, 404 for
    non-members, 403 for roles not listed per method; `GET`/`PATCH /orgs/{id}`,
    `GET /orgs/{id}/members`, `GET /orgs/{id}/members/me`
  - React sign-in page, session gate, workspace switcher with the role taken from the
    selected membership, expired-session handling with a safe return path
  - `seed_demo_orgs` (two fictional organizations, four users, DEBUG only) and
    `scripts/dev.sh seed`; [demo accounts guide](../setup/demo-accounts.md)
  - Email masking for logs, `Membership.__str__` and seed output
  - [Identity and tenancy threat model](../security/identity-threat-model.md)
- Tests added / CI result: cross-tenant and role-matrix tests on shared permission
  fixtures (`tests/conftest.py`), auth and cookie tests, masking tests: 70 pytest pass
  locally. New CI `migrations` job on PostgreSQL (drift check, apply, roll back,
  re-apply, idempotent seed).
- Security or reliability concerns: no login throttling, MFA or password reset yet;
  no audit log of role changes; listed under "Known gaps" in the threat model.
- Unfinished work: the React sign-in flow and the PostgreSQL migration job still need a
  first run on a machine with Node and Docker; no screenshot of the sign-in flow yet.
- Next: week 3, ledger and accounting primitives.
