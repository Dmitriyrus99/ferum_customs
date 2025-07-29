#!/usr/bin/env bash
set -euo pipefail

# Пост-инсталляционные проверки для bare-metal установки
if [[ $# -ne 1 ]]; then
  echo "Использование: $(basename "$0") <site_name>"
  exit 1
fi
SITE_NAME="$1"

echo "== Проверка сервисов MariaDB и Redis =="
systemctl is-active --quiet mariadb || { echo "❌ MariaDB не запущен"; exit 1; }
systemctl is-active --quiet redis-server || { echo "❌ Redis не запущен"; exit 1; }
echo "✅ MariaDB и Redis запущены"

echo "== Проверка Pydantic settings =="
if ! python3 - << 'PYCODE'
import sys
from ferum_customs.config.settings import settings
print(settings.model_dump())
PYCODE
then
  echo "❌ Не удалось загрузить Pydantic settings" >&2
  exit 1
fi
echo "✅ Pydantic settings загружены"

echo "== Выполнение bench миграций, сборки и перезапуска =="
bench --site "$SITE_NAME" migrate
bench build
bench restart
echo "✅ Bench миграции, сборка и перезапуск выполнены"

echo "=== Пост-инсталляционные проверки пройдены успешно ==="
