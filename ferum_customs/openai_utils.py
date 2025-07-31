from __future__ import annotations

import openai

from ferum_customs.config.settings import settings

openai.api_key = settings.openai_api_key or openai.api_key


def complete_code(prompt: str) -> str:
    """Return a Python code completion for the given fragment."""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты опытный программист. Пиши код аккуратно, только на языке Python."
                ),
            },
            {
                "role": "user",
                "content": f"Заверши следующий фрагмент кода:\n\n{prompt}\n\n# Допиши продолжение кода:",
            },
        ],
        temperature=0.2,
        max_tokens=400,
        stop=["\n\n", "# Конец"],
        stream=False,
    )
    content = response["choices"][0]["message"]["content"]
    return str(content).strip()
