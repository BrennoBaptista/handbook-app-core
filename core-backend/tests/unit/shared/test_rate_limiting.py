import pytest

from platform_core.shared.rate_limiting import RateLimitExceededError, rate_limit


class FakeCache:
    """Test double em memória — mesma interface assíncrona usada de
    redis.asyncio.Redis (incr/expire/ttl)."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._ttls: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self._counters[key] = self._counters.get(key, 0) + 1
        return self._counters[key]

    async def expire(self, key: str, seconds: int) -> None:
        self._ttls[key] = seconds

    async def ttl(self, key: str) -> int:
        return self._ttls.get(key, -1)


class _FakeClient:
    def __init__(self, host: str) -> None:
        self.host = host


class _FakeAppState:
    def __init__(self, cache_client: FakeCache) -> None:
        self.cache_client = cache_client


class _FakeApp:
    def __init__(self, cache_client: FakeCache) -> None:
        self.state = _FakeAppState(cache_client)


class _FakeRequest:
    def __init__(self, cache_client: FakeCache, client_host: str = "1.2.3.4") -> None:
        self.app = _FakeApp(cache_client)
        self.client = _FakeClient(client_host)


async def test_rate_limit_when_under_threshold_should_not_raise():
    dependency = rate_limit(key="login", max_requests=3, window_seconds=900)
    cache = FakeCache()

    for _ in range(3):
        await dependency(_FakeRequest(cache))


async def test_rate_limit_when_exceeds_threshold_should_raise_rate_limit_exceeded_error():
    dependency = rate_limit(key="login", max_requests=3, window_seconds=900)
    cache = FakeCache()

    for _ in range(3):
        await dependency(_FakeRequest(cache))

    with pytest.raises(RateLimitExceededError):
        await dependency(_FakeRequest(cache))


async def test_rate_limit_when_different_identifiers_should_be_tracked_independently():
    dependency = rate_limit(key="login", max_requests=1, window_seconds=900)
    cache = FakeCache()

    await dependency(_FakeRequest(cache, client_host="1.1.1.1"))
    await dependency(_FakeRequest(cache, client_host="2.2.2.2"))


async def test_rate_limit_when_custom_identifier_provided_should_use_it():
    dependency = rate_limit(
        key="password-reset",
        max_requests=1,
        window_seconds=3600,
        identifier=lambda request: "fixed-account",
    )
    cache = FakeCache()

    await dependency(_FakeRequest(cache, client_host="1.1.1.1"))

    with pytest.raises(RateLimitExceededError):
        await dependency(_FakeRequest(cache, client_host="2.2.2.2"))
