from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from platform_core.bootstrap.middleware import CorrelationIdMiddleware
from platform_core.shared.logging.context import trace_id_var


def _build_test_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/ping")
    def ping(request: Request) -> dict[str, str | None]:
        return {
            "trace_id": request.state.trace_id,
            "context_trace_id": trace_id_var.get(),
        }

    return app


def test_correlation_id_when_no_header_provided_should_generate_and_echo_trace_id():
    client = TestClient(_build_test_app())

    response = client.get("/ping")

    body_trace_id = response.json()["trace_id"]
    assert response.headers["x-trace-id"] == body_trace_id
    assert len(body_trace_id) > 0


def test_correlation_id_when_header_provided_should_reuse_it():
    client = TestClient(_build_test_app())

    response = client.get("/ping", headers={"x-trace-id": "fixed-trace-id"})

    assert response.json()["trace_id"] == "fixed-trace-id"
    assert response.headers["x-trace-id"] == "fixed-trace-id"


def test_correlation_id_should_also_be_available_via_contextvar_during_request():
    client = TestClient(_build_test_app())

    response = client.get("/ping", headers={"x-trace-id": "fixed-trace-id"})

    assert response.json()["context_trace_id"] == "fixed-trace-id"


def test_correlation_id_contextvar_should_be_reset_after_request():
    client = TestClient(_build_test_app())

    client.get("/ping", headers={"x-trace-id": "fixed-trace-id"})

    assert trace_id_var.get() is None
