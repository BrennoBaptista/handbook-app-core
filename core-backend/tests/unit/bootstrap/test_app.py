from fastapi import APIRouter
from fastapi.testclient import TestClient

from platform_core.bootstrap.app import create_app
from platform_core.bootstrap.settings import Settings


def _settings_for_test() -> Settings:
    return Settings(service_name="test-app", environment="test")


def test_create_app_should_register_health_endpoints():
    app = create_app(settings=_settings_for_test())

    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_app_should_apply_security_headers():
    app = create_app(settings=_settings_for_test())

    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.headers["content-security-policy"] == "default-src 'self'"


def test_create_app_should_register_consumer_routers():
    router = APIRouter()

    @router.get("/products")
    def list_products() -> dict[str, list]:
        return {"data": []}

    app = create_app(settings=_settings_for_test(), routers=[router])

    with TestClient(app) as client:
        response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_create_app_when_settings_omitted_should_use_get_settings():
    app = create_app()

    assert app.title == "backend"
