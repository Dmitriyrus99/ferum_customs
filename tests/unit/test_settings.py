from pathlib import Path
from _pytest.monkeypatch import MonkeyPatch
from ferum_customs.config.settings import Settings

def test_settings_env_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test loading settings from .env file and ignoring extra variables."""
    env_content = (
        "TELEGRAM_BOT_TOKEN=token123\nSITE_NAME=mysite\nEXTRA_VAR=ignored"
    )
    tmp_env = tmp_path / ".env"
    tmp_env.write_text(env_content)
    monkeypatch.chdir(tmp_path)

    settings: Settings = Settings(_env_file=tmp_env)  # Assuming Settings can load from a file
    assert settings.telegram_bot_token == "token123", "Expected TELEGRAM_BOT_TOKEN to be 'token123'"
    assert settings.site_name == "mysite", "Expected SITE_NAME to be 'mysite'"
    assert not hasattr(settings, "EXTRA_VAR"), "Expected EXTRA_VAR to be ignored"

    # Additional tests could be added here for edge cases
