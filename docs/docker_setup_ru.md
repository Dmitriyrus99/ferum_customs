# Ferum Customs Frappe/ERPNext Docker Setup

Полный минимальный набор файлов, чтобы поднять контейнеры разработки/малого продакшена с вашим кастом-приложением **ferum_customs**.

---

## Структура проекта

```
.
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── docker-entrypoint.sh
└── apps/
    └── ferum_customs/              # ваш код приложения (git-submodule или копия)
```

> Папка `apps/ferum_customs` должна содержать обычное frappe-приложение с `setup.py`, `MANIFEST.in`, `ferum_customs/` и т.д.

---

## Dockerfile

```dockerfile
ARG BENCH_TAG=v5.25.4
FROM frappe/bench:${BENCH_TAG}

# Ставим redis-server (для локального режима bench) — можно убрать, если используете внешние Redis-контейнеры
USER root
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Инициализируем bench под пользователем frappe
USER frappe
WORKDIR /home/frappe
RUN bench init --skip-assets frappe-bench --python $(which python)

WORKDIR /home/frappe/frappe-bench

# Копируем кастом-приложение внутрь образа
COPY --chown=frappe:frappe apps/ferum_customs apps/ferum_customs

# Ставим python/npm зависимости
RUN bench setup requirements

# Копируем скрипт-entrypoint и делаем его исполняемым
USER root
COPY docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
USER frappe

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bench", "start"]
```

---

## docker-compose.yml

```yaml
version: "3.9"

services:
  frappe:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BENCH_TAG: ${BENCH_TAG}
    environment:
      SITE_NAME: ${SITE_NAME}
      DB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      INSTALL_APPS: erpnext,ferum_customs
      DB_HOST: db
      REDIS_CACHE: redis-cache:6379
      REDIS_QUEUE: redis-queue:6379
      REDIS_SOCKETIO: redis-queue:6379
    ports:
      - "8000:8000"
    volumes:
      - sites:/home/frappe/frappe-bench/sites
    depends_on:
      - db
      - redis-cache
      - redis-queue
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/method/ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: mariadb:${MARIADB_TAG}
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - db-data:/var/lib/mysql

  redis-cache:
    image: redis:${REDIS_TAG}

  redis-queue:
    image: redis:${REDIS_TAG}

volumes:
  sites:
  db-data:
```

---

## .env.example

```
# Версии образов
BENCH_TAG=v5.25.4
MARIADB_TAG=10.6
REDIS_TAG=6.2

# Конфигурация сайта
SITE_NAME=erp.ferumrus.ru
DB_ROOT_PASSWORD=ReplaceMeRoot
ADMIN_PASSWORD=ReplaceMeAdmin
```

Скопируйте в `.env`, поменяйте пароли и, при необходимости, домен.

---

## docker-entrypoint.sh

```bash
#!/usr/bin/env bash
set -e

cd /home/frappe/frappe-bench

# ── 1. apps.txt ────────────────────────────────────────────────────────────
SITE_APPS_FILE="sites/apps.txt"
if [[ ! -f "${SITE_APPS_FILE}" ]]; then
  echo "frappe" > "${SITE_APPS_FILE}"
  if [[ -n "${INSTALL_APPS}" ]]; then
    IFS=',' read -ra ADD_APPS <<< "${INSTALL_APPS}"
    for app in "${ADD_APPS[@]}"; do
      echo "$app" >> "${SITE_APPS_FILE}"
    done
  fi
fi

# ── 2. Создание сайта ────────────────────────────────────────────────────
if [[ -n "${SITE_NAME}" && ! -d "sites/${SITE_NAME}" ]]; then
  bench new-site --no-mariadb-socket "${SITE_NAME}" \
       --admin-password "${ADMIN_PASSWORD}" \
       --mariadb-root-password "${DB_ROOT_PASSWORD}" \
       --db-host "${DB_HOST}"
  if [[ -n "${INSTALL_APPS}" ]]; then
    IFS=',' read -ra ADD_APPS <<< "${INSTALL_APPS}"
    for app in "${ADD_APPS[@]}"; do
      bench --site "${SITE_NAME}" install-app "$app"
    done
  fi
fi

# ── 3. Redis конфиги ─────────────────────────────────────────────────────
bench set-config -g redis_cache    "${REDIS_CACHE}"
bench set-config -g redis_queue    "${REDIS_QUEUE}"
bench set-config -g redis_socketio "${REDIS_SOCKETIO}"

exec "$@"
```

> Скрипт выполняет три задачи:
>
> 1. Создаёт `sites/apps.txt`, если его нет.
> 2. Автоматически поднимает новый сайт при первом запуске контейнера.
> 3. Прописывает адреса внешних Redis-сервисов, чтобы SocketIO не падал.

---

### Как запустить

```bash
# 1. Создаём .env на основе примера и правим пароли
cp .env.example .env
nano .env

# 2. Собираем и поднимаем
docker compose up -d --build

# 3. Проверяем
docker compose ps            # frappe → Up/healthy
open http://localhost:8000   # форма логина ERPNext
```

---

#### Дополнительно

* **ERPNext**: если нужен, добавьте исходники в `apps/erpnext` (или git-submodule) и пропишите его в `INSTALL_APPS` и в `apps.txt`.
* **Бэкапы**: том `sites/` уже содержит файлы и базу. Сделайте `bench backup --with-files` по cron и выгружайте архивы куда нужно.
* **HTTPS/Prod**: добавьте внешний NGINX/Traefik, пробросите 443, подключите TLS.

---

**Готово!** Этот набор файлов гарантирует, что контейнер `frappe` больше не «флапает» из-за Redis и автоматически разворачивает ваш кастом-сайт при первом запуске.
