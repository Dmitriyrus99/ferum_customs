# Installation Guide

This document explains how to install the `ferum_customs` app in your Frappe/ERPNext environment.

## Requirements

- Требуется **Frappe + ERPNext**.
- Tested with **Frappe/ERPNext 15.0**. Older versions are not officially supported.
- ERPNext branch must match your Frappe version (e.g. `version-15`).
- A working [bench](https://github.com/frappe/bench) setup.

## Bare-metal

1. Clone this repository inside your bench directory:
   ```bash
   bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
   ```
2. Install the application on your site:
   ```bash
   bench --site YOUR_SITE_NAME install-app ferum_customs
   ```
3. Build assets and restart bench:
   ```bash
   bench build && bench restart
   ```
## Docker

Run the stack with:
```bash
docker compose up -d --build
```


If you use Docker images, add `ferum_customs` to `apps.txt` (or `apps.json`) and rebuild the image before running the `install-app` command.

## Configuration

After installation log in as **Administrator** and open **Role List**. Make sure the following roles exist and assign them to appropriate users:

- `Проектный менеджер`
- `Инженер`
- `Заказчик` (customers only)

The app also installs a *Service Request Workflow*. Review the workflow states and transitions under **Workflow List** and adjust them if required.
