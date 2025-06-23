#!/bin/bash

# ====================================================================================
# Улучшенный скрипт для установки и развертывания ERPNext с использованием Docker
#
# Этот скрипт автоматизирует процесс, описанный в официальной документации
# репозитория frappe/frappe_docker, и адаптирован под конфигурацию
# вашего проекта ferum_customs.
# ====================================================================================

set -e

# --- Переменные конфигурации ---
GIT_REPO="https://github.com/frappe/frappe_docker.git"
PROJECT_DIR="frappe_docker"
SITE_NAME=${SITE_NAME:-"dev.localhost"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"admin"}
FRAPPE_VERSION="v15"
ERPNext_VERSION="v15"

# --- Функция для определения команды docker compose ---
if docker compose version &> /dev/null; then
  DC_COMMAND="docker compose"
else
  DC_COMMAND="docker-compose"
fi

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
$DC_COMMAND -f pwd.yml exec frappe bench new-site "${SITE_NAME}" --no-mariadb-socket --mariadb-root-password 123 --admin-password "${ADMIN_PASSWORD}"
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось создать новый сайт."
    exit 1
fi

echo "Установка Frappe версии ${FRAPPE_VERSION}..."
$DC_COMMAND -f pwd.yml exec frappe bench get-app --branch "${FRAPPE_VERSION}" frappe
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось загрузить Frappe."
    exit 1
fi

echo "Установка ERPNext версии ${ERPNext_VERSION}..."
$DC_COMMAND -f pwd.yml exec frappe bench get-app --branch "${ERPNext_VERSION}" erpnext
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось загрузить ERPNext."
    exit 1
fi

echo "Установка приложения ERPNext на сайт ${SITE_NAME}..."
$DC_COMMAND -f pwd.yml exec frappe bench --site "${SITE_NAME}" install-app erpnext
if [ $? -ne 0 ]; then
    echo "Ошибка: Не удалось установить приложение ERPNext на сайт."
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
echo "Для остановки окружения используйте: $DC_COMMAND -f pwd.yml down"

