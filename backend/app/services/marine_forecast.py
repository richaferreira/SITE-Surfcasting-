from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.exceptions import ExternalAPIError
from app.integrations.stormglass import StormglassClient


class MarineForecastService:
    def __init__(self, stormglass: StormglassClient):
        self.stormglass = stormglass

    def get_forecast(
        self,
        latitude: float,
        longitude: float,
        hours: int,
        at: datetime | None = None,
    ) -> dict[str, Any]:
        moment = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
        warnings: list[str] = []

        observations = self.stormglass.fetch_marine_forecast(
            latitude=latitude,
            longitude=longitude,
            start=moment,
            hours=hours,
        )
        if not observations:
            raise ExternalAPIError(
                "Stormglass não retornou série marítima para o período solicitado."
            )

        try:
            tides = self.stormglass.fetch_tide_extremes(
                latitude=latitude,
                longitude=longitude,
                start=moment,
                hours=hours,
            )
        except ExternalAPIError as exc:
            warnings.append(str(exc))
            tides = []

        complete_hours = sum(
            1
            for item in observations
            if item.wave_height_m is not None
            and item.wave_period_s is not None
            and item.wind_speed_mps is not None
        )
        coverage_percentage = min(100, round(len(observations) / hours * 100))

        return {
            "generated_at": moment,
            "source": "Stormglass",
            "hours": [
                {
                    "observed_at": item.observed_at,
                    "wave_height_m": item.wave_height_m,
                    "wave_period_s": item.wave_period_s,
                    "water_temperature_c": item.water_temperature_c,
                    "wind_speed_mps": item.wind_speed_mps,
                    "wind_direction_deg": item.wind_direction_deg,
                    "pressure_hpa": item.pressure_hpa,
                }
                for item in observations
            ],
            "tides": [
                {
                    "occurs_at": item.occurs_at,
                    "extreme_type": item.extreme_type,
                    "height_m": item.height_m,
                }
                for item in tides
                if item.occurs_at >= moment
            ],
            "warnings": warnings,
            "data_quality": {
                "hours_requested": hours,
                "hours_returned": len(observations),
                "complete_hours": complete_hours,
                "coverage_percentage": coverage_percentage,
            },
        }
