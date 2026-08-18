"""Lifecycle da aplicação (RA-005, Capítulo 66) — inicialização e
encerramento de recursos."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from platform_core.bootstrap.cache import build_cache_client
from platform_core.bootstrap.container import build_validate_access_token_use_case
from platform_core.bootstrap.database import build_engine, build_session_factory
from platform_core.bootstrap.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()

    http_client = httpx.AsyncClient(timeout=5.0)
    app.state.http_client = http_client
    app.state.validate_access_token_use_case = build_validate_access_token_use_case(
        http_client
    )

    engine = build_engine(settings.database_url)
    app.state.db_engine = engine
    app.state.db_session_factory = build_session_factory(engine)

    app.state.cache_client = build_cache_client(settings.valkey_url)

    yield

    await http_client.aclose()
    await engine.dispose()
    await app.state.cache_client.aclose()
