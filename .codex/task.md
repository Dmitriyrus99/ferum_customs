# .codex/tasks/standardize_fixtures_and_readme.yaml

name: Приведение fixtures к стандарту + описание модуля
description: |
  Привести структуру фикстур к списку конкретных файлов, а также дополнить README.md
  кратким описанием кастомного Frappe-приложения.

steps:
  - name: Обновить fixtures в hooks.py
    description: |
      В файле `ferum_customs/hooks.py` заменить текущий блок `fixtures = [...]`,
      в котором используется фильтр по doctype и именам, на явный список файлов.
      Использовать фактический список .json-файлов из директории `ferum_customs/fixtures/`.
    acceptance:
      - Фикстуры указаны как список строк, например:
        ```python
        fixtures = [
            "Custom Field",
            "Property Setter",
            "Custom DocPerm",
            ...
        ]
        ```
      - Используются только существующие JSON-файлы

  - name: Добавить описание в README.md
    description: |
      В корне репозитория отредактировать (или создать) `README.md`.
      Добавить описание `ferum_customs` как полнофункционального кастомного приложения для Frappe.
    content: |
      ## Ferum Customs

      Кастомное приложение для ERPNext/Frappe, предназначенное для автоматизации работы сервисной компании
      в области противопожарной безопасности.

      ### Основные возможности:
      - Управление заявками и проектами
      - Автоматизация актов, маршрутов, графиков обслуживания
      - Поддержка FSM-бота для Telegram
      - Расширения DocType, Workflow, Permission
      - Интеграция с Google Drive, аналитикой, CI/CD

      ### Требования:
      - Frappe >= 14
      - PostgreSQL / MariaDB
      - Python 3.10+

    acceptance:
      - README содержит название, краткое описание, список возможностей и требования

  - name: Commit
    description: |
      Зафиксировать изменения в hooks.py и README.md в одном коммите с сообщением:
      `🔧 Приведена структура fixtures и добавлен README`

labels:
  - frappe
  - fixtures
  - documentation
