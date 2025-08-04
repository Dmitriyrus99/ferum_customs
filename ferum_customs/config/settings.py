from typing import Optional

from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot API token
    telegram_bot_token: SecretStr

    # Frappe/ERPNext settings
    site_name: str | None = None  # Name of the Frappe site
    admin_password: SecretStr | None = None  # Admin password for Frappe site

    # URL for Frappe API (optional override)
    frappe_url: str | None = None  # Base URL for Frappe API

    # OpenAI API key for optional integrations
    openai_api_key: SecretStr | None = None  # API key for OpenAI integrations

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
