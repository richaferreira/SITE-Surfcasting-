from datetime import datetime, timezone
from unittest.mock import Mock

from sqlalchemy.dialects import mysql

from app.core.exceptions import ExternalAPIError
from app.integrations.openweather import AtmosphericObservation
from app.repositories.beach import BeachRepository
from app.services.fishing_score import FishingScoreService


class WorkingOpenWeather:
    def fetch_current(self, latitude: float, longitude: float) -> AtmosphericObservation:
        del latitude, longitude
        return AtmosphericObservation(
            wind_speed_mps=5.0,
            wind_direction_deg=0.0,
            pressure_hpa=1016.0,
        )


class FailingStormglass:
    def fetch_marine(self, latitude: float, longitude: float, at: datetime):
        del latitude, longitude, at
        raise ExternalAPIError("Dados marítimos indisponíveis.")

    def fetch_tide_trend(self, latitude: float, longitude: float, at: datetime):
        del latitude, longitude, at
        raise ExternalAPIError("Maré indisponível.")


def test_geographic_point_uses_explicit_longitude_latitude_axis_order() -> None:
    expression = BeachRepository._location_expression(-22.93, -42.49)
    sql = str(
        expression.compile(
            dialect=mysql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )

    assert "ST_GeomFromText" in sql
    assert "POINT(-42.49000000 -22.93000000)" in sql
    assert "axis-order=long-lat" in sql


def test_score_is_suspended_when_ocean_data_is_missing() -> None:
    service = FishingScoreService(
        openweather=WorkingOpenWeather(),
        stormglass=FailingStormglass(),
    )

    result = service.calculate(
        latitude=-22.93,
        longitude=-42.49,
        sea_bearing_deg=180.0,
        at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )

    assert result["score"] is None
    assert result["label"] == "dados insuficientes"
    assert result["data_quality"]["is_sufficient"] is False
    assert {"tide", "wave_height", "wave_period"}.issubset(
        result["data_quality"]["missing_components"]
    )


def test_archive_unpublishes_without_hard_deleting() -> None:
    beach = Mock(is_published=True, deleted_at=None, deleted_by_id=None)
    repository = BeachRepository(Mock())

    repository.archive(beach, actor_id=7)

    assert beach.is_published is False
    assert beach.deleted_by_id == 7
    assert beach.deleted_at is not None
