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

## Remove any pre-existing site directory to ensure clean setup
if [[ -n "${SITE_NAME}" && -d "sites/${SITE_NAME}" ]]; then
  echo "Removing pre-existing site directory: ${SITE_NAME}"
  rm -rf "sites/${SITE_NAME}"
fi

# Create site if it hasn't been configured yet
if [[ -n "${SITE_NAME}" && ! -f "sites/${SITE_NAME}/site_config.json" ]]; then
  echo "Creating new Frappe site: ${SITE_NAME}..."
  bench new-site --admin-password "${ADMIN_PASSWORD}" \
           --mariadb-root-password "${DB_ROOT_PASSWORD}" \
           --db-host "${DB_HOST}" "${SITE_NAME}"

  echo "Installing ERPNext and Ferum Customs on ${SITE_NAME}..."
  bench --site "${SITE_NAME}" install-app erpnext
  bench --site "${SITE_NAME}" install-app ferum_customs
else
  echo "Site ${SITE_NAME} already exists or already configured. Skipping site creation."
fi

# Ensure common_site_config.json exists
COMMON_SITE_CONFIG="/home/frappe/frappe-bench/sites/common_site_config.json"
# Ensure common_site_config.json exists and has initial Redis URLs to avoid CLI bootstrap errors
if [[ ! -f "${COMMON_SITE_CONFIG}" ]]; then
  echo "common_site_config.json not found. Creating an empty one."
  echo "{}" > "${COMMON_SITE_CONFIG}"
  sudo chown frappe:frappe "${COMMON_SITE_CONFIG}"
fi
# Populate or update Redis URL entries in common_site_config.json
cache_url=$(eval echo "\"$REDIS_CACHE\"")
queue_url=$(eval echo "\"$REDIS_QUEUE\"")
socketio_url=$(eval echo "\"$REDIS_SOCKETIO\"")
python3 - <<PYCODE
import json
path = "${COMMON_SITE_CONFIG}"
cfg = json.load(open(path))
cfg["redis_cache"] = "${cache_url}"
cfg["redis_queue"] = "${queue_url}"
cfg["redis_socketio"] = "${socketio_url}"
# Set default site for HTTP routing
cfg["default_site"] = "${SITE_NAME}"
json.dump(cfg, open(path, "w"), indent=2)
PYCODE
sudo chown frappe:frappe "${COMMON_SITE_CONFIG}"

# Set Redis configs
echo "Setting Redis configurations..."
## Используем полные URL из переменных окружения
cache_url=$(eval echo "\"$REDIS_CACHE\"")
queue_url=$(eval echo "\"$REDIS_QUEUE\"")
socketio_url=$(eval echo "\"$REDIS_SOCKETIO\"")
bench set-config -g redis_cache    "$cache_url"
bench set-config -g redis_queue    "$queue_url"
bench set-config -g redis_socketio "$socketio_url"
echo "Redis configurations set."

# Execute the original Docker CMD (e.g., bench start)
echo "Executing original Docker command..."
# Disable internal Redis processes in Procfile so bench start uses external Redis services
sed -i '/redis_cache/d;/redis_queue/d;/redis_socketio/d' Procfile
exec "$@"
