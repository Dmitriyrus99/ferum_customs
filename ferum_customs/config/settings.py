from pydantic import BaseSettings  # Correct import for BaseSettings
from pydantic_settings import SettingsConfigDict  # Ensure this is necessary

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot API token
    telegram_bot_token: str

    # Frappe/ERPNext settings
    site_name: str | None = None
    admin_password: str | None = None

    # URL for Frappe API (optional override)
    frappe_url: str | None = None

    # OpenAI API key for optional integrations
    openai_api_key: str | None = None

    class Config:  # Use Config class instead of model_config
        env_file = [".env", ".env.example"]
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
