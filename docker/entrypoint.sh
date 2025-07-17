#!/bin/bash
set -euo pipefail

echo "Starting Ferum Customs Docker Entrypoint..."

# Initial delay to allow all services to start fully...
echo "Initial delay to allow all services to start fully..."
sleep 10

# Change to the bench directory
cd /home/frappe/frappe-bench

# Ensure correct permissions for the sites directory
echo "Setting correct permissions for sites directory..."
sudo chown -R frappe:frappe sites/

# More robust waiting for MariaDB
echo "Waiting for MariaDB service (port 3306) to be open..."
until bash -c "</dev/tcp/db/3306"; do
  echo "MariaDB port 3306 is not open yet - sleeping"
  sleep 5
done
echo "MariaDB port 3306 is open. Now waiting for database readiness..."

until mariadb -h db -P 3306 -uroot -p"${DB_ROOT_PASSWORD}" -e "SELECT 1"; do
  echo "MariaDB is not fully ready for connections - sleeping"
  sleep 5
done
echo "MariaDB is up - executing command"

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
  bench new-site --mariadb-root-password "${DB_ROOT_PASSWORD}" --db-host "${DB_HOST}" "${SITE_NAME}"

  echo "Installing ERPNext and Ferum Customs on ${SITE_NAME}..."
  bench --site "${SITE_NAME}" install-app erpnext
  bench --site "${SITE_NAME}" install-app ferum_customs
else
  echo "Site ${SITE_NAME} already exists or SITE_NAME not set. Skipping new site creation."
fi

# Ensure common_site_config.json exists
COMMON_SITE_CONFIG="/home/frappe/frappe-bench/sites/common_site_config.json"
if [[ ! -f "${COMMON_SITE_CONFIG}" ]]; then
  echo "common_site_config.json not found. Creating an empty one."
  echo "{}" > "${COMMON_SITE_CONFIG}"
  sudo chown frappe:frappe "${COMMON_SITE_CONFIG}"
fi

# Set Redis configs
echo "Setting Redis configurations..."
# --- ИЗМЕНЕНО: Использовать пароль Redis из переменной окружения ---
bench set-config -g redis_cache    "redis://:${REDIS_PASSWORD}@${REDIS_CACHE}"
bench set-config -g redis_queue    "redis://:${REDIS_PASSWORD}@${REDIS_QUEUE}"
bench set-config -g redis_socketio "redis://:${REDIS_PASSWORD}@${REDIS_SOCKETIO}"
echo "Redis configurations set."

# Execute the original Docker CMD (e.g., bench start)
echo "Executing original Docker command..."
exec "$@"
