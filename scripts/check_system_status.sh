#!/usr/bin/env bash
set -euo pipefail

# Проверка статуса системы Ferum Customizations

echo "== Проверка сервисов MySQL и Redis =="
systemctl is-active --quiet mysql || { echo "❌ MySQL не запущен"; exit 1; }
systemctl is-active --quiet redis || { echo "❌ Redis не запущен"; exit 1; }
echo "✅ MySQL и Redis запущены"

echo "== Проверка наличия и загрузки .env =="
if [[ ! -f .env ]]; then
  echo "❌ Файл .env отсутствует" >&2
  exit 1
fi
if ! python3 - <<'PYCODE'
import sys
from ferum_customs.config.settings import settings
print(settings.model_dump())
PYCODE
then
  echo "❌ Не удалось загрузить Pydantic settings" >&2
  exit 1
fi
echo "✅ .env и Pydantic settings загружены"

echo "== Проверка конфигурации Docker Compose =="
docker compose config >/dev/null
echo "✅ Docker Compose config валиден"

echo "== Выполнение bench-команд в контейнере backend =="
docker compose exec backend bench migrate
docker compose exec backend bench build
docker compose exec backend bench restart
echo "✅ Bench миграции, сборка и перезапуск выполнены"
