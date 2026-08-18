from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from platform_core.bootstrap.error_handling import register_exception_handlers
from platform_core.shared.errors import AppError


class _Payload(BaseModel):
    name: str


def _build_test_app() -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise AppError(
            code="SOMETHING_WRONG",
            message="Something went wrong.",
            status_code=422,
            details={"field": "x"},
        )

    @app.get("/native-http-error")
    def native_http_error() -> None:
        raise HTTPException(status_code=404, detail="Not found.")

    @app.post("/validated")
    def validated(payload: _Payload) -> dict[str, str]:
        return {"name": payload.name}

    return app


def test_app_error_should_be_translated_to_api001_error_contract():
    client = TestClient(_build_test_app())

    response = client.get("/boom")

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "SOMETHING_WRONG"
    assert body["error"]["message"] == "Something went wrong."
    assert body["error"]["details"] == {"field": "x"}
    assert "trace_id" in body["error"]


def test_native_http_exception_should_also_be_translated_to_api001_error_contract():
    client = TestClient(_build_test_app())

    response = client.get("/native-http-error")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "HTTP_ERROR"
    assert body["error"]["message"] == "Not found."


def test_request_validation_error_should_also_be_translated_to_api001_error_contract():
    client = TestClient(_build_test_app())

    response = client.post("/validated", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "errors" in body["error"]["details"]
