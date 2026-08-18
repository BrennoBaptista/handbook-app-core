"""Exception handler central (API-001, Seção 7 — Tradução de Erros; RA-005,
Capítulos 125–126). Traduz qualquer erro — de domínio (AppError) ou nativo do
FastAPI/Starlette (HTTPException, RequestValidationError) — para o mesmo
contrato HTTP único. Sem isso, erros nativos (ex.: HTTPBearer sem token,
payload que falha na validação do Pydantic) escapariam com o formato padrão
do FastAPI (`{"detail": ...}`), violando API-001 Seção 7: "as três estruturas
nunca deverão ser misturadas entre si"."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from platform_core.shared.errors import AppError


def _error_response(
    request: Request, status_code: int, code: str, message: str, details: dict
) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", None)
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
                "trace_id": trace_id,
            }
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(
            request, exc.status_code, exc.code, exc.message, exc.details
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_response(
            request, exc.status_code, "HTTP_ERROR", str(exc.detail), {}
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "VALIDATION_ERROR",
            "The request payload failed validation.",
            {"errors": exc.errors()},
        )
