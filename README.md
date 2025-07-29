# Ferum Customs

![CI](https://github.com/Dmitriyrus99/ferum_customs/actions/workflows/ci.yml/badge.svg)
[![Coverage](https://img.shields.io/codecov/c/github/Dmitriyrus99/ferum_customs/main.svg?logo=codecov)](https://codecov.io/gh/Dmitriyrus99/ferum_customs)

Ferum Customs extends ERPNext with a service management layer. It keeps a registry of serviced equipment, tracks incoming requests and stores reports about performed work.

## Описание

Кастомное приложение для ERPNext/Frappe, предназначенное для автоматизации работы сервисной компании
в области противопожарной безопасности.

### Основные возможности:
- Управление заявками и проектами
- Автоматизация актов, маршрутов, графиков обслуживания
- Поддержка FSM-бота для Telegram
- Расширения DocType, Workflow, Permission
- Интеграция с Google Drive, аналитикой, CI/CD

### Требования:
- Frappe >= 15
- PostgreSQL / MariaDB
- Python 3.10+

## Key DocTypes

- **Service Object** — equipment or a site that requires maintenance.
- **Service Request** — a ticket linked to a Service Object describing required work.
- **Service Report** — a record of work done for a request.
- **Service Project** — optional container to group multiple requests.


## Documentation

- [Документация на русском](docs/overview_ru.md)
- [Frappe/ERPNext Docker Setup](docs/docker_setup_ru.md)

## Configuration

Приложение использует переменные среды для конфиденциальных настроек.
Скопируйте файл `.env.example` в `.env` и заполните ключи:

```bash
cp .env.example .env
# укажите TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, FRAPPE_ADMIN_PASSWORD и прочие
```

Переменные автоматически загружаются через Pydantic Settings.

## Requirements

- Frappe + ERPNext 15.x or later.
- Matching ERPNext branch (e.g. `version-15`).
- A working [bench](https://github.com/frappe/bench) setup if installing without Docker.

## Installation
### Bare-metal (no Docker)

Автоматическую установку и запуск без Docker можно выполнить с помощью скрипта:

```bash
sudo bash scripts/quick_setup_bare_metal.sh
```

### Using bench

```bash
# Install bench CLI if not already present
pipx install frappe-bench

# Clone the application
bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main

# (Optional) Create and activate a Python virtual environment
python3 -m venv .venv_dev
source .venv_dev/bin/activate

# Install Python dependencies and configure environment
pip install -r requirements.txt
cp .env.example .env
# Edit .env to set TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, FRAPPE_ADMIN_PASSWORD, DB_ROOT_PASSWORD, etc.

# Install the application and rebuild assets
bench --site YOUR_SITE_NAME install-app ferum_customs
bench build && bench restart
```

### Using Docker

Before running Docker, ensure your user has permission to access the Docker daemon:

```bash
# On Linux, if you get a permission denied error, add yourself to the docker group:
sudo usermod -aG docker "$USER" && newgrp docker
```

Copy and configure your environment file:

```bash
cp .env.example .env
# Edit .env to set TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, FRAPPE_ADMIN_PASSWORD, DB_ROOT_PASSWORD, etc.
```

Run the stack locally:

```bash
docker compose up -d --build
```

The helper script `scripts/setup_environment.sh` can bootstrap a development bench in Docker and install the app automatically.
The helper script `scripts/setup_codex.sh` installs Docker and builds the Codex CLI image for local use.
The lightweight `scripts/quick_setup.sh` script simply runs `docker compose` with the provided configuration.

The helper script `scripts/fix-missing-db.sh` checks for missing Frappe site database and user, creates them if needed, and updates the administrator password. Usage:

```bash
SITE_NAME=<site_name> DB_ROOT_PASSWORD=<root_db_password> ADMIN_PASSWORD=<new_password> ./scripts/fix-missing-db.sh
```

Add `ferum_customs` to `apps.txt` (or `apps.json`) if you build custom images.

## Usage

After installation the **Ferum Customs** module appears on the ERPNext desk. Typical workflow:

1. Create a **Service Object** that represents equipment or a location.
2. Open a **Service Request** for that object.
3. Technicians submit **Service Reports** describing the work done.
4. Optionally group several requests in a **Service Project**.

Roles required:

- **Проектный менеджер** or **System Manager** — manage all documents and the workflow.
- **Service Engineer** — update assigned requests and submit reports.
- **Customer** — view their own requests and related reports.

### Role workflows

**Project Manager**

1. Register new *Service Objects* and assign responsible engineers.
2. Create and triage *Service Requests*.
3. Move requests through the workflow: **Открыта → В работе → Выполнена → Закрыта**.
4. Review submitted *Service Reports* and generate invoices if required.

**Office Manager**

1. Log incoming calls or emails as *Service Requests*.
2. Track due dates and follow up with engineers or clients.
3. Update customer information and schedule visits.

**Service Engineer**

1. Check assigned *Service Requests* from the desk or via the Telegram bot.
2. Record work details in a *Service Report* and attach photos or documents.
3. Mark the request as **Выполнена** when done.

**Client/Customer**

1. Submit new requests through the portal or the Telegram bot.
2. Monitor request status and view related reports.
3. Receive invoices and close completed work.

## Telegram Bot

The optional bot simplifies field updates through Telegram. Set the bot token in
the ``TELEGRAM_BOT_TOKEN`` environment variable and run ``telegram_bot.bot_service``.

Available commands (example syntax):

```
/new_request <subject> - create a service request
/my_requests - list your open requests
/upload_photo <request_id> - attach a photo
/set_status <request_id> <status> - update request status
```

The bot internally calls whitelisted functions from ``ferum_customs.api``.

## Development

Pre‑commit hooks format and lint the code. Install development dependencies and enable hooks:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

When editing configuration files on a server use `vi` or `vim` instead of `nano`.

Project source lives inside the `ferum_customs` package. Key folders include `custom_logic` for DocType hooks, `fixtures` for exported records and `workflow` for workflow configuration.

### Running tests

Quick unit tests can be executed with bench:

```bash
bench run-tests --site <site> --app ferum_customs --test tests/unit
```

#### Test site setup

If you do not have a site yet, follow these steps inside your bench directory:

1. Switch to the `frappe` user:

   ```bash
   su frappe -s /bin/bash
   ```

2. Change into the bench folder (for example `frappe-bench`):

   ```bash
   cd /home/frappe/frappe-bench
   ```

3. Create a test site if it does not exist:

   ```bash
   bench new-site test_site --force --admin-password admin --db-name test_site_db
   ```

4. Install the app on the site:

   ```bash
   bench --site test_site install-app ferum_customs
   ```

5. Run the unit tests:

   ```bash
   bench run-tests --site test_site --app ferum_customs --test tests/unit
   ```

6. *(Optional)* Remove the site when finished:

   ```bash
   bench drop-site test_site --force
   ```

You can also run the whole suite with `pytest`:

```bash
pytest
```

### Local linting

Install development dependencies and run pre-commit hooks:

```bash
pip install -U pip
pip install .[dev,test]
pre-commit install
pre-commit run --all-files
```

### Проверка после коммита

Чтобы автоматически запускать статические проверки и тесты после каждого коммита, включите версионно‑контролируемые Git‑хуки:

```bash
git config core.hooksPath .githooks
```

## CI

GitHub Actions start containers defined in `docker-compose.test.yml` and run unit tests. The same stack can be started locally with:

```bash
docker compose -f docker-compose.test.yml up -d
```

The workflow additionally runs Bandit and `npm audit` for dependency scanning,
executes Playwright E2E checks and a short Locust load test. Mypy uses `--strict`
and coverage must not drop below 80%.

## Backup and Recovery

Export SQL dumps of your site and copy the `files` directory from the bench. Automate this with

```bash
bench backup --with-files
```

run via `cron` or a systemd timer. To restore, deploy the same version of the app, import the database dump and place attachments back into `sites/<site-name>/public/files`. Details are in [backup.md](backup.md).

## Updating images

To update Docker images:

1. Pull the new tag: `docker pull frappe/erpnext-worker:<new-tag>`
2. Update the tag in `docker-compose.test.yml` and rebuild containers.
3. Run `pytest` locally and make sure tests pass before opening a PR.

## Changelog

Release notes live in [CHANGELOG.md](CHANGELOG.md).

## Security

Report vulnerabilities via [support@ferum.ru](mailto:support@ferum.ru). Do not disclose issues publicly until patched.

For production deployments use

```bash
bench setup production <frappe-user>
```

to configure Nginx and Supervisor. Obtain TLS certificates (for example with Certbot) and update the generated config so the site is served via HTTPS.

## License

MIT. See [license.txt](license.txt) for details.
