from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.core.exceptions import ExternalAPIError
from app.domain.score import EnvironmentalConditions, calculate_fishing_score, is_offshore_wind, moon_phase_for
from app.integrations.stormglass import StormglassClient
from app.schemas.forecast import ForecastHour, ForecastResponse

router = APIRouter(prefix="/forecast", tags=["Previsão"])


@router.get("", response_model=ForecastResponse)
def hourly_forecast(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    sea_bearing_deg: float = Query(ge=0, lt=360),
    hours: int = Query(default=24, ge=6, le=48),
) -> ForecastResponse:
    settings = get_settings()
    client = StormglassClient(
        api_key=settings.stormglass_api_key,
        timeout_seconds=settings.request_timeout_seconds,
    )
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

    try:
        marine_hours = client.fetch_marine_forecast(latitude, longitude, start=now, hours=hours)
        tide_payload = client.fetch_tide_extremes_payload(
            latitude,
            longitude,
            start=now - timedelta(hours=18),
            end=now + timedelta(hours=hours + 18),
        )
    except ExternalAPIError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    result_hours: list[ForecastHour] = []
    for marine in marine_hours:
        tide = client.parse_tide_trend(tide_payload, at=marine.observed_at)
        moon = moon_phase_for(marine.observed_at)
        conditions = EnvironmentalConditions(
            sea_bearing_deg=sea_bearing_deg,
            wind_speed_mps=marine.wind_speed_mps,
            wind_direction_deg=marine.wind_direction_deg,
            tide_trend=tide,
            wave_height_m=marine.wave_height_m,
            wave_period_s=marine.wave_period_s,
            water_temperature_c=marine.water_temperature_c,
            pressure_hpa=marine.pressure_hpa,
            moon_phase=moon,
        )
        score = calculate_fishing_score(conditions)
        offshore = (
            is_offshore_wind(marine.wind_direction_deg, sea_bearing_deg)
            if marine.wind_direction_deg is not None
            else None
        )
        result_hours.append(
            ForecastHour(
                at=marine.observed_at,
                score=score.score,
                label=score.label,
                wind_speed_mps=marine.wind_speed_mps,
                wind_direction_deg=marine.wind_direction_deg,
                wind_is_offshore=offshore,
                tide_trend=tide.value,
                wave_height_m=marine.wave_height_m,
                wave_period_s=marine.wave_period_s,
                water_temperature_c=marine.water_temperature_c,
                pressure_hpa=marine.pressure_hpa,
                moon_phase=moon.value,
            )
        )

    return ForecastResponse(
        latitude=latitude,
        longitude=longitude,
        sea_bearing_deg=sea_bearing_deg,
        generated_at=datetime.now(UTC),
        hours=result_hours,
    )
