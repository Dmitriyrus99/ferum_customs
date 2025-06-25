# Ferum Customs

![CI](https://github.com/<owner>/ferum_customs/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-unknown-lightgrey.svg)

Ferum Customs extends ERPNext with a service management layer. It keeps a registry of serviced equipment, tracks incoming requests and stores reports about performed work.

## Key DocTypes

- **Service Object** — equipment or a site that requires maintenance.
- **Service Request** — a ticket linked to a Service Object describing required work.
- **Service Report** — a record of work done for a request.
- **Service Project** — optional container to group multiple requests.

## Requirements

- Frappe + ERPNext 16.x or later.
- Matching ERPNext branch (e.g. `version-16`).
- A working [bench](https://github.com/frappe/bench) setup if installing without Docker.

## Installation

### Using bench

```bash
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
bench --site <site> run-tests --app ferum_customs --tests-path tests/unit
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
