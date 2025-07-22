from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from ferum_customs.config.settings import Settings


def test_settings_env_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    """Проверка загрузки настроек из .env и игнорирование лишних переменных."""
    env_content = (
        "TELEGRAM_BOT_TOKEN=token123\n" "SITE_NAME=mysite\n" "EXTRA_VAR=ignored"
    )
    tmp_env = tmp_path / ".env"
    tmp_env.write_text(env_content)
    monkeypatch.chdir(tmp_path)

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "token123")
    monkeypatch.setenv("SITE_NAME", "mysite")

    settings = Settings(telegram_bot_token="token123")
    assert settings.telegram_bot_token == "token123"
    assert settings.site_name == "mysite"
    assert not hasattr(settings, "EXTRA_VAR")
