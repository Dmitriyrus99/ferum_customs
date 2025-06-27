# 🧠 Codex Task: Аудит Python-проекта `ferum_customs`

## Цель

Провести анализ структуры и кода проекта `ferum_customs`, чтобы подготовить рекомендации по CI, тестам и архитектуре. **Файлы изменять не нужно.**

---

## Задачи

1. **Структура**
   - Найти точку входа (`main.py`, `bot_service.py`)
   - Определить логические слои: API, бизнес-логика, FSM
   - Определить использование `ferum_customs/` и `telegram_bot/`

2. **Зависимости**
   - Прочитать `requirements.txt`, `requirements-dev.txt`
   - Указать ключевые библиотеки и лишние/устаревшие

3. **Тесты**
   - Проверить покрытие: `tests/unit/`, `integration/`, `e2e/`
   - Проверить наличие `pytest`, `conftest.py`, фикстур

4. **Стиль**
   - Есть ли `ruff`, `mypy`, `flake8`, `black`
   - Как они вызываются (`setup.sh`, `pre-commit`)

---

## Результат

Markdown-отчёт:

```markdown
## 📊 Аудит проекта ferum_customs

### 📁 Структура
- bot_service.py → Telegram FSM
- api.py → FastAPI endpoints
...

### 📦 Зависимости
- ✅ fastapi
- ✅ aiogram
- ⚠️ requests-oauthlib — не используется

### 🧪 Тесты
- ✅ Найдено: 12 файлов
- ✅ e2e покрытие
- ❌ отсутствует тест на payroll logic

### 💡 Рекомендации
- ➕ Добавить тесты FSM-сценариев
- ➕ Настроить pre-commit с ruff, black
- ⚙️ Разделить конфигурации API и Telegram FSM
