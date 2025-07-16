#!/usr/bin/env bash
set -euo pipefail

# Скрипт для создания базы данных и пользователя в MariaDB/MySQL согласно site_config.json

# Ожидаемые переменные окружения:
#   SITE_NAME         - имя Frappe-сайта (подпапка в sites/)
#   DB_ROOT_PASSWORD  - пароль root для MySQL

if [[ -z "${SITE_NAME:-}" ]]; then
  echo "Ошибка: переменная SITE_NAME не задана" >&2
  exit 1
fi
if [[ -z "${DB_ROOT_PASSWORD:-}" ]]; then
  echo "Ошибка: переменная DB_ROOT_PASSWORD не задана" >&2
  exit 1
fi

SITE_CONFIG="sites/${SITE_NAME}/site_config.json"
if [[ ! -f "$SITE_CONFIG" ]]; then
  echo "Ошибка: site_config.json не найден: $SITE_CONFIG" >&2
  exit 1
fi

DB_NAME=$(jq -r '.db_name' "$SITE_CONFIG")
DB_PASS=$(jq -r '.db_password' "$SITE_CONFIG")

echo "Создаем базу данных и пользователя, если они отсутствуют..."
mysql -uroot -p"$DB_ROOT_PASSWORD" <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
CREATE USER IF NOT EXISTS '$DB_NAME'@'%' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_NAME'@'%';
FLUSH PRIVILEGES;
SQL

echo "✔ База данных и пользователь готовы: $DB_NAME"
