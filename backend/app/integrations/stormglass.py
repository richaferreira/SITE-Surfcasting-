from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from app.core.exceptions import ExternalAPIError
from app.domain.score import TideTrend
from app.integrations.http import JsonHttpClient


@dataclass(frozen=True, slots=True)
class MarineObservation:
    observed_at: datetime
    wave_height_m: float | None
    wave_period_s: float | None
    water_temperature_c: float | None
    wind_speed_mps: float | None
    wind_direction_deg: float | None
    pressure_hpa: float | None


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _api_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _source_number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if not isinstance(value, dict):
        return None
    preferred = value.get("sg")
    if isinstance(preferred, (int, float)) and not isinstance(preferred, bool):
        return float(preferred)
    for candidate in value.values():
        if isinstance(candidate, (int, float)) and not isinstance(candidate, bool):
            return float(candidate)
    return None


def _observation_from_hour(item: dict[str, Any]) -> MarineObservation | None:
    timestamp = item.get("time")
    if not isinstance(timestamp, str):
        return None
    try:
        observed_at = _parse_timestamp(timestamp)
    except ValueError:
        return None
    return MarineObservation(
        observed_at=observed_at,
        wave_height_m=_source_number(item.get("waveHeight")),
        wave_period_s=_source_number(item.get("wavePeriod")),
        water_temperature_c=_source_number(item.get("waterTemperature")),
        wind_speed_mps=_source_number(item.get("windSpeed")),
        wind_direction_deg=_source_number(item.get("windDirection")),
        pressure_hpa=_source_number(item.get("pressure")),
    )


class StormglassClient(JsonHttpClient):
    WEATHER_URL = "https://api.stormglass.io/v2/weather/point"
    TIDE_EXTREMES_URL = "https://api.stormglass.io/v2/tide/extremes/point"

    def __init__(
        self,
        api_key: str,
        timeout_seconds: float = 10.0,
        session: requests.Session | None = None,
    ):
        super().__init__(timeout_seconds=timeout_seconds, session=session)
        self.api_key = api_key

    @property
    def auth_headers(self) -> dict[str, str]:
        if not self.api_key:
            raise ExternalAPIError("STORMGLASS_API_KEY não configurada.")
        return {"Authorization": self.api_key}

    def _fetch_weather_payload(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        return self.get_json(
            self.WEATHER_URL,
            params={
                "lat": latitude,
                "lng": longitude,
                "params": (
                    "waveHeight,wavePeriod,waterTemperature,"
                    "windSpeed,windDirection,pressure"
                ),
                "source": "sg",
                "start": _api_timestamp(start),
                "end": _api_timestamp(end),
            },
            headers=self.auth_headers,
            provider_name="Stormglass Weather",
        )

    def fetch_marine(
        self,
        latitude: float,
        longitude: float,
        at: datetime,
    ) -> MarineObservation:
        moment = at.astimezone(timezone.utc)
        payload = self._fetch_weather_payload(
            latitude,
            longitude,
            moment - timedelta(hours=1),
            moment + timedelta(hours=2),
        )
        return self.parse_marine(payload, at=moment)

    def fetch_marine_forecast(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        hours: int = 24,
    ) -> list[MarineObservation]:
        moment = start.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0)
        payload = self._fetch_weather_payload(
            latitude,
            longitude,
            moment,
            moment + timedelta(hours=hours),
        )
        return self.parse_marine_forecast(payload, start=moment, hours=hours)

    @staticmethod
    def parse_marine_forecast(
        payload: dict[str, Any],
        start: datetime,
        hours: int,
    ) -> list[MarineObservation]:
        raw_hours = payload.get("hours")
        if not isinstance(raw_hours, list) or not raw_hours:
            raise ExternalAPIError("Stormglass não retornou previsão marítima horária.")

        start_utc = start.astimezone(timezone.utc)
        end_utc = start_utc + timedelta(hours=hours)
        observations = [
            observation
            for item in raw_hours
            if isinstance(item, dict)
            for observation in [_observation_from_hour(item)]
            if observation is not None and start_utc <= observation.observed_at <= end_utc
        ]
        observations.sort(key=lambda observation: observation.observed_at)
        if not observations:
            raise ExternalAPIError("Stormglass retornou horários marítimos inválidos.")
        return observations

    @staticmethod
    def parse_marine(payload: dict[str, Any], at: datetime) -> MarineObservation:
        observations = StormglassClient.parse_marine_forecast(payload, start=at - timedelta(hours=3), hours=6)
        moment = at.astimezone(timezone.utc)
        return min(observations, key=lambda observation: abs(observation.observed_at - moment))

    def fetch_tide_extremes_payload(
        self,
        latitude: float,
        longitude: float,
        start: datetime,
        end: datetime,
    ) -> dict[str, Any]:
        return self.get_json(
            self.TIDE_EXTREMES_URL,
            params={
                "lat": latitude,
                "lng": longitude,
                "start": _api_timestamp(start),
                "end": _api_timestamp(end),
                "datum": "MSL",
            },
            headers=self.auth_headers,
            provider_name="Stormglass Tide",
        )

    def fetch_tide_trend(
        self,
        latitude: float,
        longitude: float,
        at: datetime,
    ) -> TideTrend:
        moment = at.astimezone(timezone.utc)
        payload = self.fetch_tide_extremes_payload(
            latitude,
            longitude,
            moment - timedelta(hours=18),
            moment + timedelta(hours=18),
        )
        return self.parse_tide_trend(payload, at=moment)

    @staticmethod
    def parse_tide_trend(payload: dict[str, Any], at: datetime) -> TideTrend:
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            return TideTrend.UNKNOWN

        extremes: list[tuple[datetime, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            timestamp = item.get("time")
            extreme_type = str(item.get("type", "")).lower()
            if not isinstance(timestamp, str) or extreme_type not in {"high", "low"}:
                continue
            try:
                extremes.append((_parse_timestamp(timestamp), extreme_type))
            except ValueError:
                continue

        if not extremes:
            return TideTrend.UNKNOWN
        extremes.sort(key=lambda item: item[0])
        moment = at.astimezone(timezone.utc)
        previous = next((item for item in reversed(extremes) if item[0] <= moment), None)
        upcoming = next((item for item in extremes if item[0] > moment), None)

        if previous and upcoming:
            if previous[1] == "low" and upcoming[1] == "high":
                return TideTrend.RISING
            if previous[1] == "high" and upcoming[1] == "low":
                return TideTrend.FALLING
        if upcoming:
            return TideTrend.RISING if upcoming[1] == "high" else TideTrend.FALLING
        return TideTrend.UNKNOWN
