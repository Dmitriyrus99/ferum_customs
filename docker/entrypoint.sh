#!/usr/bin/env bash
set -e

# Unified Docker entrypoint for Frappe bench
cd /home/frappe/frappe-bench

# 1. apps.txt
SITE_APPS_FILE="sites/apps.txt"
if [[ ! -f "${SITE_APPS_FILE}" ]]; then
  echo "frappe" > "${SITE_APPS_FILE}"
  if [[ -n "${INSTALL_APPS}" ]]; then
    IFS=',' read -ra ADD_APPS <<< "${INSTALL_APPS}"
    for app in "${ADD_APPS[@]}"; do
      echo "$app" >> "${SITE_APPS_FILE}"
    done
  fi
fi

# 2. Create site if not exists
if [[ -n "${SITE_NAME}" && ! -d "sites/${SITE_NAME}" ]]; then
  bench new-site --no-mariadb-socket "${SITE_NAME}" \
       --admin-password "${ADMIN_PASSWORD}" \
       --mariadb-root-password "${DB_ROOT_PASSWORD}" \
       --db-host "${DB_HOST}"
  if [[ -n "${INSTALL_APPS}" ]]; then
    IFS=',' read -ra ADD_APPS <<< "${INSTALL_APPS}"
    for app in "${ADD_APPS[@]}"; do
      bench --site "${SITE_NAME}" install-app "$app"
    done
  fi
fi

# 3. Redis config
bench set-config -g redis_cache    "${REDIS_CACHE}"
bench set-config -g redis_queue    "${REDIS_QUEUE}"
bench set-config -g redis_socketio "${REDIS_SOCKETIO}"

exec "$@"
