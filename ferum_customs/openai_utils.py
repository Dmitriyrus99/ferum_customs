from __future__ import annotations

import openai

from ferum_customs.config.settings import settings

# Ensure api_key is set correctly
if not settings.openai_api_key:
    raise ValueError("OpenAI API key is not set.")
openai.api_key = settings.openai_api_key

def complete_code(prompt: str) -> str:
    """Return a Python code completion for the given fragment."""
    
    if not isinstance(prompt, str):
        raise TypeError("Prompt must be a string.")

    response = openai.ChatCompletion.create(
        model="gpt-4",  # Corrected model name
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an experienced programmer. Write code carefully, only in Python."
                ),
            },
            {
                "role": "user",
                "content": f"Complete the following code fragment:\n\n{prompt}\n\n# Continue the code:",
            },
        ],
        temperature=0.2,
        max_tokens=400,
        stop=["\n\n", "# End"],  # Updated stop sequence for consistency
        stream=False,
    )
    
    content = response["choices"][0]["message"]["content"]
    return content.strip()
