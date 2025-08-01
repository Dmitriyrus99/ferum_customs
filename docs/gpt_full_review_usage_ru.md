# Запуск скрипта `gpt_full_review.py`

Этот скрипт автоматически запускает GPT‑ревью выбранных файлов репозитория.
Он использует OpenAI API, поэтому требуется ключ `OPENAI_API_KEY`.

## Зависимости

- Python 3.10+
- Пакеты: `openai`, `tiktoken`, `rich`, `pathspec`

Установить зависимости можно так:

```bash
pip install openai tiktoken rich pathspec
```

## Минимальный пример

```bash
export OPENAI_API_KEY=<ваш ключ>
python3 scripts/gpt_full_review.py
```

По умолчанию сканируются файлы, перечисленные в `review_include_list.txt` в
корне репозитория. Результаты сохраняются в директории `code_review/`.

## Полный список опций

Для просмотра доступных аргументов выполните:

```bash
python3 scripts/gpt_full_review.py --help
```
