# Identity and tenancy threat model

Scope: sign-in, sessions, organizations, memberships and the organization-scoped API
(`services/core-api/modules/accounts`) plus the React sign-in and workspace switcher
(`apps/web/src/auth`). Reviewed at the end of week 2; revisit whenever a new
organization-scoped module or a new way to authenticate is added.

## What we protect

| Asset | Why it matters |
|---|---|
| Ledger, invoice and forecast data of each organization | A small business's finances; leaking one tenant's data to another is the worst failure this product can have |
| Membership roles | Decide who may change money-related records |
| Session cookies | Whoever holds one acts as that person |
| Member email addresses and names | Personal data; also useful for phishing the business |

## Trust boundaries

1. **Browser ↔ core-api.** Everything from the browser is untrusted, including the
   organization ID in the URL, the role shown in the UI and the remembered workspace.
2. **core-api ↔ PostgreSQL.** The only place tenancy is enforced is core-api; the
   database user can read every tenant, so a query without an organization filter is a
   leak.
3. **core-api ↔ ai-api.** ai-api has no access to the database or Redis (separate
   Compose network) and no authentication yet; it is not reachable from the browser.

## How access is decided

- Every tenant URL has the form `/api/v1/orgs/<org_id>/...`. `IsOrganizationMember`
  looks up the caller's membership for that ID once per request
  (`modules/accounts/permissions.py`).
- Not signed in → **401**. Not a member, or the organization does not exist → **404**
  (the same body in both cases, so other tenants' IDs cannot be probed). Member whose
  role is not listed for the method → **403**. Methods a view does not list are denied,
  even for owners.
- Organization IDs are random UUIDs, never sequential.
- The role the web app shows comes from the selected membership returned by the API.
  The UI hides actions a role cannot take, but the API is the only enforcement point.

## Threats and mitigations

| # | Threat (STRIDE) | Mitigation | Verified by |
|---|---|---|---|
| T1 | Member of org A reads or writes org B by changing the ID in the URL (information disclosure, tampering) | Membership lookup per request; non-members get 404 | `test_outsider_gets_404_for_every_endpoint`, `test_owner_of_a_cannot_rename_b`, `test_owner_of_a_cannot_list_b_members` |
| T2 | Low-privilege member performs an owner action (elevation of privilege) | Per-method `org_roles` table, deny unless listed | `test_role_matrix`, `test_unlisted_methods_are_denied_even_for_owners` |
| T3 | Session cookie stolen through XSS or sent over HTTP (spoofing) | `HttpOnly`, `SameSite=Lax`, `Secure` outside local HTTP development; 8-hour lifetime; no tokens in JavaScript or `localStorage` | `test_session_cookie_is_http_only_lax_and_secure` |
| T4 | A third-party site submits forms with the victim's cookie, including signing them in to an attacker's account (CSRF, login CSRF) | CSRF token required on every unsafe request, including `POST /auth/login` | `test_login_without_csrf_token_is_rejected` |
| T5 | Session fixation | Django rotates the session key and CSRF token on login | `test_login_rotates_the_session_key` |
| T6 | Account enumeration through login errors | One message for unknown email, wrong password and inactive user | `test_bad_credentials_get_one_generic_answer`, `test_inactive_users_cannot_sign_in` |
| T7 | Deactivated person keeps using an existing session | Memberships and sessions only count for active users | `test_deactivated_user_loses_access` |
| T8 | Open redirect through `/sign-in?next=` after an expired session | `safeNextPath` accepts only same-app paths | `apps/web/src/auth/session.test.ts` |
| T9 | Personal data copied into logs, shell output, CI logs and support tickets (information disclosure) | Emails masked (`l***@lumen.example`) by a filter on the console log handler, in `Membership.__str__` and in `seed_demo_orgs` output | `tests/test_masking.py` |
| T10 | Known demo passwords end up in a shared environment | `seed_demo_orgs` refuses to run unless `DEBUG` is on; the password comes from `.env` (random per machine), never from the repository | `test_seed_refuses_to_run_without_debug`, `test_seed_rejects_weak_or_missing_passwords` |
| T11 | Weak or reused passwords | Minimum 12 characters, common-password and numeric-only checks; scrypt hashing | `AUTH_PASSWORD_VALIDATORS`, `PASSWORD_HASHERS` |
| T12 | Schema drift: a model change ships without its migration, or a migration cannot be rolled back | CI `migrations` job on PostgreSQL: `makemigrations --check`, migrate, roll back, re-apply, seed twice | `.github/workflows/ci.yml` |

## Known gaps (accepted for now)

- **No login rate limiting or lockout.** Password guessing is only slowed by scrypt.
  Planned before any deployment outside a laptop: per-IP and per-account throttling.
- **No MFA and no password reset flow.** Demo accounts only; both are on the backlog.
- **No audit log of membership and role changes.** Arrives with the audit trail work.
- **ai-api is unauthenticated.** Acceptable only while it stays on the internal Compose
  network; service-to-service authentication is required before it is exposed.
- **Database-level isolation (row-level security) is not used.** Every new query must
  filter by organization; reviewers check this and new endpoints must be added to the
  permission matrix tests.

## Checklist for new organization-scoped endpoints

1. Subclass `OrganizationScopedView`, list every allowed method in `org_roles`.
2. Query through `self.organization`; never trust an organization ID from the body.
3. Add the endpoint to `MATRIX` in `tests/test_tenancy_permissions.py`; the shared
   fixtures in `tests/conftest.py` give one user per role plus an outsider.
4. Do not log request bodies or full email addresses.
