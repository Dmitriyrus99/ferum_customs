#!/usr/bin/env bash
set -euo pipefail

# Fix missing Frappe site DB and admin access

# Default inputs
SITE_NAME="${SITE_NAME:-erp.ferumrus.ru}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-}"

# Ensure required inputs are set
if [[ -z "${DB_ROOT_PASSWORD:-}" ]]; then
  echo "❌ DB_ROOT_PASSWORD is not set" >&2
  exit 1
fi
if [[ -z "${ADMIN_PASSWORD:-}" ]]; then
  echo "❌ ADMIN_PASSWORD is not set" >&2
  exit 1
fi

# Ensure required commands are available
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required but not installed" >&2
  exit 1
fi

# Determine DB name and password from site_config.json or defaults
SITE_CONFIG="sites/${SITE_NAME}/site_config.json"
if [[ -f "$SITE_CONFIG" ]]; then
  echo "✅ Found site_config.json for ${SITE_NAME}, extracting DB credentials..."
  DB_NAME=$(jq -r '.db_name' "$SITE_CONFIG")
  DB_PASSWORD=$(jq -r '.db_password' "$SITE_CONFIG")
else
  echo "ℹ site_config.json for ${SITE_NAME} not found, using defaults"
  DB_NAME="${SITE_NAME//./_}"
  DB_PASSWORD="${ADMIN_PASSWORD}" # Using ADMIN_PASSWORD as DB_PASSWORD for new site setup
fi
echo "✅ Using DB_NAME=${DB_NAME}"

# Create database and user if they don't exist
docker compose exec -T db mariadb -h db -P 3306 -uroot -p"$DB_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
CREATE USER IF NOT EXISTS '$DB_NAME'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_NAME'@'%';
FLUSH PRIVILEGES;
EOF
echo "✅ Ensured database and user exist"

# Check database connection
docker compose exec frappe bash -c "mysql -h db -u$DB_NAME -p$DB_PASSWORD -e 'SHOW DATABASES LIKE \"$DB_NAME\";'"
echo "✅ Database connection checked from Frappe container"

# Set admin password for the site
docker compose exec frappe bash -c "bench --site $SITE_NAME set-admin-password '$ADMIN_PASSWORD'"
echo "✅ Admin password set for ${SITE_NAME}"

echo "Скрипт завершен успешно."