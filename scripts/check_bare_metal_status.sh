#!/usr/bin/env bash
set -euo pipefail

# Post-installation checks for bare-metal installation
# Author: [Your Name]
# Date: [Creation Date]
# This script checks the status of services and performs necessary migrations.

if [[ $# -ne 1 ]]; then
  echo "Usage: $(basename "$0") <site_name>"
  exit 1
fi

SITE_NAME="$1"

# Check if the site name is valid (basic validation)
if [[ ! "$SITE_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "❌ Invalid site name. Only alphanumeric characters, underscores, and hyphens are allowed." >&2
  exit 1
fi

echo "== Checking MariaDB and Redis services =="
systemctl is-active --quiet mariadb || { echo "❌ MariaDB is not running"; exit 1; }
systemctl is-active --quiet redis-server || { echo "❌ Redis is not running"; exit 1; }
echo "✅ MariaDB and Redis are running"

echo "== Checking Pydantic settings =="
if ! python3 - << 'PYCODE'
import sys
from ferum_customs.config.settings import settings
print(settings.model_dump())
PYCODE
then
  echo "❌ Failed to load Pydantic settings" >&2
  exit 1
fi
echo "✅ Pydantic settings loaded"

echo "== Running bench migrations, build, and restart =="
bench --site "$SITE_NAME" migrate
bench build
bench restart
echo "✅ Bench migrations, build, and restart completed"

echo "=== Post-installation checks completed successfully ==="
