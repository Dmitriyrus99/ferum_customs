task: "Исправь импорты и зависимости в Telegram FSM-модуле и тестах"
description: |
  После рефакторинга FSM-модуля и тестов возникли ошибки:
  
  ❌ `pre-commit` не может запустить хуки, возможно, из-за несогласованного состояния `.pre-commit-config.yaml` или отсутствия установки

  ❌ `pytest` завершился с ошибкой импорта модуля `aiogram`

  Задача:
  1. Проверь, корректно ли настроены зависимости в `requirements.txt` и `requirements-dev.txt`. Убедись, что `aiogram` и `pytest` там присутствуют.
  2. Проверь, что `__init__.py` присутствует во всех пакетах (`telegram_bot`, `fsm`, `tests`), чтобы Python корректно импортировал модули.
  3. Приведи импорты в `test_fsm_conversation.py` и `test_fsm.py` в соответствие с файловой структурой (относительные пути или корректный абсолютный путь от корня проекта).
  4. Проверь, что `start_handler` и `SomeState` действительно существуют и доступны из указанных модулей:
     - `from telegram_bot.handlers import start_handler`
     - `from telegram_bot.fsm.states import SomeState`
  5. Приведи `test_fsm_start_handler` к рабочему виду: либо реализуй мок `bot`, либо убери его, если он не используется (ruff F841).
  6. Добавь инструкции в `README.md` для локального запуска тестов и pre-commit.

goals:
  - Устранить ошибки импорта `aiogram` и модулей FSM
  - Настроить структуру проекта так, чтобы `pytest` работал без ошибок
  - Обеспечить работоспособность `pre-commit` и `ruff`

tools:
  - pytest
  - ruff
  - pre-commit
