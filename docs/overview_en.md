# Architecture and Development Guide for Ferum Customizations

## 1. Goal and overview

"Ferum Customizations" extends the Frappe/ERPNext platform to manage service tickets and projects. The aim is to automate paperwork, make processes transparent, control deadlines and integrate with a Telegram bot for quick request creation and notifications.

## 2. Architecture and technology stack

### 2.1 Backend
- Frappe Framework v15
- Python 3.10+
- MariaDB as the primary database
- Redis for background jobs and caching
- Frappe REST API with additional FastAPI endpoints

### 2.2 Frontend
- Frappe Desk and web forms
- JavaScript (ES6+), jQuery, HTML5, CSS3
- Node.js for asset building

### 2.3 Tooling and CI/CD
- Docker and Docker Compose
- GitHub Actions for tests and linters
- pre-commit, Ruff, ESLint/Prettier

## 3. Key components and structure

### 3.1 Main directories
- `ferum_customs/doctype/` – DocType definitions and related files
- `ferum_customs/custom_logic/` – business logic extracted from DocTypes
- `ferum_customs/permissions/` – dynamic permission rules
- `ferum_customs/fixtures/` – initial fixtures
- `telegram_bot/` – Telegram bot integration
- `hooks.py` – connects code with Frappe events

### 3.2 Core DocTypes
- **Service Project** – container for requests
- **Service Object** – equipment or place that requires maintenance
- **Service Request** – the service ticket
- **Service Report** – report on completed work
- **Custom Attachment** – extended attachments

### 3.3 Telegram bot integration
Modular architecture based on `aiogram` routers. Each role has its own router and handlers. Authentication is done via phone number.

## 4. User roles and permissions
- **Administrator** – full access
- **Project Manager** – manages projects and tickets
- **Office Manager** – registers client requests
- **Service Engineer** – works with assigned tickets and reports
- **Client/Customer** – sees only their own tickets
- **Chief Accountant** – access to financial documents

Client data isolation is implemented with `permission_query_conditions` and `User Permission`.

## 5. Main functionality
### 5.1 Service Request lifecycle
1. Create a request
2. Assign a responsible engineer
3. Work on the request
4. Create a Service Report
5. Close the request

### 5.2 Document management
- Automatic numbering
- Controlling links between documents

### 5.3 Code conventions
- Server logic via hooks in `hooks.py` and modules in `custom_logic`
- Constants in `constants.py`
- Client scripts in DocType `.js` files
- Use `pre-commit` for formatting and checks

## 6. Local development and testing
Run the stack and install the app:
```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
cp .env.example .env
# edit TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD, etc.
docker compose exec frappe bash -c "bench --site ${SITE_NAME} install-app ferum_customs"
```
Run tests:
```bash
bench --site ${SITE_NAME} run-tests --app ferum_customs
```

## 7. Assistant configuration
```yaml
fix_bot:
  log_sources:
    - cmd: "docker compose logs --no-color --since 5m"
      interval: "*/2 * * * *"   # every 2 minutes
  redis_default_url: "redis://:<REDIS_PASSWORD>@redis-cache:6379"
  mysql_wait_timeout: "300s"
  notify_channels:
    - telegram: "@ferum_ops_chat"
  auto_fix_limit_per_hour: 3
```

## 8. Output artifacts
- `action_plan_<timestamp>.json` – what was done and why
- `fix_bot_report.md` – daily summary of successes and failures

