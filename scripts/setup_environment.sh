#!/bin/bash

# ====================================================================================
# Улучшенный скрипт для установки и развертывания ERPNext с использованием Docker
#
# Этот скрипт автоматизирует процесс, описанный в официальной документации
# репозитория frappe/frappe_docker, и адаптирован под конфигурацию
# вашего проекта ferum_customs.
# ====================================================================================

# Shell settings
set -eo pipefail
# Check for Docker systemd proxy settings
if [ -d "/etc/systemd/system/docker.service.d" ] && ls /etc/systemd/system/docker.service.d/*proxy*.conf &>/dev/null; then
    echo "Ошибка: в настройках Docker systemd обнаружен прокси (http-proxy.conf)."
    echo "Пожалуйста, удалите или переименуйте этот файл и перезапустите службу Docker:" \
         "sudo systemctl daemon-reload && sudo systemctl restart docker"
    exit 1
fi
# --- Переменные конфигурации ---
GIT_REPO="https://github.com/frappe/frappe_docker.git"
PROJECT_DIR="frappe_docker"
SITE_NAME=${SITE_NAME:-"dev.localhost"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin"}
FRAPPE_VERSION="v15"
ERPNext_VERSION="v15"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(dirname "$SCRIPT_DIR")"
FERUM_CUSTOMS_PATH="${FERUM_CUSTOMS_PATH:-$APP_ROOT}"

# --- Функция для определения команды docker compose ---
if docker compose version &> /dev/null; then
  DC_COMMAND="docker compose"
else
  DC_COMMAND="docker-compose"
fi

# --- Проверка и загрузка .env файла ---
if [ -f .env ]; then
  echo "Найден .env файл, загружаем переменные..."
  export $(grep -v '^#' .env | xargs)
else
  echo "Ошибка: .env файл не найден."
  echo "Пожалуйста, скопируйте .env.example в .env и заполните его перед запуском."
  exit 1
fi

# Проверяем, что ключевые переменные загружены
if [ -z "${ADMIN_PASSWORD}" ] || [ -z "${DB_ROOT_PASSWORD}" ]; then
    echo "Ошибка: Переменные ADMIN_PASSWORD или DB_ROOT_PASSWORD не установлены в .env файле."
    exit 1
fi

echo "Переменные окружения успешно загружены."
echo "---"

echo "Начало установки ERPNext (Frappe/ERPNext ${FRAPPE_VERSION}) с использованием Docker..."
echo "Будет создан сайт: ${SITE_NAME}"
echo "Пароль администратора: ${ADMIN_PASSWORD}"
echo "---"

# --- Этап 1: Подготовка окружения ---
echo "--> Этап 1: Клонирование репозитория frappe_docker и настройка..."

if [ -d "$PROJECT_DIR" ]; then
  echo "Директория '$PROJECT_DIR' уже существует. Пропускаем клонирование."
else
  echo "Клонирование репозитория из '$GIT_REPO'..."
  git clone "$GIT_REPO" "$PROJECT_DIR"
  if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось клонировать репозиторий. Убедитесь, что Git установлен."
    exit 1
  fi
fi

cd "$PROJECT_DIR" || { echo "Ошибка: Не удалось перейти в директорию '$PROJECT_DIR'."; exit 1; }

echo "Репозиторий готов."
echo "---"

# --- Этап 2: Запуск контейнеров ---
echo "--> Этап 2: Запуск Docker-контейнеров для разработки..."
echo "⚠️ Убедитесь, что в настройках Docker Desktop или файле systemd для демона Docker не указан прокси (например localhost:1080), иначе будет ошибка при загрузке образов."
$DC_COMMAND -f pwd.yml up -d
if [ $? -ne 0 ]; then
  echo "Ошибка: Не удалось запустить Docker-контейнеры. Проверьте установку Docker."
  exit 1
fi

echo "Контейнеры успешно запущены в фоновом режиме."
echo "---"

# --- Этап 3: Создание сайта и установка приложений ---
echo "--> Этап 3: Создание нового сайта и установка ERPNext..."
echo "Это может занять значительное время..."

echo "Создание сайта ${SITE_NAME}..."
$DC_COMMAND -f pwd.yml exec backend bench new-site "${SITE_NAME}" --no-mariadb-socket --mariadb-root-password "${DB_ROOT_PASSWORD}" --admin-password "${ADMIN_PASSWORD}"
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось создать новый сайт."
    exit 1
fi

echo "Установка Frappe версии ${FRAPPE_VERSION}..."
$DC_COMMAND -f pwd.yml exec backend bench get-app --branch "${FRAPPE_VERSION}" frappe
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось загрузить Frappe."
    exit 1
fi

echo "Установка ERPNext версии ${ERPNext_VERSION}..."
$DC_COMMAND -f pwd.yml exec backend bench get-app --branch "${ERPNext_VERSION}" erpnext
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось загрузить ERPNext."
    exit 1
fi

echo "Установка приложения ERPNext на сайт ${SITE_NAME}..."
$DC_COMMAND -f pwd.yml exec backend bench --site "${SITE_NAME}" install-app erpnext
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось установить приложение ERPNext на сайт."
    exit 1
fi

echo "Добавление и установка приложения ferum_customs..."
$DC_COMMAND -f pwd.yml exec backend bench get-app "$FERUM_CUSTOMS_PATH"
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось добавить приложение ferum_customs."
    exit 1
fi

$DC_COMMAND -f pwd.yml exec backend bench --site "${SITE_NAME}" install-app ferum_customs
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось установить приложение ferum_customs."
    exit 1
fi

echo "Сайт и приложения успешно установлены."
echo "---"

# --- Завершение ---
echo "=========================================="
echo "Установка ERPNext успешно завершена!"
echo "=========================================="
echo
echo "Приложение доступно по адресу: http://${SITE_NAME}:8000"
echo "(Если вы используете Linux, возможно, потребуется добавить '${SITE_NAME}' в ваш /etc/hosts файл, указав на 127.0.0.1)"
echo
echo "Данные для входа:"
echo "  Пользователь: Administrator"
echo "  Пароль:       ${ADMIN_PASSWORD}"
echo
echo "Для просмотра логов используйте: $DC_COMMAND -f pwd.yml logs -f"
