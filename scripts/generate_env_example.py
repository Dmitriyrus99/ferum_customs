#!/usr/bin/env python3
"""Generate .env.example based on pydantic Settings."""

from ferum_customs.config.settings import Settings
import os


def main() -> None:
    """Main function to generate .env.example file."""
    settings = Settings(telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""))
    fields = settings.model_fields
    lines = ["# Generated .env.example"]
    
    for name, _ in fields.items():
        key = name.upper()
        default = getattr(settings, name, "")
        value = default if default is not None else ""
        lines.append(f"{key}={value}")

    content = "\n".join(lines) + "\n"
    
    try:
        with open(".env.example", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ .env.example generated.")
    except IOError as e:
        print(f"❌ Error writing .env.example: {e}")


if __name__ == "__main__":
    main()
