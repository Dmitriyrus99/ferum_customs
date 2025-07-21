from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # Telegram Bot API token
    telegram_bot_token: str = ""

    # Frappe/ERPNext settings
    site_name: str | None = None
    admin_password: str | None = None

    # URL for Frappe API (optional override)
    frappe_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.example"],
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
