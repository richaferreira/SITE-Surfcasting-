from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import ExternalAPIError
from app.domain.score import (
    EnvironmentalConditions,
    TideTrend,
    calculate_fishing_score,
    is_offshore_wind,
    moon_phase_for,
)
from app.integrations.openweather import AtmosphericObservation, OpenWeatherClient
from app.integrations.stormglass import MarineObservation, StormglassClient


class FishingScoreService:
    def __init__(
        self,
        openweather: OpenWeatherClient,
        stormglass: StormglassClient,
    ):
        self.openweather = openweather
        self.stormglass = stormglass

    def calculate(
        self,
        latitude: float,
        longitude: float,
        sea_bearing_deg: float,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        moment = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        warnings: list[str] = []

        atmosphere: AtmosphericObservation | None = None
        marine: MarineObservation | None = None
        tide_trend = TideTrend.UNKNOWN

        try:
            atmosphere = self.openweather.fetch_current(latitude, longitude)
        except ExternalAPIError as exc:
            warnings.append(str(exc))

        try:
            marine = self.stormglass.fetch_marine(latitude, longitude, at=moment)
        except ExternalAPIError as exc:
            warnings.append(str(exc))

        try:
            tide_trend = self.stormglass.fetch_tide_trend(latitude, longitude, at=moment)
        except ExternalAPIError as exc:
            warnings.append(str(exc))

        wind_speed = (
            atmosphere.wind_speed_mps
            if atmosphere is not None
            else marine.wind_speed_mps if marine is not None else None
        )
        wind_direction = (
            atmosphere.wind_direction_deg
            if atmosphere is not None
            else marine.wind_direction_deg if marine is not None else None
        )
        pressure = (
            atmosphere.pressure_hpa
            if atmosphere is not None
            else marine.pressure_hpa if marine is not None else None
        )

        if atmosphere is None and marine is None:
            raise ExternalAPIError(
                "Nenhum provedor retornou dados meteorológicos suficientes para o score."
            )

        phase = moon_phase_for(moment)
        conditions = EnvironmentalConditions(
            sea_bearing_deg=sea_bearing_deg,
            wind_speed_mps=wind_speed,
            wind_direction_deg=wind_direction,
            tide_trend=tide_trend,
            wave_height_m=marine.wave_height_m if marine else None,
            wave_period_s=marine.wave_period_s if marine else None,
            water_temperature_c=marine.water_temperature_c if marine else None,
            pressure_hpa=pressure,
            moon_phase=phase,
        )
        result = calculate_fishing_score(conditions)

        offshore = None
        if wind_direction is not None:
            offshore = is_offshore_wind(wind_direction, sea_bearing_deg)

        return {
            **result.as_dict(),
            "calculated_at": moment,
            "conditions": {
                "wind_speed_mps": wind_speed,
                "wind_direction_deg": wind_direction,
                "sea_bearing_deg": sea_bearing_deg,
                "wind_is_offshore": offshore,
                "tide_trend": tide_trend.value,
                "wave_height_m": marine.wave_height_m if marine else None,
                "wave_period_s": marine.wave_period_s if marine else None,
                "water_temperature_c": marine.water_temperature_c if marine else None,
                "pressure_hpa": pressure,
                "moon_phase": phase.value,
            },
            "warnings": warnings,
        }
