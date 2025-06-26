# ======================================================================================
# Dockerfile для разработки приложения "ferum_customs" на Frappe v15
# ======================================================================================

# 1. Используем официальный образ Frappe v15 в качестве основы.
# Это гарантирует, что все системные зависимости, Python, Node.js, redis и bench
# уже установлены и сконфигурированы правильно.
# Используем корректный тег для 15-й версии.
FROM frappe/bench:latest

# 2. Переключаемся на пользователя root для установки дополнительных системных пакетов.
# Например, git (если его нет) или другие инструменты отладки.
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    # vim или nano для редактирования файлов внутри контейнера
    vim \
    # git для работы с репозиториями напрямую из контейнера
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Переключаемся обратно на стандартного пользователя frappe.
# Все операции с bench и приложением должны выполняться от его имени.
USER frappe

# 4. Устанавливаем рабочую директорию.
# Это домашняя директория пользователя frappe, где обычно располагается bench.
WORKDIR /workspace/development

# 5. Инициализируем bench для 15-й версии Frappe
RUN bench init --frappe-branch version-15 frappe-bench

# 6. Устанавливаем рабочую директорию внутрь созданного bench
WORKDIR /workspace/development/frappe-bench

# 7. Копируем requirements.txt вашего приложения.
# Это позволит установить зависимости до копирования всего кода,
# что лучше использует кэширование слоев Docker.
COPY --chown=frappe:frappe ./requirements.txt /tmp/requirements.txt

# 8. Устанавливаем Python-зависимости вашего приложения.
# Используем pip из виртуального окружения bench.
RUN ./env/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# 9. Копируем все приложение в директорию apps внутри frappe-bench.
COPY --chown=frappe:frappe . ./apps/ferum_customs

# 10. Устанавливаем приложение на сайт по умолчанию (frontend).
# Сначала нужно создать сайт.
# ПРИМЕЧАНИЕ: Для CI этот шаг лучше вынести в docker-compose, так как он требует подключения к БД.
# Но для создания самодостаточного образа мы можем его оставить здесь,
# предполагая, что БД будет доступна при запуске.
# Для упрощения CI, мы пропустим создание сайта здесь, оно будет в `docker-compose`.
# RUN bench new-site frontend
# RUN bench --site frontend install-app ferum_customs

# 11. Собираем фронтенд-ассеты (JS/CSS).
RUN bench build --app ferum_customs

# КОНЕЦ Dockerfile.
# ENTRYPOINT и CMD наследуются из базового образа.
