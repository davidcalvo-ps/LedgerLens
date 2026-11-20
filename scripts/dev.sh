#!/usr/bin/env bash
# Local development helper for LedgerLens.
#
#   scripts/dev.sh up      create .env if missing, build and start the whole stack, wait for health
#   scripts/dev.sh web     install web dependencies and run the React dev server
#   scripts/dev.sh seed    create the two demo organizations and their users (idempotent)
#   scripts/dev.sh check   run lint and unit tests for the web app and both Python services
#   scripts/dev.sh down    stop the stack (data volumes are kept)
#   scripts/dev.sh reset   delete the local PostgreSQL and Redis volumes (asks first)
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
env_file="$root/.env"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "error: '$1' not found; install $2 first (see docs/setup/getting-started.md)" >&2
    exit 1
  fi
}

random_hex() {
  od -An -N"$1" -tx1 /dev/urandom | tr -d ' \n'
}

# Creates .env on first run with a random PostgreSQL password, Django secret key and
# demo-user password.
ensure_env() {
  if [[ ! -f "$env_file" ]]; then
    sed -e "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$(random_hex 18)/" \
      -e "s/^DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$(random_hex 32)/" \
      -e "s/^LEDGERLENS_DEMO_PASSWORD=.*/LEDGERLENS_DEMO_PASSWORD=demo-$(random_hex 8)/" \
      "$root/.env.example" >"$env_file"
    chmod 600 "$env_file"
    echo "Created .env with random PostgreSQL, Django and demo-user secrets."
  fi
}

compose() {
  docker compose --project-directory "$root" --env-file "$env_file" "$@"
}

cmd_up() {
  need docker "Docker with the Compose plugin"
  ensure_env
  echo "Building and starting PostgreSQL, Redis, core-api and ai-api..."
  compose up -d --build --wait
  local port
  port="$(grep -E '^CORE_API_PORT=' "$env_file" | cut -d= -f2)"
  port="${port:-8000}"
  echo "Stack is healthy:"
  curl -fsS "http://127.0.0.1:$port/api/v1/health/ready" && echo
  echo "Next: scripts/dev.sh web, then open http://localhost:5173"
}

cmd_web() {
  need pnpm "pnpm (corepack enable)"
  cd "$root"
  pnpm install
  exec pnpm dev
}

# Runs the same steps as CI. Python checks use a throwaway virtualenv per service.
cmd_check() {
  need pnpm "pnpm (corepack enable)"
  need python3 "Python 3.12"
  cd "$root"
  pnpm install
  pnpm lint
  pnpm typecheck
  pnpm test

  local service venv
  for service in core-api ai-api; do
    echo "== services/$service"
    venv="$root/services/$service/.venv"
    [[ -d "$venv" ]] || python3 -m venv "$venv"
    "$venv/bin/pip" install --quiet -r "$root/services/$service/requirements-dev.txt"
    (cd "$root/services/$service" && "$venv/bin/ruff" check . && "$venv/bin/pytest" -q)
  done
}

cmd_seed() {
  need docker "Docker with the Compose plugin"
  ensure_env
  compose exec -T core-api python manage.py seed_demo_orgs
  echo "Demo password: LEDGERLENS_DEMO_PASSWORD in .env"
}

cmd_down() {
  need docker "Docker with the Compose plugin"
  ensure_env
  compose down
}

cmd_reset() {
  need docker "Docker with the Compose plugin"
  ensure_env
  read -r -p "Delete the local LedgerLens database and Redis data? [y/N] " answer
  if [[ "$answer" == [yY] ]]; then
    compose down -v
    echo "Removed. Run scripts/dev.sh up to start again."
  fi
}

case "${1:-}" in
  up) cmd_up ;;
  web) cmd_web ;;
  seed) cmd_seed ;;
  check) cmd_check ;;
  down) cmd_down ;;
  reset) cmd_reset ;;
  *)
    sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac
