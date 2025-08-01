from pydantic import BaseSettings, SecretStr
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot API token
    telegram_bot_token: SecretStr

    # Frappe/ERPNext settings
    site_name: Optional[str] = None  # Name of the Frappe site
    admin_password: Optional[SecretStr] = None  # Admin password for Frappe site

    # URL for Frappe API (optional override)
    frappe_url: Optional[str] = None  # Base URL for Frappe API

    # OpenAI API key for optional integrations
    openai_api_key: Optional[SecretStr] = None  # API key for OpenAI integrations

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
