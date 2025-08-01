import importlib
from typing import List


def test_basic_imports() -> None:
    """Ensure that core dependencies are available for import.

    This test checks that the specified core modules can be imported successfully.
    If any module is not found, an AssertionError will be raised.
    """
    modules: List[str] = ["aiogram", "fastapi", "requests_oauthlib"]

    for module in modules:
        try:
            _ = importlib.import_module(module)
        except ImportError as exc:
            raise AssertionError(f"Module '{module}' not found: {exc}") from exc
