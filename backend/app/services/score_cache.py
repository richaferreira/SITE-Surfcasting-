from copy import deepcopy
from threading import Lock
from time import monotonic
from typing import Any


class ScoreCache:
    def __init__(self) -> None:
        self._lock = Lock()
        self._items: dict[tuple[float, float, float], tuple[float, dict[str, Any]]] = {}

    def get(self, key: tuple[float, float, float]) -> dict[str, Any] | None:
        now = monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= now:
                self._items.pop(key, None)
                return None
            return deepcopy(value)

    def set(
        self,
        key: tuple[float, float, float],
        value: dict[str, Any],
        *,
        ttl_seconds: int,
        max_entries: int,
    ) -> None:
        now = monotonic()
        with self._lock:
            expired = [cache_key for cache_key, item in self._items.items() if item[0] <= now]
            for cache_key in expired:
                self._items.pop(cache_key, None)
            while len(self._items) >= max_entries:
                oldest_key = min(self._items, key=lambda item_key: self._items[item_key][0])
                self._items.pop(oldest_key, None)
            self._items[key] = (now + ttl_seconds, deepcopy(value))

    def reset(self) -> None:
        with self._lock:
            self._items.clear()


score_cache = ScoreCache()
