### ferum_customs

ferum_customs

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch main
bench install-app ferum_customs
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

### Project Structure

All application code lives inside the `ferum_customs` package. Important
subdirectories include:

- `custom_logic` – Python hooks used by DocType events
- `ferum_customs/doctype` – definitions of custom DocTypes
- `fixtures` – exported records such as roles and custom fields
- `workflow` and `workspace` – workflow configuration and Desk shortcuts

The `update` folder from the original archive has been merged into these
subdirectories.
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

MIT. See [license.txt](license.txt) for details.
