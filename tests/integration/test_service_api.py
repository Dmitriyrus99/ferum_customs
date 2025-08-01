import pytest

pytest.importorskip("frappe")

from fastapi.testclient import TestClient
from ferum_customs.api import app

client = TestClient(app)

def test_health_check() -> None:
    """Test the health check endpoint to ensure the service is running."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}  # Assuming the expected response structure
