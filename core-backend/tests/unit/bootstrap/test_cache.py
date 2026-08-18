from redis.asyncio import Redis

from platform_core.bootstrap.cache import build_cache_client


def test_build_cache_client_should_return_redis_client_for_given_url():
    client = build_cache_client("redis://localhost:6379/0")

    assert isinstance(client, Redis)
