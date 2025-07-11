from fastapi.testclient import TestClient

from ferum_customs.api import app

client = TestClient(app)


def test_root_route() -> None:
    """Проверка корневого эндпоинта FastAPI."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_health_route() -> None:
    """Проверка эндпоинта health FastAPI."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
