import pytest
from fastapi.testclient import TestClient

pytest.importorskip("frappe")

from ferum_customs.api import app

client = TestClient(app)

def test_root_endpoint() -> None:
    """Test the root endpoint of the API."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API!"}  # Example expected response
