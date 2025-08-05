# 🎯 Цель:

Создать изолированную и воспроизводимую среду разработки и запуска для проекта, состоящего из следующих компонентов:

- Frappe/ERPNext (версия 14)
- FastAPI (0.110.*)
- Aiogram (3.*)
- requests + oauthlib
- Docker и docker-compose

## 📌 Задачи:

1. [✅] Создать структуру проекта:
   
   ```
   project/
   ├─ docker/
   │  ├─ Dockerfile.frappe
   │  ├─ Dockerfile.fastapi
   │  ├─ docker-compose.yml
   │  └─ .env
   └─ src/
      └─ (исходный код FastAPI/Aiogram)
   ```

2. [✅] Настроить Dockerfile для Frappe/ERPNext (`docker/Dockerfile.frappe`):
   - Использовать официальный образ: `frappe/erpnext:version-14`
   - Установить недостающие системные зависимости (curl, git, python3-dev и др.)

3. [✅] Создать Dockerfile для FastAPI + Aiogram (`docker/Dockerfile.fastapi`):
   - Базовый образ: `python:3.11-slim`
   - Установить зависимости:
     - `fastapi==0.110.*`
     - `uvicorn[standard]==0.29.*`
     - `aiogram==3.*`
     - `requests==2.*`
     - `oauthlib==3.*`
     - `python-dotenv==1.0.*`
   - Указать команду запуска Uvicorn.

4. [✅] Сконфигурировать `docker-compose.yml`:
   - Связать два сервиса: `frappe` и `fastapi`
   - Настроить порты:
     - `frappe`: 8000 (Web), 9000 (SocketIO)
     - `fastapi`: 8100 → 8000

5. [✅] Настроить переменные окружения (`docker/.env`):
   - Общие: `PYTHONUNBUFFERED`, `TZ`
   - Для Frappe: `SITE_NAME`, `MYSQL_ROOT_PASSWORD`, `REDIS_*`, `DB_HOST`
   - Для FastAPI/Aiogram: `FASTAPI_HOST`, `FASTAPI_PORT`, `TELEGRAM_TOKEN`, и другие ключи (OAuth, API и т.д.)

6. [✅] Проверить совместимость всех версий:
   - Убедиться, что версии Frappe и ERPNext соответствуют друг другу.
   - Использовать `pip check` и `pip freeze` внутри контейнера FastAPI.
   - Убедиться, что синтаксис Aiogram соответствует выбранной версии 3.x.

7. [✅] Реализовать команды запуска и логирования:
   - `docker compose build`
   - `docker compose up -d`
   - `docker compose logs -f frappe`
   - `docker compose logs -f fastapi`

8. [✅] Обеспечить безопасность и воспроизводимость:
   - Хранить `.env` вне системы контроля версий.
   - Зафиксировать версии пакетов (`requirements.txt` или `Dockerfile`).
   - При необходимости — предусмотреть миграции (`bench migrate`, `Alembic`).

---

🔁 Требование к выполнению:

> После завершения каждого пункта и проверки его выполнения, отметить его как завершённый в документе (например, проставить ✅ или ✔ рядом с пунктом).

