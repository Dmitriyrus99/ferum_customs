name: Исправление форматирования импортов в тестах
goal: Обеспечить прохождение pre-commit хуков (ruff) и успешный запуск CI
tasks:
  - description: Применить автоформатирование ruff к указанным тестовым файлам
    tools:
      - ruff
    files:
      - tests/test_imports.py
      - tests/unit/test_fsm.py
    commands:
      - ruff check tests/test_imports.py --fix
      - ruff check tests/unit/test_fsm.py --fix
  - description: Убедиться, что после исправлений ruff не возвращает ошибок
    run: ruff check . --output-format=full
  - description: Убедиться, что все хуки pre-commit проходят без ошибок
    run: pre-commit run --all-files
  - description: Запустить тесты и убедиться в их корректности
    run: pytest -q
notes:
  - Эти действия направлены на прохождение линтинга и CI
  - Не требуется менять бизнес-логику — только форматирование импортов
