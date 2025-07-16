# Installation Guide

This document explains how to install the `ferum_customs` app in your Frappe/ERPNext environment.

## Requirements

- Требуется **Frappe + ERPNext**.
- Tested with **Frappe/ERPNext 16.0**. Older versions are not officially supported.
- ERPNext branch must match your Frappe version (e.g. `version-16`).
- A working [bench](https://github.com/frappe/bench) setup.

## Bare-metal

1. Install the bench CLI if you don't have it yet:
   ```bash
   pipx install frappe-bench
   ```
2. Clone this repository inside your bench directory:
   ```bash
   bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
   ```
3. (Optional) Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv_dev
   source .venv_dev/bin/activate
   ```
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy and edit the environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env to set TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, DB_ROOT_PASSWORD, etc.
   ```
6. Install the application on your site:
   ```bash
   bench --site YOUR_SITE_NAME install-app ferum_customs
   ```
7. Build assets and restart bench:
   ```bash
   bench build && bench restart
   ```
## Docker

Before running Docker, prepare your environment file:

```bash
cp .env.example .env
# Edit .env to set TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, DB_ROOT_PASSWORD, etc.
```

Run the stack with:

```bash
docker compose up -d --build
```


If you use Docker images, add `ferum_customs` to `apps.txt` (or `apps.json`) and rebuild the image before running the `install-app` command.

## Инструменты разработчика

Для автоматизации задач код-ревью и CI используем Codex CLI.

**Установка**:
```bash
pip install codex-cli
```

**Использование**:
```bash
codex --config .codex/project.yaml
```

## Configuration

After installation log in as **Administrator** and open **Role List**. Make sure the following roles exist and assign them to appropriate users:

- `Проектный менеджер`
- `Инженер`
- `Заказчик` (customers only)

The app also installs a *Service Request Workflow*. Review the workflow states and transitions under **Workflow List** and adjust them if required.

## Backup

To protect your data run daily backups:

```bash
bench backup --with-files
```

Use `cron` or a systemd timer and copy archives to external storage.

## Production Setup

For production deployments run:

```bash
bench setup production <frappe-user>
```

The command configures Nginx and Supervisor. After obtaining TLS certificates (e.g. via Certbot), edit the generated Nginx config to reference your `fullchain.pem` and `privkey.pem` files so the site is served over HTTPS.
