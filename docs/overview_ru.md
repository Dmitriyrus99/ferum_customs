# Руководство по архитектуре и разработке Ferum Customizations

## 1. Цель и обзор проекта

"Ferum Customizations" расширяет платформу Frappe/ERPNext для управления сервисными заявками и проектами. Задачи проекта:

- **Автоматизация** документооборота и учёта.
- **Прозрачность** процессов от создания заявки до её закрытия.
- **Контроль** сроков и качества выполнения работ.
- **Интеграция** с Telegram‑ботом для быстрого создания заявок и уведомлений.

## 2. Архитектура и технологический стек

### 2.1 Серверная часть

- Frappe Framework v15
- Python 3.10+
- MariaDB (основная СУБД)
- Redis для фоновых задач и кэша
- Frappe REST API, FastAPI для кастомных эндпоинтов

### 2.2 Клиентская часть

- UI Frappe (Desk, веб‑формы)
- JavaScript (ES6+), jQuery, HTML5, CSS3
- Node.js для сборки ассетов

### 2.3 Инструменты и CI/CD

- Docker и Docker Compose
- GitHub Actions для тестов и линтеров
- pre‑commit, Ruff, ESLint/Prettier

## 3. Ключевые компоненты и структура

### 3.1 Основные директории

- `ferum_customs/doctype/` — определения DocType и связанные файлы
- `ferum_customs/custom_logic/` — бизнес‑логика, вынесенная из DocType
- `ferum_customs/permissions/` — динамические правила доступа
- `ferum_customs/fixtures/` — данные для начальной настройки
- `telegram_bot/` — интеграция с Telegram‑ботом
- `hooks.py` — связывает код с событиями Frappe

### 3.2 Ключевые DocTypes

- **Service Project** — контейнер для заявок
- **Service Object** — обслуживаемое оборудование или место
- **Service Request** — сервисная заявка
- **Service Report** — отчёт о выполненных работах
- **Custom Attachment** — расширенные вложения

### 3.3 Интеграция с Telegram‑ботом

Модульная архитектура с использованием `Router` из `aiogram`. Для каждой роли свой роутер и набор хендлеров. Аутентификация происходит по номеру телефона.

## 4. Роли пользователей и права доступа

- **Администратор** — полный доступ
- **Руководитель проекта** — управление проектами и заявками
- **Офис‑менеджер** — создание заявок от клиентов
- **Инженер** — работа с назначенными заявками и отчётами
- **Клиент/Заказчик** — видит только свои заявки
- **Главный бухгалтер** — доступ к финансовым документам

Изоляция данных клиентов реализована через `permission_query_conditions` и `User Permission`.

## 5. Основной функционал

### 5.1 Жизненный цикл Service Request

1. Создание заявки
2. Назначение ответственного инженера
3. Работа по заявке
4. Создание Service Report
5. Закрытие заявки

### 5.2 Управление документами

- Автоматическая нумерация документов
- Контроль связей между документами

### 5.3 Соглашения по коду

- Серверная логика через хуки в `hooks.py` и модули в `custom_logic`
- Константы в `constants.py`
- Клиентские скрипты в `.js` файлах DocType
- Использование `pre-commit` для форматирования и проверки

## 6. Локальная разработка и тестирование

### 6.1 Настройка окружения

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

# Настройка переменных среды для Python-приложения
Скопируйте `.env.example` в `.env` и укажите необходимые переменные:

```bash
cp .env.example .env
# отредактируйте .env (TELEGRAM_BOT_TOKEN, SITE_NAME, ADMIN_PASSWORD и т.д.)
```

Переменные автоматически загружаются через Pydantic Settings.

Установите зависимости внутри контейнера и инсталлируйте приложение:

```bash
docker compose exec frappe bash
# Код приложения уже доступен в контейнере (см. docker-compose.yml)
bench --site ${SITE_NAME} install-app ferum_customs
```

### 6.2 Запуск тестов

```bash
# Все тесты приложения
bench --site ${SITE_NAME} run-tests --app ferum_customs

# Тесты конкретного модуля
bench --site ${SITE_NAME} run-tests --module "Service Request"
```

## 7. Конфигурация ассистента

```yaml
fix_bot:
  log_sources:
    - cmd: "docker compose logs --no-color --since 5m"
      interval: "*/2 * * * *"   # каждые 2 минуты
  redis_default_url: "redis://:<REDIS_PASSWORD>@redis-cache:6379"
  mysql_wait_timeout: "300s"
  notify_channels:
    - telegram: "@ferum_ops_chat"
  auto_fix_limit_per_hour: 3
```

## 8. Выходные артефакты

- `action_plan_<timestamp>.json` – что сделано и почему.
- `fix_bot_report.md` – сводка за сутки (успешно/неуспешно).
