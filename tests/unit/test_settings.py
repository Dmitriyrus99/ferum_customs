from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from ferum_customs.config.settings import Settings


def test_settings_env_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Test loading settings from .env file and ignoring extra variables.

    This test verifies that the Settings class correctly loads
    environment variables from a .env file and ignores any
    extra variables that are not defined in the Settings class.
    """
    env_content = "TELEGRAM_BOT_TOKEN=token123\nSITE_NAME=mysite\nEXTRA_VAR=ignored"
    tmp_env = tmp_path / ".env"
    tmp_env.write_text(env_content)
    monkeypatch.chdir(tmp_path)

    settings: Settings = Settings(
        _env_file=tmp_env
    )  # Assuming Settings can load from a file
    assert (
        settings.telegram_bot_token == "token123"
    ), "Expected TELEGRAM_BOT_TOKEN to be 'token123'"
    assert settings.site_name == "mysite", "Expected SITE_NAME to be 'mysite'"
    assert not hasattr(settings, "EXTRA_VAR"), "Expected EXTRA_VAR to be ignored"

    # Additional tests for edge cases
    # Test for missing TELEGRAM_BOT_TOKEN
    env_content_missing = "SITE_NAME=mysite"
    tmp_env.write_text(env_content_missing)
    settings = Settings(_env_file=tmp_env)
    assert (
        settings.telegram_bot_token is None
    ), "Expected TELEGRAM_BOT_TOKEN to be None when not set"

    # Test for invalid values (if applicable)
    # Add more tests as necessary
