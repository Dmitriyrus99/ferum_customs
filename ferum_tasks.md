# ✅ Task List для проекта `ferum_customs`

## Основные задачи по итогам аудита:

- [ ] Проверить и обновить `.env`, `docker-compose.override.yml` под прод/дев
- [ ] Создать суперпользователя `postgres`, назначить роль `frappe`
- [ ] Исправить ошибки удаления `drop-site` вручную
- [x] Очистить `.swp` файлы, валидировать JSON
- [ ] Убедиться, что `ferum_customs` подключено в `apps.json`, Dockerfile
- [ ] Завершить установку `ferum_customs` через `install_app`
- [ ] Установить `erpnext` и `payments` перед кастомным приложением
- [ ] Проверить volumes и параметры подключения БД в Docker
- [ ] Проверить `site_config.json` на валидность
- [ ] Использовать `vi` или `vim` вместо `nano`
- [x] Настроить CI: pytest, flake8, разделение тестов
- [x] Проверить `get_notification_config` в `hooks.py`
- [x] Актуализировать `fixtures`, удалить лишнее
- [ ] Проверить `yarn run production`, зависимости node
- [x] Удалить неиспользуемые зависимости (`openai`)
- [x] Написать `README.md`, `SECURITY.md`, `install.md`
- [x] Проверить структуру `service_*` модулей
- [x] Обеспечить запуск `bench` из правильной среды
- [x] Настроить `tests/unit`, `tests/integration`, `tests/e2e`

