# Deployment Guide

This document explains how to verify the project before a production deployment and how to launch it on the target server.

## 1. Prepare the environment

1. Install **Python 3.10+**, **Docker** and **docker compose** on the server.
2. Clone the repository and enter the project directory:
   ```bash
   git clone https://github.com/Dmitriyrus99/ferum_customs.git
   cd ferum_customs
   ```
3. Copy `.env.example` to `.env` and edit the variables. At minimum set:
   - `SITE_NAME`
   - `DB_ROOT_PASSWORD`
   - `ADMIN_PASSWORD`
   - `FRAPPE_ADMIN_PASSWORD`
   - `REDIS_PASSWORD`
   - `TELEGRAM_BOT_TOKEN` (optional, for the bot)

## 2. Build containers

Run the stack and build images:

```bash
docker compose up -d --build
```

Check that services are healthy:

```bash
docker compose ps
```

The `frappe` service should show `Up/healthy`.

## 3. Create the site

If the entrypoint did not create the site automatically, run:

```bash
docker compose exec frappe bench new-site ${SITE_NAME} \
  --admin-password ${ADMIN_PASSWORD} \
  --mariadb-root-password ${DB_ROOT_PASSWORD} \
  --install-app erpnext

docker compose exec frappe bench --site ${SITE_NAME} install-app ferum_customs
```

The helper script `scripts/fix-missing-db.sh` can create the database and user if the site creation fails.

## 4. Verify application

1. Run unit tests inside the container:
   ```bash
   docker compose exec frappe pytest -q
   ```
2. Run pre-commit checks:
   ```bash
   pre-commit run --all-files
   ```

All tests should pass without errors. Investigate any failures before continuing.

## 5. Configure production

For a production deployment execute:

```bash
bench setup production frappe
```

This generates Supervisor and Nginx configs. Obtain TLS certificates (for example with Certbot) and update the Nginx config to serve the site via HTTPS.

## 6. Backup

Create regular backups using:

```bash
bench backup --with-files
```

Store the resulting archives outside the server for safety. More details are in [backup.md](backup.md).

```