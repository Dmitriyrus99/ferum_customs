#!/bin/bash
set -euo pipefail

echo "Starting Ferum Customs Docker Entrypoint..."

# Change to the bench directory
cd /home/frappe/frappe-bench

# Ensure correct permissions for the sites directory
# This is crucial for preventing "Permission denied" errors
echo "Setting correct permissions for sites directory..."
sudo chown -R frappe:frappe sites/

# Ensure apps.txt exists and includes ferum_customs and erpnext
SITE_APPS_FILE="sites/apps.txt"
if [[ ! -f "${SITE_APPS_FILE}" ]]; then
  echo "frappe" > "${SITE_APPS_FILE}"
  echo "erpnext" >> "${SITE_APPS_FILE}"
  echo "ferum_customs" >> "${SITE_APPS_FILE}"
fi

# Create site if it doesn't exist
if [[ -n "${SITE_NAME}" && ! -d "sites/${SITE_NAME}" ]]; then
  echo "Creating new Frappe site: ${SITE_NAME}..."
  bench new-site --no-mariadb-socket "${SITE_NAME}" \
       --admin-password "${ADMIN_PASSWORD}" \
       --mariadb-root-password "${DB_ROOT_PASSWORD}" \
       --db-host "${DB_HOST}"

  echo "Installing ERPNext and Ferum Customs on ${SITE_NAME}..."
  bench --site "${SITE_NAME}" install-app erpnext
  bench --site "${SITE_NAME}" install-app ferum_customs
else
  echo "Site ${SITE_NAME} already exists or SITE_NAME not set."
fi

# Set Redis configs
bench set-config -g redis_cache    "${REDIS_CACHE}"
bench set-config -g redis_queue    "${REDIS_QUEUE}"
bench set-config -g redis_socketio "${REDIS_SOCKETIO}"

# Execute the original Docker CMD (e.g., bench start)
exec "$@"
