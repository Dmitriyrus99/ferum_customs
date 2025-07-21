# Чистая установка (bare-metal) без Docker

Ниже приведена пошаговая инструкция по развёртыванию приложения ferum_customs
на «чистой» (bare-metal) системе без использования Docker.

## 1. Установить системные зависимости

На Ubuntu/Debian-подобных системах:
```bash
sudo apt update
sudo apt install -y \
  mariadb-server \
  redis-server \
  python3-dev python3-venv python3-pip \
  nodejs npm
# (по желанию) yarn:
sudo npm install --global yarn

# Убедитесь, что службы запущены:
sudo systemctl enable --now mariadb redis-server
```

## 2. Установить bench‑CLI

bench — инструмент для управления Frappe/ERPNext «скамейкой» (bench).
```bash
# Вариант 1: pipx
pipx install frappe-bench

# Вариант 2: в виртуальном окружении
python3 -m venv ~/bench-env
source ~/bench-env/bin/activate
pip install frappe-bench
```

## 3. Инициализировать bench-площадку

```bash
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
```

## 4. Создать новый сайт

```bash
bench new-site <SITE_NAME> \
  --admin-password <ADMIN_PASSWORD> \
  --db-root-password <DB_ROOT_PASSWORD>
```

## 5. Подключить приложение ferum_customs

```bash
bench get-app https://github.com/Dmitriyrus99/ferum_customs.git --branch main
```

## 6. Установить приложение на сайт

```bash
bench --site <SITE_NAME> install-app ferum_customs
```

## 7. Собрать фронтенд-ассеты и запустить

```bash
bench build
bench restart
```

После этого приложение будет доступно по адресу http://localhost:8000
или на указанном порту. Войдите под учётной записью Administrator и паролем,
который вы задали при создании сайта.
