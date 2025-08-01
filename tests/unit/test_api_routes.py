from fastapi.testclient import TestClient
from ferum_customs.api import app

client = TestClient(app)

def test_root_route() -> None:
    """Test the root endpoint of FastAPI, expecting a successful response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert response.headers["Content-Type"] == "application/json"

def test_health_route() -> None:
    """Test the health endpoint of FastAPI, expecting a healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["Content-Type"] == "application/json"

def test_non_existent_route() -> None:
    """Test a non-existent route to ensure it returns a 404 status."""
    response = client.get("/non-existent")
    assert response.status_code == 404
