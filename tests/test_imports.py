import importlib


def test_basic_imports() -> None:
    """Ensure that core dependencies are available for import."""

    for module in ("aiogram", "fastapi", "requests_oauthlib"):
        try:
            _ = importlib.import_module(module)
        except Exception as exc:  # pragma: no cover - fails only if missing
            raise AssertionError(f"Не найден модуль {module}: {exc}") from exc
