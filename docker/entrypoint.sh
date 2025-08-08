#!/bin/bash
set -euo pipefail

/usr/local/bin/wait_for_db.sh

cd /home/frappe/frappe-bench || { echo "No bench dir!"; exit 1; }

# Fix permissions
chown -R frappe:frappe sites logs || true

INIT_LOCK_FILE="sites/${SITE_NAME}/.docker_site_initialized"

# Idempotent site init
if [[ -n "$SITE_NAME" ]]; then
  if [[ ! -f "$INIT_LOCK_FILE" ]]; then
    echo "==> First-time init for site $SITE_NAME"

    mkdir -p "sites/${SITE_NAME}"

    if [[ ! -f "sites/${SITE_NAME}/site_config.json" ]]; then
      echo "==> Creating site $SITE_NAME"
      bench new-site --no-mariadb-socket \
        --admin-password "$ADMIN_PASSWORD" \
        --db-type postgres \
        --db-host "$DB_HOST" \
        --db-user "${POSTGRES_USER:-erp_user}" \
        --db-password "$POSTGRES_PASSWORD" \
        "$SITE_NAME"
    else
      echo "==> site_config.json exists, skipping new-site"
    fi

    echo "==> Installing apps"
    bench --site "$SITE_NAME" install-app erpnext || echo "erpnext already installed"
    bench --site "$SITE_NAME" install-app ferum_customs || echo "ferum_customs already installed"

    touch "$INIT_LOCK_FILE"
  else
    echo "==> Site $SITE_NAME already initialized"
  fi

  echo "==> Running migrate"
  bench --site "$SITE_NAME" migrate || true

  echo "==> Create rq users / enable scheduler"
  bench create-rq-users || true
  bench --site "$SITE_NAME" enable-scheduler || true
  bench set-config -g default_site "$SITE_NAME" || true
  bench --site "$SITE_NAME" set-config -g enable_two_factor_auth 1 || true
  bench --site "$SITE_NAME" set-config -g sentry_dsn "${SENTRY_DSN}" || true
  bench --site "$SITE_NAME" set-config -g enable_prometheus 1 || true
fi

echo "==> Starting CMD: bench start"
exec bench start