# Ferum Customs

![CI](https://github.com/<owner>/ferum_customs/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-unknown-lightgrey.svg)

Ferum Customs extends ERPNext with a service management layer. It keeps a registry of serviced equipment, tracks incoming requests and stores reports about performed work.

## Key DocTypes

- **Service Object** — equipment or a site that requires maintenance.
- **Service Request** — a ticket linked to a Service Object describing required work.
- **Service Report** — a record of work done for a request.
- **Service Project** — optional container to group multiple requests.


## Documentation

- [Документация на русском](docs/overview_ru.md)
- [Frappe/ERPNext Docker Setup](docs/docker_setup_ru.md)

## Requirements

- Frappe + ERPNext 16.x or later.
- Matching ERPNext branch (e.g. `version-16`).
- A working [bench](https://github.com/frappe/bench) setup if installing without Docker.

## Installation

### Using bench

```bash
pipx install frappe-bench  # install bench CLI if not already present
bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
bench --site YOUR_SITE_NAME install-app ferum_customs
bench build && bench restart
```

### Using Docker

Run the stack locally:

```bash
docker compose up -d --build
```

The helper script `scripts/setup_environment.sh` can bootstrap a development bench in Docker and install the app automatically.
The helper script `scripts/setup_codex.sh` installs Docker and builds the Codex CLI image for local use.

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

Pre‑commit hooks format and lint the code. Enable them inside the app directory:

```bash
cd apps/ferum_customs
pre-commit install
```

When editing configuration files on a server use `vi` or `vim` instead of `nano`.

Project source lives inside the `ferum_customs` package. Key folders include `custom_logic` for DocType hooks, `fixtures` for exported records and `workflow` for workflow configuration.

### Running tests

Quick unit tests can be executed with bench:

```bash
bench --site <site> run-tests --app ferum_customs --test tests/unit
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
   bench --site test_site run-tests --app ferum_customs --test tests/unit
   ```

6. *(Optional)* Remove the site when finished:

   ```bash
   bench drop-site test_site --force
   ```

You can also run the whole suite with `pytest`:

```bash
pytest
```

## CI

GitHub Actions start containers defined in `docker-compose.test.yml` and run unit tests. The same stack can be started locally with:

```bash
docker compose -f docker-compose.test.yml up -d
```

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
