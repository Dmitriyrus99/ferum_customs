# План доработки проекта до production-ready

Ниже приведён пошаговый план доведения проекта **Ferum Customs** до состояния готовности к боевому запуску.

## 1. Документация
- Унификация RU/EN‑документации:
  - Перевести ключевые разделы (overview, docker_setup, INSTALL.md) на английский.
  - Создать `README_EN.md` и добавить переключатель между версиями.
- Добавление prod‑профиля конфигурации:
  - Добавить `.env.prod.example` с рекомендациями по SSL, доменам, security‑headers.
  - Описать zero‑downtime‑миграции и апгрейд.
- Шаблоны релиза и чеклисты:
  - Обновить CHANGELOG для соблюдения semantic versioning.
  - Добавить ISSUE_TEMPLATE и PR_TEMPLATE с пунктами проверки перед релизом.
- Runbook по бэкапам и восстановлению:
  - Детализировать процедуру backup/restore с примерами systemd‑timer/cron.
- Deployment Guide:
  - Описать деплой в Kubernetes (helm-chart) или Docker Swarm.

## 2. Тестирование и качество кода
- Security-сканинг зависимостей через Bandit и `npm audit`/`yarn audit`.
- Нагрузочное и E2E-тестирование: добавить сценарии Locust и E2E на Playwright/Puppeteer.
- Покрытие тестов: установить порог покрытия (не менее 80%).
- Строгие проверки типов (`mypy --strict`) и линтинг для JS (ESLint/Prettier).

## 3. CI/CD и релизы
- Docker image build & push: добавить шаги CI для сборки и публикации образов.
- Автоматизация релизов: draft-режим с CHANGELOG на основе PR.
- Защита ветки main: require passing CI, код-ревью, tag-релиз.

## 4. Безопасность и мониторинг
- TLS/HTTPS и HSTS: подготовить nginx-конфиг с Certbot.
- Интеграция Sentry для backend exceptions и уведомлений.
- Мониторинг: добавить Prometheus exporter, примеры Grafana-дашбордов и правил alertmanager.
- Жесткие security headers (CSP, X-Frame, X-Content-Type).

## 5. Производительность и масштабирование
- Анализ slow_query_log и доработка индексов БД.
- Кеширование и CDN: рекомендации по Redis, Varnish, CDN для статических файлов.
- Benchmarking: нагрузочные тесты и сбор отчетов.
- Горизонтальное масштабирование: настройка кластера Frappe workers за LB.

## 6. Обслуживание и поддержка
- Runbook рутинных операций: очистка кэша, миграции, удаление устаревших файлов.
- Шаблон post-mortem для инцидентов.
- Документирование контактов и SLA в SUPPORT.md.

---

*Этот файл был автоматически создан по запросу в рамках планирования production-ready.*
