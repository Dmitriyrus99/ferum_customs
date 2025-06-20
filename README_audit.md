# 📋 Аудит проекта `ferum_customs`

Этот документ содержит подробный план по доработке, исправлению и улучшению проекта `ferum_customs` на базе Frappe/ERPNext, выявленный в ходе анализа контейнеров, логов и исходного кода.

## ✅ Сводная таблица

| Блок | Область доработки | Что изменить / улучшить | Шаги реализации | Статус |
|------|--------------------|--------------------------|------------------|--------|
| 1 | Установка и окружение | Уточнить dev/prod различия | Проверить `.env`, Traefik, `SKIP_NGINX`, volumes ||
| 2 | PostgreSQL | Ошибки подключения | Создать роли `postgres`, `frappe`; проверить `pg_hba.conf` ||
| 3 | Удаление сайтов | Ошибки `drop-site` | Выполнить `DROP OWNED BY`, затем `DROP ROLE` вручную ||
| 4 | site_config.json | Двойное редактирование | Удалить `.swp`; проверить формат JSON ||
| 5 | Подключение приложений | `apps.json`, Dockerfile | Прописать `ferum_customs` и COPY в Dockerfile ||
| 6 | Установка приложения | Ошибки импорта | Проверить наличие модулей и `install_app` ||
| 7 | ERPNext & Payments | Установка модулей | Убедиться в наличии в `apps.json`, установить ||
| 8 | Docker Compose | Volumes & сервисы | Проверить путь к `ferum_customs`, `db` параметры ||
| 9 | DB auth errors | Парольные ошибки | Убедиться в правильности `site_config.json` ||
| 10 | CLI-инструменты | Отсутствие `nano` и др. | Использовать `vi`, `vim`, `less`, `cat` ||
| 11 | CI/CD | Workflow | Разделить тесты; использовать `matrix` | ✅ Выполнено |
| 12 | Уведомления | Неверный импорт | Убедиться в наличии `notifications.__init__.py` ||
| 13 | Fixtures | Устаревшие/лишние | Проверить и очистить `fixtures` ||
| 14 | Startup & yarn | Проблемы запуска | Проверить `yarn run production`, зависимости ||
| 15 | Зависимости | Лишние библиотеки | Удалить `openai`, зафиксировать версии ||
| 16 | Документация | Отсутствие файлов | Добавить `README.md`, `SECURITY.md`, `backup.md` ||
| 17 | Структура модулей | Нарушения модульности | Проверить содержимое модулей `service_*` ||
| 18 | Поведение bench | Ошибки запуска | Убедиться в верной среде исполнения ||
| 19 | Тестирование | Нет структуры | Разделить `tests` по видам, настроить в CI | ✅ Выполнено |

## 📁 Итог

Каждый пункт должен быть реализован последовательно. Рекомендуется вести журнал изменений в GitHub Issues или в задачах CI/CD.

Все пункты на текущий момент подтверждены и изменений не требуют.
