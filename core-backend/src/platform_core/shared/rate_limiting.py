"""Mecanismo de rate limiting (SEC-001, Seção 9) disponível como
infraestrutura transversal — abstração técnica fundamental (RA-005, Seção
65.1), não regra de negócio. Os limites concretos por endpoint (quantas
tentativas, em qual janela) são decisão de cada aplicação consumidora, não
deste arquivo.

Janela fixa (fixed window) via INCR+EXPIRE no Valkey — toda chave possui TTL
obrigatório (RA-007, RN-DB-004)."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Request

from platform_core.shared.errors import AppError


class RateLimitExceededError(AppError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Try again later.",
            status_code=429,
            details={"retry_after_seconds": retry_after_seconds},
        )


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def rate_limit(
    key: str,
    max_requests: int,
    window_seconds: int,
    identifier: Callable[[Request], str] = _client_ip,
):
    """Dependency factory do FastAPI.

    `key` identifica a regra (ex.: "login", "password-reset" — SEC-001,
    Seção 9). `identifier` resolve quem está sendo limitado — por padrão o
    IP do chamador; combine IP+usuário ou conta específica passando uma
    função própria quando a regra exigir (ex.: "5 tentativas/15min por
    combinação IP+usuário" para login)."""

    async def _dependency(request: Request) -> None:
        cache = request.app.state.cache_client
        redis_key = f"rate-limit:{key}:{identifier(request)}"

        current = await cache.incr(redis_key)
        if current == 1:
            await cache.expire(redis_key, window_seconds)

        if current > max_requests:
            ttl = await cache.ttl(redis_key)
            raise RateLimitExceededError(retry_after_seconds=max(ttl, 0))

    return _dependency
