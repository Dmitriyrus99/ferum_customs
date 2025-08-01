#!/usr/bin/env bash
# Quick start helper for bare-metal installation and launch without Docker
set -euo pipefail

# 1. Install system dependencies
if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root or via sudo"
  exit 1
fi

apt update
apt install -y mariadb-server redis-server python3-dev python3-venv python3-pip nodejs npm

# Optionally install yarn for frontend asset builds
if command -v npm >/dev/null 2>&1; then
  npm install --global yarn
fi

systemctl enable --now mariadb redis-server

# 2. Configure MariaDB root user
MYSQL_ROOT_PWD="${DB_ROOT_PASSWORD:-}"
if [[ -z "$MYSQL_ROOT_PWD" ]]; then
  read -s -p "Enter desired MariaDB root password: " MYSQL_ROOT_PWD
  echo
fi

# Securely set the MariaDB root password
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PWD}'; FLUSH PRIVILEGES;"

# 3. Install bench CLI
if command -v pipx >/dev/null 2>&1; then
  pipx install frappe-bench
else
  python3 -m venv ~/bench-env
  source ~/bench-env/bin/activate
  pip install frappe-bench
fi

# 4. Initialize bench directory
if [ -d "frappe-bench" ]; then
  echo "frappe-bench directory already exists. Please remove it or choose a different directory."
  exit 1
fi

bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# 5. Create new site
SITE_NAME="${SITE_NAME:-}"
if [[ -z "$SITE_NAME" ]]; then
  read -p "Enter Frappe site name (e.g. site1.local): " SITE_NAME
fi

ADMIN_PWD="${ADMIN_PASSWORD:-}"
if [[ -z "$ADMIN_PWD" ]]; then
  read -s -p "Enter Frappe Administrator password: " ADMIN_PWD
  echo
fi

bench new-site "$SITE_NAME" --admin-password "$ADMIN_PWD" --db-root-password "$MYSQL_ROOT_PWD"

# 6. Fetch and install ferum_customs app
bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
bench --site "$SITE_NAME" install-app ferum_customs

# 7. Build assets and restart bench
bench build
bench restart

# 8. Post-installation checks
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$SCRIPT_DIR/check_bare_metal_status.sh" "$SITE_NAME"
echo "Installation complete. Application available at http://localhost:8000"
