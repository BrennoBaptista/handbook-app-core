"""Fábrica da aplicação FastAPI (RA-005, Capítulo 68) — Composition Root
genérico do Núcleo Compartilhado.

A aplicação consumidora deverá chamar `create_app()` e registrar seus
próprios routers de domínio via o parâmetro `routers`, ou com
`app.include_router(...)` sobre o app retornado. Este pacote nunca importa
nem conhece nenhum módulo de domínio — é isso que o mantém reutilizável
por qualquer aplicação derivada da plataforma."""

from __future__ import annotations

from collections.abc import Iterable

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from platform_core.bootstrap.error_handling import register_exception_handlers
from platform_core.bootstrap.lifecycle import lifespan
from platform_core.bootstrap.logging_config import configure_logging
from platform_core.bootstrap.middleware import CorrelationIdMiddleware
from platform_core.bootstrap.security_headers import SecurityHeadersMiddleware
from platform_core.bootstrap.settings import Settings, get_settings
from platform_core.shared.errors import AppError
from platform_core.shared.logging import get_logger

logger = get_logger(__name__)


def create_app(
    *,
    settings: Settings | None = None,
    routers: Iterable[APIRouter] = (),
) -> FastAPI:
    """Constrói a aplicação com bootstrap completo (logging, lifecycle,
    middlewares, exception handlers, health checks) já conectado.

    `settings`: injete uma instância própria (ex.: de uma subclasse de
    `Settings` com campos adicionais específicos da aplicação) quando os
    valores padrão de `get_settings()` não bastarem.

    `routers`: routers de domínio da aplicação consumidora, registrados
    depois do bootstrap e antes dos health checks — equivalente a chamar
    `app.include_router(...)` manualmente após `create_app()`.
    """
    settings = settings or get_settings()
    configure_logging(settings.service_name, settings.environment)
    app = FastAPI(title=settings.service_name, lifespan=lifespan)

    # Ordem de registro importa: o middleware adicionado por último é o mais
    # externo (primeiro a ver a requisição) — CORS por último para que o
    # preflight seja respondido antes de qualquer outra camada.
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    for router in routers:
        app.include_router(router)

    @app.get("/health/live")
    async def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready() -> dict[str, str]:
        # RA-005, Seção 466 (Dependency Health) — readiness verifica as
        # dependências que a aplicação já possui: banco e cache.
        try:
            async with app.state.db_session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            logger.error(
                "Database dependency unreachable",
                extra={"event": "dependency_unavailable"},
            )
            raise AppError(
                code="DEPENDENCY_UNAVAILABLE",
                message="A required dependency is not reachable.",
                status_code=503,
                details={"dependency": "database"},
            ) from exc

        try:
            await app.state.cache_client.ping()
        except Exception as exc:
            logger.error(
                "Cache dependency unreachable",
                extra={"event": "dependency_unavailable"},
            )
            raise AppError(
                code="DEPENDENCY_UNAVAILABLE",
                message="A required dependency is not reachable.",
                status_code=503,
                details={"dependency": "cache"},
            ) from exc

        return {"status": "ok"}

    return app
