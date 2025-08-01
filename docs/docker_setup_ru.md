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
bench set-config -g redis_cache    "redis://:${REDIS_PASSWORD}@${REDIS_CACHE}"
bench set-config -g redis_queue    "redis://:${REDIS_PASSWORD}@${REDIS_QUEUE}"
bench set-config -g redis_socketio "redis://:${REDIS_PASSWORD}@${REDIS_SOCKETIO}"

exec "$@"
```

> Скрипт выполняет три задачи:
>
> 1. Создаёт `sites/apps.txt`, если его нет.
> 2. Автоматически поднимает новый сайт при первом запуске контейнера.
> 3. Прописывает адреса внешних Redis-сервисов, чтобы SocketIO не падал.

### Обновление конфигурации Redis в запущенном контейнере

Чтобы проверить, какие URL Redis сохранены в `common_site_config.json` и в конфиге сайта:
```bash
docker compose exec frappe bash -c "
  grep -A1 -B0 redis_ sites/common_site_config.json
  grep -A1 -B0 sites/${SITE_NAME}/site_config.json
"
```

Чтобы обновить все три ключа за одну команду:
```bash
docker compose exec frappe bash -c "
  bench set-config -g redis_cache     redis://redis-cache:6379  &&
  bench set-config -g redis_queue     redis://redis-queue:6379  &&
  bench set-config -g redis_socketio  redis://redis-socketio:6379
"
```

Чтобы записать те же URL в `site_config.json` конкретного сайта (например, `erp.ferumrus.ru`), выполните:
```bash
docker compose exec frappe bash -c "
  bench --site erp.ferumrus.ru set-config redis_cache    redis://redis-cache:6379 &&
  bench --site erp.ferumrus.ru set-config redis_queue    redis://redis-queue:6379 &&
  bench --site erp.ferumrus.ru set-config redis_socketio redis://redis-socketio:6379
"
```

---

### Ошибка: ValueError: Redis URL must specify одну из схем (redis://, rediss://, unix://)

Иногда в логах Frappe появляется ошибка:

```bash
ValueError: Redis URL must specify one of the following schemes (redis://, rediss://, unix://)
```

Это означает, что ключ `redis_cache` (или `redis_queue`, `redis_socketio`) в `sites/common_site_config.json`
пустой или указан без префикса `redis://` (например, `redis:6379`).

#### 1. Проверьте переменные окружения в `docker-compose.yml` (или `.env`)

```yaml
environment:
  REDIS_PASSWORD: ${ADMIN_PASSWORD}
  REDIS_CACHE:    redis://:${REDIS_PASSWORD}@redis:6379/0
  REDIS_QUEUE:    redis://:${REDIS_PASSWORD}@redis:6379/1
  REDIS_SOCKETIO: redis://:${REDIS_PASSWORD}@redis:6379/2
```

Обязательно указывайте `redis://` в начале каждой строки.

#### 2. Перезапустите Frappe, чтобы переменные точно попали внутрь

```bash
docker compose restart frappe
```

#### 3. Убедитесь, что они действительно в контейнере

```bash
docker compose exec frappe env | grep REDIS_
```

Должны увидеть три полных URL.

#### 4. Проверьте значения в конфиге сайта

```bash
docker compose exec frappe bash -c \
  "jq '.redis_cache, .redis_queue, .redis_socketio' sites/common_site_config.json"
```

Если какая‑то строка пустая — пропишите вручную:

```bash
docker compose exec frappe bench set-config -g redis_cache \
  "redis://:${REDIS_PASSWORD}@redis:6379/0"
docker compose exec frappe bench set-config -g redis_queue \
  "redis://:${REDIS_PASSWORD}@redis:6379/1"
docker compose exec frappe bench set-config -g redis_socketio \
  "redis://:${REDIS_PASSWORD}@redis:6379/2"

docker compose exec frappe bench --site all clear-cache
```

#### 5. Снова перезапустите Frappe и проверьте логи

```bash
docker compose restart frappe
docker compose logs -f frappe | tail -n 50
```

Ожидаем этапы:

```text
Setting Redis configurations...
Migrating site <SITE_NAME>
Bench started.
```

---

### Как запустить

```bash
# 1. Создаём .env на основе шаблона и задаём пароли
cp example.env .env
nano .env

# 1. (Опционально) Устраните ошибки доступа к Docker:
#
# Если при запуске ниже команд вы видите ошибку permission denied при подключении к Docker,
# добавьте своего пользователя в группу docker и перезапустите сеанс:
#
# ```bash
# sudo usermod -aG docker "$USER" && newgrp docker
# ```

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
