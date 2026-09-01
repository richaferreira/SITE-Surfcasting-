from datetime import datetime, timezone

from app.domain.score import (
    EnvironmentalConditions,
    MoonPhase,
    TideTrend,
    angular_distance,
    calculate_fishing_score,
    is_offshore_wind,
    moon_phase_for,
)


def test_ideal_conditions_reach_one_hundred() -> None:
    conditions = EnvironmentalConditions(
        sea_bearing_deg=180.0,
        wind_speed_mps=5.0,
        wind_direction_deg=0.0,
        tide_trend=TideTrend.RISING,
        wave_height_m=1.2,
        wave_period_s=10.0,
        water_temperature_c=22.0,
        pressure_hpa=1016.0,
        moon_phase=MoonPhase.NEW,
    )

    result = calculate_fishing_score(conditions)

    assert result.score == 100
    assert result.label == "excelente"
    assert sum(result.breakdown.values()) == 100


def test_strong_onshore_wind_reduces_score() -> None:
    ideal = EnvironmentalConditions(
        sea_bearing_deg=180.0,
        wind_speed_mps=5.0,
        wind_direction_deg=0.0,
        tide_trend=TideTrend.RISING,
    )
    adverse = EnvironmentalConditions(
        sea_bearing_deg=180.0,
        wind_speed_mps=16.0,
        wind_direction_deg=180.0,
        tide_trend=TideTrend.FALLING,
    )

    assert calculate_fishing_score(ideal).score > calculate_fishing_score(adverse).score


def test_wind_direction_uses_from_direction_and_handles_wraparound() -> None:
    assert is_offshore_wind(wind_from_deg=350.0, sea_bearing_deg=170.0)
    assert not is_offshore_wind(wind_from_deg=170.0, sea_bearing_deg=170.0)
    assert angular_distance(350.0, 10.0) == 20.0


def test_known_epoch_is_new_moon() -> None:
    moment = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    assert moon_phase_for(moment) is MoonPhase.NEW
