# ======================================================================================
# Dockerfile для разработки приложения "ferum_customs" на Frappe v15
# Версия 4: Используем готовый к работе образ erpnext-worker
# ======================================================================================

# 1. Используем официальный, полноценный образ ERPNext v15.
# Этот образ уже содержит Frappe, ERPNext, bench и все системные зависимости.
# Bench уже инициализирован, и сайт 'frontend' создан.
FROM frappe/erpnext-worker:v15

# 2. Переключаемся на пользователя root для установки дополнительных пакетов (опционально).
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    # vim или nano для редактирования файлов внутри контейнера
    vim \
    # git для работы с репозиториями напрямую из контейнера
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Переключаемся обратно на стандартного пользователя frappe.
USER frappe

# 4. Устанавливаем рабочую директорию в уже существующий bench.
WORKDIR /home/frappe/frappe-bench

# 5. Копируем и устанавливаем Python-зависимости нашего кастомного приложения.
COPY --chown=frappe:frappe ./requirements.txt /tmp/requirements.txt
RUN ./env/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# 6. Копируем код нашего приложения в директорию apps.
COPY --chown=frappe:frappe . ./apps/ferum_customs

# 7. Устанавливаем наше приложение на сайт 'frontend', который уже существует в базовом образе.
RUN bench --site frontend install-app ferum_customs

# 8. Собираем фронтенд-ассеты (JS/CSS) для нашего приложения, чтобы они были видны в интерфейсе.
RUN bench build --app ferum_customs

# КОНЕЦ Dockerfile.
# Все необходимые сервисы будут запущены через docker-compose.
