from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_docs_available() -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "E-commerce Whitelabel API" in response.json()["info"]["title"]
