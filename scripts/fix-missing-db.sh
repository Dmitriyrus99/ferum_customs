#!/usr/bin/env bash
set -euo pipefail

# Fix missing Frappe site DB and admin access

# Default inputs
SITE="${SITE:-erp.ferumrus.ru}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-fFeRu1011#f}"

# Ensure MYSQL_ROOT_PASSWORD is set
if [[ -z "${MYSQL_ROOT_PASSWORD:-}" ]]; then
  echo "❌ MYSQL_ROOT_PASSWORD is not set" >&2
  exit 1
fi

# Ensure required commands are available
if ! command -v jq >/dev/null 2>&1; then
  echo "❌ jq is required but not installed" >&2
  exit 1
fi

# Detect Docker Compose command
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  DC="docker-compose"
else
  echo "❌ Docker Compose not found (requires 'docker compose' or 'docker-compose')" >&2
  exit 1
fi

# Load DB name and password from site_config.json
SITE_CONFIG="sites/${SITE}/site_config.json"
if [[ ! -f "$SITE_CONFIG" ]]; then
  echo "❌ site_config.json not found: $SITE_CONFIG" >&2
  exit 1
fi

DB_NAME=$(jq -r '.db_name' "$SITE_CONFIG")
DB_PASSWORD=$(jq -r '.db_password' "$SITE_CONFIG")

if [[ -z "$DB_NAME" || "$DB_NAME" == "null" ]]; then
  echo "❌ db_name not found in site_config.json" >&2
  exit 1
fi

echo "✅ Loaded DB_NAME: $DB_NAME"

# Create database and user if they don't exist
${DC} -f frappe_docker/pwd.yml exec -T db mariadb -uroot -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
CREATE USER IF NOT EXISTS '$DB_NAME'@'%' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_NAME'@'%';
FLUSH PRIVILEGES;
EOF

echo "✅ Ensured database and user exist"

# Check database connection
${DC} -f frappe_docker/pwd.yml exec backend bash -c "mysql -h db -u$DB_NAME -p$DB_PASSWORD -e 'SHOW TABLES IN \`$DB_NAME\`;'"

echo "✅ Connection to database confirmed"

# Set admin password for the site
${DC} -f frappe_docker/pwd.yml exec backend bash -c "bench --site $SITE set-admin-password $ADMIN_PASSWORD"

echo "✅ Admin password updated for site '$SITE'"
