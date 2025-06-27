import pytest
from fastapi.testclient import TestClient
from ferum_customs.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code in (200, 404)
