from __future__ import annotations

from collections import defaultdict
import json
from threading import Lock
from time import perf_counter
from typing import Any
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self.requests_total = 0
        self.errors_total = 0
        self.total_latency_ms = 0.0
        self.by_status: dict[str, int] = defaultdict(int)
        self.providers: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {"requests": 0, "errors": 0, "latency_ms_total": 0.0}
        )

    def record_request(self, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self.requests_total += 1
            self.total_latency_ms += latency_ms
            self.by_status[str(status_code)] += 1
            if status_code >= 500:
                self.errors_total += 1

    def record_provider(self, provider: str, latency_ms: float, success: bool) -> None:
        with self._lock:
            item = self.providers[provider]
            item["requests"] = int(item["requests"]) + 1
            item["latency_ms_total"] = float(item["latency_ms_total"]) + latency_ms
            if not success:
                item["errors"] = int(item["errors"]) + 1

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            average = self.total_latency_ms / self.requests_total if self.requests_total else 0.0
            providers = {}
            for name, values in self.providers.items():
                requests = int(values["requests"])
                providers[name] = {
                    "requests": requests,
                    "errors": int(values["errors"]),
                    "average_latency_ms": round(float(values["latency_ms_total"]) / requests, 2) if requests else 0.0,
                }
            return {
                "requests_total": self.requests_total,
                "errors_total": self.errors_total,
                "error_rate": round(self.errors_total / self.requests_total, 4) if self.requests_total else 0.0,
                "average_latency_ms": round(average, 2),
                "by_status": dict(self.by_status),
                "providers": providers,
            }


metrics = MetricsRegistry()


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid4().hex
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            latency_ms = (perf_counter() - started) * 1000
            metrics.record_request(status_code, latency_ms)
            log = {
                "event": "http_request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": status_code,
                "duration_ms": round(latency_ms, 2),
            }
            print(json.dumps(log, ensure_ascii=False, separators=(",", ":")))
            if "response" in locals():
                response.headers["X-Request-ID"] = request_id
