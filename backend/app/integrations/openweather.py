from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from app.core.exceptions import ExternalAPIError
from app.integrations.http import JsonHttpClient


@dataclass(frozen=True, slots=True)
class AtmosphericObservation:
    wind_speed_mps: float
    wind_direction_deg: float
    pressure_hpa: float


class OpenWeatherClient(JsonHttpClient):
    CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(
        self,
        api_key: str,
        timeout_seconds: float = 10.0,
        session: requests.Session | None = None,
    ):
        super().__init__(timeout_seconds=timeout_seconds, session=session)
        self.api_key = api_key

    def fetch_current(self, latitude: float, longitude: float) -> AtmosphericObservation:
        if not self.api_key:
            raise ExternalAPIError("OPENWEATHER_API_KEY não configurada.")

        payload = self.get_json(
            self.CURRENT_WEATHER_URL,
            params={
                "lat": latitude,
                "lon": longitude,
                "appid": self.api_key,
                "units": "metric",
                "lang": "pt_br",
            },
            provider_name="OpenWeather",
        )
        return self.parse_current(payload)

    @staticmethod
    def parse_current(payload: dict[str, Any]) -> AtmosphericObservation:
        try:
            wind = payload["wind"]
            main = payload["main"]
            return AtmosphericObservation(
                wind_speed_mps=float(wind["speed"]),
                wind_direction_deg=float(wind["deg"]),
                pressure_hpa=float(main["pressure"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ExternalAPIError("OpenWeather retornou campos meteorológicos incompletos.") from exc
