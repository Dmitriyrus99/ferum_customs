### ferum_customs

Ferum Customs extends ERPNext with a simple service management module. It adds
documents for keeping a register of serviced equipment, creating service
requests and logging performed work. These documents are connected via a
workflow that drives a request from "Открыта" to "Закрыта".

Key DocTypes:

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
bench install-app ferum_customs
# Run all bench commands from within your bench directory so that the correct
# Python environment is used
```

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

After installation a new **Ferum Customs** module appears on the ERPNext desk.
Users with roles "Проектный менеджер" or "System Manager" can create Service
Objects and manage Service Requests through the provided workflow. Engineers
update requests assigned to them and submit Service Reports. Customers see only
their own documents if granted the "Customer" role.
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

### Testing

Run the test suite with `pytest` from the repository root:

```bash
pytest
```

If you prefer using bench:

```bash
bench --site <your-site> run-tests apps/ferum_customs
```


### License

MIT. See [license.txt](license.txt) for details.
