# Ferum Customs Frappe/ERPNext Docker Setup

This guide explains how to run the application in containers using the `frappe_docker` template.

## Project layout
```
.
├── docker-bake.hcl        # build configuration for `docker buildx bake`
├── compose.yaml           # service definitions for `docker compose`
├── example.env            # environment variables template
└── apps/
    └── ferum_customs/     # your application code (submodule or copy)
```
The `apps/ferum_customs` directory should contain a standard Frappe app with `setup.py`, `MANIFEST.in` and the package itself.

## docker-bake.hcl and compose.yaml
`docker-bake.hcl` describes image build parameters, while `compose.yaml` defines the running services. Both files reside in the `frappe_docker/` folder.

## compose.yaml snippet
```yaml
services:
  backend:
    # Frappe + ERPNext + ferum_customs
  db:
    # MariaDB
  redis-cache:
  redis-queue:

volumes:
  sites:
  db-data:
```

## example.env
```ini
# Image versions for frappe_docker
BENCH_TAG=v5.25.4
MARIADB_TAG=10.6
REDIS_TAG=6.2

# Site configuration
SITE_NAME=erp.example.com
DB_ROOT_PASSWORD=ReplaceMeRoot
ADMIN_PASSWORD=ReplaceMeAdmin
```
Copy it to `.env`, change passwords and the domain.

## docker-entrypoint.sh
The entrypoint script performs three tasks:
1. Creates `sites/apps.txt` if missing and appends apps listed in `INSTALL_APPS`.
2. Automatically creates a new site on first run.
3. Writes external Redis service URLs so SocketIO works.

## Updating Redis configuration
Check saved URLs in `common_site_config.json` and site config:
```bash
docker compose exec frappe bash -c "grep -A1 -B0 redis_ sites/common_site_config.json && grep -A1 -B0 sites/${SITE_NAME}/site_config.json"
```
To update all keys at once:
```bash
docker compose exec frappe bash -c "\
  bench set-config -g redis_cache     redis://redis-cache:6379 &&\
  bench set-config -g redis_queue     redis://redis-queue:6379 &&\
  bench set-config -g redis_socketio  redis://redis-socketio:6379"
```

## Running
```bash
# 1. Create .env from the template and set passwords
cp example.env .env

# 2. Create the ERPNext site with your app
docker compose run --rm backend bash -c "\
  bench new-site ${SITE_NAME} \
    --admin-password ${ADMIN_PASSWORD} \
    --mariadb-root-password ${DB_ROOT_PASSWORD} \
    --mariadb-user-host-login-scope='%' \
    --install-app erpnext"

# 3. Start all services
docker compose up -d

# 4. Verify
docker compose ps
open http://localhost:8000
```

### Extras
* **ERPNext**: add sources in `apps/erpnext` if needed and include it in `INSTALL_APPS` and `apps.txt`.
* **Backups**: the `sites/` volume already stores files and the database. Schedule `bench backup --with-files` via cron and upload archives to external storage.
* **HTTPS/Prod**: use an external NGINX/Traefik, expose port 443 and configure TLS.

That's it! This setup prevents Frappe from flapping because of Redis and automatically bootstraps your custom site on the first run.

