# Ferum Customs Frappe/ERPNext Docker Setup

Полный минимальный набор файлов, чтобы поднять контейнеры разработки/малого продакшена с вашим кастом-приложением **ferum_customs**.

---

## Структура проекта

```plain
.
├── docker-bake.hcl            # конфигурация сборки (docker buildx bake)
├── compose.yaml               # описание сервисов (docker compose)
├── example.env                # шаблон переменных окружения
└── apps/
    └── ferum_customs/         # ваш код приложения (git-submodule или копия)
```

> Папка `apps/ferum_customs` должна содержать обычное frappe-приложение с `setup.py`, `MANIFEST.in`, `ferum_customs/` и т.д.

---

## docker-bake.hcl и compose.yaml

Проект использует шаблон `frappe_docker`, в котором:
- `docker-bake.hcl` описывает параметры сборки образов для `docker buildx bake`.
- `compose.yaml` содержит конфигурацию сервисов для `docker compose`.

Файлы находятся в каталоге `frappe_docker/`.

---

## compose.yaml

Ниже — пример фрагмента из `frappe_docker/compose.yaml`:
```yaml
services:
  backend:
    # ... описание сервиса backend (Frappe + ERPNext + ferum_customs)
  db:
    # ...
  redis-cache:
    # ...
  redis-queue:
    # ...

volumes:
  sites:
  db-data:
```

---

## example.env

```ini
# Версии образов и теги для frappe_docker
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
# 1. Создаём .env на основе шаблона и задаём пароли
cp example.env .env
nano .env

# 2. Создаём сайт ERPNext с вашим приложением
docker compose run --rm backend bash -c "\
  bench new-site ${SITE_NAME} \
    --admin-password ${ADMIN_PASSWORD} \
    --mariadb-root-password ${DB_ROOT_PASSWORD} \
    --mariadb-user-host-login-scope='%' \
    --install-app erpnext"

# 3. Поднимаем все сервисы
docker compose up -d

# 4. Проверяем
docker compose ps            # backend → Up/healthy
open http://localhost:8000   # форма логина ERPNext
```

---

#### Дополнительно

* **ERPNext**: если нужен, добавьте исходники в `apps/erpnext` (или git-submodule) и пропишите его в `INSTALL_APPS` и в `apps.txt`.
* **Бэкапы**: том `sites/` уже содержит файлы и базу. Сделайте `bench backup --with-files` по cron и выгружайте архивы куда нужно.
* **HTTPS/Prod**: добавьте внешний NGINX/Traefik, пробросите 443, подключите TLS.

---

**Готово!** Этот набор файлов гарантирует, что контейнер `frappe` больше не «флапает» из-за Redis и автоматически разворачивает ваш кастом-сайт при первом запуске.
