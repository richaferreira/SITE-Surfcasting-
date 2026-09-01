from datetime import datetime

from pydantic import BaseModel


class TrafficMetricsResponse(BaseModel):
    requests: int
    average_latency_ms: float
    status_groups: dict[str, int]


class ExternalProviderMetricsResponse(BaseModel):
    requests: int
    successes: int
    failures: int
    success_rate_percentage: float
    average_latency_ms: float
    last_status_code: int | None
    last_error_code: str | None
    last_called_at: datetime | None


class MonitoringSummaryResponse(BaseModel):
    started_at: datetime
    traffic: TrafficMetricsResponse
    external_apis: dict[str, ExternalProviderMetricsResponse]

