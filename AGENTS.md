Ниже — «AGENTS.md» (на русском) — файл-инструкция, который кладётся в корень репозитория. Он расскажет Codex-агенту, **как поднять окружение, запускать тесты и оформлять PR для проекта с Docker-сборкой ferum\_customs**.

````markdown
# AGENTS.md — инструкции для Codex

## ☑️  Цель
Работая с этим репозиторием, агент должен
1. **Поднять dev-окружение** в Docker (`frappe`, `mariadb`, `redis*`).
2. Исполнять Python/JS-тесты и линтеры перед коммитом.
3. Соблюдать описанные ниже соглашения по коду и PR.

## 🐳  Быстрый старт окружения
```bash
# Шаг 1 — скопируй пример переменных и задай пароли/домен
cp .env.example .env      # затем отредактируй файл .env
# Файл .env содержит BENCH_TAG, MARIADB_TAG, REDIS_TAG, SITE_NAME и паролиfileciteturn1file1

# Шаг 2 — собери и запусти контейнеры
docker compose up -d --build            # ждём статус Up/healthyfileciteturn1file0
````

Контейнер `frappe` слушает на `http://localhost:8000` (см. healthcheck в *docker-compose.yml*).fileciteturn1file2

## 🔧  Основные команды в контейнере `frappe`

```bash
# shell внутри контейнера
docker compose exec frappe bash

# тесты Python (pytest)
bench --site $SITE_NAME run-tests --app ferum_customs

# линтеры и тип-чеки
bench run npm run lint
bench run npm run type-check
```

## ✅  Перед каждым коммитом

1. Убедись, что `pytest`, `lint`, `type-check` завершаются без ошибок.
2. Выполни `git add -p && git commit -m "<type>: <summary>"`
   Используем **Conventional Commits** (`feat:`, `fix:`, `chore:`…).

## 🗂  Структура проекта (выдержка)

````
.
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── docker-entrypoint.sh
└── apps/
    └── ferum_customs/     # исходники приложения
```fileciteturn1file3

## 📐  Соглашения по коду
| Язык | Форматирование | Проверки |
|------|----------------|----------|
| Python | **black** 23.x | pytest |
| JS/TS | **prettier**   | eslint, type-check |

## 🔄  Добавление зависимостей
- **Python**: пропиши пакет в `apps/ferum_customs/requirements.txt` и запусти `bench setup requirements`.
- **JS**: `bench run yarn add <pkg>` — коммитим `package.json`, `yarn.lock`.

## 📝  Оформление PR
- Краткий заголовок по Conventional Commits.  
- В описании: _что сделано_ + _как проверить_.  
- Если PR меняет окружение (Dockerfile, compose, bench setup), укажи шаги по обновлению.

---

**Эти правила обязательны для всех файлов в репозитории.**  
Codex-агент должен отказывать или запрашивать уточнения, если инструкции нарушены.
````

Файл можно сохранить как `AGENTS.md`; после этого Codex будет автоматически следовать описанным процедурам.

