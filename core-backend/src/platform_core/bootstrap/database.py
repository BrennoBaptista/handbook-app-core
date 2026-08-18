"""Conexão com o banco de dados (RA-005, Capítulo 66 — bootstrap/).
Composition Root para o engine/Session do SQLAlchemy — nenhum módulo deverá
criar seu próprio engine."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Valores de referência de RA-007, Seção 8 (Connection Pooling) — ajustáveis
# conforme carga real, nunca ausentes.
_POOL_SIZE = 10
_MAX_OVERFLOW = 5
_POOL_TIMEOUT_SECONDS = 30


def build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(
        database_url,
        pool_size=_POOL_SIZE,
        max_overflow=_MAX_OVERFLOW,
        pool_timeout=_POOL_TIMEOUT_SECONDS,
    )


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Dependency FastAPI — cada módulo que precisar de uma Session por
    requisição deverá usar `Depends(get_db_session)`, nunca instanciar uma
    Session diretamente (RA-005, Capítulo 67 — Composition Root)."""
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.db_session_factory
    )
    async with session_factory() as session:
        yield session
