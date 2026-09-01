from collections import deque
from threading import Lock
from time import monotonic


class SlidingWindowRateLimiter:
    def __init__(self, max_clients: int = 5000):
        self.max_clients = max_clients
        self._events: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str, *, limit: int, window_seconds: int = 60) -> bool:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events.setdefault(key, deque())
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return False
            events.append(now)
            if len(self._events) > self.max_clients:
                self._purge(cutoff, protected_key=key)
            return True

    def _purge(self, cutoff: float, protected_key: str) -> None:
        empty_keys: list[str] = []
        for key, events in self._events.items():
            while events and events[0] <= cutoff:
                events.popleft()
            if not events and key != protected_key:
                empty_keys.append(key)
        for key in empty_keys:
            self._events.pop(key, None)
        while len(self._events) > self.max_clients:
            oldest_key = next(key for key in self._events if key != protected_key)
            self._events.pop(oldest_key, None)

    def reset(self) -> None:
        with self._lock:
            self._events.clear()


public_rate_limiter = SlidingWindowRateLimiter()

