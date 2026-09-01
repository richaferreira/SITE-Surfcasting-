from datetime import datetime, timezone

from app.domain.score import TideTrend
from app.integrations.openweather import OpenWeatherClient
from app.integrations.stormglass import StormglassClient


def test_openweather_parser_extracts_required_fields() -> None:
    observation = OpenWeatherClient.parse_current(
        {
            "wind": {"speed": 4.5, "deg": 220},
            "main": {"pressure": 1018},
        }
    )

    assert observation.wind_speed_mps == 4.5
    assert observation.wind_direction_deg == 220.0
    assert observation.pressure_hpa == 1018.0


def test_stormglass_parser_prefers_sg_source_and_nearest_hour() -> None:
    target = datetime(2026, 9, 1, 12, 20, tzinfo=timezone.utc)
    observation = StormglassClient.parse_marine(
        {
            "hours": [
                {
                    "time": "2026-09-01T11:00:00+00:00",
                    "waveHeight": {"sg": 0.7},
                },
                {
                    "time": "2026-09-01T12:00:00+00:00",
                    "waveHeight": {"noaa": 1.1, "sg": 1.3},
                    "wavePeriod": {"sg": 9.0},
                    "waterTemperature": {"sg": 21.5},
                    "windSpeed": {"sg": 5.0},
                    "windDirection": {"sg": 210.0},
                    "pressure": {"sg": 1015.0},
                },
            ]
        },
        at=target,
    )

    assert observation.wave_height_m == 1.3
    assert observation.wave_period_s == 9.0
    assert observation.water_temperature_c == 21.5
    assert observation.observed_at.hour == 12


def test_tide_parser_detects_rising_and_falling_intervals() -> None:
    payload = {
        "data": [
            {"time": "2026-09-01T06:00:00+00:00", "type": "low", "height": -0.4},
            {"time": "2026-09-01T12:00:00+00:00", "type": "high", "height": 0.8},
            {"time": "2026-09-01T18:00:00+00:00", "type": "low", "height": -0.3},
        ]
    }

    rising = StormglassClient.parse_tide_trend(
        payload,
        at=datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc),
    )
    falling = StormglassClient.parse_tide_trend(
        payload,
        at=datetime(2026, 9, 1, 15, 0, tzinfo=timezone.utc),
    )

    assert rising is TideTrend.RISING
    assert falling is TideTrend.FALLING
