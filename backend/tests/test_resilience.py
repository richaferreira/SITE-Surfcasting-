from app.core.rate_limit import SlidingWindowRateLimiter
from app.services.score_cache import ScoreCache


def test_rate_limiter_blocks_requests_above_window_quota() -> None:
    limiter = SlidingWindowRateLimiter()

    assert limiter.allow("score:client", limit=2)
    assert limiter.allow("score:client", limit=2)
    assert limiter.allow("score:client", limit=2) is False
    assert limiter.allow("score:another-client", limit=2)


def test_score_cache_returns_copy_and_evicts_oldest_entry() -> None:
    cache = ScoreCache()
    first = {"score": 80, "warnings": []}
    cache.set((1.0, 2.0, 3.0), first, ttl_seconds=60, max_entries=1)

    cached = cache.get((1.0, 2.0, 3.0))
    assert cached == first
    assert cached is not first
    cached["warnings"].append("mutated")
    assert cache.get((1.0, 2.0, 3.0))["warnings"] == []

    cache.set((4.0, 5.0, 6.0), {"score": 50}, ttl_seconds=60, max_entries=1)
    assert cache.get((1.0, 2.0, 3.0)) is None
    assert cache.get((4.0, 5.0, 6.0)) == {"score": 50}
