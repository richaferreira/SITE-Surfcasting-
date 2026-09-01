from app.monitoring.registry import MonitoringRegistry


def test_monitoring_registry_aggregates_traffic_and_external_apis() -> None:
    registry = MonitoringRegistry()
    registry.record_http(200, 10.0)
    registry.record_http(503, 30.0)
    registry.record_external(
        "Stormglass Weather",
        success=True,
        latency_ms=80.0,
        status_code=200,
        error_code=None,
    )
    registry.record_external(
        "Stormglass Weather",
        success=False,
        latency_ms=120.0,
        status_code=429,
        error_code="http_error",
    )

    snapshot = registry.snapshot()
    assert snapshot["traffic"]["requests"] == 2
    assert snapshot["traffic"]["average_latency_ms"] == 20.0
    assert snapshot["traffic"]["status_groups"] == {"2xx": 1, "5xx": 1}
    stormglass = snapshot["external_apis"]["Stormglass Weather"]
    assert stormglass["requests"] == 2
    assert stormglass["success_rate_percentage"] == 50.0
    assert stormglass["average_latency_ms"] == 100.0
    assert stormglass["last_error_code"] == "http_error"
