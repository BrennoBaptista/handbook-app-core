"""Conexão com o Valkey (OTS-001, Seção 7.5; RA-005, Capítulo 66 —
bootstrap/). `redis-py` conecta-se a um servidor Valkey sem alteração de
código — wire-compatible (OTS-001, Seção 8.3)."""

from __future__ import annotations

from redis.asyncio import Redis


def build_cache_client(valkey_url: str) -> Redis:
    return Redis.from_url(valkey_url, decode_responses=True)
