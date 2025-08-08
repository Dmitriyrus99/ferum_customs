#!/bin/bash
set -euo pipefail

: "${DB_HOST:?DB_HOST not set}"
: "${POSTGRES_USER:?POSTGRES_USER not set}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}"

export PGPASSWORD=$POSTGRES_PASSWORD

echo "==> Waiting for PostgreSQL..."

until psql -h "$DB_HOST" -U "$POSTGRES_USER" -c '\q' 2>/dev/null; do
  echo "   ... still waiting for $DB_HOST"
  sleep 30
done

echo "==> PostgreSQL is ready."
