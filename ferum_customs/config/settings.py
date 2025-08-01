from pydantic import BaseSettings, SecretStr

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot API token
    telegram_bot_token: SecretStr

    # Frappe/ERPNext settings
    site_name: str | None = None
    admin_password: SecretStr | None = None

    # URL for Frappe API (optional override)
    frappe_url: str | None = None

    # OpenAI API key for optional integrations
    openai_api_key: SecretStr | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
