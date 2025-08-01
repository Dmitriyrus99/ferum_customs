import importlib


def test_basic_imports() -> None:
    """Ensure that core dependencies are available for import."""

    for module in ("aiogram", "fastapi", "requests_oauthlib"):
        try:
            _ = importlib.import_module(module)
        except ImportError as exc:  # More specific exception
            raise AssertionError(f"Module {module} not found: {exc}") from exc
