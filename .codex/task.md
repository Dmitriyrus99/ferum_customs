# .codex/tasks/add_missing_system_fixtures.yaml

name: Добавить отсутствующие системные DocTypes в fixtures
description: |
  Проверить наличие критически важных системных DocTypes (например, Custom Role, Client Script)
  в списке fixtures приложения ferum_customs, и при отсутствии — добавить их.

steps:
  - name: Проверить существующие фикстуры
    description: |
      Проанализировать папку `ferum_customs/fixtures/` и текущий список `fixtures` в `hooks.py`,
      чтобы определить, какие стандартные системные типы данных отсутствуют.
    acceptance:
      - Выявлены все отсутствующие системные DocTypes (например: "Custom Role", "Client Script", "Custom DocPerm")

  - name: Обновить fixtures в hooks.py
    description: |
      Добавить в список `fixtures = [...]` отсутствующие, но необходимые DocTypes
      для корректной работы кастомной логики и ролей.
    acceptance:
      - "Custom Role" и "Client Script" присутствуют в списке fixtures
      - Все добавленные DocTypes действительно существуют в проекте (их JSON-файлы находятся в `fixtures/`)

  - name: Commit
    description: |
      Сохранить изменения с комментарием:
      `📦 Добавлены отсутствующие системные DocTypes в fixtures`

labels:
  - frappe
  - fixtures
  - roles
  - permissions
