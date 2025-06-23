### ferum_customs

![CI](https://github.com/<owner>/ferum_customs/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-unknown-lightgrey.svg)

Ferum Customs adds a service management layer to ERPNext. The app helps keep
a registry of serviced equipment, register incoming requests and collect reports
about the work performed. All documents are linked so that a Service Request
always refers to a Service Object and can be closed with a Service Report. The
workflow takes a request from "Открыта" to "Закрыта".

Key DocTypes and their relations:

- **Service Object** — equipment or site that requires maintenance.
- **Service Request** — a ticket linked to a Service Object describing required
  work.
- **Service Report** — a record of work done for a request.
- **Service Project** — optional container to group multiple requests.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
# ERPNext branch should match your installed Frappe version
bench get-app erpnext --branch version-XX https://github.com/frappe/erpnext
# Replace XX with your Frappe major version, e.g. 16
bench install-app ferum_customs
# Run all bench commands from within your bench directory so that the correct
# Python environment is used

```
Alternatively, run `scripts/setup_environment.sh` to spin up a Docker-based bench and install this app automatically. The script clones `frappe_docker`, starts the containers and creates the site for you.


### Запуск в Docker

Run the stack with:
```bash
docker compose up -d
```

To replicate the CI environment locally run:
```bash
docker compose -f docker-compose.test.yml up -d
```

When Frappe releases a new minor version, update the `image` tag in
`docker-compose.test.yml` to that version and rebuild the containers.


### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/ferum_customs
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CLI Tips

When editing configuration files on the server, use **vi** or **vim** instead of
`nano`, which might not be available by default.

### Project Structure

All application code lives inside the `ferum_customs` package. Important
subdirectories include:

- `custom_logic` – Python hooks used by DocType events
- `ferum_customs/doctype` – definitions of custom DocTypes
- `fixtures` – exported records such as roles and custom fields
- `workflow` and `workspace` – workflow configuration and Desk shortcuts

The `update` folder from the original archive has been merged into these
subdirectories.

### Usage

After installing the app you will see a new **Ferum Customs** module on the
ERPNext desk. Typical workflow looks as follows:

1. Create a **Service Object** that represents equipment or a location.
2. Open a **Service Request** for that object.
3. Technicians update the request and submit **Service Reports** describing the
   work done.
4. Optionally group several requests in a **Service Project**.

Users require the following roles:

- **Проектный менеджер** or **System Manager** — manage all documents and the
  workflow.
- **Service Engineer** — update assigned Service Requests and submit reports.
- **Customer** — view their own Service Requests and related reports.
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Spins up official Frappe containers via `docker-compose.test.yml` and runs unit tests.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### Testing

Unit tests can be run locally with `pytest` or through bench. From the
repository root execute:

```bash
pytest
```

If you prefer using bench:

```bash
bench --site <your-site> run-tests apps/ferum_customs
```

### Backup

Regularly export a SQL dump of your site and copy the `files` directory from the
bench. To restore, deploy the same version of the app from GitHub, import the
database dump and place the attachments back into the `sites/<site-name>/public/files`
folder. See [backup.md](backup.md) for details.

### Changelog

Release notes are tracked in [CHANGELOG.md](CHANGELOG.md).

### Обновление образа

1. Проверьте доступность нового тега:

   ```bash
   docker pull frappe/erpnext-worker:<new-tag>
   ```

2. Обновите тег в `docker-compose.test.yml`.
3. Запустите `pytest` локально и убедитесь, что тесты проходят.
4. Создайте PR и проверьте, что CI зелёный.


### License

MIT. See [license.txt](license.txt) for details.
