import pytest
from fastapi.testclient import TestClient

pytest.importorskip("frappe")

from ferum_customs.api import app

client: TestClient = TestClient(app)


def test_root_endpoint() -> None:
    """Test the root endpoint of the API to ensure it returns the expected welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the API!"
    }  # Example expected response


def test_root_endpoint_not_found() -> None:
    """Test the root endpoint for a non-existent route."""
    response = client.get("/non-existent")
    assert response.status_code == 404  # Expecting a 404 for non-existent route
