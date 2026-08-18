"""Requer Postgres e Valkey reais em execução (docker-compose.yml de
referência, PB-006) — TEST-001, Seção 7: testes de integração validam contra
infraestrutura real, nunca apenas mocks. Também exercita, de ponta a ponta,
a composição real da aplicação (create_app(), lifespan, middlewares) — o que
os testes unitários de bootstrap/ não cobrem isoladamente."""

from fastapi.testclient import TestClient

from platform_core.bootstrap.app import create_app
from platform_core.bootstrap.settings import Settings

_settings = Settings(cors_allowed_origins=["http://localhost:5173"])
app = create_app(settings=_settings)


def test_health_live_should_return_ok():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_ready_should_check_database_and_cache_and_return_ok():
    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_security_headers_should_be_present_on_real_app():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.headers["content-security-policy"] == "default-src 'self'"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_cors_preflight_from_allowed_origin_should_be_accepted():
    with TestClient(app) as client:
        response = client.options(
            "/health/live",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_preflight_from_disallowed_origin_should_be_rejected():
    with TestClient(app) as client:
        response = client.options(
            "/health/live",
            headers={
                "Origin": "http://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert "access-control-allow-origin" not in response.headers
