from datetime import datetime, timezone

from app.core.exceptions import ExternalAPIError
from app.integrations.stormglass import MarineObservation, TideExtreme
from app.services.marine_forecast import MarineForecastService


class FakeStormglass:
    def fetch_marine_forecast(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        hours: int,
    ) -> list[MarineObservation]:
        del latitude, longitude, start, hours
        return [
            MarineObservation(
                observed_at=datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
                wave_height_m=1.2,
                wave_period_s=9.0,
                water_temperature_c=22.0,
                wind_speed_mps=4.0,
                wind_direction_deg=210.0,
                pressure_hpa=1016.0,
            ),
            MarineObservation(
                observed_at=datetime(2026, 9, 1, 13, 0, tzinfo=timezone.utc),
                wave_height_m=1.3,
                wave_period_s=9.5,
                water_temperature_c=22.0,
                wind_speed_mps=4.3,
                wind_direction_deg=215.0,
                pressure_hpa=1015.0,
            ),
        ]

    def fetch_tide_extremes(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        hours: int,
    ) -> list[TideExtreme]:
        del latitude, longitude, hours
        return [
            TideExtreme(
                occurs_at=start.replace(hour=15, minute=0, second=0, microsecond=0),
                extreme_type="high",
                height_m=0.9,
            )
        ]


class TideFailingStormglass(FakeStormglass):
    def fetch_tide_extremes(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        hours: int,
    ) -> list[TideExtreme]:
        del latitude, longitude, start, hours
        raise ExternalAPIError("Maré temporariamente indisponível.")


def test_forecast_service_returns_hourly_data_and_next_tide() -> None:
    at = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    result = MarineForecastService(FakeStormglass()).get_forecast(
        latitude=-22.97,
        longitude=-42.03,
        hours=6,
        at=at,
    )

    assert result["source"] == "Stormglass"
    assert len(result["hours"]) == 2
    assert result["tides"][0]["extreme_type"] == "high"
    assert result["data_quality"]["hours_returned"] == 2
    assert result["data_quality"]["complete_hours"] == 2
    assert result["data_quality"]["coverage_percentage"] == 33


def test_forecast_service_keeps_weather_when_tide_provider_fails() -> None:
    at = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)
    result = MarineForecastService(TideFailingStormglass()).get_forecast(
        latitude=-22.97,
        longitude=-42.03,
        hours=6,
        at=at,
    )

    assert len(result["hours"]) == 2
    assert result["tides"] == []
    assert result["warnings"] == ["Maré temporariamente indisponível."]
