from fastapi.testclient import TestClient

from ferum_customs.api import app

client = TestClient(app)


def test_root_route() -> None:
    """Test the root endpoint of FastAPI, expecting a successful response with a JSON payload."""
    response = client.get("/")
    assert response.status_code == 200, "Expected status code 200 for root route"
    assert response.json() == {"ok": True}, "Expected JSON response to be {'ok': True}"
    assert (
        response.headers["Content-Type"] == "application/json"
    ), "Expected Content-Type to be application/json"


def test_health_route() -> None:
    """Test the health endpoint of FastAPI, expecting a healthy status response."""
    response = client.get("/health")
    assert response.status_code == 200, "Expected status code 200 for health route"
    assert response.json() == {
        "status": "ok"
    }, "Expected JSON response to be {'status': 'ok'}"
    assert (
        response.headers["Content-Type"] == "application/json"
    ), "Expected Content-Type to be application/json"


def test_non_existent_route() -> None:
    """Test a non-existent route to ensure it returns a 404 status."""
    response = client.get("/non-existent")
    assert (
        response.status_code == 404
    ), "Expected status code 404 for non-existent route"
