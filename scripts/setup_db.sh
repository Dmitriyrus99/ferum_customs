#!/usr/bin/env bash
set -euo pipefail

# Script to create a database and user in MariaDB/MySQL according to site_config.json

# Expected environment variables:
#   SITE_NAME         - name of the Frappe site (subfolder in sites/)
#   DB_ROOT_PASSWORD  - root password for MySQL

if [[ -z "${SITE_NAME:-}" ]]; then
  echo "Error: SITE_NAME variable is not set" >&2
  exit 1
fi
if [[ -z "${DB_ROOT_PASSWORD:-}" ]]; then
  echo "Error: DB_ROOT_PASSWORD variable is not set" >&2
  exit 1
fi

SITE_CONFIG="sites/${SITE_NAME}/site_config.json"
if [[ ! -f "$SITE_CONFIG" ]]; then
  echo "Error: site_config.json not found: $SITE_CONFIG" >&2
  exit 1
fi

DB_NAME=$(jq -r '.db_name' "$SITE_CONFIG")
DB_PASS=$(jq -r '.db_password' "$SITE_CONFIG")

# Validate that db_name and db_password are not empty
if [[ -z "$DB_NAME" || -z "$DB_PASS" ]]; then
  echo "Error: db_name or db_password is not set in site_config.json" >&2
  exit 1
fi

echo "Creating database and user if they do not exist..."
mysql -uroot -p"$DB_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_NAME//\'/\'\\\'\' }\`;
CREATE USER IF NOT EXISTS '${DB_NAME//\'/\'\\\'\' }'@'%' IDENTIFIED BY '${DB_PASS//\'/\'\\\'\' }';
GRANT SELECT, INSERT, UPDATE, DELETE ON \`${DB_NAME//\'/\'\\\'\' }\`.* TO '${DB_NAME//\'/\'\\\'\' }'@'%';
FLUSH PRIVILEGES;
SQL

echo "✔ Database and user are ready: $DB_NAME"
