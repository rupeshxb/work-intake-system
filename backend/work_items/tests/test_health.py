# Smoke test: verifies the health check endpoint returns 200 and correct payload.
from rest_framework.test import APIClient


def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
