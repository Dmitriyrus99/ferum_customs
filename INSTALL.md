# Installation Guide

This document explains how to install the `ferum_customs` app in your Frappe/ERPNext environment.

## Requirements

- Frappe + ERPNext 15.x or later.
- Matching ERPNext branch (e.g. `version-15`).
- A working [bench](https://github.com/frappe/bench) setup if installing without Docker.

## Installation

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

### Bare-metal (no Docker)

To automate all steps for bare-metal installation without Docker, run:

```bash
sudo bash scripts/quick_setup_bare_metal.sh
```

#### Manual bare-metal installation

1. **Install system dependencies**

   On Ubuntu/Debian-based systems:
   ```bash
   sudo apt update
   sudo apt install -y \
     mariadb-server \
     redis-server \
     python3-dev python3-venv python3-pip \
     nodejs npm
   # (optional) yarn:
   sudo npm install --global yarn

   # Make sure services are running:
   sudo systemctl enable --now mariadb redis-server
   ```

2. **Install bench CLI**

   ```bash
   pipx install frappe-bench
   ```

3. **Initialize bench**

   ```bash
   bench init frappe-bench --frappe-branch version-15
   cd frappe-bench
   ```

4. **Create a new site**

   ```bash
   bench new-site <SITE_NAME> \
     --admin-password <ADMIN_PASSWORD> \
     --db-root-password <DB_ROOT_PASSWORD>
   ```

5. **Get the app**

   ```bash
   bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
   ```

6. **Install the app on your site**

   ```bash
   bench --site <SITE_NAME> install-app ferum_customs
   ```

7. **Build assets and restart**

   ```bash
   bench build
   bench restart
   ```