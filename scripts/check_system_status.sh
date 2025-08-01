#!/usr/bin/env bash
set -euo pipefail

# System Status Check for Ferum Customizations

check_service() {
  local service_name=$1
  if ! systemctl is-active --quiet "$service_name"; then
    echo "❌ $service_name не запущен" >&2
    exit 1
  fi
}

check_env_file() {
  if [[ ! -f .env ]]; then
    echo "❌ Файл .env отсутствует" >&2
    exit 1
  fi
}

check_pydantic_settings() {
  if ! python3 - <<'PYCODE'
import sys
from ferum_customs.config.settings import settings
print(settings.model_dump())
PYCODE
  then
    echo "❌ Не удалось загрузить Pydantic settings" >&2
    exit 1
  fi
}

check_docker_compose() {
  if ! docker compose config >/dev/null; then
    echo "❌ Docker Compose config не валиден" >&2
    exit 1
  fi
}

run_bench_commands() {
  docker compose exec backend bench migrate
  docker compose exec backend bench build
  docker compose exec backend bench restart
}

echo "== Проверка сервисов MySQL и Redis =="
check_service mysql
check_service redis
echo "✅ MySQL и Redis запущены"

echo "== Проверка наличия и загрузки .env =="
check_env_file
check_pydantic_settings
echo "✅ .env и Pydantic settings загружены"

echo "== Проверка конфигурации Docker Compose =="
check_docker_compose
echo "✅ Docker Compose config валиден"

echo "== Выполнение bench-команд в контейнере backend =="
run_bench_commands
echo "✅ Bench миграции, сборка и перезапуск выполнены"
