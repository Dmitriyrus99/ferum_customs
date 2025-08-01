#!/bin/bash
set -euo pipefail

echo "==> Ferum Customs entrypoint started"

cd /home/frappe/frappe-bench || { echo "No bench dir!"; exit 1; }

# fix permissions
chown -R frappe:frappe sites || true
chown -R frappe:frappe logs  || true

DB_HOST="${DB_HOST:-db}"
SITE_NAME="${SITE_NAME:-}"
INIT_LOCK_FILE="sites/${SITE_NAME}/.docker_site_initialized"

echo "==> Waiting for MariaDB..."
until mariadb -h "$DB_HOST" -P 3306 -uroot -p"${DB_ROOT_PASSWORD:-}" -e "SELECT 1" >/dev/null 2>&1; do
  echo "   ... still waiting"
  sleep 2
done
echo "==> MariaDB ready."

# idempotent site init
if [[ -n "$SITE_NAME" ]]; then
  if [[ ! -f "$INIT_LOCK_FILE" ]]; then
    echo "==> First-time init for site $SITE_NAME"

    mkdir -p "sites/${SITE_NAME}"

    if [[ ! -f "sites/${SITE_NAME}/site_config.json" ]]; then
      echo "==> Creating site $SITE_NAME"
      bench new-site --no-mariadb-socket \
        --admin-password "${ADMIN_PASSWORD:-}" \
        --mariadb-root-password "${DB_ROOT_PASSWORD:-}" \
        --db-host "${DB_HOST}" "${SITE_NAME}"
    else
      echo "==> site_config.json exists, skipping new-site"
    fi

    echo "==> Installing apps"
    bench --site "${SITE_NAME}" install-app erpnext || echo "erpnext already?"
    bench --site "${SITE_NAME}" install-app ferum_customs || echo "ferum_customs already?"

    touch "$INIT_LOCK_FILE"
  else
    echo "==> Site $SITE_NAME already initialized"
  fi

  echo "==> Running migrate"
  bench --site "${SITE_NAME}" migrate || true

  echo "==> Create rq users / enable scheduler"
  bench create-rq-users || true
  bench --site "${SITE_NAME}" enable-scheduler || true
  bench set-config -g default_site "${SITE_NAME}" || true
fi

# update common_site_config
COMMON_CFG="sites/common_site_config.json"
[ -f "$COMMON_CFG" ] || echo "{}" > "$COMMON_CFG"

python3 - <<'PY'
import json
import os

p = "sites/common_site_config.json"
with open(p) as f:
    try:
        cfg = json.load(f)
    except Exception:
        cfg = {}
cfg["redis_cache"] = os.environ.get("REDIS_CACHE", cfg.get("redis_cache"))
cfg["redis_queue"] = os.environ.get("REDIS_QUEUE", cfg.get("redis_queue"))
cfg["redis_socketio"] = os.environ.get("REDIS_SOCKETIO", cfg.get("redis_socketio"))
if os.environ.get("SITE_NAME"):
    cfg["default_site"] = os.environ["SITE_NAME"]
with open(p, "w") as f:
    json.dump(cfg, f, indent=2)
PY

chown frappe:frappe "$COMMON_CFG"

echo "==> bench set-config for redis"
bench set-config -g redis_cache    "${REDIS_CACHE:-}" || true
bench set-config -g redis_queue    "${REDIS_QUEUE:-}" || true
bench set-config -g redis_socketio "${REDIS_SOCKETIO:-}" || true

echo "==> Build assets (non-fatal)"
bench build || true

echo "==> Remove redis lines from Procfile (use external redis)"
sed -i '/redis_cache/d;/redis_queue/d;/redis_socketio/d' Procfile || true

echo "==> Starting CMD: $*"
exec "$@"
