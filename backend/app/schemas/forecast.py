from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class MarineForecastHourResponse(BaseModel):
    observed_at: datetime
    wave_height_m: float | None
    wave_period_s: float | None
    water_temperature_c: float | None
    wind_speed_mps: float | None
    wind_direction_deg: float | None
    pressure_hpa: float | None


class TideExtremeResponse(BaseModel):
    occurs_at: datetime
    extreme_type: Literal["high", "low"]
    height_m: float | None


class ForecastDataQualityResponse(BaseModel):
    hours_requested: int = Field(ge=1, le=48)
    hours_returned: int = Field(ge=0, le=48)
    complete_hours: int = Field(ge=0, le=48)
    coverage_percentage: int = Field(ge=0, le=100)


class MarineForecastResponse(BaseModel):
    generated_at: datetime
    source: str
    hours: list[MarineForecastHourResponse]
    tides: list[TideExtremeResponse]
    warnings: list[str]
    data_quality: ForecastDataQualityResponse
