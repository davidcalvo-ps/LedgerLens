# Demo accounts

Two fictional organizations for local development and walkthroughs. Every name and
address is invented; `.example` is a reserved domain, so no mail can be delivered.
Do not add real people, businesses or bank data to the demo set.

## Create them

```bash
scripts/dev.sh up      # if the stack is not running
scripts/dev.sh seed    # idempotent: safe to run again, resets the demo passwords
```

The seed command only runs when `DEBUG` is on (the local settings), so it cannot create
accounts with a known password on a shared server. All demo users share one password:
`LEDGERLENS_DEMO_PASSWORD` in your `.env`, generated randomly the first time
`scripts/dev.sh up` runs. To pick your own (at least 12 characters):

```bash
docker compose exec core-api python manage.py seed_demo_orgs --password 'your-own-pass-phrase'
```

The command prints emails masked (`l***@lumen.example`) because its output tends to end
up in CI logs and screenshots; the full list is below.

## Who is who

| Email | Organization | Role | Use it to see |
|---|---|---|---|
| `lucia@lumen.example` | Lumen Design Studio | owner | everything in one workspace, renaming it, the member list |
| `sara@lumen.example` | Lumen Design Studio | analyst | read-only access; owner actions answer 403 |
| `tomas@harbor.example` | Harbor Street Bakery | owner | the second tenant; Lumen's data answers 404 |
| `martin@books.example` | both | accountant | the workspace switcher and a different role per workspace |

Base currency is EUR for both organizations.

## Things to try

- Sign in as Martín, switch between the two workspaces and reload: the last workspace
  is remembered per browser.
- Sign in as Tomás and request `/api/v1/orgs/<lumen-id>/members/me`: 404, the same
  answer as for an ID that does not exist.
- Sign in as Sara and `PATCH /api/v1/orgs/<lumen-id>`: 403.
- Delete the `ledgerlens_session` cookie and click any page: you are sent to sign-in
  with a notice and returned to the same page afterwards.

## Resetting

`scripts/dev.sh reset` deletes the PostgreSQL volume, which removes the demo accounts
along with everything else. Run `up` and `seed` again afterwards.

See also the [identity threat model](../security/identity-threat-model.md).
