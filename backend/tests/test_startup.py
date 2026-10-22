from fastapi.testclient import TestClient
from backend.app.core.config import settings


def test_root_endpoint(client: TestClient):
    """Test root endpoint provides service info and documentation links."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs"] == "/docs"
    assert data["version"] == settings.APP_VERSION


def test_health_endpoint_root(client: TestClient):
    """Test GET /health returns 200 and healthy database status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.APP_NAME
    assert data["database"]["connected"] is True
    assert data["database"]["database"] in ["sqlite", "postgresql"]


def test_health_endpoint_api_prefix(client: TestClient):
    """Test GET /api/health also returns 200 and database connectivity status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["status"] == "healthy"
