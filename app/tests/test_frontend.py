from fastapi.testclient import TestClient


def test_frontend_is_served(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="es"' in response.text
    assert 'id="auth-template"' in response.text
    assert 'aria-live="polite"' in response.text


def test_static_assets_are_served(client: TestClient) -> None:
    css = client.get("/static/styles.css")
    script = client.get("/static/app.js")
    assert css.status_code == 200
    assert "text/css" in css.headers["content-type"]
    assert script.status_code == 200
    assert "javascript" in script.headers["content-type"]


def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "CRM API is running"}
