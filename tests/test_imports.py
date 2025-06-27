import pytest

def test_basic_imports():
    """
    Базовый тест: проверка, что ключевые зависимости проекта импортируются без ошибок.
    """
    try:
        import fastapi
        import aiogram
        import requests_oauthlib
    except ImportError as e:
        pytest.fail(f"Не удалось импортировать модуль: {e}")
