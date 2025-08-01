import pytest

pytest.importorskip("frappe")

from fastapi.testclient import TestClient
from ferum_customs.api import app

client = TestClient(app)

def test_health_check() -> None:
    """Test the health check endpoint to ensure the service is running and returns the expected response."""
    response = client.get("/health")
    
    # Assert that the response status code is 200
    assert response.status_code == 200
    
    # Assert that the response JSON matches the expected structure
    assert response.json() == {"status": "healthy"}  # Assuming the expected response structure

    # Additional assertions can be added here to cover edge cases
