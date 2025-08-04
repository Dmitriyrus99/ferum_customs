import importlib


def test_basic_imports() -> None:
    """Ensure that core dependencies are available for import.

    This test checks that the specified core modules can be imported successfully.
    If any module is not found, an AssertionError will be raised. All specified modules
    should be importable without errors.
    """
    modules: list[str] = ["aiogram", "fastapi", "requests_oauthlib"]

    for module in modules:
        try:
            importlib.import_module(module)
            print(f"Module '{module}' imported successfully.")
        except ImportError as exc:
            raise AssertionError(f"Module '{module}' not found: {exc}") from exc
