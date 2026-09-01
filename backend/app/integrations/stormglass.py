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

    def fetch_marine(
        self,
        latitude: float,
        longitude: float,
        at: datetime,
    ) -> MarineObservation:
        moment = at.astimezone(timezone.utc)
        payload = self.get_json(
            self.WEATHER_URL,
            params={
                "lat": latitude,
                "lng": longitude,
                "params": (
                    "waveHeight,wavePeriod,waterTemperature,"
                    "windSpeed,windDirection,pressure"
                ),
                "source": "sg",
                "start": _api_timestamp(moment - timedelta(hours=1)),
                "end": _api_timestamp(moment + timedelta(hours=2)),
            },
            headers=self.auth_headers,
            provider_name="Stormglass Weather",
        )
        return self.parse_marine(payload, at=moment)

    @staticmethod
    def parse_marine(payload: dict[str, Any], at: datetime) -> MarineObservation:
        hours = payload.get("hours")
        if not isinstance(hours, list) or not hours:
            raise ExternalAPIError("Stormglass não retornou previsão marítima horária.")

        valid_hours: list[tuple[datetime, dict[str, Any]]] = []
        for item in hours:
            if not isinstance(item, dict) or not isinstance(item.get("time"), str):
                continue
            try:
                valid_hours.append((_parse_timestamp(item["time"]), item))
            except ValueError:
                continue
        if not valid_hours:
            raise ExternalAPIError("Stormglass retornou horários marítimos inválidos.")

        moment = at.astimezone(timezone.utc)
        observed_at, closest = min(valid_hours, key=lambda pair: abs(pair[0] - moment))
        return MarineObservation(
            observed_at=observed_at,
            wave_height_m=_source_number(closest.get("waveHeight")),
            wave_period_s=_source_number(closest.get("wavePeriod")),
            water_temperature_c=_source_number(closest.get("waterTemperature")),
            wind_speed_mps=_source_number(closest.get("windSpeed")),
            wind_direction_deg=_source_number(closest.get("windDirection")),
            pressure_hpa=_source_number(closest.get("pressure")),
        )

    def fetch_tide_trend(
        self,
        latitude: float,
        longitude: float,
        at: datetime,
    ) -> TideTrend:
        moment = at.astimezone(timezone.utc)
        payload = self.get_json(
            self.TIDE_EXTREMES_URL,
            params={
                "lat": latitude,
                "lng": longitude,
                "start": _api_timestamp(moment - timedelta(hours=18)),
                "end": _api_timestamp(moment + timedelta(hours=18)),
                "datum": "MSL",
            },
            headers=self.auth_headers,
            provider_name="Stormglass Tide",
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
