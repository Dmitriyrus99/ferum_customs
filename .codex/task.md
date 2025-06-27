# .codex/tasks/fix-fastapi-dependency.yaml

name: Исправить ошибку импорта fastapi при запуске pytest
description: |
  При запуске тестов возникает ошибка импорта fastapi. Требуется добавить fastapi в зависимости,
  убедиться в его наличии в среде и обновить инструкции по установке зависимостей.

steps:
  - name: Проверить зависимости
    description: |
      Убедиться, что fastapi указан в `requirements.txt` и/или `pyproject.toml` (если используется poetry/pip-tools).
      При необходимости — добавить строку:
        fastapi==0.110.0
    acceptance:
      - fastapi присутствует в requirements.txt
      - версия соответствует остальной совместимости проекта

  - name: Обновить инструкции установки
    description: |
      Проверить, что README.md и install.md (если есть) содержат инструкции по установке зависимостей,
      включая fastapi и aiogram. При отсутствии — добавить блок:
        pip install -r requirements.txt
    acceptance:
      - README.md содержит актуальные команды установки

  - name: Подтвердить тесты
    description: |
      Убедиться, что после установки зависимостей `pytest -q` запускается без ошибок fastapi.
    acceptance:
      - pytest проходит стадию импорта без ошибок fastapi

  - name: Commit
    description: |
      Закоммитить изменения с сообщением:
        🔧 Добавлена зависимость fastapi в requirements.txt и обновлена документация

labels:
  - dependencies
  - fastapi
  - testing
  - pytest
