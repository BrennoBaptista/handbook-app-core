from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from platform_core.bootstrap.database import build_engine, build_session_factory

_DATABASE_URL = "postgresql+asyncpg://app:app@localhost:5432/app"


def test_build_engine_should_return_async_engine_configured_per_ra007():
    engine = build_engine(_DATABASE_URL)

    assert isinstance(engine, AsyncEngine)
    assert engine.pool.size() == 10
    assert engine.url.database == "app"


def test_build_session_factory_should_produce_async_sessions():
    engine = build_engine(_DATABASE_URL)
    session_factory = build_session_factory(engine)

    session = session_factory()

    assert isinstance(session, AsyncSession)
