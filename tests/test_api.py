from fastapi.testclient import TestClient
from superagent.main import app


client = TestClient(app)


def test_health_does_not_expose_credentials():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "github_token" not in body
    assert "llm_api_key" not in body


def test_project_endpoint_returns_eleven_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) == 11


def test_dashboard_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "ERP Super Agent" in response.text
