from fastapi import FastAPI
from fastapi.testclient import TestClient

from platform_core.bootstrap.security_headers import SecurityHeadersMiddleware


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/ping")
    def ping() -> dict[str, bool]:
        return {"ok": True}

    return app


def test_security_headers_when_http_should_apply_static_headers_without_hsts():
    client = TestClient(_build_test_app())

    response = client.get("/ping")

    assert response.headers["content-security-policy"] == "default-src 'self'"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert "permissions-policy" in response.headers
    assert "strict-transport-security" not in response.headers


def test_security_headers_when_https_should_also_include_hsts():
    client = TestClient(_build_test_app(), base_url="https://testserver")

    response = client.get("/ping")

    assert (
        response.headers["strict-transport-security"]
        == "max-age=31536000; includeSubDomains"
    )
