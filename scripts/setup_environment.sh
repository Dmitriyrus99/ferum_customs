#!/bin/bash
# This script sets up a Frappe/ERPNext bench with the ferum_customs app.

set -euo pipefail

APP_REPO="https://github.com/Dmitriyrus99/ferum_customs.git"
APP_BRANCH="main"
ERPNEXT_REPO="https://github.com/frappe/erpnext"
ERPNEXT_BRANCH="version-16"

SITE_NAME="${SITE_NAME:-test_site}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-root}"

if ! command -v bench >/dev/null; then
    echo "Error: bench command not found. Please install Frappe bench first." >&2
    exit 1
fi

# Get apps
bench get-app "$APP_REPO" --branch "$APP_BRANCH"
bench get-app erpnext --branch "$ERPNEXT_BRANCH" "$ERPNEXT_REPO"

# Create a new site and install applications
bench new-site "$SITE_NAME" \
    --admin-password "$ADMIN_PASSWORD" \
    --mariadb-root-password "$DB_ROOT_PASSWORD"

bench --site "$SITE_NAME" install-app erpnext
bench --site "$SITE_NAME" install-app ferum_customs

# Build assets and restart bench
bench build && bench restart

echo "ferum_customs installed successfully on site '$SITE_NAME'."

