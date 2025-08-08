#!/bin/bash
set -euo pipefail

: "${DB_HOST:?DB_HOST not set}"
: "${POSTGRES_USER:?POSTGRES_USER not set}"

echo "==> Waiting for PostgreSQL..."

until pg_isready -h "$DB_HOST" -p 5432 -U "$POSTGRES_USER" >/dev/null 2>&1; do
  echo "   ... still waiting for $DB_HOST"
  sleep 2
done

echo "==> PostgreSQL is ready."
