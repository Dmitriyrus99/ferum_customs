# 🧠 Codex CLI Task: Аудит проекта `ferum_customs`

## 📌 Цель

Провести технический аудит Python-проекта `ferum_customs`, чтобы подготовить CI, автотесты и улучшения архитектуры. Не менять файлы — только анализировать.

---

## 📁 Задачи

1. **Структура проекта**
   - Определи точку входа (`main.py`, `app.py`)
   - Перечисли модули и директории (`api/`, `handlers/`, `services/`)
   - Отметь конфигурации (`config.py`, `.env`, `logging`, `constants`)

2. **Зависимости**
   - Прочитай `requirements.txt` или `pyproject.toml`
   - Отметь основные библиотеки и dev-зависимости
   - Проверь наличие устаревших или дублирующихся пакетов

3. **Тесты**
   - Найди `tests/`, опиши структуру
   - Уточни, есть ли `pytest`, `test_*.py`, мок-объекты, клиент API

4. **Линтеры и стиль**
   - Есть ли `ruff`, `black`, `flake8`
   - Как вызывается (из `setup.sh`, `pre-commit`, `Makefile`)
   - Найди конфиги: `ruff.toml`, `pyproject.toml`, `.flake8`

5. **Вывод в Markdown**
   Представь результат в формате:

```markdown
## 📦 ferum_customs — Аудит Codex

### Структура
- main.py ✅
- handlers/ ✅ FSM
- config.py ✅

### Зависимости
- ✅ fastapi, aiogram
- ⚠️ requests-oauthlib (не используется)

### Тесты
- ✅ tests/test_imports.py
- ❌ нет бизнес-логики

### Стиль
- ✅ ruff найден
- ❌ нет black

### Рекомендации
- ➕ Написать тесты для FSM и REST API
- ➕ Добавить pre-commit
- ⚙️ Вынести переменные в `.env`
