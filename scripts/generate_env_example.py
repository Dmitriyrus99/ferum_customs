#!/usr/bin/env python3
"""Generate .env.example based on pydantic Settings."""

from ferum_customs.config.settings import Settings


def main() -> None:
    settings = Settings(telegram_bot_token="")
    fields = settings.model_fields
    lines = ["# Generated .env.example"]
    for name, field in fields.items():
        key = name.upper()
        default = getattr(settings, name, "")
        value = default if default is not None else ""
        lines.append(f"{key}={value}")

    content = "\n".join(lines) + "\n"
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ .env.example generated.")


if __name__ == "__main__":
    main()
