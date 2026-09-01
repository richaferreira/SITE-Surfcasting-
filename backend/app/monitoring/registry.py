from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock


@dataclass
class ExternalProviderMetrics:
    requests: int = 0
    successes: int = 0
    failures: int = 0
    total_latency_ms: float = 0.0
    last_status_code: int | None = None
    last_error_code: str | None = None
    last_called_at: datetime | None = None


class MonitoringRegistry:
    """Bounded in-process metrics for the first backoffice dashboard."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.reset()

    def reset(self) -> None:
        with getattr(self, "_lock", Lock()):
            self.started_at = datetime.now(timezone.utc)
            self.http_requests = 0
            self.http_total_latency_ms = 0.0
            self.http_status_groups: Counter[str] = Counter()
            self.external: dict[str, ExternalProviderMetrics] = {}

    def record_http(self, status_code: int, latency_ms: float) -> None:
        group = f"{status_code // 100}xx"
        with self._lock:
            self.http_requests += 1
            self.http_total_latency_ms += latency_ms
            self.http_status_groups[group] += 1

    def record_external(
        self,
        provider: str,
        *,
        success: bool,
        latency_ms: float,
        status_code: int | None,
        error_code: str | None,
    ) -> None:
        with self._lock:
            metrics = self.external.setdefault(provider, ExternalProviderMetrics())
            metrics.requests += 1
            metrics.successes += int(success)
            metrics.failures += int(not success)
            metrics.total_latency_ms += latency_ms
            metrics.last_status_code = status_code
            metrics.last_error_code = error_code
            metrics.last_called_at = datetime.now(timezone.utc)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            providers = {
                name: {
                    "requests": item.requests,
                    "successes": item.successes,
                    "failures": item.failures,
                    "success_rate_percentage": round(item.successes / item.requests * 100, 1),
                    "average_latency_ms": round(item.total_latency_ms / item.requests, 1),
                    "last_status_code": item.last_status_code,
                    "last_error_code": item.last_error_code,
                    "last_called_at": item.last_called_at,
                }
                for name, item in self.external.items()
            }
            return {
                "started_at": self.started_at,
                "traffic": {
                    "requests": self.http_requests,
                    "average_latency_ms": (
                        round(self.http_total_latency_ms / self.http_requests, 1)
                        if self.http_requests
                        else 0.0
                    ),
                    "status_groups": dict(self.http_status_groups),
                },
                "external_apis": providers,
            }


monitoring_registry = MonitoringRegistry()
