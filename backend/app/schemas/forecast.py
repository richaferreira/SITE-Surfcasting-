from datetime import datetime

from pydantic import BaseModel, Field


class ForecastHour(BaseModel):
    at: datetime
    score: int = Field(ge=0, le=100)
    label: str
    wind_speed_mps: float | None
    wind_direction_deg: float | None
    wind_is_offshore: bool | None
    tide_trend: str
    wave_height_m: float | None
    wave_period_s: float | None
    water_temperature_c: float | None
    pressure_hpa: float | None
    moon_phase: str


class ForecastResponse(BaseModel):
    latitude: float
    longitude: float
    sea_bearing_deg: float
    generated_at: datetime
    hours: list[ForecastHour]
